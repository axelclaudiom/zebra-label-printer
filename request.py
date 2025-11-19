import argparse
import sys
import requests

codigo1 = "BOR0003"

def fetch_data(codigo):
    """Fetch article data by COD_STA11. Returns a dict (first item if API returns a list)."""
    url = 'https://apitango.venialacocina.com.ar/api/articulos?cod_sta11=' + codigo
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, list):
        return data[0] if data else {}
    return data or {}

def _get_field(item, *keys):
    """Return first existing non-empty value from item for provided keys (case-insensitive)."""
    if not item:
        return None
    for k in keys:
        v = item.get(k)
        if v:
            return v
        v = item.get(k.upper()) or item.get(k.lower())
        if v:
            return v
    return None

def generate_zpl(item: dict) -> str:
    """Generate ZPL (Code128) label from an item dict.

    Returns a complete ZPL document string ready to send to a Zebra printer.
    """
    if not item:
        return ''

    desc = _get_field(item, 'DESCRIPCIO', 'DESCRIP', 'DESCRIPCION') or ''
    sku = _get_field(item, 'COD_STA11', 'COD_STA11', 'cod_sta11') or ''
    barra = _get_field(item, 'COD_BARRA', 'CODBARRA', 'cod_barra') or ''
    barcode = barra if barra else sku

    desc = ' '.join(str(desc).splitlines())
    sku = str(sku)
    barcode = str(barcode)

    zpl = (
        '^XA^CI28\n'
        '^LH0,0\n'
        '^FO65,18^BY2,,0^BCN,54,N,N^FD{barcode}^FS\n'
        '^FO145,80^A0N,20,25^FH^FD{barcode}^FS\n'
        '^FO146,80^A0N,20,25^FH^FD{barcode}^FS\n'
        '^FO22,115^A0N,18,18^FB380,2,0,L^FH^FD{desc}^FS\n'
        '^FO22,170^A0N,18,18^FH^FDSKU: {sku}^FS\n'
        '^CI28\n'
        '^XZ'
    ).format(barcode=barcode, sku=sku, desc=desc)

    return zpl

def send_labels_to_printer(zpl_labels):
    """Send generated ZPL labels to the Zebra printer."""
    printer = ZebraPrinterConnector()
    try:
        printer.connect()
        printer.send_data(zpl_labels)
    except Exception as e:
        print(f'Error sending labels to printer: {e}', file=sys.stderr)
    finally:
        printer.disconnect()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch article and generate ZPL labels')
    parser.add_argument('-c', '--codigo', default=codigo1, help='COD_STA11 to search')
    parser.add_argument('-n', '--count', type=int, default=1, help='Number of labels to generate')
    args = parser.parse_args()

    try:
        item = fetch_data(args.codigo)
    except Exception as e:
        print(f'Error fetching data for {args.codigo}: {e}', file=sys.stderr)
        sys.exit(1)

    if not item:
        print(f'No item found for codigo: {args.codigo}', file=sys.stderr)
        sys.exit(1)

    labels = ''.join(generate_zpl(item) for _ in range(max(1, args.count)))
    send_labels_to_printer(labels)
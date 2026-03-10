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


def fetch_price_for_list(article_id, list_number=2):
    """Fetch price from GVA17 where NRO_DE_LIS matches list_number."""
    if not article_id:
        return None

    url = f'https://apitango.venialacocina.com.ar/api/precios/{article_id}'
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    data = resp.json() or {}

    value = data.get('value') if isinstance(data, dict) else {}
    value = value or {}
    gva17 = value.get('GVA17') if isinstance(value, dict) else []

    if not isinstance(gva17, list):
        return None

    for row in gva17:
        if not isinstance(row, dict):
            continue
        nro = row.get('NRO_DE_LIS')
        if str(nro).strip() != str(list_number).strip():
            continue

        for key in ('PRECIO', 'PRECIO_VTA', 'PRECIO_VENTA', 'IMPORTE'):
            if key in row and row.get(key) is not None and str(row.get(key)).strip() != '':
                return row.get(key)

    return None

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


def _format_price(value):
    """Format a numeric price value for labels."""
    if value is None or value == '':
        return 'N/D'
    try:
        return f"{float(str(value).replace(',', '.')):.2f}"
    except (TypeError, ValueError):
        return str(value)

def generate_zpl(item: dict, price=None) -> str:
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
    price_text = _format_price(price)

    zpl = (
        '^XA^CI28\n'
        '^LH-80,0\n'
        '^FO22,18^A0N,20,25^FB380,2,0,L^FH^FD{desc}^FS\n'
        '^FO23,18^A0N,20,25^FB380,2,0,L^FH^FD{desc}^FS\n'
        '^FO65,68^BY2,,0^BCN,54,N,N^FD{barcode}^FS\n'
        '^FO145,132^A0N,20,25^FH^FD{barcode}^FS\n'
        '^FO146,132^A0N,20,25^FH^FD{barcode}^FS\n'
        '^FO22,170^A0N,18,18^FH^FDSKU: {sku}^FS\n'
        '^FO22,192^A0N,24,24^FH^FDPRECIO: ${price_text}^FS\n'
        '^CI28\n'
        '^XZ'
    ).format(barcode=barcode, sku=sku, desc=desc, price_text=price_text)

    """
    # 50x25 label
    zpl = (
        '^XA^CI28\n'
        '^LH-80,0\n'
        '^FO65,18^BY2,,0^BCN,54,N,N^FD{barcode}^FS\n'
        '^FO145,80^A0N,20,25^FH^FD{barcode}^FS\n'
        '^FO146,80^A0N,20,25^FH^FD{barcode}^FS\n'
        '^FO22,115^A0N,18,18^FB380,2,0,L^FH^FD{desc}^FS\n'
        '^FO22,170^A0N,18,18^FH^FDSKU: {sku}^FS\n'
        '^CI28\n'
        '^XZ'
    ).format(barcode=barcode, sku=sku, desc=desc)
    """
    print(zpl)
    return zpl

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

    article_id = _get_field(item, 'id', 'ID', 'ID_STA11', 'id_sta11')
    try:
        price = fetch_price_for_list(article_id, 2)
    except Exception as e:
        print(f'Warning fetching price for article id {article_id}: {e}', file=sys.stderr)
        price = None

    labels = ''.join(generate_zpl(item, price=price) for _ in range(max(1, args.count)))
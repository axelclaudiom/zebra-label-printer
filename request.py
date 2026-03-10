import argparse
import sys
from decimal import Decimal, InvalidOperation, ROUND_DOWN
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


def fetch_price_for_item(item, list_number=2):
    """Resolve article id from item and fetch list price."""
    if not item:
        return None
    article_id = _get_field(item, 'id', 'ID', 'ID_STA11', 'id_sta11')
    return fetch_price_for_list(article_id, list_number)

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
        numeric = Decimal(str(value).replace(',', '.'))
        return str(numeric.to_integral_value(rounding=ROUND_DOWN))
    except (TypeError, ValueError, InvalidOperation):
        return str(value)


def _apply_discount(value, discount_pct=20):
    """Return discounted numeric value, or None if value is not numeric."""
    try:
        numeric = Decimal(str(value).replace(',', '.'))
    except (TypeError, ValueError, InvalidOperation):
        return None
    multiplier = Decimal('1') - (Decimal(str(discount_pct)) / Decimal('100'))
    return numeric * multiplier

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
    discount_price = _apply_discount(price, 20)
    discount_text = _format_price(discount_price)

    zpl = (
        '^XA^CI28\n'
        '^MD22\n'
        '^PR3\n'
        '^LH-80,0\n'
        '^FO22,18^A0N,25,25^FB380,2,0,L^FH^FD{desc}^FS\n'
        '^FO65,68^BY2,,0^BCN,54,N,N^FD{barcode}^FS\n'
        '^FO145,132^A0N,20,25^FH^FD{barcode}^FS\n'
        '^FO146,132^A0N,20,25^FH^FD{barcode}^FS\n'
        '^FO22,160^A0N,25,25^FH^FDHasta 6 Cuotas:^FS\n'
        '^FO22,202^A0N,50,50^FH^FD${price_text}^FS\n'
        '^FO220,160^A0N,25,25^FH^FDEfectivo/Debito:^FS\n'
        '^FO220,202^A0N,50,50^FH^FD${discount_text}^FS\n'
        '^CI28\n'
        '^XZ'
    ).format(barcode=barcode, sku=sku, desc=desc, price_text=price_text, discount_text=discount_text)

    """
    Backup version de etiqueta funcional
        zpl = (
        '^XA^CI28\n'
        '^LH-80,0\n'
        '^FO22,18^A0N,20,25^FB380,2,0,L^FH^FD{desc}^FS\n'
        '^FO23,18^A0N,20,25^FB380,2,0,L^FH^FD{desc}^FS\n'
        '^FO65,68^BY2,,0^BCN,54,N,N^FD{barcode}^FS\n'
        '^FO145,132^A0N,20,25^FH^FD{barcode}^FS\n'
        '^FO146,132^A0N,20,25^FH^FD{barcode}^FS\n'
        '^FO22,170^A0N,18,18^FH^FDSKU: {sku}^FS\n'
        '^FO22,192^A0N,24,24^FH^FDTarjeta: ${price_text}^FS\n'
        '^FO220,192^A0N,24,24^FH^FDEfectivo: ${discount_text}^FS\n'
        '^CI28\n'
        '^XZ'
    ).format(barcode=barcode, sku=sku, desc=desc, price_text=price_text, discount_text=discount_text)
    """

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

    try:
        price = fetch_price_for_item(item, 2)
    except Exception as e:
        print(f'Warning fetching price for codigo {args.codigo}: {e}', file=sys.stderr)
        price = None

    labels = ''.join(generate_zpl(item, price=price) for _ in range(max(1, args.count)))
import argparse
import sys
from printer.connector import ZebraPrinterConnector
from request import fetch_data, generate_zpl

def main(codigo, count):
    try:
        item = fetch_data(codigo)
    except Exception as e:
        print(f'Error fetching data for {codigo}: {e}', file=sys.stderr)
        sys.exit(1)

    if not item:
        print(f'No item found for codigo: {codigo}', file=sys.stderr)
        sys.exit(1)

    labels = ''.join(generate_zpl(item) for _ in range(max(1, count)))

    printer = ZebraPrinterConnector()
    try:
        printer.connect()
        printer.send(labels)
        print('Labels sent to printer successfully.')
    except Exception as e:
        print(f'Error sending labels to printer: {e}', file=sys.stderr)
    finally:
        printer.disconnect()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch article and send ZPL labels to Zebra printer')
    parser.add_argument('-c', '--codigo', required=True, help='COD_STA11 to search')
    parser.add_argument('-n', '--count', type=int, default=1, help='Number of labels to generate')
    args = parser.parse_args()

    main(args.codigo, args.count)
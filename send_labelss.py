import argparse
import os
import sys
from request import fetch_data, generate_zpl

# Printer can be set here or via environment variable ZEBRA_PRINTER.
# Examples:
#   ZEBRA_PRINTER="winspool://Mi Impresora"  (env)
#   PRINTER = "Mi Impresora"                 (directly edit below)
PRINTER = "winspool://ZDesigner_GC420t"

def send_winspool(printer_name, data):
    try:
        import win32print
        import win32api
    except Exception as e:
        raise RuntimeError("pywin32 is required for winspool: pip install pywin32") from e

    hPrinter = win32print.OpenPrinter(printer_name)
    try:
        # RAW
        hJob = win32print.StartDocPrinter(hPrinter, 1, ("ZPL Label", None, "RAW"))
        try:
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, data.encode('utf-8'))
            win32print.EndPagePrinter(hPrinter)
        finally:
            win32print.EndDocPrinter(hPrinter)
    finally:
        win32print.ClosePrinter(hPrinter)


def parse_printer(uri):
    # Accept winspool://Printer Name or plain printer name
    if uri.startswith("winspool://"):
        return ("winspool", uri[len("winspool://"):])
    return ("winspool", uri)


# nueva función: enviar contenido de un archivo .txt (ZPL o texto) a la impresora
def send_from_file(path, printer_uri=None):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if not content:
        raise RuntimeError("Archivo vacío")
    kind, pname = parse_printer(printer_uri or PRINTER)
    if kind != "winspool":
        raise RuntimeError("Unsupported printer scheme; only winspool is supported")
    send_winspool(pname, content)


def main():
    p = argparse.ArgumentParser()
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--codigo", "-c", help="COD_STA11 to search")
    group.add_argument("--text-file", "-t", help="Path to text/ZPL file to send directly to printer")
    # --count only applies when using --codigo; ignored for --text-file (the file defines quantity)
    p.add_argument("--count", "-n", type=int, default=None, help="Number of labels (only for --codigo)")
    args = p.parse_args()

    # use PRINTER variable instead of CLI parameter
    printer_uri = PRINTER
    if not printer_uri:
        print("Printer not configured. Set PRINTER in the script or environment variable ZEBRA_PRINTER.", file=sys.stderr)
        sys.exit(2)

    # si se pidió enviar desde archivo, hacerlo y salir
    if args.text_file:
        try:
            send_from_file(args.text_file, printer_uri)
        except Exception as e:
            print(f"Failed to send file: {e}", file=sys.stderr)
            sys.exit(7)
        print("File sent to printer.")
        return

    # caso por codigo: mantener comportamiento anterior
    if not args.codigo:
        print("codigo is required when not using --text-file", file=sys.stderr)
        sys.exit(2)

    try:
        item = fetch_data(args.codigo)
    except Exception as e:
        print(f"Error fetching data for {args.codigo}: {e}", file=sys.stderr)
        sys.exit(5)

    if not item:
        print(f"No item found for codigo: {args.codigo}", file=sys.stderr)
        sys.exit(6)

    # build combined ZPL with `count` labels (default 1 if not provided)
    count = args.count if isinstance(args.count, int) and args.count > 0 else 1
    zpls = ''.join(generate_zpl(item) for _ in range(count))

    kind = parse_printer(printer_uri)
    try:
        if kind[0] == "winspool":
            _, pname = kind
            send_winspool(pname, zpls)
        else:
            raise RuntimeError("Unsupported printer scheme; only winspool is supported")
    except Exception as e:
        print(f"Failed to send labels: {e}", file=sys.stderr)
        sys.exit(7)

    print("Labels sent.")


if __name__ == "__main__":
    main()
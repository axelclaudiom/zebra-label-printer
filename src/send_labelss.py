import argparse
import os
import socket
import sys
import importlib.util

DEFAULT_BACKEND = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'request.py')
)


def load_request_module(path):
    spec = importlib.util.spec_from_file_location("backend_request", path)
    if spec is None:
        raise FileNotFoundError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def send_tcp(host, port, data, timeout=10):
    with socket.create_connection((host, port), timeout=timeout) as s:
        # ZPL must be bytes
        s.sendall(data.encode('utf-8'))


def send_file(path, data):
    with open(path, 'wb') as f:
        f.write(data.encode('utf-8'))


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
    # formats: tcp://host:port  | file://C:/path/out.zpl | winspool://Printer Name
    if uri.startswith("tcp://"):
        hostport = uri[len("tcp://"):]
        if ':' in hostport:
            host, port = hostport.split(":", 1)
            return ("tcp", host, int(port))
        return ("tcp", hostport, 9100)
    if uri.startswith("file://"):
        return ("file", uri[len("file://"):])
    if uri.startswith("winspool://"):
        return ("winspool", uri[len("winspool://"):])
    # fallback assume tcp host:port
    if ':' in uri:
        host, port = uri.split(":", 1)
        return ("tcp", host, int(port))
    return ("tcp", uri, 9100)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--printer", required=True,
                   help="Printer target: tcp://host:port  | file://C:/out.zpl | winspool://Printer Name")
    p.add_argument("--codigo", "-c", required=True, help="COD_STA11 to search")
    p.add_argument("--count", "-n", type=int, default=1, help="Number of labels")
    p.add_argument("--backend", default=DEFAULT_BACKEND, help="Path to backend/request.py")
    args = p.parse_args()

    if not os.path.exists(args.backend):
        print(f"backend not found: {args.backend}", file=sys.stderr)
        sys.exit(2)

    try:
        mod = load_request_module(args.backend)
    except Exception as e:
        print(f"Failed to load backend module: {e}", file=sys.stderr)
        sys.exit(3)

    fetch = getattr(mod, "fetch_data", None)
    gen = getattr(mod, "generate_zpl", None)
    if not fetch or not gen:
        print("backend module must provide fetch_data() and generate_zpl()", file=sys.stderr)
        sys.exit(4)

    try:
        item = fetch(args.codigo)
    except Exception as e:
        print(f"Error fetching data for {args.codigo}: {e}", file=sys.stderr)
        sys.exit(5)

    if not item:
        print(f"No item found for codigo: {args.codigo}", file=sys.stderr)
        sys.exit(6)

    # build combined ZPL with `count` labels
    zpls = ''.join(gen(item) for _ in range(max(1, args.count)))

    kind = parse_printer(args.printer)
    try:
        if kind[0] == "tcp":
            _, host, port = kind
            send_tcp(host, port, zpls)
        elif kind[0] == "file":
            _, path = kind
            send_file(path, zpls)
        elif kind[0] == "winspool":
            _, pname = kind
            send_winspool(pname, zpls)
        else:
            raise RuntimeError("Unknown printer scheme")
    except Exception as e:
        print(f"Failed to send labels: {e}", file=sys.stderr)
        sys.exit(7)

    print("Labels sent.")


if __name__ == "__main__":
    main()
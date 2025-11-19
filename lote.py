from request import fetch_data, generate_zpl
from pathlib import Path
import sys
from send_labelss import send_from_file

def read_list(path):
    """Lee archivo con 'codigo,cantidad' por línea y devuelve lista de (codigo, cantidad)."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    items = []
    for ln in p.read_text(encoding="utf-8").splitlines():
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        parts = [x.strip() for x in s.split(",", 1)]
        codigo = parts[0]
        cantidad = 1
        if len(parts) > 1:
            try:
                cantidad = max(1, int(parts[1]))
            except Exception:
                cantidad = 1
        items.append((codigo, cantidad))
    return items

def build_labels_from_file(path):
    items = read_list(path)
    out = []
    for codigo, cantidad in items:
        item = fetch_data(codigo)
        if not item:
            print(f"Warning: no se encontró {codigo}", file=sys.stderr)
            continue
        for _ in range(cantidad):
            out.append(generate_zpl(item))
    return "".join(out)

if __name__ == "__main__":
    # uso: python lote.py [codes.txt] [out.zpl]
    inp = sys.argv[1] if len(sys.argv) > 1 else "codes.txt"
    outpath = sys.argv[2] if len(sys.argv) > 2 else None
    zpl = build_labels_from_file(inp)
    if outpath:
        Path(outpath).write_text(zpl, encoding="utf-8")
        print(f"ZPL escrito en {outpath}")
        # preguntar si imprimir y usar send_from_file si responde afirmativamente
        try:
            resp = input("¿Querés imprimirlo? (Y/N): ").strip().lower()
        except EOFError:
            resp = "n"
        if resp in ("y", "s"):  # acepta 'y' (yes) o 's' (si)
            try:
                send_from_file(outpath)
                print("Enviado a la impresora.")
            except Exception as e:
                print(f"Error al enviar a impresora: {e}", file=sys.stderr)
                sys.exit(1)
    else:
        sys.stdout.write(zpl)

#cantidad = 3
#labels = ''.join(generate_zpl(fetch_data("BOR0003R")) for _ in range(max(1, cantidad)))
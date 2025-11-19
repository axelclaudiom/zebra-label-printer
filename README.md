# zebra-label-printer

Pequeña utilidad para generar etiquetas ZPL a partir de un backend (backend/request.py) y enviarlas a una impresora Zebra (TCP o WinSpool) o guardar la salida en archivo.

## Estructura relevante
- backend/request.py — funciones usadas: `fetch_data(codigo)` y `generate_zpl(item)`
- lote.py — lee un archivo `codes.txt` con líneas `CODIGO,cantidad` y genera ZPL concatenado; opcionalmente pregunta si imprimir.
- send_labelss.py — envío a impresora (tcp://host:port | winspool://Printer Name | file://C:/out.zpl)

## Requisitos
- Python 3.8+
- requests (para `fetch_data`)
- pywin32 (opcional, sólo si se usa `winspool://` en Windows)

## Instalación
Desde la raíz del proyecto:
```powershell
python -m pip install -r requirements.txt
```

## Formato del archivo de lote
Archivo por defecto `codes.txt`. Ejemplo:
```
# Comentario ignorado
BOR0003,3
PUCSDFPB28,1
```
Cada línea: `CODIGO,cantidad`. Si no hay cantidad se usa 1.

## Uso
- Generar ZPL y mostrar por stdout:
```powershell
python lote.py
```
- Generar ZPL y guardar en archivo:
```powershell
python lote.py codes.txt out.zpl
```
- Generar y preguntar para enviar a impresora (si eliges "Y" llama a `send_from_file` en send_labelss.py).

- Enviar directamente con send_labelss.py (ejemplo TCP):
```powershell
python src\send_labelss.py --printer tcp://192.168.1.50:9100 --codigo BOR0003 --count 2
```

## Printer URI soportados
- tcp://host:port  (envía datos a puerto 9100)
- file://C:/ruta/out.zpl
- winspool://Nombre impresora  (Windows, requiere pywin32)

## Notas
- `backend/request.py` debe exponer `fetch_data` y `generate_zpl`.
- Ajusta desplazamiento horizontal de la etiqueta con `^LH` en el ZPL generado si necesitas mover a la izquierda/derecha.
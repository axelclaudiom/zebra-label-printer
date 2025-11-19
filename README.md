# zebra-label-printer

Script para obtener datos de artículos y generar etiquetas ZPL listas para imprimir en impresoras Zebra (WinSpool).

## Requisitos
- Python 3.8+
- Dependencias: instalar desde requirements.txt

Instalación:
```powershell
python -m pip install -r requirements.txt
```

## Configuración de impresora
La impresora se define en la variable `PRINTER` dentro de `send_labelss.py` o mediante la variable de entorno `ZEBRA_PRINTER`.

Ejemplos de valores:
- Directo en el script: `PRINTER = "winspool://Mi Impresora"`
- Variable de entorno (PowerShell):
```powershell
$env:ZEBRA_PRINTER = "winspool://Mi Impresora"
```

## Uso
Ejecutar desde la carpeta del proyecto:

PowerShell / CMD:
```powershell
python .\send_labelss.py -c BOR0003 -n 2
```

Donde:
- `-c, --codigo` COD_STA11 a buscar (requerido)
- `-n, --count` número de etiquetas a generar (por defecto 1)

## Nota sobre request.py
El módulo `request.py` debe estar en la misma carpeta y exponer:
- `fetch_data(codigo)` -> dict con los datos del artículo
- `generate_zpl(item)` -> string con ZPL listo para enviar

## Solución de problemas
- Si falla por falta de `requests` o `pywin32`:
```powershell
python -m pip install requests pywin32
```
- Error relacionado a pywin32 al usar winspool: instalar `pywin32` y reiniciar la sesión de Python/terminal.
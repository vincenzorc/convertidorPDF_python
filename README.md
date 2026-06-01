# Convertidor PDF

Herramienta de escritorio para convertir imagenes a PDF y manipular archivos PDF, desarrollada con Python y Tkinter.

## Funcionalidades

### Imagen a PDF
- Convierte multiples imagenes a un solo PDF
- Formatos soportados: **PNG**, **JPG**, **JPEG**, **WEBP**
- Formato de hoja: **A4**, **Carta**, **Legal** o **Sin formato** (tamano original)
- Orientacion: **Vertical** u **Horizontal**
- Margenes: **Sin margenes**, **Poco**, **Medio**, **Mucho**
- Reordenamiento de imagenes antes de convertir
- **Vista previa** de imagenes seleccionadas
- **Drag and drop** de imagenes directamente a la ventana

### Herramientas PDF
| Operacion | Descripcion |
|---|---|
| Unir PDFs | Combina multiples archivos en uno solo |
| Dividir PDF | Separa por rangos de paginas (ej: `1-3,5,8-10`) o una pagina por archivo |
| Reordenar paginas | Cambia el orden de las paginas (ej: `3,1,2,4`) |
| Eliminar paginas | Remueve paginas especificadas |
| Extraer paginas | Crea un PDF nuevo con solo las paginas seleccionadas |
| Optimizar PDF | Reduce el tamano del archivo (Ligera / Media / Fuerte) |
| PDF a Imagenes | Convierte cada pagina del PDF a PNG o JPG (DPI configurable) |

> Todas las operaciones aceptan **drag and drop** de archivos PDF directamente a la lista.

## Requisitos

- Python 3.9 o superior
- pip (gestor de paquetes)

## Instalacion

```bash
# Clonar o descargar el proyecto
cd convertidorPDF

# Instalar dependencias
pip install -r requirements.txt
```

## Dependencias

| Paquete | Uso |
|---|---|
| Pillow | Conversion de imagenes a PDF, vista previa |
| pypdf | Manipulacion de PDF (unir, dividir, reordenar, extraer, eliminar) |
| PyMuPDF | Optimizacion de PDF y conversion PDF a imagenes |
| tkinterdnd2 | Drag and drop de archivos |

## Ejecucion

```bash
python main.py
```

## Estructura del proyecto

```
convertidorPDF/
├── main.py              # Punto de entrada
├── ui.py                # Interfaz grafica (Tkinter)
├── image_tools.py       # Conversion de imagenes a PDF
├── pdf_tools.py         # Operaciones PDF (unir, dividir, etc.)
├── optimize_tools.py    # Compresion de PDF
├── page_ranges.py       # Parser de rangos de paginas
├── requirements.txt     # Dependencias
└── README.md            # Este archivo
```

## Uso

### Convertir imagenes a PDF

1. Ir a la pestana **Imagen a PDF**
2. Hacer clic en **+ Agregar** y seleccionar las imagenes
3. (Opcional) Reordenar con los botones **^ Subir** y **v Bajar**
4. Elegir formato de hoja, orientacion y margenes
5. Ingresar nombre del archivo de salida
6. Seleccionar carpeta de destino
7. Hacer clic en **Convertir a PDF**

### Manipular PDFs

1. Ir a la pestana **Herramientas PDF**
2. Seleccionar la operacion deseada
3. Agregar el o los archivos PDF
4. Configurar las opciones segun la operacion
5. Elegir carpeta de destino
6. Hacer clic en **Ejecutar**

### Ejemplos de rangos

| Entrada | Resultado |
|---|---|
| `1` | Solo pagina 1 |
| `1-5` | Paginas 1, 2, 3, 4, 5 |
| `1,3,5` | Paginas 1, 3 y 5 |
| `1-3,7,10-12` | Paginas 1-3, 7 y 10-12 |

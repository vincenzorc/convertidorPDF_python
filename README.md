# Convertidor PDF

Herramienta de escritorio para convertir imagenes a PDF y manipular archivos PDF, desarrollada con Python, Tkinter y arquitectura MVC.

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

## Estructura del proyecto (MVC)

```
convertidorPDF/
├── main.py                              # Punto de entrada
├── models/
│   ├── image_converter.py               # Conversion imagenes → PDF
│   ├── pdf_operations.py                # Unir, dividir, reordenar, extraer, eliminar
│   ├── pdf_optimizer.py                 # Compresion de PDF
│   └── pdf_to_image_converter.py        # PDF → imagenes
├── views/
│   ├── main_window.py                   # Ventana principal, header, status bar
│   ├── image_tab.py                     # UI pestana "Imagen a PDF"
│   ├── pdf_tools_tab.py                 # UI pestana "Herramientas PDF"
│   └── widgets.py                       # Helpers reutilizables (colores, secciones, botones)
├── controllers/
│   ├── image_controller.py              # Logica del tab de imagenes + threading
│   └── pdf_controller.py                # Logica del tab de PDFs + threading
├── utils/
│   └── page_ranges.py                   # Parser de rangos de paginas
├── requirements.txt
└── README.md
```

### Arquitectura

- **Models**: Logica de negocio pura (sin tkinter). Cada model encapsula una operacion.
- **Views**: Construccion de widgets y getters para leer valores. Sin logica de negocio.
- **Controllers**: Orquestan models y views. Manejan threading de forma segura con `after()`.

## Requisitos

- Python 3.9 o superior
- pip (gestor de paquetes)

## Instalacion

```bash
cd convertidorPDF
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

## Uso

### Convertir imagenes a PDF
1. Ir a la pestana **Imagen a PDF**
2. Hacer clic en **+ Agregar** o arrastrar imagenes a la lista
3. Reordenar con **^ Subir** / **v Bajar** si es necesario
4. Elegir formato de hoja, orientacion y margenes
5. Ingresar nombre y carpeta de destino
6. Hacer clic en **Convertir a PDF**

### Manipular PDFs
1. Ir a la pestana **Herramientas PDF**
2. Seleccionar la operacion deseada
3. Agregar PDFs (boton o drag and drop)
4. Configurar opciones segun la operacion
5. Hacer clic en **Ejecutar**

### Ejemplos de rangos
| Entrada | Resultado |
|---|---|
| `1` | Solo pagina 1 |
| `1-5` | Paginas 1, 2, 3, 4, 5 |
| `1,3,5` | Paginas 1, 3 y 5 |
| `1-3,7,10-12` | Paginas 1-3, 7 y 10-12 |

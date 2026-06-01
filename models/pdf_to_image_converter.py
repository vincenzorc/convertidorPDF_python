import os
import fitz


class PdfToImageConverter:

    def convert(
        self,
        input_path: str,
        output_dir: str,
        fmt: str = "PNG",
        quality: int = 95,
        dpi: int = 150,
    ):
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"Archivo no encontrado: {input_path}")
        doc = fitz.open(input_path)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        ext = "png" if fmt == "PNG" else "jpg"
        zoom = dpi / 72
        matrix = fitz.Matrix(zoom, zoom)

        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            out = os.path.join(output_dir, f"{base_name}_pagina_{i + 1}.{ext}")
            if fmt == "PNG":
                pix.save(out)
            else:
                pix.save(out, jpg_quality=quality)

        doc.close()

import os
from pypdf import PdfReader, PdfWriter
from typing import List


class PdfOperations:

    def get_page_count(self, pdf_path: str) -> int:
        try:
            return len(PdfReader(pdf_path).pages)
        except Exception:
            return 0

    def merge(self, input_paths: List[str], output_path: str):
        if not input_paths:
            raise ValueError("No hay archivos PDF para unir")
        if len(input_paths) < 2:
            raise ValueError("Se necesitan al menos 2 PDFs para unir")
        writer = PdfWriter()
        for path in input_paths:
            if not os.path.isfile(path):
                raise FileNotFoundError(f"Archivo no encontrado: {path}")
            reader = PdfReader(path)
            writer.append(reader)
        with open(output_path, "wb") as f:
            writer.write(f)

    def split(self, input_path: str, output_dir: str, ranges: List[List[int]]):
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"Archivo no encontrado: {input_path}")
        if not ranges:
            raise ValueError("No hay rangos de paginas para dividir")
        reader = PdfReader(input_path)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        for i, page_list in enumerate(ranges):
            writer = PdfWriter()
            for page_num in page_list:
                writer.add_page(reader.pages[page_num - 1])
            out = os.path.join(output_dir, f"{base_name}_part{i + 1}.pdf")
            with open(out, "wb") as f:
                writer.write(f)

    def remove_pages(self, input_path: str, output_path: str, pages_to_remove: List[int]):
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"Archivo no encontrado: {input_path}")
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for i, page in enumerate(reader.pages):
            if (i + 1) not in pages_to_remove:
                writer.add_page(page)
        with open(output_path, "wb") as f:
            writer.write(f)

    def extract_pages(self, input_path: str, output_path: str, pages_to_extract: List[int]):
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"Archivo no encontrado: {input_path}")
        if not pages_to_extract:
            raise ValueError("No se especificaron paginas para extraer")
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for page_num in pages_to_extract:
            writer.add_page(reader.pages[page_num - 1])
        with open(output_path, "wb") as f:
            writer.write(f)

    def reorder(self, input_path: str, output_path: str, new_order: List[int]):
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"Archivo no encontrado: {input_path}")
        if not new_order:
            raise ValueError("El orden de paginas esta vacio")
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for page_num in new_order:
            writer.add_page(reader.pages[page_num - 1])
        with open(output_path, "wb") as f:
            writer.write(f)

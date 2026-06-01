import os
from pypdf import PdfReader, PdfWriter
from typing import List


class PdfOperations:

    def get_page_count(self, pdf_path: str) -> int:
        try:
            return len(PdfReader(pdf_path).pages)
        except Exception:
            return 0

    def merge(self, input_paths: List[str], output_path: str) -> bool:
        writer = PdfWriter()
        try:
            for path in input_paths:
                reader = PdfReader(path)
                writer.append(reader)
            with open(output_path, "wb") as f:
                writer.write(f)
            return True
        except Exception as e:
            print(f"Error merging PDFs: {e}")
            return False

    def split(self, input_path: str, output_dir: str, ranges: List[List[int]]) -> bool:
        try:
            reader = PdfReader(input_path)
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            for i, page_list in enumerate(ranges):
                writer = PdfWriter()
                for page_num in page_list:
                    writer.add_page(reader.pages[page_num - 1])
                out = os.path.join(output_dir, f"{base_name}_part{i + 1}.pdf")
                with open(out, "wb") as f:
                    writer.write(f)
            return True
        except Exception as e:
            print(f"Error splitting PDF: {e}")
            return False

    def remove_pages(self, input_path: str, output_path: str, pages_to_remove: List[int]) -> bool:
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            for i, page in enumerate(reader.pages):
                if (i + 1) not in pages_to_remove:
                    writer.add_page(page)
            with open(output_path, "wb") as f:
                writer.write(f)
            return True
        except Exception as e:
            print(f"Error removing pages: {e}")
            return False

    def extract_pages(self, input_path: str, output_path: str, pages_to_extract: List[int]) -> bool:
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            for page_num in pages_to_extract:
                writer.add_page(reader.pages[page_num - 1])
            with open(output_path, "wb") as f:
                writer.write(f)
            return True
        except Exception as e:
            print(f"Error extracting pages: {e}")
            return False

    def reorder(self, input_path: str, output_path: str, new_order: List[int]) -> bool:
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            for page_num in new_order:
                writer.add_page(reader.pages[page_num - 1])
            with open(output_path, "wb") as f:
                writer.write(f)
            return True
        except Exception as e:
            print(f"Error reordering pages: {e}")
            return False

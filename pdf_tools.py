import os
import fitz
from pypdf import PdfReader, PdfWriter, PageRange
from typing import List

def merge_pdfs(input_paths: List[str], output_path: str) -> bool:
    """
    Merge multiple PDFs into one.
    """
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

def split_pdf(input_path: str, output_dir: str, ranges: List[List[int]]) -> bool:
    """
    Split a PDF into multiple PDFs based on list of page ranges (each range is list of page numbers 1-indexed).
    Each range will produce a separate PDF.
    """
    try:
        reader = PdfReader(input_path)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        for i, page_list in enumerate(ranges):
            writer = PdfWriter()
            for page_num in page_list:
                # pypdf uses 0-indexed
                writer.add_page(reader.pages[page_num - 1])
            output_path = os.path.join(output_dir, f"{base_name}_part{i+1}.pdf")
            with open(output_path, "wb") as f:
                writer.write(f)
        return True
    except Exception as e:
        print(f"Error splitting PDF: {e}")
        return False

def remove_pages(input_path: str, output_path: str, pages_to_remove: List[int]) -> bool:
    """
    Remove specific pages (1-indexed) from PDF.
    """
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

def extract_pages(input_path: str, output_path: str, pages_to_extract: List[int]) -> bool:
    """
    Extract specific pages (1-indexed) into a new PDF.
    """
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

def reorder_pages(input_path: str, output_path: str, new_order: List[int]) -> bool:
    """
    Reorder pages according to new_order list (1-indexed).
    """
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


def pdf_to_images(
    input_path: str,
    output_dir: str,
    fmt: str = "PNG",
    quality: int = 95,
    dpi: int = 150,
) -> bool:
    """
    Convert each page of a PDF into a separate image file.

    Args:
        input_path: Path to the source PDF.
        output_dir: Directory where images will be saved.
        fmt: Output format, "PNG" or "JPG".
        quality: JPEG quality (1-100), ignored for PNG.
        dpi: Resolution for rendering.

    Returns:
        True on success, False on failure.
    """
    try:
        doc = fitz.open(input_path)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        ext = "png" if fmt == "PNG" else "jpg"
        zoom = dpi / 72
        matrix = fitz.Matrix(zoom, zoom)

        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            output_path = os.path.join(output_dir, f"{base_name}_pagina_{i + 1}.{ext}")
            if fmt == "PNG":
                pix.save(output_path)
            else:
                pix.save(output_path, jpg_quality=quality)

        doc.close()
        return True
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return False
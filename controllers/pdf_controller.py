import os
import threading
from tkinter import filedialog, messagebox

from views.widgets import COLORS
from models.pdf_operations import PdfOperations
from models.pdf_optimizer import PdfOptimizer
from models.pdf_to_image_converter import PdfToImageConverter
from utils.page_ranges import parse_page_ranges, parse_reorder_range


class PdfController:

    def __init__(self, view, main_window):
        self.view = view
        self.main_window = main_window
        self.ops = PdfOperations()
        self.optimizer = PdfOptimizer()
        self.converter = PdfToImageConverter()

        self.view.set_callbacks(
            on_add=self._add_pdfs,
            on_remove=self._remove_pdfs,
            on_clear=self._clear_pdfs,
            on_browse_folder=self._browse_folder,
            on_execute=self._execute,
        )
        self.view.setup_dnd()

    def _add_pdfs(self):
        files = filedialog.askopenfilenames(
            title="Seleccionar PDFs",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        existing = set(self.view.pdf_listbox.get(0, "end"))
        for f in files:
            if f not in existing:
                self.view.pdf_listbox.insert("end", f)
        count = self.view.pdf_listbox.size()
        self.main_window.set_status(f"{count} PDF(s) seleccionado(s)")

    def _remove_pdfs(self):
        for i in reversed(self.view.pdf_listbox.curselection()):
            self.view.pdf_listbox.delete(i)
        count = self.view.pdf_listbox.size()
        self.main_window.set_status(f"{count} PDF(s) en la lista")

    def _clear_pdfs(self):
        self.view.pdf_listbox.delete(0, "end")
        self.main_window.set_status("Lista de PDFs vacia")

    def _browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.view.set_output_folder(folder)

    def _validate_single_pdf(self, pdf_files, operation_name):
        if len(pdf_files) != 1:
            self.main_window.after(0, lambda: messagebox.showwarning(
                "Advertencia", f"Para {operation_name}, seleccione exactamente un PDF"
            ))
            self.main_window.after(0, lambda: self.main_window.set_status("Listo"))
            return False
        return True

    def _execute(self):
        op = self.view.get_operation()
        pdf_files = self.view.get_pdf_paths()
        if not pdf_files:
            messagebox.showwarning("Advertencia", "No hay PDFs seleccionados")
            return
        output_folder = self.view.get_output_folder()
        if not output_folder:
            messagebox.showwarning("Advertencia", "Seleccione una carpeta de salida")
            return

        self.main_window.set_status(f"Ejecutando: {op}...", COLORS["warning"])

        def worker():
            try:
                self._dispatch(op, pdf_files, output_folder)
            except Exception as e:
                self.main_window.after(0, lambda: self._error(str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _dispatch(self, op, pdf_files, output_folder):
        if op == "Unir PDFs":
            self._do_merge(pdf_files, output_folder)
        elif op == "Dividir PDF":
            self._do_split(pdf_files, output_folder)
        elif op == "Reordenar paginas":
            self._do_reorder(pdf_files, output_folder)
        elif op == "Eliminar paginas":
            self._do_remove(pdf_files, output_folder)
        elif op == "Extraer paginas":
            self._do_extract(pdf_files, output_folder)
        elif op == "Optimizar PDF":
            self._do_optimize(pdf_files, output_folder)
        elif op == "PDF a Imagenes":
            self._do_pdf_to_images(pdf_files, output_folder)

    def _do_merge(self, pdf_files, output_folder):
        out = os.path.join(output_folder, "unido.pdf")
        self.ops.merge(pdf_files, out)
        self.main_window.after(0, lambda: self._success("PDFs unidos correctamente", out))

    def _do_split(self, pdf_files, output_folder):
        if not self._validate_single_pdf(pdf_files, "dividir"):
            return
        input_path = pdf_files[0]
        ranges_str = self.view.get_split_ranges()
        one_per_page = self.view.get_split_one_per_page()

        total = self.ops.get_page_count(input_path)
        if one_per_page:
            ranges = [[i + 1] for i in range(total)]
        else:
            ranges = []
            for part in ranges_str.split(","):
                part = part.strip()
                if "-" in part:
                    start_s, end_s = part.split("-")
                    start, end = int(start_s.strip()), int(end_s.strip())
                else:
                    start = end = int(part)
                start = max(1, min(start, total))
                end = max(1, min(end, total))
                if start > end:
                    start, end = end, start
                ranges.append(list(range(start, end + 1)))

        self.ops.split(input_path, output_folder, ranges)
        self.main_window.after(0, lambda: self._success(f"PDF dividido en {len(ranges)} parte(s)"))

    def _do_reorder(self, pdf_files, output_folder):
        if not self._validate_single_pdf(pdf_files, "reordenar"):
            return
        input_path = pdf_files[0]
        order_str = self.view.get_reorder_entry()
        total = self.ops.get_page_count(input_path)
        new_order = parse_reorder_range(order_str, total)
        if not new_order:
            self.main_window.after(0, lambda: messagebox.showwarning(
                "Advertencia", "Orden no valido. Use formato como '3,1,2,4'."
            ))
            self.main_window.after(0, lambda: self.main_window.set_status("Listo"))
            return
        out = os.path.join(output_folder, "reordenado.pdf")
        self.ops.reorder(input_path, out, new_order)
        self.main_window.after(0, lambda: self._success("Paginas reordenadas", out))

    def _do_remove(self, pdf_files, output_folder):
        if not self._validate_single_pdf(pdf_files, "eliminar paginas"):
            return
        input_path = pdf_files[0]
        ranges_str = self.view.get_remove_ranges()
        total = self.ops.get_page_count(input_path)
        pages = parse_page_ranges(ranges_str, total)
        if not pages and ranges_str:
            self.main_window.after(0, lambda: messagebox.showwarning("Advertencia", "Rangos no validos"))
            self.main_window.after(0, lambda: self.main_window.set_status("Listo"))
            return
        out = os.path.join(output_folder, "sin_eliminadas.pdf")
        self.ops.remove_pages(input_path, out, pages)
        self.main_window.after(0, lambda: self._success("Paginas eliminadas", out))

    def _do_extract(self, pdf_files, output_folder):
        if not self._validate_single_pdf(pdf_files, "extraer paginas"):
            return
        input_path = pdf_files[0]
        ranges_str = self.view.get_extract_ranges()
        total = self.ops.get_page_count(input_path)
        pages = parse_page_ranges(ranges_str, total)
        if not pages and ranges_str:
            self.main_window.after(0, lambda: messagebox.showwarning("Advertencia", "Rangos no validos"))
            self.main_window.after(0, lambda: self.main_window.set_status("Listo"))
            return
        out = os.path.join(output_folder, "extraidas.pdf")
        self.ops.extract_pages(input_path, out, pages)
        self.main_window.after(0, lambda: self._success("Paginas extraidas", out))

    def _do_optimize(self, pdf_files, output_folder):
        if not self._validate_single_pdf(pdf_files, "optimizar"):
            return
        input_path = pdf_files[0]
        level_text = self.view.get_compress_level()
        level_map = {"Ligera": "light", "Media": "medium", "Fuerte": "strong"}
        level = level_map.get(level_text, "medium")
        out = os.path.join(output_folder, "optimizado.pdf")
        self.optimizer.optimize(input_path, out, level)
        self.main_window.after(0, lambda: self._success("PDF optimizado", out))

    def _do_pdf_to_images(self, pdf_files, output_folder):
        if not self._validate_single_pdf(pdf_files, "convertir PDF a imagenes"):
            return
        input_path = pdf_files[0]
        fmt = self.view.get_img_format()
        dpi = int(self.view.get_img_dpi())
        quality_map = {"Baja (60)": 60, "Media (80)": 80, "Alta (95)": 95}
        quality = quality_map.get(self.view.get_img_quality(), 95)

        self.converter.convert(input_path, output_folder, fmt=fmt, quality=quality, dpi=dpi)
        total = self.ops.get_page_count(input_path)
        self.main_window.after(0, lambda: self._success(f"{total} imagen(es) generadas en:\n{output_folder}"))

    def _success(self, msg, path=None):
        self.main_window.set_status(msg, COLORS["success"])
        text = msg if path is None else f"{msg}:\n{path}"
        messagebox.showinfo("Exito", text)

    def _error(self, msg):
        self.main_window.set_status("Error", COLORS["error"])
        messagebox.showerror("Error", msg)

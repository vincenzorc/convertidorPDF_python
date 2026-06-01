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
        for f in files:
            if f not in self.view.pdf_listbox.get(0, "end"):
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
        success = self.ops.merge(pdf_files, out)
        self.main_window.after(0, lambda: self._success("PDFs unidos correctamente", out) if success else self._error("No se pudo unir los PDFs"))

    def _do_split(self, pdf_files, output_folder):
        if len(pdf_files) != 1:
            self.main_window.after(0, lambda: messagebox.showwarning("Advertencia", "Para dividir, seleccione exactamente un PDF"))
            self.main_window.after(0, lambda: self.main_window.set_status("Listo"))
            return
        input_path = pdf_files[0]
        widget = self.view.get_split_ranges()
        ranges_str = widget.get().strip() if widget else "1"
        one_per_page_widget = self.view.get_split_one_per_page()
        one_per_page = one_per_page_widget.get() if one_per_page_widget else False

        total = self.ops.get_page_count(input_path)
        if one_per_page:
            ranges = [[i + 1] for i in range(total)]
        else:
            parts = ranges_str.split(",")
            ranges = []
            for part in parts:
                part = part.strip()
                if "-" in part:
                    start, end = part.split("-")
                    start, end = int(start.strip()), int(end.strip())
                else:
                    start = end = int(part)
                start = max(1, min(start, total))
                end = max(1, min(end, total))
                if start > end:
                    start, end = end, start
                ranges.append(list(range(start, end + 1)))

        success = self.ops.split(input_path, output_folder, ranges)
        msg = f"PDF dividido en {len(ranges)} parte(s)"
        self.main_window.after(0, lambda: self._success(msg) if success else self._error("No se pudo dividir el PDF"))

    def _do_reorder(self, pdf_files, output_folder):
        if len(pdf_files) != 1:
            self.main_window.after(0, lambda: messagebox.showwarning("Advertencia", "Para reordenar, seleccione exactamente un PDF"))
            self.main_window.after(0, lambda: self.main_window.set_status("Listo"))
            return
        input_path = pdf_files[0]
        widget = self.view.get_reorder_entry()
        order_str = widget.get().strip() if widget else ""
        total = self.ops.get_page_count(input_path)
        new_order = parse_reorder_range(order_str, total)
        if not new_order:
            self.main_window.after(0, lambda: messagebox.showwarning("Advertencia", "Orden no valido. Use formato como '3,1,2,4'."))
            self.main_window.after(0, lambda: self.main_window.set_status("Listo"))
            return
        out = os.path.join(output_folder, "reordenado.pdf")
        success = self.ops.reorder(input_path, out, new_order)
        self.main_window.after(0, lambda: self._success("Paginas reordenadas", out) if success else self._error("No se pudo reordenar las paginas"))

    def _do_remove(self, pdf_files, output_folder):
        if len(pdf_files) != 1:
            self.main_window.after(0, lambda: messagebox.showwarning("Advertencia", "Para eliminar paginas, seleccione exactamente un PDF"))
            self.main_window.after(0, lambda: self.main_window.set_status("Listo"))
            return
        input_path = pdf_files[0]
        widget = self.view.get_remove_ranges()
        ranges_str = widget.get().strip() if widget else ""
        total = self.ops.get_page_count(input_path)
        pages = parse_page_ranges(ranges_str, total)
        if not pages and ranges_str:
            self.main_window.after(0, lambda: messagebox.showwarning("Advertencia", "Rangos no validos"))
            self.main_window.after(0, lambda: self.main_window.set_status("Listo"))
            return
        out = os.path.join(output_folder, "sin_eliminadas.pdf")
        success = self.ops.remove_pages(input_path, out, pages)
        self.main_window.after(0, lambda: self._success("Paginas eliminadas", out) if success else self._error("No se pudo eliminar las paginas"))

    def _do_extract(self, pdf_files, output_folder):
        if len(pdf_files) != 1:
            self.main_window.after(0, lambda: messagebox.showwarning("Advertencia", "Para extraer paginas, seleccione exactamente un PDF"))
            self.main_window.after(0, lambda: self.main_window.set_status("Listo"))
            return
        input_path = pdf_files[0]
        widget = self.view.get_extract_ranges()
        ranges_str = widget.get().strip() if widget else ""
        total = self.ops.get_page_count(input_path)
        pages = parse_page_ranges(ranges_str, total)
        if not pages and ranges_str:
            self.main_window.after(0, lambda: messagebox.showwarning("Advertencia", "Rangos no validos"))
            self.main_window.after(0, lambda: self.main_window.set_status("Listo"))
            return
        out = os.path.join(output_folder, "extraidas.pdf")
        success = self.ops.extract_pages(input_path, out, pages)
        self.main_window.after(0, lambda: self._success("Paginas extraidas", out) if success else self._error("No se pudo extraer las paginas"))

    def _do_optimize(self, pdf_files, output_folder):
        if len(pdf_files) != 1:
            self.main_window.after(0, lambda: messagebox.showwarning("Advertencia", "Para optimizar, seleccione exactamente un PDF"))
            self.main_window.after(0, lambda: self.main_window.set_status("Listo"))
            return
        input_path = pdf_files[0]
        widget = self.view.get_compress_level()
        level_text = widget.get() if widget else "Media"
        level_map = {"Ligera": "light", "Media": "medium", "Fuerte": "strong"}
        level = level_map.get(level_text, "medium")
        out = os.path.join(output_folder, "optimizado.pdf")
        success = self.optimizer.optimize(input_path, out, level)
        self.main_window.after(0, lambda: self._success("PDF optimizado", out) if success else self._error("No se pudo optimizar el PDF"))

    def _do_pdf_to_images(self, pdf_files, output_folder):
        if len(pdf_files) != 1:
            self.main_window.after(0, lambda: messagebox.showwarning("Advertencia", "Seleccione exactamente un PDF"))
            self.main_window.after(0, lambda: self.main_window.set_status("Listo"))
            return
        input_path = pdf_files[0]
        fmt_w = self.view.get_img_format()
        dpi_w = self.view.get_img_dpi()
        quality_w = self.view.get_img_quality()
        fmt = fmt_w.get() if fmt_w else "PNG"
        dpi = int(dpi_w.get() if dpi_w else "150")
        quality_map = {"Baja (60)": 60, "Media (80)": 80, "Alta (95)": 95}
        quality = quality_map.get(quality_w.get() if quality_w else "Alta (95)", 95)

        success = self.converter.convert(input_path, output_folder, fmt=fmt, quality=quality, dpi=dpi)
        total = self.ops.get_page_count(input_path) if success else 0
        if success:
            self.main_window.after(0, lambda: self._success(f"{total} imagen(es) generadas en:\n{output_folder}"))
        else:
            self.main_window.after(0, lambda: self._error("No se pudo convertir el PDF a imagenes"))

    def _success(self, msg, path=None):
        self.main_window.set_status(msg, COLORS["success"])
        text = msg if path is None else f"{msg}:\n{path}"
        messagebox.showinfo("Exito", text)

    def _error(self, msg):
        self.main_window.set_status("Error", COLORS["error"])
        messagebox.showerror("Error", msg)

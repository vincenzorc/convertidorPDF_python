import os
import threading
from tkinter import filedialog, messagebox

from views.widgets import COLORS
from models.image_converter import ImageConverter


class ImageController:

    def __init__(self, view, main_window):
        self.view = view
        self.main_window = main_window
        self.model = ImageConverter()

        self.view.set_callbacks(
            on_add=self._add_images,
            on_remove=self._remove_images,
            on_clear=self._clear_images,
            on_browse_folder=self._browse_folder,
            on_select=self._on_select,
            on_convert=self._convert,
        )
        self.view.listbox.bind("<<ListboxSelect>>", self._on_select)
        self.view.setup_dnd()

    def _add_images(self):
        files = filedialog.askopenfilenames(
            title="Seleccionar imagenes",
            filetypes=[
                ("Imagenes", "*.png *.jpg *.jpeg *.webp"),
                ("Todos los archivos", "*.*"),
            ],
        )
        self.view.add_images(files)
        count = self.view.listbox.size()
        self.main_window.set_status(f"{count} imagen(es) seleccionada(s)")
        self.view.auto_select_first()

    def _remove_images(self):
        self.view.remove_selected()
        count = self.view.listbox.size()
        self.main_window.set_status(f"{count} imagen(es) en la lista")
        self.view.update_preview()

    def _clear_images(self):
        self.view.clear_images()
        self.main_window.set_status("Lista de imagenes vacia")

    def _browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.view.set_output_folder(folder)

    def _on_select(self, event=None):
        self.view.update_preview()

    def _convert(self):
        image_paths = self.view.get_image_paths()
        if not image_paths:
            messagebox.showwarning("Advertencia", "No hay imagenes seleccionadas")
            return

        output_name = self.view.get_output_name()
        if not output_name:
            messagebox.showwarning("Advertencia", "Ingrese un nombre para el PDF de salida")
            return
        if not output_name.lower().endswith(".pdf"):
            output_name += ".pdf"

        output_folder = self.view.get_output_folder()
        if not output_folder:
            messagebox.showwarning("Advertencia", "Seleccione una carpeta de salida")
            return

        page_format = self.view.get_page_format()
        margin_option = self.view.get_margin_option()
        orientation = self.view.get_orientation()
        output_path = os.path.join(output_folder, output_name)

        self.main_window.set_status("Convirtiendo...", COLORS["warning"])

        def worker():
            success = self.model.convert(
                image_paths, output_path,
                page_size=page_format, margins=margin_option,
                orientation=orientation,
            )
            self.main_window.after(0, lambda: self._on_convert_done(success, output_path))

        threading.Thread(target=worker, daemon=True).start()

    def _on_convert_done(self, success, output_path):
        if success:
            self.main_window.set_status(f"Completado: {os.path.basename(output_path)}", COLORS["success"])
            messagebox.showinfo("Exito", f"PDF creado correctamente:\n{output_path}")
        else:
            self.main_window.set_status("Error en la conversion", COLORS["error"])
            messagebox.showerror("Error", "No se pudo convertir las imagenes a PDF")

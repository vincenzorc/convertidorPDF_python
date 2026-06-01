import tkinter as tk
from tkinter import ttk, filedialog
import os
from PIL import Image, ImageTk

try:
    from tkinterdnd2 import DND_FILES
except ImportError:
    DND_FILES = None

from views.widgets import COLORS, make_section, make_list_row_buttons, make_file_row


class ImageTab:

    IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")

    def __init__(self, parent):
        self.frame = parent
        self._preview_image_ref = None
        self._on_select_callback = None
        self._build()

    def _build(self):
        sec_files = make_section(self.frame, "Archivos", 0)

        files_body = tk.Frame(sec_files, bg=COLORS["section_bg"])
        files_body.pack(fill="both", expand=True)

        left_panel = tk.Frame(files_body, bg=COLORS["section_bg"])
        left_panel.pack(side="left", fill="both", expand=True)

        self.listbox = tk.Listbox(
            left_panel, selectmode=tk.EXTENDED, height=7,
            font=("Consolas", 9), bg=COLORS["input_bg"],
            selectbackground=COLORS["accent"], selectforeground="#ffffff",
            relief="solid", bd=1, activestyle="none",
        )
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        self.preview_frame = tk.Frame(
            files_body, bg=COLORS["border"],
            highlightbackground=COLORS["border"], highlightthickness=1,
            width=200, height=160,
        )
        self.preview_frame.pack(side="right", padx=(10, 0))
        self.preview_frame.pack_propagate(False)

        self.preview_label = tk.Label(
            self.preview_frame, text="Sin vista previa",
            font=("Segoe UI", 9), fg=COLORS["muted"],
            bg=COLORS["section_bg"], anchor="center",
        )
        self.preview_label.pack(fill="both", expand=True, padx=1, pady=1)

        make_list_row_buttons(sec_files, [
            ("+ Agregar", self._emit_add),
            ("^ Subir", self.move_up),
            ("v Bajar", self.move_down),
            ("x Quitar", self._emit_remove),
            ("Limpiar", self._emit_clear),
        ])

        sec_name = make_section(self.frame, "Nombre del archivo", 1)
        row_name = tk.Frame(sec_name, bg=COLORS["section_bg"])
        row_name.pack(fill="x")
        tk.Label(
            row_name, text="Nombre PDF:", font=("Segoe UI", 9),
            bg=COLORS["section_bg"], width=18, anchor="w",
        ).pack(side="left")
        self.output_name = tk.Entry(
            row_name, font=("Segoe UI", 9), bg=COLORS["input_bg"],
            relief="solid", bd=1,
        )
        self.output_name.insert(0, "salida.pdf")
        self.output_name.pack(side="left", fill="x", expand=True)

        sec_out = make_section(self.frame, "Destino", 2)
        self.output_folder = tk.Entry(
            sec_out, font=("Segoe UI", 9), bg=COLORS["input_bg"],
            relief="solid", bd=1,
        )
        make_file_row(sec_out, self.output_folder, self._emit_browse_folder)

        sec_opts = make_section(self.frame, "Formato de pagina", 3)
        opts_grid = tk.Frame(sec_opts, bg=COLORS["section_bg"])
        opts_grid.pack(fill="x")
        for col in range(3):
            opts_grid.columnconfigure(col, weight=1, uniform="opts")

        for text, col in [("Formato:", 0), ("Orientacion:", 1), ("Margenes:", 2)]:
            tk.Label(
                opts_grid, text=text, font=("Segoe UI", 9, "bold"),
                bg=COLORS["section_bg"], fg=COLORS["accent"],
            ).grid(row=0, column=col, sticky="w", padx=4, pady=(0, 2))

        self.page_format = ttk.Combobox(
            opts_grid, values=["Sin formato", "A4", "Carta", "Legal"],
            state="readonly", font=("Segoe UI", 9),
        )
        self.page_format.grid(row=1, column=0, sticky="we", padx=4, pady=2)
        self.page_format.current(0)

        self.orientation = ttk.Combobox(
            opts_grid, values=["Vertical", "Horizontal"],
            state="readonly", font=("Segoe UI", 9),
        )
        self.orientation.grid(row=1, column=1, sticky="we", padx=4, pady=2)
        self.orientation.current(0)

        self.margin_option = ttk.Combobox(
            opts_grid, values=["Sin margenes", "Poco", "Medio", "Mucho"],
            state="readonly", font=("Segoe UI", 9),
        )
        self.margin_option.grid(row=1, column=2, sticky="we", padx=4, pady=2)
        self.margin_option.current(0)

        btn_convert = tk.Frame(self.frame, bg=COLORS["bg"])
        btn_convert.grid(row=4, column=0, pady=(10, 0))
        self._convert_btn = tk.Button(
            btn_convert, text="Convertir a PDF",
            font=("Segoe UI", 11, "bold"), bg=COLORS["accent"], fg="#ffffff",
            activebackground=COLORS["accent_active"], activeforeground="#ffffff",
            relief="flat", padx=24, pady=8, cursor="hand2",
        )
        self._convert_btn.pack()

        self.frame.columnconfigure(0, weight=1)

    def set_callbacks(self, on_add=None, on_remove=None, on_clear=None,
                      on_browse_folder=None, on_select=None, on_convert=None):
        if on_add:
            self._on_add_callback = on_add
        if on_remove:
            self._on_remove_callback = on_remove
        if on_clear:
            self._on_clear_callback = on_clear
        if on_browse_folder:
            self._on_browse_folder_callback = on_browse_folder
        if on_select:
            self._on_select_callback = on_select
        if on_convert:
            self._convert_btn.config(command=on_convert)

    def setup_dnd(self):
        if DND_FILES is not None:
            self.listbox.drop_target_register(DND_FILES)
            self.listbox.dnd_bind("<<Drop>>", self._on_drop)

    def _emit_add(self):
        if hasattr(self, "_on_add_callback") and self._on_add_callback:
            self._on_add_callback()

    def _emit_remove(self):
        if hasattr(self, "_on_remove_callback") and self._on_remove_callback:
            self._on_remove_callback()

    def _emit_clear(self):
        if hasattr(self, "_on_clear_callback") and self._on_clear_callback:
            self._on_clear_callback()

    def _emit_browse_folder(self):
        if hasattr(self, "_on_browse_folder_callback") and self._on_browse_folder_callback:
            self._on_browse_folder_callback()

    def _on_drop(self, event):
        import re
        files = re.findall(r'\{([^}]+)\}|(\S+)', event.data)
        paths = [f.strip() for match in files for f in match if f.strip()]
        added = 0
        for f in paths:
            if f.lower().endswith(self.IMAGE_EXTENSIONS) and f not in self.listbox.get(0, tk.END):
                self.listbox.insert(tk.END, f)
                added += 1
        return added

    def get_image_paths(self):
        return list(self.listbox.get(0, tk.END))

    def get_output_name(self):
        return self.output_name.get().strip()

    def get_output_folder(self):
        return self.output_folder.get().strip()

    def get_page_format(self):
        return self.page_format.get().strip() or "Sin formato"

    def get_orientation(self):
        return self.orientation.get().strip() or "Vertical"

    def get_margin_option(self):
        return self.margin_option.get().strip() or "Sin margenes"

    def set_output_folder(self, path):
        self.output_folder.delete(0, tk.END)
        self.output_folder.insert(0, path)

    def add_images(self, paths):
        for p in paths:
            if p not in self.listbox.get(0, tk.END):
                self.listbox.insert(tk.END, p)

    def remove_selected(self):
        for i in reversed(self.listbox.curselection()):
            self.listbox.delete(i)

    def clear_images(self):
        self.listbox.delete(0, tk.END)
        self.preview_label.config(image="", text="Sin vista previa")
        self._preview_image_ref = None

    def move_up(self):
        selected = self.listbox.curselection()
        if not selected:
            return
        for i in selected:
            if i == 0:
                continue
            text = self.listbox.get(i)
            self.listbox.delete(i)
            self.listbox.insert(i - 1, text)
        self.listbox.selection_clear(0, tk.END)
        for i in selected:
            if i > 0:
                self.listbox.selection_set(i - 1)

    def move_down(self):
        selected = self.listbox.curselection()
        if not selected:
            return
        for i in reversed(selected):
            if i == self.listbox.size() - 1:
                continue
            text = self.listbox.get(i)
            self.listbox.delete(i)
            self.listbox.insert(i + 1, text)
        self.listbox.selection_clear(0, tk.END)
        for i in selected:
            if i < self.listbox.size() - 1:
                self.listbox.selection_set(i + 1)

    def update_preview(self, path=None):
        if path is None:
            selection = self.listbox.curselection()
            if not selection:
                self.preview_label.config(image="", text="Sin vista previa")
                self._preview_image_ref = None
                return
            path = self.listbox.get(selection[0])

        if not os.path.isfile(path):
            self.preview_label.config(image="", text="Archivo no encontrado")
            self._preview_image_ref = None
            return
        try:
            with Image.open(path) as img:
                img.thumbnail((190, 150), Image.LANCZOS)
                if img.mode == "RGBA":
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    bg.paste(img, mask=img.split()[3])
                    img = bg
                elif img.mode != "RGB":
                    img = img.convert("RGB")
                photo = ImageTk.PhotoImage(img)
                self.preview_label.config(image=photo, text="")
                self._preview_image_ref = photo
        except Exception:
            self.preview_label.config(image="", text="No se pudo cargar")
            self._preview_image_ref = None

    def auto_select_first(self):
        if self.listbox.size() > 0 and not self.listbox.curselection():
            self.listbox.selection_set(0)
            self.update_preview()

import tkinter as tk
from tkinter import ttk, filedialog

try:
    from tkinterdnd2 import DND_FILES
except ImportError:
    DND_FILES = None

from views.widgets import COLORS, make_section, make_list_row_buttons, make_file_row
from views.field_factory import FieldFactory


class PdfToolsTab:

    OPERATIONS = [
        "Unir PDFs",
        "Dividir PDF",
        "Reordenar paginas",
        "Eliminar paginas",
        "Extraer paginas",
        "Optimizar PDF",
        "PDF a Imagenes",
    ]

    def __init__(self, parent):
        self.frame = parent
        self._on_operation_change_callback = None
        self._build()

    def _build(self):
        frame = self.frame

        sec_op = make_section(frame, "Operacion", 0)
        op_row = tk.Frame(sec_op, bg=COLORS["section_bg"])
        op_row.pack(fill="x")
        tk.Label(
            op_row, text="Seleccionar:", font=("Segoe UI", 9, "bold"),
            bg=COLORS["section_bg"], fg=COLORS["accent"], width=12, anchor="w",
        ).pack(side="left")
        self.operation = ttk.Combobox(
            op_row, values=self.OPERATIONS,
            state="readonly", font=("Segoe UI", 9),
        )
        self.operation.pack(side="left", fill="x", expand=True)
        self.operation.current(0)
        self.operation.bind("<<ComboboxSelected>>", self._on_operation_change)

        sec_files = make_section(frame, "Archivos PDF", 1)
        self.pdf_listbox = tk.Listbox(
            sec_files, selectmode=tk.EXTENDED, height=5,
            font=("Consolas", 9), bg=COLORS["input_bg"],
            selectbackground=COLORS["accent"], selectforeground="#ffffff",
            relief="solid", bd=1, activestyle="none",
        )
        self.pdf_listbox.pack(fill="x")
        scrollbar = ttk.Scrollbar(self.pdf_listbox, orient="vertical", command=self.pdf_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.pdf_listbox.config(yscrollcommand=scrollbar.set)

        make_list_row_buttons(sec_files, [
            ("+ Agregar", self._emit_add),
            ("x Quitar", self._emit_remove),
            ("Limpiar", self._emit_clear),
        ])

        self.dynamic_frame = ttk.LabelFrame(frame, text="  Opciones de operacion  ")
        self.dynamic_frame.grid(row=2, column=0, sticky="we", padx=8, pady=6)
        self.dynamic_inner = tk.Frame(self.dynamic_frame, bg=COLORS["section_bg"])
        self.dynamic_inner.pack(fill="x", padx=10, pady=8)

        sec_out = make_section(frame, "Destino", 3)
        self.pdf_output_folder = tk.Entry(
            sec_out, font=("Segoe UI", 9), bg=COLORS["input_bg"],
            relief="solid", bd=1,
        )
        make_file_row(sec_out, self.pdf_output_folder, self._emit_browse_folder)

        btn_exec = tk.Frame(frame, bg=COLORS["bg"])
        btn_exec.grid(row=4, column=0, pady=(10, 0))
        self._exec_btn = tk.Button(
            btn_exec, text="Ejecutar",
            font=("Segoe UI", 11, "bold"), bg=COLORS["accent"], fg="#ffffff",
            activebackground=COLORS["accent_active"], activeforeground="#ffffff",
            relief="flat", padx=24, pady=8, cursor="hand2",
        )
        self._exec_btn.pack()

        frame.columnconfigure(0, weight=1)
        self._setup_dynamic_fields()

    def set_callbacks(self, on_add=None, on_remove=None, on_clear=None,
                      on_browse_folder=None, on_execute=None):
        if on_add:
            self._on_add_callback = on_add
        if on_remove:
            self._on_remove_callback = on_remove
        if on_clear:
            self._on_clear_callback = on_clear
        if on_browse_folder:
            self._on_browse_folder_callback = on_browse_folder
        if on_execute:
            self._exec_btn.config(command=on_execute)

    def setup_dnd(self):
        if DND_FILES is not None:
            self.pdf_listbox.drop_target_register(DND_FILES)
            self.pdf_listbox.dnd_bind("<<Drop>>", self._on_drop)

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
            if f.lower().endswith(".pdf") and f not in self.pdf_listbox.get(0, tk.END):
                self.pdf_listbox.insert(tk.END, f)
                added += 1
        return added

    def _on_operation_change(self, event=None):
        self._setup_dynamic_fields()
        if self._on_operation_change_callback:
            self._on_operation_change_callback(self.operation.get())

    def get_operation(self):
        return self.operation.get()

    def get_pdf_paths(self):
        return list(self.pdf_listbox.get(0, tk.END))

    def get_output_folder(self):
        return self.pdf_output_folder.get().strip()

    def set_output_folder(self, path):
        self.pdf_output_folder.delete(0, tk.END)
        self.pdf_output_folder.insert(0, path)

    def get_split_ranges(self):
        return self._split_ranges_var.get().strip() if hasattr(self, "_split_ranges_var") else "1"

    def get_split_one_per_page(self):
        return self._split_one_per_page_var.get() if hasattr(self, "_split_one_per_page_var") else False

    def get_reorder_entry(self):
        return self._reorder_entry_var.get().strip() if hasattr(self, "_reorder_entry_var") else ""

    def get_remove_ranges(self):
        return self._remove_ranges_var.get().strip() if hasattr(self, "_remove_ranges_var") else ""

    def get_extract_ranges(self):
        return self._extract_ranges_var.get().strip() if hasattr(self, "_extract_ranges_var") else ""

    def get_compress_level(self):
        return self._compress_level_var.get() if hasattr(self, "_compress_level_var") else "Media"

    def get_img_format(self):
        return self._img_format_var.get() if hasattr(self, "_img_format_var") else "PNG"

    def get_img_dpi(self):
        return self._img_dpi_var.get() if hasattr(self, "_img_dpi_var") else "150"

    def get_img_quality(self):
        return self._img_quality_var.get() if hasattr(self, "_img_quality_var") else "Alta (95)"

    def _setup_dynamic_fields(self):
        for widget in self.dynamic_inner.winfo_children():
            widget.destroy()

        F = FieldFactory
        p = self.dynamic_inner
        op = self.operation.get()

        if op == "Unir PDFs":
            F.create_info_field(p, "Seleccione varios PDFs y se combinaran en un solo archivo.")

        elif op == "Dividir PDF":
            self._split_ranges_var = F.create_range_field(p, "Rangos:", "ej: 1-3,5,8-10", "1")
            self._split_one_per_page_var = F.create_checkbutton_field(p, "Una pagina por archivo")

        elif op == "Reordenar paginas":
            self._reorder_entry_var = F.create_range_field(p, "Nuevo orden:", "ej: 3,1,2,4")

        elif op == "Eliminar paginas":
            self._remove_ranges_var = F.create_range_field(p, "Paginas:", "ej: 1,3,5-7")

        elif op == "Extraer paginas":
            self._extract_ranges_var = F.create_range_field(p, "Paginas:", "ej: 1,3,5-7")

        elif op == "Optimizar PDF":
            self._compress_level_var = F.create_labeled_combobox_row(
                p, "Nivel:", ["Ligera", "Media", "Fuerte"], 1,
                "Mas compression = menor tamano, posible perdida de calidad",
            )

        elif op == "PDF a Imagenes":
            self._img_format_var = F.create_labeled_combobox_row(p, "Formato:", ["PNG", "JPG"], 0)
            self._img_dpi_var = F.create_labeled_combobox_row(p, "DPI:", ["72", "150", "300"], 1)
            self._img_quality_var = F.create_labeled_combobox_row(
                p, "Calidad JPG:", ["Baja (60)", "Media (80)", "Alta (95)"], 2,
                "Solo aplica si el formato es JPG",
            )

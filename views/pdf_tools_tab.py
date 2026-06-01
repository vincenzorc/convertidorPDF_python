import tkinter as tk
from tkinter import ttk, filedialog

try:
    from tkinterdnd2 import DND_FILES
except ImportError:
    DND_FILES = None

from views.widgets import COLORS, make_section, make_list_row_buttons, make_file_row


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
        return getattr(self, "split_ranges_var", None)

    def get_split_one_per_page(self):
        return getattr(self, "split_one_per_page", None)

    def get_reorder_entry(self):
        return getattr(self, "reorder_entry_var", None)

    def get_remove_ranges(self):
        return getattr(self, "remove_ranges_var", None)

    def get_extract_ranges(self):
        return getattr(self, "extract_ranges_var", None)

    def get_compress_level(self):
        return getattr(self, "compress_level_widget", None)

    def get_img_format(self):
        return getattr(self, "img_format_widget", None)

    def get_img_dpi(self):
        return getattr(self, "img_dpi_widget", None)

    def get_img_quality(self):
        return getattr(self, "img_quality_widget", None)

    def _setup_dynamic_fields(self):
        for widget in self.dynamic_inner.winfo_children():
            widget.destroy()

        op = self.operation.get()
        bg = COLORS["section_bg"]

        if op == "Unir PDFs":
            tk.Label(
                self.dynamic_inner,
                text="Seleccione varios PDFs y se combinaran en un solo archivo.",
                font=("Segoe UI", 9), fg=COLORS["muted"], bg=bg,
                wraplength=500, justify="left",
            ).pack(anchor="w")

        elif op == "Dividir PDF":
            row = tk.Frame(self.dynamic_inner, bg=bg)
            row.pack(fill="x", pady=2)
            tk.Label(row, text="Rangos:", font=("Segoe UI", 9, "bold"), bg=bg, width=12, anchor="w").pack(side="left")
            self.split_ranges_var = tk.StringVar(value="1")
            tk.Entry(row, textvariable=self.split_ranges_var, font=("Segoe UI", 9), bg=COLORS["input_bg"], relief="solid", bd=1).pack(side="left", fill="x", expand=True)
            tk.Label(row, text="ej: 1-3,5,8-10", font=("Segoe UI", 8), fg=COLORS["muted"], bg=bg).pack(side="left", padx=(6, 0))
            self.split_one_per_page = tk.BooleanVar()
            ttk.Checkbutton(self.dynamic_inner, text="Una pagina por archivo", variable=self.split_one_per_page).pack(anchor="w", pady=(6, 0))

        elif op == "Reordenar paginas":
            row = tk.Frame(self.dynamic_inner, bg=bg)
            row.pack(fill="x", pady=2)
            tk.Label(row, text="Nuevo orden:", font=("Segoe UI", 9, "bold"), bg=bg, width=12, anchor="w").pack(side="left")
            self.reorder_entry_var = tk.StringVar()
            tk.Entry(row, textvariable=self.reorder_entry_var, font=("Segoe UI", 9), bg=COLORS["input_bg"], relief="solid", bd=1).pack(side="left", fill="x", expand=True)
            tk.Label(row, text="ej: 3,1,2,4", font=("Segoe UI", 8), fg=COLORS["muted"], bg=bg).pack(side="left", padx=(6, 0))

        elif op == "Eliminar paginas":
            row = tk.Frame(self.dynamic_inner, bg=bg)
            row.pack(fill="x", pady=2)
            tk.Label(row, text="Paginas:", font=("Segoe UI", 9, "bold"), bg=bg, width=12, anchor="w").pack(side="left")
            self.remove_ranges_var = tk.StringVar()
            tk.Entry(row, textvariable=self.remove_ranges_var, font=("Segoe UI", 9), bg=COLORS["input_bg"], relief="solid", bd=1).pack(side="left", fill="x", expand=True)
            tk.Label(row, text="ej: 1,3,5-7", font=("Segoe UI", 8), fg=COLORS["muted"], bg=bg).pack(side="left", padx=(6, 0))

        elif op == "Extraer paginas":
            row = tk.Frame(self.dynamic_inner, bg=bg)
            row.pack(fill="x", pady=2)
            tk.Label(row, text="Paginas:", font=("Segoe UI", 9, "bold"), bg=bg, width=12, anchor="w").pack(side="left")
            self.extract_ranges_var = tk.StringVar()
            tk.Entry(row, textvariable=self.extract_ranges_var, font=("Segoe UI", 9), bg=COLORS["input_bg"], relief="solid", bd=1).pack(side="left", fill="x", expand=True)
            tk.Label(row, text="ej: 1,3,5-7", font=("Segoe UI", 8), fg=COLORS["muted"], bg=bg).pack(side="left", padx=(6, 0))

        elif op == "Optimizar PDF":
            row = tk.Frame(self.dynamic_inner, bg=bg)
            row.pack(fill="x", pady=2)
            tk.Label(row, text="Nivel:", font=("Segoe UI", 9, "bold"), bg=bg, width=12, anchor="w").pack(side="left")
            self.compress_level_widget = ttk.Combobox(row, values=["Ligera", "Media", "Fuerte"], state="readonly", font=("Segoe UI", 9))
            self.compress_level_widget.pack(side="left")
            self.compress_level_widget.current(1)
            tk.Label(row, text="Mas compression = menor tamano, posible perdida de calidad", font=("Segoe UI", 8), fg=COLORS["muted"], bg=bg).pack(side="left", padx=(10, 0))

        elif op == "PDF a Imagenes":
            row_fmt = tk.Frame(self.dynamic_inner, bg=bg)
            row_fmt.pack(fill="x", pady=2)
            tk.Label(row_fmt, text="Formato:", font=("Segoe UI", 9, "bold"), bg=bg, width=12, anchor="w").pack(side="left")
            self.img_format_widget = ttk.Combobox(row_fmt, values=["PNG", "JPG"], state="readonly", font=("Segoe UI", 9))
            self.img_format_widget.pack(side="left")
            self.img_format_widget.current(0)

            row_dpi = tk.Frame(self.dynamic_inner, bg=bg)
            row_dpi.pack(fill="x", pady=2)
            tk.Label(row_dpi, text="DPI:", font=("Segoe UI", 9, "bold"), bg=bg, width=12, anchor="w").pack(side="left")
            self.img_dpi_widget = ttk.Combobox(row_dpi, values=["72", "150", "300"], state="readonly", font=("Segoe UI", 9))
            self.img_dpi_widget.pack(side="left")
            self.img_dpi_widget.current(1)

            row_q = tk.Frame(self.dynamic_inner, bg=bg)
            row_q.pack(fill="x", pady=2)
            tk.Label(row_q, text="Calidad JPG:", font=("Segoe UI", 9, "bold"), bg=bg, width=12, anchor="w").pack(side="left")
            self.img_quality_widget = ttk.Combobox(row_q, values=["Baja (60)", "Media (80)", "Alta (95)"], state="readonly", font=("Segoe UI", 9))
            self.img_quality_widget.pack(side="left")
            self.img_quality_widget.current(2)
            tk.Label(row_q, text="Solo aplica si el formato es JPG", font=("Segoe UI", 8), fg=COLORS["muted"], bg=bg).pack(side="left", padx=(10, 0))

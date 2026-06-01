import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from pypdf import PdfReader
from image_tools import images_to_pdf
from pdf_tools import merge_pdfs, split_pdf, remove_pages, extract_pages, reorder_pages
from optimize_tools import optimize_pdf
from page_ranges import parse_page_ranges, parse_reorder_range


COLORS = {
    "bg": "#f0f2f5",
    "fg": "#1a1a2e",
    "accent": "#4361ee",
    "accent_hover": "#3a56d4",
    "accent_active": "#2f4bc0",
    "section_bg": "#ffffff",
    "border": "#d1d5db",
    "muted": "#6b7280",
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "input_bg": "#ffffff",
    "btn_secondary": "#e5e7eb",
    "btn_secondary_fg": "#374151",
}


class RoundedFrame(tk.Frame):
    def __init__(self, parent, **kwargs):
        bg = kwargs.pop("bg", COLORS["section_bg"])
        super().__init__(parent, bg=bg, **kwargs)
        self.configure(highlightbackground=COLORS["border"], highlightthickness=1)


class PDFConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Convertidor PDF")
        self.geometry("700x620")
        self.minsize(700, 620)
        self.configure(bg=COLORS["bg"])

        self._center_window()
        self._apply_theme()

        container = tk.Frame(self, bg=COLORS["bg"])
        container.pack(fill="both", expand=True, padx=16, pady=(12, 0))

        self._build_header(container)

        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True, pady=(8, 0))

        self.tab_image = tk.Frame(self.notebook, bg=COLORS["bg"])
        self.notebook.add(self.tab_image, text="  Imagen a PDF  ")
        self.setup_image_tab()

        self.tab_pdf = tk.Frame(self.notebook, bg=COLORS["bg"])
        self.notebook.add(self.tab_pdf, text="  Herramientas PDF  ")
        self.setup_pdf_tab()

        self._build_status_bar()

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"+{x}+{y}")

    def _apply_theme(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(".", background=COLORS["bg"], foreground=COLORS["fg"])
        style.configure("TNotebook", background=COLORS["bg"], borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=COLORS["btn_secondary"],
            foreground=COLORS["btn_secondary_fg"],
            padding=[16, 6],
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", COLORS["section_bg"])],
            foreground=[("selected", COLORS["accent"])],
        )

        style.configure(
            "Accent.TButton",
            background=COLORS["accent"],
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=[12, 6],
        )
        style.map(
            "Accent.TButton",
            background=[
                ("active", COLORS["accent_active"]),
                ("pressed", COLORS["accent_active"]),
            ],
        )

        style.configure(
            "Secondary.TButton",
            background=COLORS["btn_secondary"],
            foreground=COLORS["btn_secondary_fg"],
            font=("Segoe UI", 9),
            padding=[8, 4],
        )
        style.map(
            "Secondary.TButton",
            background=[("active", COLORS["border"])],
        )

        style.configure(
            "TLabel",
            background=COLORS["bg"],
            foreground=COLORS["fg"],
            font=("Segoe UI", 9),
        )
        style.configure(
            "Header.TLabel",
            font=("Segoe UI", 11, "bold"),
            foreground=COLORS["fg"],
            background=COLORS["bg"],
        )
        style.configure(
            "Muted.TLabel",
            foreground=COLORS["muted"],
            font=("Segoe UI", 8),
            background=COLORS["bg"],
        )

        style.configure("TCombobox", padding=4, font=("Segoe UI", 9))
        style.configure("TCheckbutton", font=("Segoe UI", 9), background=COLORS["section_bg"])

        style.configure(
            "TLabelframe",
            background=COLORS["section_bg"],
            foreground=COLORS["fg"],
            font=("Segoe UI", 9, "bold"),
            bordercolor=COLORS["border"],
            relief="groove",
        )
        style.configure(
            "TLabelframe.Label",
            background=COLORS["section_bg"],
            foreground=COLORS["accent"],
            font=("Segoe UI", 9, "bold"),
        )

    def _build_header(self, parent):
        header = tk.Frame(parent, bg=COLORS["bg"])
        header.pack(fill="x", pady=(0, 4))

        tk.Label(
            header,
            text="Convertidor PDF",
            font=("Segoe UI", 16, "bold"),
            fg=COLORS["accent"],
            bg=COLORS["bg"],
        ).pack(side="left")

        tk.Label(
            header,
            text="v1.0",
            font=("Segoe UI", 9),
            fg=COLORS["muted"],
            bg=COLORS["bg"],
        ).pack(side="left", padx=(8, 0), pady=(4, 0))

    def _build_status_bar(self):
        bar = tk.Frame(self, bg=COLORS["border"], height=1)
        bar.pack(fill="x", side="bottom")

        status_frame = tk.Frame(self, bg=COLORS["section_bg"], height=28)
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)

        self.status_dot = tk.Label(
            status_frame,
            text="\u25cf",
            font=("Segoe UI", 8),
            fg=COLORS["success"],
            bg=COLORS["section_bg"],
        )
        self.status_dot.pack(side="left", padx=(12, 4), pady=4)

        self.progress = tk.Label(
            status_frame,
            text="Listo",
            font=("Segoe UI", 9),
            fg=COLORS["muted"],
            bg=COLORS["section_bg"],
            anchor="w",
        )
        self.progress.pack(side="left", fill="x", expand=True, pady=4)

    def _set_status(self, text, color=None):
        self.progress.config(text=text, fg=color or COLORS["muted"])
        self.status_dot.config(fg=color or COLORS["success"])

    def _make_section(self, parent, title, row, column=0, columnspan=3, **pack_kwargs):
        section = ttk.LabelFrame(parent, text=f"  {title}  ")
        section.grid(row=row, column=column, columnspan=columnspan, sticky="we", padx=8, pady=6)
        inner = tk.Frame(section, bg=COLORS["section_bg"])
        inner.pack(fill="x", padx=10, pady=8)
        return inner

    def _make_list_row_buttons(self, parent, commands):
        btn_frame = tk.Frame(parent, bg=COLORS["section_bg"])
        btn_frame.pack(fill="x", pady=(4, 0))
        for text, cmd in commands:
            ttk.Button(btn_frame, text=text, style="Secondary.TButton", command=cmd).pack(side="left", padx=2)
        return btn_frame

    def _make_file_row(self, parent, entry, browse_cmd, row_label="Carpeta de salida:"):
        row = tk.Frame(parent, bg=COLORS["section_bg"])
        row.pack(fill="x", pady=3)
        tk.Label(
            row, text=row_label, font=("Segoe UI", 9),
            bg=COLORS["section_bg"], fg=COLORS["fg"], width=18, anchor="w",
        ).pack(side="left")
        entry.config(bg=COLORS["input_bg"], font=("Segoe UI", 9), relief="solid", bd=1)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(row, text="Examinar", style="Secondary.TButton", command=browse_cmd).pack(side="right")
        return row

    # ------------------------------------------------------------------ #
    #  IMAGE TAB                                                          #
    # ------------------------------------------------------------------ #
    def setup_image_tab(self):
        frame = self.tab_image

        sec_files = self._make_section(frame, "Archivos", 0)
        self.listbox_images = tk.Listbox(
            sec_files,
            selectmode=tk.EXTENDED,
            height=7,
            font=("Consolas", 9),
            bg=COLORS["input_bg"],
            selectbackground=COLORS["accent"],
            selectforeground="#ffffff",
            relief="solid",
            bd=1,
            activestyle="none",
        )
        self.listbox_images.pack(fill="x")
        scrollbar = ttk.Scrollbar(self.listbox_images, orient="vertical", command=self.listbox_images.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox_images.config(yscrollcommand=scrollbar.set)

        self._make_list_row_buttons(sec_files, [
            ("+ Agregar", self.add_images),
            ("^ Subir", self.move_up),
            ("v Bajar", self.move_down),
            ("x Quitar", self.remove_selected),
            ("Limpiar", self.clear_images),
        ])

        sec_name = self._make_section(frame, "Nombre del archivo", 1)
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

        sec_out = self._make_section(frame, "Destino", 2)
        self.output_folder = tk.Entry(
            sec_out, font=("Segoe UI", 9), bg=COLORS["input_bg"],
            relief="solid", bd=1,
        )
        self._make_file_row(sec_out, self.output_folder, self.browse_output_folder)

        sec_opts = self._make_section(frame, "Formato de pagina", 3)
        opts_grid = tk.Frame(sec_opts, bg=COLORS["section_bg"])
        opts_grid.pack(fill="x")

        for col in range(3):
            opts_grid.columnconfigure(col, weight=1, uniform="opts")

        labels = [("Formato:", 0), ("Orientacion:", 1), ("Margenes:", 2)]
        for text, col in labels:
            tk.Label(
                opts_grid, text=text, font=("Segoe UI", 9, "bold"),
                bg=COLORS["section_bg"], fg=COLORS["accent"],
            ).grid(row=0, column=col, sticky="w", padx=4, pady=(0, 2))

        self.page_format = ttk.Combobox(
            opts_grid,
            values=["Sin formato", "A4", "Carta", "Legal"],
            state="readonly",
            font=("Segoe UI", 9),
        )
        self.page_format.grid(row=1, column=0, sticky="we", padx=4, pady=2)
        self.page_format.current(0)

        self.orientation = ttk.Combobox(
            opts_grid,
            values=["Vertical", "Horizontal"],
            state="readonly",
            font=("Segoe UI", 9),
        )
        self.orientation.grid(row=1, column=1, sticky="we", padx=4, pady=2)
        self.orientation.current(0)

        self.margin_option = ttk.Combobox(
            opts_grid,
            values=["Sin margenes", "Poco", "Medio", "Mucho"],
            state="readonly",
            font=("Segoe UI", 9),
        )
        self.margin_option.grid(row=1, column=2, sticky="we", padx=4, pady=2)
        self.margin_option.current(0)

        btn_convert = tk.Frame(frame, bg=COLORS["bg"])
        btn_convert.grid(row=4, column=0, pady=(10, 0))
        tk.Button(
            btn_convert,
            text="Convertir a PDF",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["accent"],
            fg="#ffffff",
            activebackground=COLORS["accent_active"],
            activeforeground="#ffffff",
            relief="flat",
            padx=24,
            pady=8,
            cursor="hand2",
            command=self.convert_images_to_pdf,
        ).pack()

        frame.columnconfigure(0, weight=1)

    # ------------------------------------------------------------------ #
    #  PDF TOOLS TAB                                                      #
    # ------------------------------------------------------------------ #
    def setup_pdf_tab(self):
        frame = self.tab_pdf

        sec_op = self._make_section(frame, "Operacion", 0)
        op_row = tk.Frame(sec_op, bg=COLORS["section_bg"])
        op_row.pack(fill="x")
        tk.Label(
            op_row, text="Seleccionar:", font=("Segoe UI", 9, "bold"),
            bg=COLORS["section_bg"], fg=COLORS["accent"], width=12, anchor="w",
        ).pack(side="left")
        self.operation = ttk.Combobox(
            op_row,
            values=[
                "Unir PDFs",
                "Dividir PDF",
                "Reordenar paginas",
                "Eliminar paginas",
                "Extraer paginas",
                "Optimizar PDF",
            ],
            state="readonly",
            font=("Segoe UI", 9),
        )
        self.operation.pack(side="left", fill="x", expand=True)
        self.operation.current(0)
        self.operation.bind("<<ComboboxSelected>>", self.on_operation_change)

        sec_files = self._make_section(frame, "Archivos PDF", 1)
        self.pdf_listbox = tk.Listbox(
            sec_files,
            selectmode=tk.EXTENDED,
            height=5,
            font=("Consolas", 9),
            bg=COLORS["input_bg"],
            selectbackground=COLORS["accent"],
            selectforeground="#ffffff",
            relief="solid",
            bd=1,
            activestyle="none",
        )
        self.pdf_listbox.pack(fill="x")
        scrollbar = ttk.Scrollbar(self.pdf_listbox, orient="vertical", command=self.pdf_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.pdf_listbox.config(yscrollcommand=scrollbar.set)

        self._make_list_row_buttons(sec_files, [
            ("+ Agregar", self.add_pdfs),
            ("x Quitar", self.remove_selected_pdfs),
            ("Limpiar", self.clear_pdfs),
        ])

        self.dynamic_frame = ttk.LabelFrame(frame, text="  Opciones de operacion  ")
        self.dynamic_frame.grid(row=2, column=0, sticky="we", padx=8, pady=6)
        inner = tk.Frame(self.dynamic_frame, bg=COLORS["section_bg"])
        inner.pack(fill="x", padx=10, pady=8)
        self.dynamic_inner = inner
        self.setup_dynamic_fields()

        sec_out = self._make_section(frame, "Destino", 3)
        self.pdf_output_folder = tk.Entry(
            sec_out, font=("Segoe UI", 9), bg=COLORS["input_bg"],
            relief="solid", bd=1,
        )
        self._make_file_row(sec_out, self.pdf_output_folder, self.browse_pdf_output_folder)

        btn_exec = tk.Frame(frame, bg=COLORS["bg"])
        btn_exec.grid(row=4, column=0, pady=(10, 0))
        tk.Button(
            btn_exec,
            text="Ejecutar",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["accent"],
            fg="#ffffff",
            activebackground=COLORS["accent_active"],
            activeforeground="#ffffff",
            relief="flat",
            padx=24,
            pady=8,
            cursor="hand2",
            command=self.execute_pdf_operation,
        ).pack()

        frame.columnconfigure(0, weight=1)
        self.on_operation_change()

    def setup_dynamic_fields(self):
        for widget in self.dynamic_inner.winfo_children():
            widget.destroy()

        op = self.operation.get()
        bg = COLORS["section_bg"]

        if op == "Unir PDFs":
            tk.Label(
                self.dynamic_inner,
                text="Seleccione varios PDFs y se combinaran en un solo archivo.",
                font=("Segoe UI", 9),
                fg=COLORS["muted"],
                bg=bg,
                wraplength=500,
                justify="left",
            ).pack(anchor="w")

        elif op == "Dividir PDF":
            row = tk.Frame(self.dynamic_inner, bg=bg)
            row.pack(fill="x", pady=2)
            tk.Label(
                row, text="Rangos:", font=("Segoe UI", 9, "bold"),
                bg=bg, width=12, anchor="w",
            ).pack(side="left")
            self.split_ranges = tk.Entry(
                row, font=("Segoe UI", 9), bg=COLORS["input_bg"],
                relief="solid", bd=1,
            )
            self.split_ranges.insert(0, "1")
            self.split_ranges.pack(side="left", fill="x", expand=True)
            tk.Label(
                row, text="ej: 1-3,5,8-10", font=("Segoe UI", 8),
                fg=COLORS["muted"], bg=bg,
            ).pack(side="left", padx=(6, 0))

            self.split_one_per_page = tk.BooleanVar()
            ttk.Checkbutton(
                self.dynamic_inner,
                text="Una pagina por archivo",
                variable=self.split_one_per_page,
            ).pack(anchor="w", pady=(6, 0))

        elif op == "Reordenar paginas":
            row = tk.Frame(self.dynamic_inner, bg=bg)
            row.pack(fill="x", pady=2)
            tk.Label(
                row, text="Nuevo orden:", font=("Segoe UI", 9, "bold"),
                bg=bg, width=12, anchor="w",
            ).pack(side="left")
            self.reorder_entry = tk.Entry(
                row, font=("Segoe UI", 9), bg=COLORS["input_bg"],
                relief="solid", bd=1,
            )
            self.reorder_entry.pack(side="left", fill="x", expand=True)
            tk.Label(
                row, text="ej: 3,1,2,4", font=("Segoe UI", 8),
                fg=COLORS["muted"], bg=bg,
            ).pack(side="left", padx=(6, 0))

        elif op == "Eliminar paginas":
            row = tk.Frame(self.dynamic_inner, bg=bg)
            row.pack(fill="x", pady=2)
            tk.Label(
                row, text="Paginas:", font=("Segoe UI", 9, "bold"),
                bg=bg, width=12, anchor="w",
            ).pack(side="left")
            self.remove_ranges = tk.Entry(
                row, font=("Segoe UI", 9), bg=COLORS["input_bg"],
                relief="solid", bd=1,
            )
            self.remove_ranges.pack(side="left", fill="x", expand=True)
            tk.Label(
                row, text="ej: 1,3,5-7", font=("Segoe UI", 8),
                fg=COLORS["muted"], bg=bg,
            ).pack(side="left", padx=(6, 0))

        elif op == "Extraer paginas":
            row = tk.Frame(self.dynamic_inner, bg=bg)
            row.pack(fill="x", pady=2)
            tk.Label(
                row, text="Paginas:", font=("Segoe UI", 9, "bold"),
                bg=bg, width=12, anchor="w",
            ).pack(side="left")
            self.extract_ranges = tk.Entry(
                row, font=("Segoe UI", 9), bg=COLORS["input_bg"],
                relief="solid", bd=1,
            )
            self.extract_ranges.pack(side="left", fill="x", expand=True)
            tk.Label(
                row, text="ej: 1,3,5-7", font=("Segoe UI", 8),
                fg=COLORS["muted"], bg=bg,
            ).pack(side="left", padx=(6, 0))

        elif op == "Optimizar PDF":
            row = tk.Frame(self.dynamic_inner, bg=bg)
            row.pack(fill="x", pady=2)
            tk.Label(
                row, text="Nivel:", font=("Segoe UI", 9, "bold"),
                bg=bg, width=12, anchor="w",
            ).pack(side="left")
            self.compress_level = ttk.Combobox(
                row,
                values=["Ligera", "Media", "Fuerte"],
                state="readonly",
                font=("Segoe UI", 9),
            )
            self.compress_level.pack(side="left")
            self.compress_level.current(1)

            tk.Label(
                row,
                text="Mas compression = menor tamano, posible perdida de calidad",
                font=("Segoe UI", 8),
                fg=COLORS["muted"],
                bg=bg,
            ).pack(side="left", padx=(10, 0))

    def on_operation_change(self, event=None):
        self.setup_dynamic_fields()

    # ------------------------------------------------------------------ #
    #  IMAGE TAB LOGIC                                                    #
    # ------------------------------------------------------------------ #
    def add_images(self):
        files = filedialog.askopenfilenames(
            title="Seleccionar imagenes",
            filetypes=[
                ("Imagenes", "*.png *.jpg *.jpeg *.webp"),
                ("Todos los archivos", "*.*"),
            ],
        )
        for f in files:
            if f not in self.listbox_images.get(0, tk.END):
                self.listbox_images.insert(tk.END, f)
        self._set_status(f"{self.listbox_images.size()} imagen(es) seleccionada(s)")

    def move_up(self):
        selected = self.listbox_images.curselection()
        if not selected:
            return
        for i in selected:
            if i == 0:
                continue
            text = self.listbox_images.get(i)
            self.listbox_images.delete(i)
            self.listbox_images.insert(i - 1, text)
        self.listbox_images.selection_clear(0, tk.END)
        for i in selected:
            if i > 0:
                self.listbox_images.selection_set(i - 1)

    def move_down(self):
        selected = self.listbox_images.curselection()
        if not selected:
            return
        for i in reversed(selected):
            if i == self.listbox_images.size() - 1:
                continue
            text = self.listbox_images.get(i)
            self.listbox_images.delete(i)
            self.listbox_images.insert(i + 1, text)
        self.listbox_images.selection_clear(0, tk.END)
        for i in selected:
            if i < self.listbox_images.size() - 1:
                self.listbox_images.selection_set(i + 1)

    def remove_selected(self):
        selected = self.listbox_images.curselection()
        for i in reversed(selected):
            self.listbox_images.delete(i)
        self._set_status(f"{self.listbox_images.size()} imagen(es) en la lista")

    def clear_images(self):
        self.listbox_images.delete(0, tk.END)
        self._set_status("Lista de imagenes vacia")

    def browse_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder.delete(0, tk.END)
            self.output_folder.insert(0, folder)

    def convert_images_to_pdf(self):
        image_paths = self.listbox_images.get(0, tk.END)
        if not image_paths:
            messagebox.showwarning("Advertencia", "No hay imagenes seleccionadas")
            return
        output_name = self.output_name.get().strip()
        if not output_name:
            messagebox.showwarning("Advertencia", "Ingrese un nombre para el PDF de salida")
            return
        if not output_name.lower().endswith(".pdf"):
            output_name += ".pdf"
        output_folder = self.output_folder.get().strip()
        if not output_folder:
            messagebox.showwarning("Advertencia", "Seleccione una carpeta de salida")
            return

        page_format = self.page_format.get().strip() or "Sin formato"
        margin_option = self.margin_option.get().strip() or "Sin margenes"
        orientation = self.orientation.get().strip() or "Vertical"
        output_path = os.path.join(output_folder, output_name)

        self._set_status("Convirtiendo...", COLORS["warning"])
        threading.Thread(
            target=self._convert_images_thread,
            args=(list(image_paths), output_path, page_format, margin_option, orientation),
            daemon=True,
        ).start()

    def _convert_images_thread(self, image_paths, output_path, page_format, margin_option, orientation):
        success = images_to_pdf(
            image_paths,
            output_path,
            page_size=page_format,
            margins=margin_option,
            orientation=orientation,
        )
        if success:
            self._set_status(f"Completado: {os.path.basename(output_path)}", COLORS["success"])
            messagebox.showinfo("Exito", f"PDF creado correctamente:\n{output_path}")
        else:
            self._set_status("Error en la conversion", COLORS["error"])
            messagebox.showerror("Error", "No se pudo convertir las imagenes a PDF")

    # ------------------------------------------------------------------ #
    #  PDF TOOLS LOGIC                                                    #
    # ------------------------------------------------------------------ #
    def add_pdfs(self):
        files = filedialog.askopenfilenames(
            title="Seleccionar PDFs",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        for f in files:
            if f not in self.pdf_listbox.get(0, tk.END):
                self.pdf_listbox.insert(tk.END, f)
        self._set_status(f"{self.pdf_listbox.size()} PDF(s) seleccionado(s)")

    def remove_selected_pdfs(self):
        selected = self.pdf_listbox.curselection()
        for i in reversed(selected):
            self.pdf_listbox.delete(i)
        self._set_status(f"{self.pdf_listbox.size()} PDF(s) en la lista")

    def clear_pdfs(self):
        self.pdf_listbox.delete(0, tk.END)
        self._set_status("Lista de PDFs vacia")

    def browse_pdf_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.pdf_output_folder.delete(0, tk.END)
            self.pdf_output_folder.insert(0, folder)

    def execute_pdf_operation(self):
        op = self.operation.get()
        pdf_files = self.pdf_listbox.get(0, tk.END)
        if not pdf_files:
            messagebox.showwarning("Advertencia", "No hay PDFs seleccionados")
            return
        output_folder = self.pdf_output_folder.get().strip()
        if not output_folder:
            messagebox.showwarning("Advertencia", "Seleccione una carpeta de salida")
            return

        self._set_status(f"Ejecutando: {op}...", COLORS["warning"])
        threading.Thread(
            target=self._pdf_operation_thread,
            args=(op, list(pdf_files), output_folder),
            daemon=True,
        ).start()

    def _pdf_operation_thread(self, op, pdf_files, output_folder):
        try:
            if op == "Unir PDFs":
                output_name = "unido.pdf"
                output_path = os.path.join(output_folder, output_name)
                success = merge_pdfs(pdf_files, output_path)
                if success:
                    self._set_status("PDFs unidos correctamente", COLORS["success"])
                    messagebox.showinfo("Exito", f"PDFs unidos correctamente:\n{output_path}")
                else:
                    self._set_status("Error al unir PDFs", COLORS["error"])
                    messagebox.showerror("Error", "No se pudo unir los PDFs")

            elif op == "Dividir PDF":
                if len(pdf_files) != 1:
                    messagebox.showwarning("Advertencia", "Para dividir, seleccione exactamente un PDF")
                    self._set_status("Listo")
                    return
                input_path = pdf_files[0]
                ranges_str = self.split_ranges.get().strip()
                one_per_page = self.split_one_per_page.get()
                if one_per_page:
                    reader = PdfReader(input_path)
                    total_pages = len(reader.pages)
                    ranges = [[i + 1] for i in range(total_pages)]
                else:
                    ranges_list = parse_page_ranges(ranges_str, len(PdfReader(input_path).pages))
                    if not ranges_list:
                        messagebox.showwarning("Advertencia", "Rangos no validos")
                        self._set_status("Listo")
                        return
                    parts = ranges_str.split(",")
                    ranges = []
                    for part in parts:
                        part = part.strip()
                        if "-" in part:
                            start, end = part.split("-")
                            start = int(start.strip())
                            end = int(end.strip())
                        else:
                            start = end = int(part)
                        reader = PdfReader(input_path)
                        total_pages = len(reader.pages)
                        start = max(1, min(start, total_pages))
                        end = max(1, min(end, total_pages))
                        if start > end:
                            start, end = end, start
                        ranges.append(list(range(start, end + 1)))
                success = split_pdf(input_path, output_folder, ranges)
                if success:
                    self._set_status(f"PDF dividido en {len(ranges)} parte(s)", COLORS["success"])
                    messagebox.showinfo("Exito", f"PDF dividido correctamente en {len(ranges)} parte(s)")
                else:
                    self._set_status("Error al dividir PDF", COLORS["error"])
                    messagebox.showerror("Error", "No se pudo dividir el PDF")

            elif op == "Reordenar paginas":
                if len(pdf_files) != 1:
                    messagebox.showwarning("Advertencia", "Para reordenar, seleccione exactamente un PDF")
                    self._set_status("Listo")
                    return
                input_path = pdf_files[0]
                order_str = self.reorder_entry.get().strip()
                reader = PdfReader(input_path)
                total_pages = len(reader.pages)
                new_order = parse_reorder_range(order_str, total_pages)
                if not new_order:
                    messagebox.showwarning(
                        "Advertencia",
                        "Orden no valido. Use formato como '3,1,2,4' y asegurese de incluir todas las paginas sin repetir.",
                    )
                    self._set_status("Listo")
                    return
                output_name = "reordenado.pdf"
                output_path = os.path.join(output_folder, output_name)
                success = reorder_pages(input_path, output_path, new_order)
                if success:
                    self._set_status("Paginas reordenadas", COLORS["success"])
                    messagebox.showinfo("Exito", f"Paginas reordenadas correctamente:\n{output_path}")
                else:
                    self._set_status("Error al reordenar paginas", COLORS["error"])
                    messagebox.showerror("Error", "No se pudo reordenar las paginas")

            elif op == "Eliminar paginas":
                if len(pdf_files) != 1:
                    messagebox.showwarning("Advertencia", "Para eliminar paginas, seleccione exactamente un PDF")
                    self._set_status("Listo")
                    return
                input_path = pdf_files[0]
                ranges_str = self.remove_ranges.get().strip()
                pages_to_remove = parse_page_ranges(ranges_str, len(PdfReader(input_path).pages))
                if not pages_to_remove and ranges_str:
                    messagebox.showwarning("Advertencia", "Rangos no validos")
                    self._set_status("Listo")
                    return
                output_name = "sin_eliminadas.pdf"
                output_path = os.path.join(output_folder, output_name)
                success = remove_pages(input_path, output_path, pages_to_remove)
                if success:
                    self._set_status("Paginas eliminadas", COLORS["success"])
                    messagebox.showinfo("Exito", f"Paginas eliminadas correctamente:\n{output_path}")
                else:
                    self._set_status("Error al eliminar paginas", COLORS["error"])
                    messagebox.showerror("Error", "No se pudo eliminar las paginas")

            elif op == "Extraer paginas":
                if len(pdf_files) != 1:
                    messagebox.showwarning("Advertencia", "Para extraer paginas, seleccione exactamente un PDF")
                    self._set_status("Listo")
                    return
                input_path = pdf_files[0]
                ranges_str = self.extract_ranges.get().strip()
                pages_to_extract = parse_page_ranges(ranges_str, len(PdfReader(input_path).pages))
                if not pages_to_extract and ranges_str:
                    messagebox.showwarning("Advertencia", "Rangos no validos")
                    self._set_status("Listo")
                    return
                output_name = "extraidas.pdf"
                output_path = os.path.join(output_folder, output_name)
                success = extract_pages(input_path, output_path, pages_to_extract)
                if success:
                    self._set_status("Paginas extraidas", COLORS["success"])
                    messagebox.showinfo("Exito", f"Paginas extraidas correctamente:\n{output_path}")
                else:
                    self._set_status("Error al extraer paginas", COLORS["error"])
                    messagebox.showerror("Error", "No se pudo extraer las paginas")

            elif op == "Optimizar PDF":
                if len(pdf_files) != 1:
                    messagebox.showwarning("Advertencia", "Para optimizar, seleccione exactamente un PDF")
                    self._set_status("Listo")
                    return
                input_path = pdf_files[0]
                level_map = {"Ligera": "light", "Media": "medium", "Fuerte": "strong"}
                level = level_map[self.compress_level.get()]
                output_name = "optimizado.pdf"
                output_path = os.path.join(output_folder, output_name)
                success = optimize_pdf(input_path, output_path, level)
                if success:
                    self._set_status("PDF optimizado", COLORS["success"])
                    messagebox.showinfo("Exito", f"PDF optimizado correctamente:\n{output_path}")
                else:
                    self._set_status("Error al optimizar PDF", COLORS["error"])
                    messagebox.showerror("Error", "No se pudo optimizar el PDF")

        except Exception as e:
            self._set_status("Error inesperado", COLORS["error"])
            messagebox.showerror("Error", f"Ocurrio un error inesperado:\n{str(e)}")
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    app = PDFConverterApp()
    app.mainloop()

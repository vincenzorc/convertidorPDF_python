import tkinter as tk
from tkinter import ttk
from views.widgets import COLORS


class FieldFactory:

    @staticmethod
    def create_info_field(parent, text):
        tk.Label(
            parent, text=text,
            font=("Segoe UI", 9), fg=COLORS["muted"], bg=COLORS["section_bg"],
            wraplength=500, justify="left",
        ).pack(anchor="w")

    @staticmethod
    def create_range_field(parent, label, hint, default=""):
        bg = COLORS["section_bg"]
        row = tk.Frame(parent, bg=bg)
        row.pack(fill="x", pady=2)
        tk.Label(
            row, text=label, font=("Segoe UI", 9, "bold"),
            bg=bg, width=12, anchor="w",
        ).pack(side="left")
        var = tk.StringVar(value=default)
        tk.Entry(
            row, textvariable=var, font=("Segoe UI", 9),
            bg=COLORS["input_bg"], relief="solid", bd=1,
        ).pack(side="left", fill="x", expand=True)
        tk.Label(
            row, text=hint, font=("Segoe UI", 8),
            fg=COLORS["muted"], bg=bg,
        ).pack(side="left", padx=(6, 0))
        return var

    @staticmethod
    def create_combobox_field(parent, label, values, default_index=0):
        bg = COLORS["section_bg"]
        row = tk.Frame(parent, bg=bg)
        row.pack(fill="x", pady=2)
        tk.Label(
            row, text=label, font=("Segoe UI", 9, "bold"),
            bg=bg, width=12, anchor="w",
        ).pack(side="left")
        widget = ttk.Combobox(
            row, values=values, state="readonly", font=("Segoe UI", 9),
        )
        widget.pack(side="left")
        widget.current(default_index)
        return widget

    @staticmethod
    def create_checkbutton_field(parent, text):
        var = tk.BooleanVar()
        ttk.Checkbutton(parent, text=text, variable=var).pack(anchor="w", pady=(6, 0))
        return var

    @staticmethod
    def create_labeled_combobox_row(parent, label, values, default_index=0, hint=""):
        bg = COLORS["section_bg"]
        row = tk.Frame(parent, bg=bg)
        row.pack(fill="x", pady=2)
        tk.Label(
            row, text=label, font=("Segoe UI", 9, "bold"),
            bg=bg, width=12, anchor="w",
        ).pack(side="left")
        widget = ttk.Combobox(
            row, values=values, state="readonly", font=("Segoe UI", 9),
        )
        widget.pack(side="left")
        widget.current(default_index)
        if hint:
            tk.Label(
                row, text=hint, font=("Segoe UI", 8),
                fg=COLORS["muted"], bg=bg,
            ).pack(side="left", padx=(10, 0))
        return widget

import tkinter as tk
from tkinter import ttk


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


def apply_theme(root):
    style = ttk.Style(root)
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
    style.map("Secondary.TButton", background=[("active", COLORS["border"])])
    style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["fg"], font=("Segoe UI", 9))
    style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"), foreground=COLORS["fg"], background=COLORS["bg"])
    style.configure("Muted.TLabel", foreground=COLORS["muted"], font=("Segoe UI", 8), background=COLORS["bg"])
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
    return style


def make_section(parent, title, row, column=0, columnspan=3):
    section = ttk.LabelFrame(parent, text=f"  {title}  ")
    section.grid(row=row, column=column, columnspan=columnspan, sticky="we", padx=8, pady=6)
    inner = tk.Frame(section, bg=COLORS["section_bg"])
    inner.pack(fill="x", padx=10, pady=8)
    return inner


def make_list_row_buttons(parent, commands):
    btn_frame = tk.Frame(parent, bg=COLORS["section_bg"])
    btn_frame.pack(fill="x", pady=(4, 0))
    for text, cmd in commands:
        ttk.Button(btn_frame, text=text, style="Secondary.TButton", command=cmd).pack(side="left", padx=2)
    return btn_frame


def make_file_row(parent, entry, browse_cmd, row_label="Carpeta de salida:"):
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

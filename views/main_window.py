import tkinter as tk
from tkinter import ttk

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAS_DND = True
except ImportError:
    HAS_DND = False

from views.widgets import COLORS, apply_theme


class MainWindow(TkinterDnD.Tk if HAS_DND else tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Convertidor PDF")
        self.geometry("860x710")
        self.minsize(860, 710)
        self.configure(bg=COLORS["bg"])

        self._center_window()
        apply_theme(self)

        container = tk.Frame(self, bg=COLORS["bg"])
        container.pack(fill="both", expand=True, padx=16, pady=(12, 0))

        self._build_header(container)

        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True, pady=(8, 0))

        self._build_status_bar()

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"+{x}+{y}")

    def _build_header(self, parent):
        header = tk.Frame(parent, bg=COLORS["bg"])
        header.pack(fill="x", pady=(0, 4))
        tk.Label(
            header, text="Convertidor PDF",
            font=("Segoe UI", 16, "bold"), fg=COLORS["accent"], bg=COLORS["bg"],
        ).pack(side="left")
        tk.Label(
            header, text="v1.0",
            font=("Segoe UI", 9), fg=COLORS["muted"], bg=COLORS["bg"],
        ).pack(side="left", padx=(8, 0), pady=(4, 0))

    def _build_status_bar(self):
        bar = tk.Frame(self, bg=COLORS["border"], height=1)
        bar.pack(fill="x", side="bottom")

        status_frame = tk.Frame(self, bg=COLORS["section_bg"], height=28)
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)

        self.status_dot = tk.Label(
            status_frame, text="\u25cf", font=("Segoe UI", 8),
            fg=COLORS["success"], bg=COLORS["section_bg"],
        )
        self.status_dot.pack(side="left", padx=(12, 4), pady=4)

        self.status_label = tk.Label(
            status_frame, text="Listo", font=("Segoe UI", 9),
            fg=COLORS["muted"], bg=COLORS["section_bg"], anchor="w",
        )
        self.status_label.pack(side="left", fill="x", expand=True, pady=4)

    def set_status(self, text, color=None):
        self.status_label.config(text=text, fg=color or COLORS["muted"])
        self.status_dot.config(fg=color or COLORS["success"])

    def add_tab(self, title):
        tab = tk.Frame(self.notebook, bg=COLORS["bg"])
        self.notebook.add(tab, text=f"  {title}  ")
        return tab

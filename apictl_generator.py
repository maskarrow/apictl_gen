# ┌─────────────────────────────────────────────────────────────────────────┐
# │  apictl Command Generator                                               │
# │  Blueprint Dark theme — Palantir-inspired UI                           │
# │                                                                         │
# │  pip dependencies (standard library is all else required):             │
# │    pip install sv-ttk pywinstyles                                       │
# └─────────────────────────────────────────────────────────────────────────┘

import os
import sys
import tkinter as tk

try:
    import sv_ttk
    HAS_SV_TTK = True
except ImportError:
    HAS_SV_TTK = False

try:
    import pywinstyles
    HAS_PYWINSTYLES = True
except ImportError:
    HAS_PYWINSTYLES = False

# ── Blueprint Dark palette ─────────────────────────────────────────────────────
BG_BASE      = "#1C2127"
BG_ELEVATED  = "#252A31"
BG_CONTROL   = "#2F3640"
BORDER       = "#394048"
FG_PRIMARY   = "#F6F7F8"
FG_MUTED     = "#ABB3BF"
ACCENT_BLUE  = "#2D72D2"
ACCENT_HOVER = "#215DB0"
ACCENT_GREEN = "#238551"
MONO_FONT    = "Consolas"


def make_border_entry(parent, textvariable, width=None, readonly=False):
    """
    Returns (border_frame, entry).
    The border_frame is a 1-px coloured wrapper that acts as a focus ring.
    """
    border_frame = tk.Frame(parent, bg=BORDER, bd=0)
    inner = tk.Frame(border_frame, bg=BG_CONTROL, bd=0)
    inner.pack(padx=1, pady=1, fill="both", expand=True)

    kw = dict(
        textvariable=textvariable,
        relief="flat", bd=0,
        bg=BG_CONTROL,
        fg=FG_PRIMARY,
        insertbackground=FG_PRIMARY,
        selectbackground=ACCENT_BLUE,
        selectforeground=FG_PRIMARY,
        font=("Segoe UI", 10),
        highlightthickness=0,
    )
    if width:
        kw["width"] = width
    if readonly:
        kw["state"] = "readonly"
        kw["readonlybackground"] = BG_BASE
        kw["fg"] = FG_PRIMARY
        kw["font"] = (MONO_FONT, 11)

    entry = tk.Entry(inner, **kw)
    entry.pack(padx=6, pady=5, fill="both", expand=True)

    if not readonly:
        def on_focus_in(_):
            border_frame.config(bg=ACCENT_BLUE)
        def on_focus_out(_):
            border_frame.config(bg=BORDER)
        entry.bind("<FocusIn>",  on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    return border_frame, entry


class ApiCtlGenerator:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("apictl Command Generator")
        self.root.configure(bg=BG_BASE)
        self.root.resizable(True, False)
        self.root.minsize(560, 420)

        # ── theme base ────────────────────────────────────────────────────────
        if HAS_SV_TTK:
            sv_ttk.set_theme("dark")

        if HAS_PYWINSTYLES and sys.platform == "win32":
            pywinstyles.apply_style(root, "dark")

        # ── outer shell ───────────────────────────────────────────────────────
        outer = tk.Frame(root, bg=BG_BASE)
        outer.pack(fill="both", expand=True, padx=20, pady=20)
        outer.columnconfigure(0, weight=1)

        # ── PARAMETERS section label ──────────────────────────────────────────
        tk.Label(
            outer, text="PARAMETERS",
            bg=BG_BASE, fg=FG_MUTED,
            font=("Segoe UI", 8), anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        # ── parameter card ────────────────────────────────────────────────────
        card = tk.Frame(outer, bg=BG_ELEVATED, bd=0,
                        highlightthickness=1,
                        highlightbackground=BORDER,
                        highlightcolor=BORDER)
        card.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        card.columnconfigure(1, weight=1)

        params = [
            ("API ID",       "-n",    ""),
            ("Version",      "-v",    "1"),
            ("Revision",     "--rev", ""),
            ("Email",        "-r",    "a.visoiu@phoenixgroup.eu"),
            ("Environment",  "-e",    "cloud-dev"),
        ]

        self.vars: dict[str, tk.StringVar] = {}

        for i, (label, flag, default) in enumerate(params):
            # separator between rows
            if i > 0:
                tk.Frame(card, height=1, bg=BORDER).grid(
                    row=i * 2 - 1, column=0, columnspan=2, sticky="ew",
                )

            row_frame = tk.Frame(card, bg=BG_ELEVATED)
            row_frame.grid(row=i * 2, column=0, columnspan=2, sticky="ew",
                           padx=16, pady=(12, 12))
            row_frame.columnconfigure(1, weight=1)

            # label + flag hint stacked
            lbl_frame = tk.Frame(row_frame, bg=BG_ELEVATED, width=110)
            lbl_frame.pack_propagate(False)
            lbl_frame.grid(row=0, column=0, sticky="w", padx=(0, 14))

            tk.Label(lbl_frame, text=label, bg=BG_ELEVATED, fg=FG_MUTED,
                     font=("Segoe UI", 9), anchor="w").pack(anchor="w")
            tk.Label(lbl_frame, text=flag, bg=BG_ELEVATED,
                     fg="#5F6B7C", font=("Consolas", 8), anchor="w").pack(anchor="w")

            var = tk.StringVar(value=default)
            border_frame, _ = make_border_entry(row_frame, var)
            border_frame.grid(row=0, column=1, sticky="ew")
            self.vars[flag] = var

        # ── generate button ───────────────────────────────────────────────────
        btn_row = tk.Frame(outer, bg=BG_BASE)
        btn_row.grid(row=2, column=0, sticky="ew", pady=(0, 16))

        self._gen_btn = tk.Button(
            btn_row,
            text="⚡  Generate Command",
            command=self.generate,
            bg=ACCENT_BLUE, fg="#FFFFFF",
            activebackground=ACCENT_HOVER, activeforeground="#FFFFFF",
            relief="flat", bd=0,
            padx=24, pady=8,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
        )
        self._gen_btn.pack(side="left")
        self._gen_btn.bind("<Enter>", lambda _: self._gen_btn.config(bg=ACCENT_HOVER))
        self._gen_btn.bind("<Leave>", lambda _: self._gen_btn.config(bg=ACCENT_BLUE))

        # ── OUTPUT section label ──────────────────────────────────────────────
        tk.Label(
            outer, text="OUTPUT",
            bg=BG_BASE, fg=FG_MUTED,
            font=("Segoe UI", 8), anchor="w",
        ).grid(row=3, column=0, sticky="w", pady=(0, 6))

        # ── output text box (wrapped in border frame) ─────────────────────────
        out_border = tk.Frame(outer, bg=BORDER, bd=0,
                              highlightthickness=0)
        out_border.grid(row=4, column=0, sticky="ew", pady=(0, 10))

        out_inner = tk.Frame(out_border, bg=BG_BASE, bd=0)
        out_inner.pack(padx=1, pady=1, fill="both", expand=True)

        self._out_text = tk.Text(
            out_inner,
            height=3, wrap="word",
            bg=BG_BASE, fg=FG_PRIMARY,
            font=(MONO_FONT, 11),
            relief="flat", bd=0,
            highlightthickness=0,
            insertbackground=FG_PRIMARY,
            selectbackground=ACCENT_BLUE,
            selectforeground=FG_PRIMARY,
            state="disabled",
            cursor="arrow",
        )
        self._out_text.pack(padx=10, pady=8, fill="both", expand=True)

        # ── copy button + status ──────────────────────────────────────────────
        copy_row = tk.Frame(outer, bg=BG_BASE)
        copy_row.grid(row=5, column=0, sticky="e")

        self._status_var = tk.StringVar()
        self._status_lbl = tk.Label(
            copy_row, textvariable=self._status_var,
            bg=BG_BASE, fg=ACCENT_GREEN,
            font=("Segoe UI", 9, "bold"),
        )
        self._status_lbl.pack(side="left", padx=(0, 12))

        self._copy_btn = tk.Button(
            copy_row,
            text="⎘  Copy to Clipboard",
            command=self.copy,
            bg=BG_CONTROL, fg=FG_PRIMARY,
            activebackground=BORDER, activeforeground=FG_PRIMARY,
            relief="flat", bd=0,
            padx=16, pady=6,
            cursor="hand2",
            font=("Segoe UI", 9),
        )
        self._copy_btn.pack(side="left")
        self._copy_btn.bind("<Enter>", lambda _: self._copy_btn.config(bg=BORDER))
        self._copy_btn.bind("<Leave>", lambda _: self._copy_btn.config(bg=BG_CONTROL))

        # ── hint footer ───────────────────────────────────────────────────────
        tk.Label(
            outer, text="-k flag is always appended automatically",
            bg=BG_BASE, fg="#5F6B7C",
            font=("Segoe UI", 8), anchor="w",
        ).grid(row=6, column=0, sticky="w", pady=(10, 0))

        self.root.after(100, self._fit_window)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _fit_window(self):
        self.root.update_idletasks()
        w = max(self.root.winfo_reqwidth(), 560)
        h = max(self.root.winfo_reqheight(), 420)
        self.root.minsize(w, h)

    def generate(self):
        n   = self.vars["-n"].get().strip()
        v   = self.vars["-v"].get().strip()
        rev = self.vars["--rev"].get().strip()
        r   = self.vars["-r"].get().strip()
        e   = self.vars["-e"].get().strip()
        cmd = f"apictl export api -n {n} -v v{v} --rev {rev} -r {r} -e {e} -k"

        self._out_text.config(state="normal")
        self._out_text.delete("1.0", "end")
        self._out_text.insert("1.0", cmd)
        self._out_text.config(state="disabled")
        self._status_var.set("")

    def copy(self):
        cmd = self._out_text.get("1.0", "end").strip()
        if not cmd:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(cmd)
        self._status_var.set("✔  Copied!")
        self.root.after(2000, lambda: self._status_var.set(""))


def _resource(filename):
    """Resolve path whether running as script or PyInstaller bundle."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


if __name__ == "__main__":
    root = tk.Tk()
    _ico = _resource("letter-a.ico")
    if os.path.exists(_ico):
        root.iconbitmap(_ico)          # .ico → title bar + taskbar on Windows
    app = ApiCtlGenerator(root)
    root.mainloop()

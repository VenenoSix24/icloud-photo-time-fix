# -*- coding: utf-8 -*-
"""System folder picker with manual-input fallback."""
import os
from .i18n import t
from .console import ok, warn, err, ask
def pick_folder(prompt_text):
    """System folder picker; returns None on cancel / unsupported."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askdirectory(title=prompt_text, parent=root)
        root.destroy()
        return os.path.normpath(path) if path else None
    except Exception as e:
        warn(t("pick_fallback", e=e))
        return None
def choose_folder_with_fallback(prompt_text):
    while True:
        picked = pick_folder(prompt_text)
        if picked:
            ok(f"{picked}")
            return picked
        warn(t("pick_cancel"))
        manual = ask(t("pick_retry", p=t("pick_manual")), default="")
        if manual and os.path.isdir(manual):
            return os.path.normpath(manual)
        if manual:
            err(t("bad_dir"))

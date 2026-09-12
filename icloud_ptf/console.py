# -*- coding: utf-8 -*-
"""Terminal UI helpers."""
import os

from .i18n import t

# ---------------------------------------------------------------- console UI
os.system("")  # enable ANSI escapes on Windows

class C:
    RESET = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
    RED = "\033[91m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
    BLUE = "\033[94m"; MAGENTA = "\033[95m"; CYAN = "\033[96m"

def banner():
    print(f"{C.CYAN}{C.BOLD}\n  ╔══════════════════════════════════════════════════════════╗")
    print(f"  ║        {t('banner').ljust(54)}║")
    print(f"  ╚══════════════════════════════════════════════════════════╝{C.RESET}")

def title(text):
    print(f"\n{C.BOLD}{C.BLUE}── {text} {C.RESET}" + "─" * max(0, 58 - len(text) * 2))

def ok(msg):    print(f"  {C.GREEN}✓{C.RESET} {msg}")
def warn(msg):  print(f"  {C.YELLOW}⚠{C.RESET} {msg}")
def err(msg):   print(f"  {C.RED}✗{C.RESET} {msg}")
def info(msg):  print(f"  {C.CYAN}ℹ{C.RESET} {msg}")

def ask(prompt, default=None):
    suffix = f" {C.DIM}[Enter = {default}]{C.RESET}" if default else ""
    while True:
        v = input(f"  {C.MAGENTA}?{C.RESET} {prompt}{suffix}: ").strip()
        if v:
            return v
        if default is not None:
            return default
        warn(t("empty_input"))


def pause():
    """Wait for Enter; tolerate closed stdin (e.g. double-click launches)."""
    try:
        input("\n" + t("press_enter"))
    except EOFError:
        pass

# -*- coding: utf-8 -*-
"""Terminal UI helpers."""
import os
import unicodedata

from .i18n import t

os.system("")


class C:
    RESET = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
    RED = "\033[91m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
    BLUE = "\033[94m"; MAGENTA = "\033[95m"; CYAN = "\033[96m"


def _width(s):
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in s)


def banner():
    lines = [t("banner"), "By VenenoSix24  ·  https://github.com/VenenoSix24"]
    inner = max(56, max(_width(x) for x in lines) + 10)
    bar = "═" * inner
    print(f"{C.CYAN}{C.BOLD}\n  ╔{bar}╗")
    for text in lines:
        total = inner - _width(text)
        left = max(4, (total - 2) // 2 + 1)
        pad = " " * max(2, total - left)
        print(f"  ║{' ' * left}{text}{pad}║")
    print(f"  ╚{bar}╝{C.RESET}")


def title(text):
    print(f"\n{C.BOLD}{C.BLUE}── {text} {C.RESET}" + "─" * max(0, 58 - _width(text) * 2))


def ok(msg):    print(f"  {C.GREEN}✓ {C.RESET}{msg}")
def warn(msg):  print(f"  {C.YELLOW}⚠ {C.RESET}{msg}")
def err(msg):   print(f"  {C.RED}✗ {C.RESET}{msg}")
def info(msg):  print(f"  {C.CYAN}ℹ {C.RESET}{msg}")


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
    try:
        input("\n" + t("press_enter"))
    except EOFError:
        pass

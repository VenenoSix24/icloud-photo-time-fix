# -*- coding: utf-8 -*-
"""Base directory (works both as script and frozen exe)."""
import os, sys
def base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

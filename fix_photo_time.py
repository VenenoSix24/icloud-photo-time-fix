# -*- coding: utf-8 -*-
"""
iCloud Photo Time Fixer / iCloud 照片时间修正工具 — entry point.

Usage:
  python fix_photo_time.py            interactive fix flow (Chinese)
  python fix_photo_time.py en         interactive fix flow (English)
  python fix_photo_time.py --merge    merge csv/ only, then exit
"""
import sys

from icloud_ptf.app import main, merge_only
from icloud_ptf.i18n import t
from icloud_ptf.console import C

if __name__ == "__main__":
    try:
        if "--merge" in sys.argv:
            merge_only()
        else:
            main()
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}{t('interrupted')}{C.RESET}")

# -*- coding: utf-8 -*-
"""ExifTool location and batch writing."""
import csv, os, subprocess, sys, tempfile
from .i18n import t
from .console import title, ok, err, info, ask, C
from .paths import base_dir
from .timeutil import TZ_SUFFIX
def choose_exiftool():
    title(t("exiftool_title"))
    default_exe = os.path.join(base_dir(), "exiftool",
                               "exiftool.exe" if sys.platform == "win32" else "exiftool")
    if os.path.isfile(default_exe):
        ok(t("exiftool_found", p=default_exe))
        ans = input(f"  {C.MAGENTA}?{C.RESET} {t('use_default')} ").strip().lower()
        if ans in ("", "y"):
            return default_exe
    err(t("exiftool_missing", p=default_exe))
    info(t("exiftool_site"))
    info(t("exiftool_win") if sys.platform == "win32" else t("exiftool_unix"))
    info(t("exiftool_unix") if sys.platform == "win32" else t("exiftool_win"))
    while True:
        raw = ask(t("exiftool_path"), default="")
        exe = raw or default_exe
        if os.path.isfile(exe):
            ok(t("exiftool_ok", p=exe))
            return exe
        err(t("exiftool_bad"))
def run_exiftool_batch(exe, jobs):
    """jobs: list of (dst_path, time_str). Writes times via exiftool's CSV
    import (one invocation per chunk, per-file values). Returns dict
    dst_path -> (status_bool, msg)."""
    results = {}
    CHUNK = 500
    supports_birthtime = sys.platform in ("win32", "darwin")
    for start in range(0, len(jobs), CHUNK):
        chunk = jobs[start:start + CHUNK]
        print(f"\r{t('chunk_done', done=min(start + len(chunk), len(jobs)), total=len(jobs))}"
              + " " * 8, end="", flush=True)
        fd, csv_path = tempfile.mkstemp(suffix=".csv")
        fd2, args_path = tempfile.mkstemp(suffix=".args")
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
                cols = ["SourceFile", "DateTimeOriginal", "CreateDate",
                        "ModifyDate", "FileModifyDate"]
                if supports_birthtime:
                    cols.append("FileCreateDate")
                w = csv.writer(f)
                w.writerow(cols)
                for dst, ts in chunk:
                    row = [dst, ts, ts, ts, f"{ts}{TZ_SUFFIX}"]
                    if supports_birthtime:
                        row.append(f"{ts}{TZ_SUFFIX}")
                    w.writerow(row)
            with os.fdopen(fd2, "w", encoding="utf-8", newline="\n") as f:
                f.write("-charset\nfilename=UTF8\n")
                f.write(f"-csv={csv_path}\n-overwrite_original\n-q\n")
                for dst, _ in chunk:
                    f.write(dst + "\n")
            r = subprocess.run([exe, "-@", args_path], capture_output=True)
        finally:
            os.unlink(csv_path)
            os.unlink(args_path)
        if r.returncode == 0:
            for dst, _ in chunk:
                results[dst] = (True, "")
        else:
            out = r.stderr.decode(errors="replace") + r.stdout.decode(errors="replace")
            for dst, _ in chunk:
                failed = os.path.basename(dst) in out
                results[dst] = (False, t("err_chunk")) if failed else (True, "")
    return results

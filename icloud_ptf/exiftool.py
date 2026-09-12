# -*- coding: utf-8 -*-
"""ExifTool location and batch writing."""
import csv, json, os, re, shutil, subprocess, sys, tempfile
from .i18n import t
from .console import title, ok, err, info, ask, C
from .paths import base_dir
from .timeutil import TZ_SUFFIX
def choose_exiftool():
    title(t("exiftool_title"))
    local_exe = os.path.join(base_dir(), "exiftool",
                             "exiftool.exe" if sys.platform == "win32" else "exiftool")
    path_exe = shutil.which("exiftool")
    if path_exe:
        ok(t("exiftool_ok", p=path_exe))
        return path_exe
    if os.path.isfile(local_exe):
        ok(t("exiftool_found", p=local_exe))
        ans = input(f"  {C.MAGENTA}?{C.RESET} {t('use_default')} ").strip().lower()
        if ans in ("", "y"):
            return local_exe
    err(t("exiftool_missing", p=local_exe))
    info(t("exiftool_site"))
    info(t("exiftool_win") if sys.platform == "win32" else t("exiftool_unix"))
    info(t("exiftool_unix") if sys.platform == "win32" else t("exiftool_win"))
    while True:
        raw = ask(t("exiftool_path"), default="")
        exe = raw or local_exe
        if os.path.isfile(exe):
            ok(t("exiftool_ok", p=exe))
            return exe
        err(t("exiftool_bad"))

REAL_EXT = {"JPEG": "jpg", "PNG": "png", "HEIC": "heic", "MOV": "mov",
            "MP4": "mp4", "M4V": "m4v", "AVI": "avi", "QT": "mov"}
ERR_RE = re.compile(r'^["\']?(Error|Warning):\s*(.*?\S)\s+-\s+(.+?)\s*[\'"]?\r?$', re.M)
def probe_types(exe, paths):
    """One exiftool JSON pass: real file type per path (unreadable files omitted)."""
    fd, args_path = tempfile.mkstemp(suffix=".args")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write("-charset\nfilename=UTF8\n-j\n-FileType\n")
        for p in paths:
            f.write(p + "\n")
    r = subprocess.run([exe, "-@", args_path], capture_output=True)
    os.unlink(args_path)
    try:
        return {os.path.normcase(it["SourceFile"].replace("\\", "/")): it.get("FileType", "")
                for it in json.loads(r.stdout.decode("utf-8", errors="replace"))}
    except ValueError:
        return {}
def run_exiftool_batch(exe, jobs):
    """jobs: list of (dst_path, time_str). Writes times via exiftool's CSV
    import (one invocation per chunk, per-file values). Files whose content
    does not match their extension are temporarily renamed to the real
    extension for the write, then renamed back. Returns dict
    dst_path -> (status_bool, msg)."""
    results = {}
    CHUNK = 500
    supports_birthtime = sys.platform in ("win32", "darwin")

    def run_write(pairs, extra=()):
        """One exiftool CSV-import invocation; extra args (e.g. -m) are
        inserted before the CSV import. Returns (rc, error_map)."""
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
                for p, ts in pairs:
                    row = [p, ts, ts, ts, f"{ts}{TZ_SUFFIX}"]
                    if supports_birthtime:
                        row.append(f"{ts}{TZ_SUFFIX}")
                    w.writerow(row)
            with os.fdopen(fd2, "w", encoding="utf-8", newline="\n") as f:
                f.write("-charset\nfilename=UTF8\n")
                for e in extra:
                    f.write(e + "\n")
                f.write(f"-csv={csv_path}\n-overwrite_original\n-q\n")
                for p, _ in pairs:
                    f.write(p + "\n")
            r = subprocess.run([exe, "-@", args_path], capture_output=True)
        finally:
            os.unlink(csv_path)
            os.unlink(args_path)
        out = (r.stderr.decode(errors="replace")
               + r.stdout.decode(errors="replace"))
        errors = {}
        for kind, msg, path in ERR_RE.findall(out):
            if kind != "Error":
                continue
            errors[os.path.normcase(path.strip().strip("'\"").replace("\\", "/"))] = msg.strip()
        return r.returncode, errors

    for start in range(0, len(jobs), CHUNK):
        chunk = jobs[start:start + CHUNK]
        print(f"\r{t('chunk_done', done=min(start + len(chunk), len(jobs)), total=len(jobs))}"
              + " " * 8, end="", flush=True)
        types = probe_types(exe, [dst for dst, _ in chunk])
        alias, renames, write_jobs = {}, [], []
        for dst, ts in chunk:
            p = dst
            real = REAL_EXT.get(types.get(os.path.normcase(dst.replace("\\", "/")), ""))
            if real and os.path.splitext(dst)[1].lstrip(".").lower() != real:
                tmp = os.path.splitext(dst)[0] + "." + real
                n = 1
                while os.path.exists(tmp):
                    tmp = f"{os.path.splitext(dst)[0]}_{n}.{real}"
                    n += 1
                try:
                    os.rename(dst, tmp)
                    renames.append((tmp, dst))
                    p = tmp
                    alias[os.path.normcase(tmp.replace("\\", "/"))] = dst
                except OSError:
                    pass
            write_jobs.append((p, ts, dst))

        def restore():
            for tmp, dst in renames:
                if os.path.exists(tmp):
                    try:
                        os.rename(tmp, dst)
                    except OSError:
                        results[dst] = (False, t("err_rename"))
        rc, errors = run_write([(p, ts) for p, ts, _ in write_jobs])
        restore()
        failed = []
        for p, ts, dst in write_jobs:
            msg = errors.get(os.path.normcase(p.replace("\\", "/")))
            if msg is None:
                results[dst] = (True, t("ext_mismatch") if dst in alias.values() else "")
            elif rc == 0:
                results[dst] = (True, t("ext_mismatch") if dst in alias.values() else "")
            else:
                results[dst] = (False, msg)
                failed.append((dst, ts, msg))
        if not failed:
            continue
        renames2, retry = [], []
        for dst, ts, msg in failed:
            tmp = alias_rev = None
            for k, v in alias.items():
                if v == dst:
                    alias_rev = k.rsplit("/", 1)[-1]
            tmp = alias_rev or dst
            p = dst
            if alias_rev:
                tmp_full = os.path.join(os.path.dirname(dst), os.path.basename(alias_rev))
                n = 1
                while os.path.exists(tmp_full):
                    stem, ext = os.path.splitext(tmp_full)
                    tmp_full = f"{stem}_{n}{ext}"
                    n += 1
                try:
                    os.rename(dst, tmp_full)
                    renames2.append((tmp_full, dst))
                    p = tmp_full
                except OSError:
                    pass
            retry.append((p, ts, dst))
        if retry:
            rc2, errors2 = run_write([(p, ts) for p, ts, _ in retry], extra=["-m"])
            for tmp, dst in renames2:
                if os.path.exists(tmp):
                    try:
                        os.rename(tmp, dst)
                    except OSError:
                        results[dst] = (False, t("err_rename"))
                        continue
            for p, ts, dst in retry:
                msg = errors2.get(os.path.normcase(p.replace("\\", "/")))
                if msg is None or rc2 == 0:
                    results[dst] = (True, t("ext_mismatch") if dst in alias.values() else "")
                else:
                    results[dst] = (False, msg)
    return results

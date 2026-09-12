# -*- coding: utf-8 -*-
"""
iCloud Photo Time Fixer / iCloud 照片时间修正工具

Rewrites photo/video capture times from iCloud "Photo Details" CSV exports
using ExifTool, in batch and recursively.

Language / 语言: set PTF_LANG=en or zh, or pass "en" / "zh" as first argument.
"""
import csv
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------- language
LANG = os.environ.get("PTF_LANG", "zh")
if len(sys.argv) > 1 and sys.argv[1].lower() in ("en", "zh"):
    LANG = sys.argv[1].lower()

S = {
"zh": {
 "banner": "iCloud 照片时间修正工具  ·  Photo Time Fixer",
 "step": "第 {n} 步 · {what}",
 "merged_found": "已找到汇总文件: merged_photo_details.csv",
 "remerge_q": "是否重新合并一次 (csv/ 目录下有新文件时建议重新合并) [y/N]",
 "no_merged": "尚未生成汇总文件。merge_csv.py 会把 csv/ 目录下的全部 Photo Details*.csv\n  合并成 merged_photo_details.csv (自动去重)。手动合并: python merge_csv.py",
 "no_csv_dir": "未找到 merged_photo_details.csv，也没有 csv/ 目录: {d}",
 "merging": "正在合并 CSV ...",
 "merge_ok": "合并完成",
 "merge_fail": "合并失败，请检查上方输出",
 "no_merge_script": "未找到合并脚本: {p}",
 "loading": "载入时间数据 ...",
 "loaded": "共载入 {n} 条记录",
 "pick_input": "选择照片所在的文件夹",
 "pick_input_hint": "即将弹出文件夹选择窗口，请选择照片所在的文件夹 ...",
 "pick_output": "选择照片输出文件夹",
 "pick_manual": "请输入目录的完整路径",
 "pick_fallback": "无法打开文件夹选择窗口 ({e})，将改为手动输入路径",
 "pick_cancel": "未选择任何文件夹 (或窗口被关闭)",
 "pick_retry": "{p} (也可直接回车重试窗口选择)",
 "bad_dir": "该目录不存在，请重试",
 "empty_dir": "该文件夹是空的",
 "out_menu": "       1. 同级目录: 输入目录名 + \"_fixed\" (自动新建)\n       2. 自定义: 选择一个已有文件夹, 结果直接输出到那里",
 "out_q": "请选择",
 "out_same": "输出目录不能与输入目录相同，请重新选择",
 "out_inside": "输出目录不能在输入目录内部，请重新选择",
 "exiftool_title": "指定 ExifTool",
 "exiftool_found": "检测到默认 ExifTool: {p}",
 "use_default": "是否使用它? [Y/n]",
 "exiftool_missing": "未在 {p} 中检测到 exiftool 可执行文件",
 "exiftool_site": "请前往官网下载对应系统的可执行文件: https://exiftool.org/",
 "exiftool_win": "  · Windows: 下载 Windows Executable, 解压到脚本同级的 exiftool 文件夹",
 "exiftool_unix": "  · macOS / Linux: brew install exiftool, 或按官网说明安装",
 "exiftool_path": "请输入 exiftool 程序的完整路径 (回车重新检测默认位置)",
 "exiftool_bad": "该路径不存在或不是文件，请重新输入",
 "exiftool_ok": "ExifTool 可用: {p}",
 "tz_list": "选择时区",
 "tz_q": "请输入序号",
 "tz_bad": "请输入数字序号",
 "tz_range": "序号超出范围",
 "tz_ok": "已选择: {n}",
 "scan": "扫描照片",
 "scan_result": "成功匹配 {m} 个文件, 未匹配 {u} 个",
 "scan_example": "示例: {f}  →  {t}",
 "scan_unmatched": "未在 CSV 中找到: {f}",
 "scan_unmatched_more": "… 以及另外 {n} 个未匹配文件",
 "no_jobs": "没有可处理的文件，退出",
 "confirm_title": "确认执行",
 "confirm_body": "将把 {n} 个文件的拍摄时间写入 EXIF/QuickTime 标签\n  (DateTimeOriginal / CreateDate / ModifyDate) 以及文件的创建/修改时间。原文件不动。",
 "confirm_out": "输出目录: {d}",
 "confirm_q": "确认执行? [Y/n]",
 "cancelled": "已取消",
 "running": "执行中",
 "chunk_done": "  [进度 {done}/{total}]",
 "done_title": "完成",
 "done_ok": "成功修正 {d}/{t} 个文件 → {o}",
 "done_unmatched": "未匹配 {n} 个文件 (未做任何修改)",
 "done_failed": "失败 {n} 个, 详见报告",
 "report_path": "修正报告: {f}",
 "report_note": "报告记录了每个文件的处理状态、写入的时间及失败原因。",
 "press_enter": "按回车键退出 ...",
 "empty_input": "输入不能为空，请重新输入",
 "interrupted": "已中断",
 "report_name": "修正报告_{ts}.csv",
 "report_header": ["文件名", "状态", "写入的拍摄时间", "CSV原始记录(GMT)", "备注/错误"],
 "st_ok": "成功", "st_fail": "失败", "st_unmatched": "未匹配",
 "err_no_csv_record": "在 CSV 中没有找到对应记录",
 "err_parse": "时间解析失败",
 "err_unknown": "未知错误",
 "err_chunk": "本批次中以下文件可能失败, 请用 exiftool 抽查",
},
"en": {
 "banner": "iCloud Photo Time Fixer",
 "step": "Step {n} · {what}",
 "merged_found": "Found merged file: merged_photo_details.csv",
 "remerge_q": "Re-merge CSVs now? (recommended if csv/ has new files) [y/N]",
 "no_merged": "No merged file yet. merge_csv.py combines all Photo Details*.csv in csv/\n  into merged_photo_details.csv (deduplicated). Manual: python merge_csv.py",
 "no_csv_dir": "Neither merged_photo_details.csv nor csv/ directory found: {d}",
 "merging": "Merging CSVs ...",
 "merge_ok": "Merge complete",
 "merge_fail": "Merge failed, see output above",
 "no_merge_script": "Merge script not found: {p}",
 "loading": "Loading time records ...",
 "loaded": "Loaded {n} records",
 "pick_input": "Select the folder containing your photos",
 "pick_input_hint": "A folder picker will open — select the folder containing your photos ...",
 "pick_output": "Select the output folder",
 "pick_manual": "Enter the full directory path",
 "pick_fallback": "Cannot open folder picker ({e}); falling back to manual input",
 "pick_cancel": "No folder selected (or the dialog was closed)",
 "pick_retry": "{p} (press Enter to retry the picker)",
 "bad_dir": "Directory does not exist, try again",
 "empty_dir": "This folder is empty",
 "out_menu": "       1. Sibling folder: input folder name + \"_fixed\" (auto-created)\n       2. Custom: pick an existing folder, results go there directly",
 "out_q": "Choose",
 "out_same": "Output folder cannot equal the input folder, choose again",
 "out_inside": "Output folder cannot be inside the input folder, choose again",
 "exiftool_title": "Locate ExifTool",
 "exiftool_found": "Found default ExifTool: {p}",
 "use_default": "Use it? [Y/n]",
 "exiftool_missing": "No exiftool executable found at {p}",
 "exiftool_site": "Please download the executable for your system from: https://exiftool.org/",
 "exiftool_win": "  · Windows: download the Windows Executable and extract it into the 'exiftool' folder next to this script",
 "exiftool_unix": "  · macOS / Linux: brew install exiftool, or follow the official site",
 "exiftool_path": "Enter the full path to the exiftool executable (Enter = re-check default)",
 "exiftool_bad": "Path does not exist or is not a file, try again",
 "exiftool_ok": "ExifTool available: {p}",
 "tz_list": "Select timezone",
 "tz_q": "Enter number",
 "tz_bad": "Please enter a number",
 "tz_range": "Number out of range",
 "tz_ok": "Selected: {n}",
 "scan": "Scanning photos",
 "scan_result": "Matched {m} files, unmatched {u}",
 "scan_example": "Example: {f}  →  {t}",
 "scan_unmatched": "Not found in CSV: {f}",
 "scan_unmatched_more": "… and {n} more unmatched files",
 "no_jobs": "Nothing to process, exiting",
 "confirm_title": "Confirm",
 "confirm_body": "Will write capture time into {n} files' EXIF/QuickTime tags\n  (DateTimeOriginal / CreateDate / ModifyDate) and file timestamps. Originals untouched.",
 "confirm_out": "Output folder: {d}",
 "confirm_q": "Proceed? [Y/n]",
 "cancelled": "Cancelled",
 "running": "Running",
 "chunk_done": "  [progress {done}/{total}]",
 "done_title": "Done",
 "done_ok": "Fixed {d}/{t} files → {o}",
 "done_unmatched": "{n} unmatched files (left untouched)",
 "done_failed": "{n} failed, see report",
 "report_path": "Report: {f}",
 "report_note": "The report records per-file status, written time and failure reasons.",
 "press_enter": "Press Enter to exit ...",
 "empty_input": "Input cannot be empty, try again",
 "interrupted": "Interrupted",
 "report_name": "fix_report_{ts}.csv",
 "report_header": ["File", "Status", "Written capture time", "CSV record (GMT)", "Note/Error"],
 "st_ok": "OK", "st_fail": "FAILED", "st_unmatched": "UNMATCHED",
 "err_no_csv_record": "No matching record found in CSV",
 "err_parse": "Failed to parse time",
 "err_unknown": "Unknown error",
 "err_chunk": "Some files in this batch may have failed; spot-check with exiftool",
},
}

def t(key, **kw):
    return S[LANG][key].format(**kw) if kw else S[LANG][key]

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

# ---------------------------------------------------------------- folder picker
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

# ---------------------------------------------------------------- CSV merge
def merge_csv_files(base, csv_dir, merged_path):
    """Merge all Photo Details*.csv in csv_dir into merged_path (dedup)."""
    import glob
    fields = ["imgName", "fileChecksum", "favorite", "hidden", "deleted",
              "originalCreationDate", "viewCount", "importDate"]
    seen, rows = set(), []
    for path in sorted(glob.glob(os.path.join(csv_dir, "*.csv"))):
        with open(path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if [h.strip() for h in reader.fieldnames or []] != fields:
                continue
            for row in reader:
                row = {k: (row.get(k) or "").strip() for k in fields}
                key = (row["imgName"], row["fileChecksum"], row["originalCreationDate"])
                if key in seen:
                    continue
                seen.add(key)
                rows.append(row)
    with open(merged_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return len(rows)

def ensure_merged_csv():
    base = base_dir()
    merged = os.path.join(base, "merged_photo_details.csv")
    csv_dir = os.path.join(base, "csv")

    title(t("step", n=1, what="CSV"))
    if os.path.isfile(merged):
        ok(t("merged_found"))
        ans = input(f"  {C.MAGENTA}?{C.RESET} {t('remerge_q')}: ").strip().lower()
        if ans != "y":
            return merged
    elif os.path.isdir(csv_dir):
        info(t("no_merged"))
    else:
        err(t("no_csv_dir", d=csv_dir))
        return None

    info(t("merging"))
    try:
        n = merge_csv_files(base, csv_dir, merged)
        ok(f"{t('merge_ok')} ({n})")
        return merged
    except Exception as e:
        err(f"{t('merge_fail')}: {e}")
        return None

# ---------------------------------------------------------------- time parsing
WEEKDAY_RE = re.compile(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+")

def parse_gmt(text, tz):
    """'Tuesday June 2,2026 2:36 AM GMT' -> 'YYYY:MM:DD HH:MM:SS' in target tz."""
    text = WEEKDAY_RE.sub("", text.strip().replace(" GMT", "").strip())
    dt = datetime.strptime(text, "%B %d,%Y %I:%M %p").replace(tzinfo=timezone.utc)
    return dt.astimezone(tz).strftime("%Y:%m:%d %H:%M:%S")

TZ_NAMES_ZH = ["东12区  (GMT+12)", "东11区  (GMT+11)", "东10区  (GMT+10)",
"东9区   (GMT+9)", "东8区   (GMT+8, 北京时间)", "东7区   (GMT+7)", "东6区   (GMT+6)",
"东5区   (GMT+5)", "东4区   (GMT+4)", "东3区   (GMT+3)", "东2区   (GMT+2)",
"东1区   (GMT+1)", "0时区   (GMT)", "西1区   (GMT-1)", "西2区   (GMT-2)",
"西3区   (GMT-3)", "西4区   (GMT-4)", "西5区   (GMT-5)", "西6区   (GMT-6)",
"西7区   (GMT-7)", "西8区   (GMT-8)", "西9区   (GMT-9)", "西10区  (GMT-10)",
"西11区  (GMT-11)", "西12区  (GMT-12)"]
TZ_NAMES_EN = ["UTC+12", "UTC+11", "UTC+10", "UTC+9", "UTC+8 (Beijing)", "UTC+7",
"UTC+6", "UTC+5", "UTC+4", "UTC+3", "UTC+2", "UTC+1", "UTC+0 (GMT)", "UTC-1",
"UTC-2", "UTC-3", "UTC-4", "UTC-5", "UTC-6", "UTC-7", "UTC-8", "UTC-9", "UTC-10",
"UTC-11", "UTC-12"]
TZ_HOURS = [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5, -6,
-7, -8, -9, -10, -11, -12]
TZ_SUFFIX = datetime.now().astimezone().strftime("%z")

def choose_timezone():
    title(f"{t('tz_list')}")
    names = TZ_NAMES_ZH if LANG == "zh" else TZ_NAMES_EN
    for i, name in enumerate(names, 1):
        print(f"      {i:>2}. {name}")
    default_idx = 5  # UTC+8 Beijing
    while True:
        raw = input(f"  {C.MAGENTA}?{C.RESET} {t('tz_q')} "
                    f"{C.DIM}[Enter = {default_idx}. {names[default_idx-1]}]{C.RESET}: ").strip()
        idx = default_idx if not raw else None
        if idx is None:
            try:
                idx = int(raw)
            except ValueError:
                warn(t("tz_bad")); continue
        if 1 <= idx <= len(names):
            ok(t("tz_ok", n=names[idx - 1]))
            return timezone(timedelta(hours=TZ_HOURS[idx - 1]))
        warn(t("tz_range"))

# ---------------------------------------------------------------- exiftool
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

# ---------------------------------------------------------------- misc
def base_dir():
    if getattr(sys, "frozen", False):  # PyInstaller bundle
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def load_records(merged_csv):
    records = {}
    with open(merged_csv, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            name = row["imgName"].strip().lower()
            rec = {"orig": row["originalCreationDate"].strip()}
            records[name] = rec                                     # full name
            records.setdefault(os.path.splitext(name)[0], rec)      # stem fallback
    return records

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

# ---------------------------------------------------------------- main
def main():
    banner()

    merged_csv = ensure_merged_csv()
    if not merged_csv:
        input(f"\n{t('press_enter')}")
        return
    info(t("loading"))
    records = load_records(merged_csv)
    ok(t("loaded", n=len(records)))

    # input dir
    title(t("step", n=2, what=t("pick_input")))
    info(t("pick_input_hint"))
    in_dir = choose_folder_with_fallback(t("pick_input"))
    if not os.listdir(in_dir):
        warn(t("empty_dir"))

    # output dir
    title(t("step", n=3, what=t("pick_output")))
    print(t("out_menu"))
    while True:
        c = input(f"  {C.MAGENTA}?{C.RESET} {t('out_q')} {C.DIM}[Enter = 1]{C.RESET}: ").strip()
        if c in ("", "1"):
            out_dir = in_dir.rstrip("\\/") + "_fixed"
            os.makedirs(out_dir, exist_ok=True)
            break
        if c == "2":
            info(t("pick_input_hint").replace(t("pick_input"), t("pick_output")))
            out_dir = choose_folder_with_fallback(t("pick_output"))
            if os.path.normpath(out_dir) == os.path.normpath(in_dir):
                err(t("out_same")); continue
            if os.path.normpath(out_dir).startswith(os.path.normpath(in_dir) + os.sep):
                err(t("out_inside")); continue
            break
        continue
    ok(f"{out_dir}")

    exe = choose_exiftool()
    tz = choose_timezone()

    # recursive scan
    title(t("scan"))
    jobs, unmatched = [], []
    out_norm = os.path.normpath(out_dir)
    for root, dirs, files in os.walk(in_dir):
        # never descend into the output folder if it lives under the input
        if os.path.normpath(root) == os.path.normpath(in_dir):
            dirs[:] = [d for d in dirs
                       if os.path.normpath(os.path.join(root, d)) != out_norm]
        for name in sorted(files):
            if name.startswith(("修正报告_", "fix_report_")):
                continue
            src = os.path.join(root, name)
            rel = os.path.relpath(src, in_dir)
            rec = records.get(name.lower()) or records.get(os.path.splitext(name.lower())[0])
            if rec is None or not rec["orig"]:
                unmatched.append(rel)
                continue
            try:
                ts = parse_gmt(rec["orig"], tz)
            except ValueError as e:
                warn(f"{t('err_parse')} {rel}: {e}")
                unmatched.append(rel)
                continue
            dst = os.path.join(out_dir, rel)
            jobs.append((src, dst, ts, rec["orig"]))

    ok(t("scan_result", m=len(jobs), u=len(unmatched)))
    if jobs:
        ok(t("scan_example", f=jobs[0][0], t=jobs[0][2]))
    for u in unmatched[:10]:
        warn(t("scan_unmatched", f=u))
    if len(unmatched) > 10:
        warn(t("scan_unmatched_more", n=len(unmatched) - 10))
    if not jobs:
        err(t("no_jobs"))
        input(f"\n{t('press_enter')}")
        return

    # confirm
    title(t("confirm_title"))
    print(f"  {t('confirm_body', n=len(jobs))}")
    print(f"  {t('confirm_out', d=out_dir)}")
    if input(f"  {C.MAGENTA}?{C.RESET} {t('confirm_q')} ").strip().lower() == "n":
        info(t("cancelled"))
        input(f"\n{t('press_enter')}")
        return

    # execute: copy all, then batch exiftool
    title(t("running"))
    for src, dst, _, _ in jobs:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    results = run_exiftool_batch(exe, [(dst, ts) for _, dst, ts, _ in jobs])

    # report
    report_path = os.path.join(out_dir, t("report_name", ts=f"{datetime.now():%Y%m%d_%H%M%S}"))
    with open(report_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(t("report_header"))
        for src, dst, ts, orig in jobs:
            good, msg = results.get(dst, (False, t("err_unknown")))
            w.writerow([os.path.relpath(src, in_dir),
                        t("st_ok") if good else t("st_fail"),
                        ts if good else "", orig, msg])
        for u in unmatched:
            w.writerow([u, t("st_unmatched"), "", "", t("err_no_csv_record")])

    done = sum(1 for g, _ in results.values() if g)
    failed = len(results) - done
    title(t("done_title"))
    ok(t("done_ok", d=done, t=len(jobs), o=out_dir))
    if unmatched:
        warn(t("done_unmatched", n=len(unmatched)))
    if failed:
        err(t("done_failed", n=failed))
    ok(t("report_path", f=os.path.basename(report_path)))
    info(t("report_note"))

    input(f"\n{t('press_enter')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}{t('interrupted')}{C.RESET}")

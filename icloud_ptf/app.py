# -*- coding: utf-8 -*-
"""Main application flow."""
import csv, os, shutil
from datetime import datetime, timedelta, timezone
from .i18n import t, LANG
from .console import banner, title, ok, warn, err, info, ask, pause, C
from .picker import choose_folder_with_fallback
from .merge import merge_csv_files
from .paths import base_dir
from .timeutil import parse_gmt, TZ_NAMES_ZH, TZ_NAMES_EN, TZ_HOURS
from .exiftool import choose_exiftool, run_exiftool_batch
def load_records(merged_csv):
    records = {}
    with open(merged_csv, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            name = row["imgName"].strip().lower()
            rec = {"orig": row["originalCreationDate"].strip()}
            records[name] = rec
            records.setdefault(os.path.splitext(name)[0], rec)
    return records
def ensure_merged_csv(force_merge=False):
    base = base_dir()
    merged = os.path.join(base, "merged_photo_details.csv")
    csv_dir = os.path.join(base, "csv")
    title(t("step", n=2, what="CSV"))
    if os.path.isfile(merged) and not force_merge:
        ok(t("merged_found"))
        ans = input(f"  {C.MAGENTA}?{C.RESET} {t('remerge_q')}: ").strip().lower()
        if ans != "y":
            return merged
    elif not os.path.isdir(csv_dir) and not os.path.isfile(merged):
        err(t("no_csv_dir", d=csv_dir))
        return None
    elif not force_merge and not os.path.isfile(merged):
        info(t("no_merged"))
    info(t("merging"))
    try:
        n = merge_csv_files(base, csv_dir, merged)
        ok(f"{t('merge_ok')} ({n})")
        return merged
    except Exception as e:
        err(f"{t('merge_fail')}: {e}")
        return None
def merge_only():
    """--merge: merge csv/ into merged_photo_details.csv and exit."""
    banner()
    ensure_merged_csv(force_merge=True)
    pause()
def choose_timezone():
    title(t("tz_list"))
    names = TZ_NAMES_ZH if LANG == "zh" else TZ_NAMES_EN
    for i, name in enumerate(names, 1):
        print(f"      {i:>2}. {name}")
    default_idx = 5
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
def main():
    banner()
    exe = choose_exiftool()
    merged_csv = ensure_merged_csv()
    if not merged_csv:
        input(f"\n{t('press_enter')}")
        return
    info(t("loading"))
    records = load_records(merged_csv)
    ok(t("loaded", n=len(records)))
    title(t("step", n=3, what=t("pick_input")))
    info(t("pick_input_hint"))
    in_dir = choose_folder_with_fallback(t("pick_input"))
    if not os.listdir(in_dir):
        warn(t("empty_dir"))
    title(t("step", n=4, what=t("pick_output")))
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
    tz = choose_timezone()
    title(t("scan"))
    jobs, unmatched = [], []
    out_norm = os.path.normpath(out_dir)
    for root, dirs, files in os.walk(in_dir):
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
    title(t("confirm_title"))
    print(f"  {t('confirm_body', n=len(jobs))}")
    print(f"  {t('confirm_out', d=out_dir)}")
    if input(f"  {C.MAGENTA}?{C.RESET} {t('confirm_q')} ").strip().lower() == "n":
        info(t("cancelled"))
        input(f"\n{t('press_enter')}")
        return
    title(t("running"))
    for src, dst, _, _ in jobs:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    results = run_exiftool_batch(exe, [(dst, ts) for _, dst, ts, _ in jobs])
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

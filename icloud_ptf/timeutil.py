# -*- coding: utf-8 -*-
"""GMT CSV timestamp parsing and timezone tables."""
import re
from datetime import datetime, timedelta, timezone
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

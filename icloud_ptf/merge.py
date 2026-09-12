# -*- coding: utf-8 -*-
"""Merge iCloud Photo Details CSVs."""
import csv, glob, os
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

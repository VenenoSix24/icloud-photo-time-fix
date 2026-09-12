# -*- coding: utf-8 -*-
"""把 csv 目录下所有 iCloud 导出的 Photo Details CSV 汇总成一个总表。

- 统一表头: imgName,fileChecksum,favorite,hidden,deleted,originalCreationDate,viewCount,importDate
- 按 (imgName, fileChecksum, originalCreationDate) 去重
- 输出: merged_photo_details.csv (UTF-8 with BOM, Excel 可直接打开)
"""
import csv
import glob
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(BASE, "csv")
OUTPUT = os.path.join(BASE, "merged_photo_details.csv")

FIELDS = ["imgName", "fileChecksum", "favorite", "hidden", "deleted",
          "originalCreationDate", "viewCount", "importDate"]

def main():
    files = sorted(glob.glob(os.path.join(CSV_DIR, "*.csv")))
    if not files:
        sys.exit(f"在 {CSV_DIR} 下没有找到 CSV 文件")

    seen = set()
    rows = []
    duplicate_count = 0
    for path in files:
        with open(path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            header = [h.strip() for h in reader.fieldnames or []]
            if header != FIELDS:
                print(f"[跳过] {os.path.basename(path)}: 表头不匹配 {header}")
                continue
            for row in reader:
                row = {k: (row.get(k) or "").strip() for k in FIELDS}
                key = (row["imgName"], row["fileChecksum"], row["originalCreationDate"])
                if key in seen:
                    duplicate_count += 1
                    continue
                seen.add(key)
                rows.append(row)
        print(f"[读取] {os.path.basename(path)}")

    with open(OUTPUT, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n共读取 {len(files)} 个文件, 汇总 {len(rows)} 条记录 (去除 {duplicate_count} 条重复)")
    print(f"输出: {OUTPUT}")

if __name__ == "__main__":
    main()

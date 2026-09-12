# iCloud 照片时间修正工具

从 iCloud 下载的照片经常丢失 EXIF 拍摄时间，但 iCloud 会同时导出 **Photo Details CSV**（含原始拍摄时间）。本工具读取 CSV，通过 [ExifTool](https://exiftool.org/) 把照片/视频的拍摄时间批量写回 EXIF/QuickTime 标签及文件时间戳。

**[English](README_EN.md)**

## 功能

- 图形窗口选择输入/输出目录，原文件不会被修改（结果输出到新目录）
- 自动合并多份 Photo Details CSV 并按文件名匹配照片
- GMT → 本地时区转换（默认东 8 区，可切换）
- 递归扫描子文件夹，保留目录结构
- ExifTool CSV 批量写入，速度快；照片（HEIC/JPG/PNG 等）和视频（MOV/MP4 等）都支持
- 每次运行在输出目录生成修正报告 CSV（逐文件记录状态、写入时间、失败原因）

## 使用

需要 [Python 3.8+](https://www.python.org/) 和 [ExifTool](https://exiftool.org/)。

```bash
# 1. 把从 iCloud 导出的 Photo Details*.csv 放入 csv/ 文件夹
# 2. 把 exiftool 可执行文件放入 exiftool/ 文件夹 (Windows 为 exiftool.exe)
# 3. 运行
python fix_photo_time.py        # 中文
python fix_photo_time.py en     # English
```

按提示选择目录和时区即可。也可以直接运行 `python merge_csv.py` 单独合并 CSV。

不想装 Python？GitHub Actions 提供了 Windows / macOS / Linux 的打包版本（见下方）。

## 打包版本

在 GitHub 仓库页面手动触发 **Actions → Build → Run workflow**，或推送 `v*` 标签，即可构建 3 系统 × 中/英文共 6 个可执行文件，在 Artifacts（或 Release）中下载。运行时同样需要脚本旁边的 `csv/` 和 `exiftool/` 文件夹。

## 目录结构

```
├── fix_photo_time.py     # 主程序 (中英双语)
├── merge_csv.py          # CSV 汇总脚本 (可独立使用)
├── csv/                  # 放 iCloud 导出的 Photo Details CSV
├── exiftool/             # 放 ExifTool 可执行文件
└── .github/workflows/    # 打包 CI
```

## License

MIT

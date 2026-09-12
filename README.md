# iCloud 照片时间修正工具

从 iCloud 下载的部分照片没有 EXIF 拍摄时间，但 iCloud 会导出 **Photo Details CSV**。本工具读取 CSV，通过 [ExifTool](https://exiftool.org/) 把照片/视频的拍摄时间批量写回 EXIF/QuickTime 标签及文件时间戳。

**[English](README_EN.md)**

## 功能

- 图形窗口选择输入/输出目录，原文件不会被修改
- 自动合并多份 Photo Details CSV 并按文件名匹配照片
- GMT → 本地时区转换
- 递归扫描子文件夹，保留目录结构
- ExifTool CSV 批量写入，速度快；支持照片和视频
- 每次运行在输出目录生成修正报告 CSV

## 使用

需要 [Python 3.8+](https://www.python.org/) 和 [ExifTool](https://exiftool.org/)。

```bash
# 1. 把从 iCloud 导出的 Photo Details*.csv 放入 csv/ 文件夹
# 2. 把下载的 exiftool 文件解压放入 exiftool/ 文件夹
# 3. 运行
python fix_photo_time.py        # 中文
python fix_photo_time.py en     # English
```

按提示选择目录和时区即可。也可以运行 `python fix_photo_time.py --merge` 单独合并 CSV。

不想装 Python？GitHub Actions 提供了 Windows / macOS / Linux 的打包版本。

## 打包版本

推送 `v*` 标签后，CI 会自动构建 3 系统 × 中/英文共 6 个可执行文件，并上传到 **Release 草稿**（不自动发布，由开发者手动发布发布说明后上线）。同样需要创建 `csv/` 和 `exiftool/` 文件夹。

## 目录结构

```
├── fix_photo_time.py     # 主程序入口
├── icloud_ptf/           # 主程序模块 (界面/合并/时间解析/ExifTool 等)
├── csv/                  # 放 iCloud 导出的 Photo Details CSV
├── exiftool/             # 放 ExifTool 可执行文件
└── .github/workflows/    # 打包 CI
```

## License

MIT

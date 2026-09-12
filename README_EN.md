# iCloud Photo Time Fixer

![iCloud Photo Time Fixer](docs/cover.png)

[![Build](https://github.com/VenenoSix24/icloud-photo-time-fix/actions/workflows/build.yml/badge.svg)](https://github.com/VenenoSix24/icloud-photo-time-fix/actions/workflows/build.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)

[English](README_EN.md) | [简体中文](README.md)

Some photos downloaded from iCloud lose their EXIF capture times, but iCloud exports a **Photo Details CSV**. This tool reads the CSV and writes the capture times back into the EXIF/QuickTime tags and file timestamps of your photos/videos in batch, via [ExifTool](https://exiftool.org/).

## Preview

<table>
  <tr>
    <td width="50%" align="center"><img src="docs/p1.png" alt="Running" width="100%"></td>
    <td width="50%" align="center"><img src="docs/p2.png" alt="Result" width="100%"></td>
  </tr>
</table>

## Features

- Graphical folder pickers for input/output; originals are never modified
- Merges multiple Photo Details CSVs and matches photos by filename
- GMT → local timezone conversion
- Recursive scanning with folder structure preserved
- Fast batch writing via ExifTool CSV import; supports photos and videos
- Detects files whose extension does not match their actual format (e.g. a .png that is really a JPEG) and writes them via the real format without renaming
- Automatically retries files with minor metadata problems
- Generates a per-file fix report CSV in the output folder, with the exact ExifTool error for any failure

### Files that cannot be processed

If a file itself is corrupt (e.g. an interrupted HEIC download with a truncated internal atom), ExifTool cannot safely write to it; the report records the exact error and the file must be re-downloaded from iCloud before running this tool again.

## Usage

Requires [Python 3.8+](https://www.python.org/) and [ExifTool](https://exiftool.org/).

```bash
# 1. Put the exported Photo Details*.csv files into the csv/ folder
# 2. Install ExifTool: brew install exiftool, or extract it into the exiftool/ folder
# 3. Run
python fix_photo_time.py en     # English
python fix_photo_time.py        # Chinese
```

Follow the prompts to pick folders and a timezone. You can also run `python fix_photo_time.py --merge` to merge CSVs only.

No Python? Download the executables from [Releases](https://github.com/VenenoSix24/icloud-photo-time-fix/releases). The `csv/` folder is still required; ExifTool can be installed system-wide (e.g. `brew install exiftool` on macOS) and is found automatically, with the `exiftool/` folder and manual path as fallbacks.

### First run on macOS

The downloaded executable is unsigned; on first run you need to remove the quarantine flag and grant execute permission. Open Terminal:

```bash
# Type the command before /xxx (mind the space), then drag the downloaded file onto the window
xattr -dr com.apple.quarantine /xxx/icloud-photo-time-fix-macos-latest-zh
chmod +x /xxx/icloud-photo-time-fix-macos-latest-zh
```

After that, double-click to open it.

## Layout

```
├── fix_photo_time.py     # entry point
├── icloud_ptf/           # modules (UI / CSV merge / time parsing / ExifTool ...)
├── csv/                  # iCloud-exported Photo Details CSVs
├── exiftool/             # ExifTool executable
└── .github/workflows/    # packaging CI
```

## License

MIT

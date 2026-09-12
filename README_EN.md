# iCloud Photo Time Fixer

Photos downloaded from iCloud often lose their EXIF capture times, but iCloud exports a **Photo Details CSV** containing the original creation dates. This tool reads the CSV and writes the capture times back into the EXIF/QuickTime tags and file timestamps of your photos/videos in batch, via [ExifTool](https://exiftool.org/).

**[中文说明](README.md)**

## Features

- Graphical folder pickers for input/output; originals are never modified (results go to a new folder)
- Merges multiple Photo Details CSVs and matches photos by filename
- GMT → local timezone conversion (defaults to UTC+8, switchable)
- Recursive scanning with folder structure preserved
- Fast batch writing via ExifTool CSV import; supports photos (HEIC/JPG/PNG, etc.) and videos (MOV/MP4, etc.)
- Generates a per-file fix report CSV (status, written time, errors) in the output folder

## Usage

Requires [Python 3.8+](https://www.python.org/) and [ExifTool](https://exiftool.org/).

```bash
# 1. Put the exported Photo Details*.csv files into the csv/ folder
# 2. Put the exiftool executable into the exiftool/ folder (exiftool.exe on Windows)
# 3. Run
python fix_photo_time.py en     # English
python fix_photo_time.py        # Chinese
```

Follow the prompts to pick folders and a timezone. You can also run `python merge_csv.py` to merge CSVs only.

No Python? The GitHub Actions workflow builds executables for Windows / macOS / Linux (see below).

## Packed binaries

Trigger **Actions → Build → Run workflow** manually, or push a `v*` tag, to build 6 executables (3 OS × zh/en). Download them from Artifacts (or Releases). The `csv/` and `exiftool/` folders are still required next to the executable.

## Layout

```
├── fix_photo_time.py     # main program (bilingual zh/en)
├── merge_csv.py          # CSV merge script (standalone)
├── csv/                  # iCloud-exported Photo Details CSVs
├── exiftool/             # ExifTool executable
└── .github/workflows/    # packaging CI
```

## License

MIT

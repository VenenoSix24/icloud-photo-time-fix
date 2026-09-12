# iCloud Photo Time Fixer

Some photos downloaded from iCloud lose their EXIF capture times, but iCloud exports a **Photo Details CSV**. This tool reads the CSV and writes the capture times back into the EXIF/QuickTime tags and file timestamps of your photos/videos in batch, via [ExifTool](https://exiftool.org/).

**[中文说明](README.md)**

## Features

- Graphical folder pickers for input/output; originals are never modified
- Merges multiple Photo Details CSVs and matches photos by filename
- GMT → local timezone conversion
- Recursive scanning with folder structure preserved
- Fast batch writing via ExifTool CSV import; supports photos and videos
- Generates a per-file fix report CSV in the output folder

## Usage

Requires [Python 3.8+](https://www.python.org/) and [ExifTool](https://exiftool.org/).

```bash
# 1. Put the exported Photo Details*.csv files into the csv/ folder
# 2. Extract the downloaded exiftool package into the exiftool/ folder
# 3. Run
python fix_photo_time.py en     # English
python fix_photo_time.py        # Chinese
```

Follow the prompts to pick folders and a timezone. You can also run `python fix_photo_time.py --merge` to merge CSVs only.

No Python? Download the executables from [Releases](https://github.com/VenenoSix24/icloud-photo-time-fix/releases). The `csv/` and `exiftool/` folders are still required next to the executable.

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

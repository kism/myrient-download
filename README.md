# Myrient ROM Downloader

Adaptation of this repo:

- https://github.com/secretx51/myrient-rsync
- https://github.com/TuckerWarlock/myrient-download

A Python script to download ROM files from Myrient's collection. The script allows you to specify multiple systems and filter games based on region, type, and other criteria.

## Run

Install with either pipx or uv

`pipx install git+https://github.com/kism/myrient-download`

`uv tool install git+https://github.com/kism/myrient-download`

Run

`myrient-download --config config.toml`

## Run (Developers)

Setup

```bash
uv venv
source .venv/bin/activate
uv sync
```

Run

```bash
python -m myrientdownload --config config.json
```

## Example Directory Structure

For the configuration shown above, files will be organized as:

```text
Share Path/
├── Atari - 7800/
│   └── Dark Chambers (USA).zip
└── Video CD/
    └── Club iKTV 02 (USA).zip
```

## Features

- Downloads directly from Myrient's servers
- Supports multiple systems in one run
- Creates organized folder structure
- Shows download progress
- Skips existing files
- Handles network paths
- Keeps original zip files intact
- Load settings from a config file

## Notes

- The script downloads files in zip format
- Most emulators can read ROMs directly from zip files
- Network paths should use raw strings (r"\\SERVER\Share")
- Files are organized by system automatically

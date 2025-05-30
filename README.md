# Myrient ROM Downloader

A Python script to download ROM files from Myrient's collection. The script allows you to specify multiple systems and filter games based on region, type, and other criteria.

## Run

Install with either pipx or uv

`pipx install git+https://github.com/kism/myrient-download`

`uv tool install git+https://github.com/kism/myrient-download`

Run

`myrient-download --config config.toml`

`myrient-download --help`

## Run (Developers)

Setup

```bash
uv venv
source .venv/bin/activate
uv sync
```

Run

`python -m myrientdownload --config config.toml`

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
- Verifies zip files
- Partial downloads have different file names

## Notes

- The script downloads files in zip format
- Most emulators can read ROMs directly from zip files
- Network paths should use raw strings (r"\\SERVER\Share")
- Files are organized by system automatically

## Todo

- TOSEC and friends
- ~~Retry on failure~~

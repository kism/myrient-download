# Myrient ROM Downloader

Adaptation of this repo: https://github.com/secretx51/myrient-rsync

A Python script to download ROM files from Myrient's collection. The script allows you to specify multiple systems and filter games based on region, type, and other criteria.

## Prerequisites

- Python 3.12+

Install dependencies using:
```bash
pip install -r requirements.txt
```

## Configuration

Configure the script by modifying these variables at the top:

```python
MYRIENT_URL = ''
DOWNLOAD_DIR = r'\\SERVER-NAME\Share Path'  # Use raw string for network paths
EXTRACT_ZIP = False  # Keep files as zips
SKIP_EXISTING = True  # Skip files that already exist
SYSTEMS = [  # Specify systems to download
    "Atari 7800",
    "Video CD"
]
GAME_WHITELIST = ["(USA)"]  # Only download USA games
GAME_BLACKLIST = ["Demo", "BIOS", "(Proto)", "(Beta)", "(Program)"]  # Skip these
```

### Available Options:

- `SYSTEMS`: List of systems to download. Leave empty to use whitelist/blacklist
- `DOWNLOAD_DIR`: Directory for downloads (supports network paths)
- `EXTRACT_ZIP`: Whether to extract zip files after download (default: False)
- `SKIP_EXISTING`: Skip files that already exist (default: True)
- `GAME_WHITELIST`: Only download games containing these terms
- `GAME_BLACKLIST`: Skip games containing these terms

## Usage

1. Configure the variables as needed
2. Run the script:
```bash
python myrient_downloader.py
```

The script will:
1. Create system-specific folders in your download directory
2. Download matching games for each system
3. Show progress bars for downloads
4. Skip existing files if enabled

## Example Directory Structure

For the configuration shown above, files will be organized as:
```
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

## Notes

- The script downloads files in zip format
- Most emulators can read ROMs directly from zip files
- Network paths should use raw strings (r"\\SERVER\Share")
- Files are organized by system automatically

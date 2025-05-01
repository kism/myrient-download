"""Constants for the Myrient Download Script."""

DEFAULT_CONFIG = {
    "myrinet_url": "https://myrient.erista.me/files",
    "myrinet_path": "No-Intro",
    # "download_dir": r"\\TUCKER-DESKTOP\Shared S Drive",
    "download_dir": "output",
    "skip_existing": True,
    "systems": [
        "Nintendo - Nintendo Entertainment System (Headered)",
        "Nintendo - Super Nintendo Entertainment System",
    ],
    "system_whitelist": [],
    "system_blacklist": [],
    "game_whitelist": ["(USA)"],
    "game_blacklist": ["Demo", "BIOS", "(Proto)", "(Beta)", "(Program)"],
}

HTTP_HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

REQUESTS_TIMEOUT = 10

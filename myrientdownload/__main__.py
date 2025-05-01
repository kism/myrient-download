"""Main entry point for CLI."""

import os

from .constants import DEFAULT_SETTINGS
from .logger import get_logger, setup_logger
from .myr_download import download_files
from .myr_files import get_files_list

setup_logger()
logger = get_logger(__name__)


def main():
    # Process each system
    for system in DEFAULT_SETTINGS["systems"]:
        system_url = f"{DEFAULT_SETTINGS['myrinet_url']}{system}/"
        files_list = get_files_list(system_url)

        # Apply filters
        filtered_files = [
            f
            for f in files_list
            if any(term in f for term in DEFAULT_SETTINGS["game_whitelist"])
            and not any(term in f for term in DEFAULT_SETTINGS["game_blacklist"])
        ]

        if filtered_files:
            logger.info(f"\nFound {len(filtered_files)} matching files for {system}")
            # Pass the system name to download_files
            download_files(
                filtered_files,
                system_url,
                DEFAULT_SETTINGS["DOWNLOAD_DIR"],
                system,
                skip_existing=DEFAULT_SETTINGS["skip_existing"],
            )
        else:
            logger.info(f"No matching files found for {system}")


if __name__ == "__main__":
    # Make sure base download directory exists
    os.makedirs(DEFAULT_SETTINGS["download_dir"], exist_ok=True)
    main()

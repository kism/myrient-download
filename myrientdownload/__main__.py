"""Main entry point for CLI."""

import argparse

from .config import load_config
from .logger import get_logger, setup_logger
from .myr_download import download_files
from .myr_files import get_files_list

setup_logger()
logger = get_logger(__name__)


def main() -> None:
    """Main CLI."""
    parser = argparse.ArgumentParser(description="Download files from Myrient.")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="config.toml",
        help="Path to the configuration file (default: config.toml)",
    )

    args = parser.parse_args()

    config = load_config(args.config)

    for system in config["systems"]:
        system_url = f"{config['myrinet_url']}/{config['myrinet_path']}/{system}/"
        files_list = get_files_list(system_url)

        # Apply filters
        filtered_files = [
            f
            for f in files_list
            if any(term in f for term in config["game_allow_list"])
            and not any(term in f for term in config["game_disallow_list"])
        ]

        if filtered_files:
            msg = f"\nFound {len(filtered_files)} matching files for {system}"
            logger.info(msg)
            # Pass the system name to download_files
            download_files(
                filtered_files,
                system_url,
                config["download_dir"],
                system,
                skip_existing=config["skip_existing"],
            )
        else:
            logger.info("No matching files found for %s", system)


if __name__ == "__main__":
    main()

"""Main entry point for CLI."""

import argparse
from pathlib import Path

from . import DESCRIPTION, PROGRAM_NAME, __version__
from .config import MyrDLConfig
from .logger import get_logger, setup_logger
from .myr_download import MyrDownloader

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
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        help="Set the logging level (default: INFO)",
    )
    parser.add_argument(
        "--directory",
        type=str,
        default="",
        help="Specify the directory to save downloaded files, will override and save to the config file",
    )

    args = parser.parse_args()

    print_program_info()

    setup_logger(args.log_level)

    config_path = Path(args.config).expanduser().resolve()
    download_directory = Path(args.directory).expanduser().resolve() if args.directory else None
    config = MyrDLConfig(config_path, download_directory)

    mry_downloader = MyrDownloader(config)
    mry_downloader.download_from_system_list()


def print_program_info() -> None:
    """Print program information."""
    msg = f"{PROGRAM_NAME} v{__version__}, {DESCRIPTION}"
    logger.info(msg)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("")
        logger.info("Download interrupted by user.")

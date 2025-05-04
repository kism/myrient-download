"""Main entry point for CLI."""

import argparse

from . import DESCRIPTION, PROGRAM_NAME, __version__
from .config import load_config
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

    args = parser.parse_args()

    print_program_info()

    setup_logger(args.log_level)
    config = load_config(args.config)

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

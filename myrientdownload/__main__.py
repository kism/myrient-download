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
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        default="config.toml",
        help="Path to the configuration file (default: config.toml)",
    )
    args = parser.parse_args()

    logger.info("%s v%s %s", PROGRAM_NAME, __version__, DESCRIPTION)
    setup_logger(args.log_level)

    config_path = Path(args.config).expanduser().resolve()

    config = MyrDLConfig.load_config(config_path)
    if args.directory != "":
        config.download_dir = Path(args.directory)
    config.print_config_overview()
    config.write_config(config_path)  # Override the config post-validation

    mry_downloader = MyrDownloader(config)
    mry_downloader.download_from_system_list()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("")
        logger.info("Download interrupted by user.")

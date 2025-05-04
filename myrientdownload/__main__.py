"""Main entry point for CLI."""

import argparse
from pathlib import Path

import tomlkit

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
    toml_file = Path(__file__).parent.parent / "pyproject.toml"
    with toml_file.open("r", encoding="utf-8") as f:
        toml_data = tomlkit.load(f)

    version = toml_data.get("project", {}).get("version", "UNKNOWN")
    description = toml_data.get("project", {}).get("description", "No description available.")
    msg = f"myrient-download {version}, {description}"
    logger.info(msg)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("")
        logger.info("Download interrupted by user.")

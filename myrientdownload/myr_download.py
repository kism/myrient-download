"""Download management for Myrinet files."""

import logging
import zipfile
from pathlib import Path
from urllib.parse import quote  # Add this for URL encoding

import requests
from colorama import Fore, Style, init
from tqdm import tqdm

from .config import MyrDLConfig
from .constants import FUN_TQDM_LOADING_BAR, HTTP_HEADERS, REQUESTS_TIMEOUT
from .logger import get_logger
from .myr_files import get_files_list

logger = get_logger(__name__)

init()


class MyrDownloader:
    """Class to manage downloading files from Myrinet."""

    def __init__(self, config: MyrDLConfig) -> None:
        """Initialize the downloader with the given configuration."""
        self.config = config

        self.stats = {
            "skipped": 0,
            "downloaded": 0,
            "failed": 0,
        }

        self.skip_streak = 0

    def report_stat(self, stat: str) -> None:
        """Report the status of the download."""
        if stat in self.stats:
            self.stats[stat] += 1
            logger.debug("Status: %s", stat)
            if stat == "skipped":
                self.skip_streak += 1
        else:
            logger.warning("Unknown stat: %s", stat)

    def _reset_skipped_streak(self) -> None:
        """Check if there was a streak of skipped files."""
        if self.skip_streak > 0:
            logger.info("Skipped %d existing files", self.skip_streak)
            self.skip_streak = 0

    def print_stats(self) -> None:
        """Print the download statistics."""
        msg = "\nDownload statistics:"
        for stat, count in self.stats.items():
            msg += f"\n  {stat.capitalize()}: {count}"

        logger.info(msg)

    def download_from_system_list(
        self,
    ) -> None:
        """Download files from the list of systems in the configuration."""
        print()  # noqa: T201 # Add a newline for better readability
        logger.info("Starting download from Myrinet...")

        for system in self.config.systems:
            print()  # noqa: T201 # Add a newline for better readability
            system_url = f"{self.config.myrinet_url}/{self.config.myrinet_path}/{system}/"
            files_list = get_files_list(system_url)

            # Apply filters
            if self.config.game_allow_list == []:  # Small hack to allow all files if nothing is specified
                self.config.game_allow_list = ["."]
            filtered_files = [
                f
                for f in files_list
                if any(term in f for term in self.config.game_allow_list)
                and not any(term in f for term in self.config.game_disallow_list)
            ]

            if filtered_files:
                msg = f"Found {len(filtered_files)} matching files for {system}"
                logger.info(msg)

                self.download_files(
                    filtered_files,
                    system_url,
                    system=system,
                )
            else:
                logger.info("No matching files found for %s", system)

        self.print_stats()
        print()  # noqa: T201 # Add a newline for better readability
        logger.info("Download complete!")

    def download_file(self, url: str, destination: Path) -> bool:
        """Download an individual file."""
        try:
            encoded_url = quote(url, safe=":/")
            response = requests.get(encoded_url, headers=HTTP_HEADERS, stream=True, timeout=REQUESTS_TIMEOUT)
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))

            destination_temp = destination.with_suffix(".part")

            with (
                destination_temp.open("wb") as f,
                tqdm(total=total_size, unit="iB", unit_scale=True, ascii=FUN_TQDM_LOADING_BAR, leave=False) as pbar,
            ):
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        size = f.write(chunk)
                        pbar.update(size)

            destination_temp.rename(destination)

        except (
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectionError,
        ) as e:
            if logger.isEnabledFor(logging.DEBUG):
                logger.exception("Connection error: %s", url)
            else:
                logger.error("%s: %s", e, url)  # noqa: TRY400 # logger.exception is too verbose, we don't need the stack trace for these exceptions
            self.report_stat("failed")
            return False

        return True

    def download_files(
        self,
        filtered_files: list[str],
        base_url: str,
        *,
        system: str = "",
    ) -> None:
        """Download files from Myrient based on the filtered list."""
        # Create system-specific directory
        download_dir = self.config.download_dir
        if self.config.create_and_use_system_directories:
            download_dir = self.config.download_dir / system

        download_dir.mkdir(parents=True, exist_ok=True)

        # Remove any files that end with .part in the download directory
        for part_file in download_dir.glob("*.part"):
            logger.warning("Deleting incomplete file: %s", part_file)
            part_file.unlink()

        for n_files_processed, file_name in enumerate(filtered_files):
            # Put files in their system directory
            output_file = download_dir / file_name

            # Check that zip file isn't completely cooked
            if self.config.verify_zips and output_file.exists() and str(output_file).endswith(".zip"):
                try:
                    zipfile.ZipFile(output_file)
                except zipfile.BadZipFile:
                    logger.warning("Deleting broken zip file: %s", output_file)
                    output_file.unlink()

            if self.config.skip_existing and output_file.exists():
                logger.debug("Skipping %s - already exists", file_name)
                self.report_stat("skipped")
                continue

            self._reset_skipped_streak()

            def magenta_str(s: str) -> str:
                return f"{Fore.MAGENTA}{s}{Style.RESET_ALL}"

            msg = f"{system} {magenta_str('@')}{n_files_processed}/{len(filtered_files)} {magenta_str('»')} {file_name} "

            logger.info(msg)

            # Download the file
            file_url = f"{base_url}{file_name}"
            if self.download_file(file_url, output_file):
                self.report_stat("downloaded")

        self._reset_skipped_streak()

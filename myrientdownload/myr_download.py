"""Handle downloading files from Myrient."""

from pathlib import Path
from urllib.parse import quote  # Add this for URL encoding

import requests
from tqdm import tqdm

from .constants import HTTP_HEADERS, REQUESTS_TIMEOUT
from .logger import get_logger

logger = get_logger(__name__)

def download_file(url: str, destination: Path) -> bool:
    """Download an individual file."""
    try:
        encoded_url = quote(url, safe=":/")
        response = requests.get(encoded_url, headers=HTTP_HEADERS, stream=True, timeout=REQUESTS_TIMEOUT)
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))

        with destination.open("wb") as f, tqdm(total=total_size, unit="iB", unit_scale=True) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    size = f.write(chunk)
                    pbar.update(size)

    except (
        requests.exceptions.ConnectTimeout,
        requests.exceptions.ReadTimeout,
        requests.exceptions.ConnectionError,
    ):
        logger.exception("Error downloading %s", url)
        return False

    return True


def download_files(
    filtered_files: list[str],
    base_url: str,
    download_dir: Path,
    *,
    skip_existing: bool = True,
) -> None:
    """Download files from Myrient based on the filtered list."""
    # Create system-specific directory
    download_dir.mkdir(parents=True, exist_ok=True)

    for file_name in tqdm(filtered_files, desc="Processing files", unit="file"):
        # Put files in their system directory
        zip_file = download_dir / file_name

        if skip_existing and zip_file.exists():
            logger.info("Skipping %s - already exists", file_name)
            continue

        # Download the file
        file_url = f"{base_url}{file_name}"
        logger.info("Downloading: %s", file_name)
        if download_file(file_url, zip_file):
            logger.info("Successfully downloaded: %s", file_name)

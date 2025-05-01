"""Handle downloading files from Myrient."""

import os
from urllib.parse import quote  # Add this for URL encoding

import requests
from requests.exceptions import ConnectTimeout, ReadTimeout
from tqdm import tqdm

from .constants import HTTP_HEADERS, REQUESTS_TIMEOUT
from .logger import get_logger

logger = get_logger(__name__)


def download_file(url, destination):
    """Download an individual file."""
    try:
        encoded_url = quote(url, safe=":/")
        response = requests.get(encoded_url, headers=HTTP_HEADERS, stream=True, timeout=REQUESTS_TIMEOUT)
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))

        with open(destination, "wb") as f, tqdm(total=total_size, unit="iB", unit_scale=True) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    size = f.write(chunk)
                    pbar.update(size)

    except (ConnectTimeout, ReadTimeout):
        logger.exception("Error downloading %s", url)
        return False

    return True


def download_files(filtered_files, base_url, download_dir, system, skip_existing=True):
    # Create system-specific directory
    system_dir = os.path.join(download_dir, system)
    os.makedirs(system_dir, exist_ok=True)

    for file_name in tqdm(filtered_files, desc="Processing files", unit="file"):
        # Put files in their system directory
        zip_file = os.path.join(system_dir, file_name)

        if skip_existing and os.path.exists(zip_file):
            print(f"Skipping {file_name} - already exists")
            continue

        # Download the file
        file_url = f"{base_url}{file_name}"
        logger.info("Downloading: %s", file_name)
        if download_file(file_url, zip_file):
            logger.info("Successfully downloaded: %s", file_name)

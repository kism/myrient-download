"""File wrangling for Myrient."""

from urllib.parse import quote  # Add this for URL encoding

import requests
from bs4 import BeautifulSoup

from .constants import HTTP_HEADERS, REQUESTS_TIMEOUT
from .logger import get_logger

logger = get_logger(__name__)


def get_files_list(url: str) -> list[str]:
    """Get the list of files from the Myrient website."""
    logger.info("Getting file list from: %s", url)
    try:
        # Encode URL properly
        encoded_url = quote(url, safe=":/")
        response = requests.get(encoded_url, headers=HTTP_HEADERS, timeout=REQUESTS_TIMEOUT)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        files = []
        # Look for links in the table with id='list'
        table = soup.find("table", id="list")
        if table:
            for link in table.find_all("a"): # type: ignore[attr-defined] # God knows
                href = link.get("title")  # Use title instead of href
                if href and href.endswith(".zip"):
                    files.append(href)

    except Exception:
        logger.exception("Error getting file list")
        return []

    return files

"""Download management for Myrinet files."""

from .config import MyrDLConfig
from .logger import get_logger
from .myr_download import download_files
from .myr_files import get_files_list

logger = get_logger(__name__)


def download_from_system_list(config: MyrDLConfig) -> None:
    """Download files from the list of systems in the configuration."""
    for system in config.systems:
        system_url = f"{config.myrinet_url}/{config.myrinet_path}/{system}/"
        files_list = get_files_list(system_url)

        # Apply filters
        if config.game_allow_list == []:  # Small hack to allow all files if nothing is specified
            config.game_allow_list = ["."]
        filtered_files = [
            f
            for f in files_list
            if any(term in f for term in config.game_allow_list)
            and not any(term in f for term in config.game_disallow_list)
        ]

        if filtered_files:
            msg = f"\nFound {len(filtered_files)} matching files for {system}"
            logger.info(msg)

            download_dir = config.download_dir
            if not config.no_download_system_dir:  # Silly double negative since it's what I want the key to be named
                download_dir = config.download_dir / system

            download_files(
                filtered_files,
                system_url,
                download_dir,
                skip_existing=config.skip_existing,
            )
        else:
            logger.info("No matching files found for %s", system)

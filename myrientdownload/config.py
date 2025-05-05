"""Handle loading and writing the configuration file."""

import time
from pathlib import Path
from typing import Any

import tomlkit

from . import PROGRAM_NAME, URL
from .logger import get_logger

logger = get_logger(__name__)


class MyrDLConfig:
    """Configuration for the Myrient download script."""

    def __init__(self, config_path: Path | None, download_directory_override: Path | None = None) -> None:
        """Initialize the configuration with default values."""
        self.myrinet_url: str = "https://myrient.erista.me/files"
        self.myrinet_path: str = "No-Intro"
        self.download_dir: Path = Path.cwd()
        if download_directory_override:
            logger.info("Overriding download directory with '%s'", download_directory_override)
            self.download_dir = Path(download_directory_override).expanduser().resolve()
        self.no_download_system_dir: bool = False
        self.skip_existing: bool = True
        self.verify_zips: bool = True  # Check existing zips are valid before skipping
        self.systems: list[str] = [
            "Nintendo - Nintendo Entertainment System (Headered)",
            "Nintendo - Super Nintendo Entertainment System",
        ]
        self.system_allow_list: list[str] = []
        self.system_disallow_list: list[str] = []
        self.game_allow_list: list[str] = ["(USA)"]
        self.game_disallow_list: list[str] = ["Demo", "BIOS", "(Proto)", "(Beta)", "(Program)"]

        if config_path:
            self.load_from_file(config_path)

        self.validate_config()
        self.write_to_file(config_path or Path("config.toml"))

    def validate_config(self) -> None:
        """Validate the configuration values."""
        if self.no_download_system_dir and len(self.systems) > 1:
            msg = "Cannot set 'no_system_dir' to True when multiple systems are specified."
            raise ValueError(msg)

        if not self.download_dir.exists():
            logger.warning(
                "Download directory '%s' does not exist. \nCreating it in 10 seconds.", self.download_dir.resolve()
            )
            time.sleep(10)
            self.download_dir.mkdir(parents=True, exist_ok=True)

    def load_from_file(self, config_path: Path) -> None:
        """Load configuration from a file."""
        logger.info("Loading configuration from '%s'", config_path)
        with config_path.open() as f:
            config_dict_toml = tomlkit.load(f)

        config_dict: dict[str, Any] = dict(config_dict_toml)
        # Ensure download_dir is a Path object
        if "download_dir" in config_dict:
            config_dict["download_dir"] = Path(str(config_dict["download_dir"])).expanduser().resolve()

        for key in self.__dict__:
            if key not in config_dict:
                logger.warning("Missing key '%s' in configuration. Using default value.", key)
                config_dict[key] = getattr(self, key)

        self.__dict__.update(config_dict)
        self.download_dir = Path(self.download_dir).expanduser().resolve()

    def write_to_file(self, config_path: Path) -> None:
        """Write configuration to a file."""
        logger.debug("Writing configuration to '%s'", config_path)
        temp_dict = self.__dict__.copy()

        # Convert Path object to string for TOML serialization
        temp_dict["download_dir"] = str(self.download_dir)

        with config_path.open("w") as f:
            f.write(f"# Configuration file for {PROGRAM_NAME} script {URL}\n")
            tomlkit.dump(temp_dict, f)
        logger.info("Configuration written to '%s'", config_path)

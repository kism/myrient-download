"""Handle loading and writing the configuration file."""

from pathlib import Path
from typing import Any

import tomlkit

from . import __url__
from .logger import get_logger

logger = get_logger(__name__)


class Config:
    """Configuration for the Myrient download script."""

    def __init__(self, config_path: Path | None) -> None:
        """Initialize the configuration with default values."""
        self.myrinet_url: str = "https://myrient.erista.me/files"
        self.myrinet_path: str = "No-Intro"
        self.download_dir: Path = Path("output")
        self.skip_existing: bool = True
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

    def load_from_file(self, config_path: Path) -> None:
        """Load configuration from a file."""
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
        logger.info("Writing configuration to '%s'", config_path)
        temp_dict = self.__dict__.copy()

        # Convert Path object to string for TOML serialization
        temp_dict["download_dir"] = str(self.download_dir)

        with config_path.open("w") as f:
            f.write(f"# Configuration file for Myrient download script {__url__}\n")
            tomlkit.dump(temp_dict, f)
        logger.info("Configuration written to '%s'", config_path)


def load_config(config_path_str: str) -> Config:
    """Load configuration from a JSON file."""
    config_path = Path(config_path_str).expanduser().resolve()

    if config_path.exists():
        config = Config(config_path)
    else:
        logger.warning("Configuration file '%s' not found. Using default values.", config_path)
        config = Config(None)

    config.write_to_file(config_path)

    return config

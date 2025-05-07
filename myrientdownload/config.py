"""Handle loading and writing the configuration file."""

import time
from pathlib import Path
from typing import Any

import tomlkit
from colorama import Back, Fore, Style, init

from . import PROGRAM_NAME, URL, __version__
from .logger import get_logger

logger = get_logger(__name__)

init(autoreset=True)


class MyrDLConfig:
    """Configuration for the Myrient download script."""

    def __init__(self, config_path: Path | None = None, download_directory_override: Path | None = None) -> None:
        """Initialize the configuration with default values."""
        self.myrinet_url: str = "https://myrient.erista.me/files"
        self.myrinet_path: str = "No-Intro"  # Database name, see the website
        self.download_dir: Path = Path.cwd()
        if download_directory_override:
            self.download_dir = download_directory_override.expanduser().resolve()
        self.create_and_use_system_directories: bool = True  # System name, per the list
        self.create_and_use_database_directories: bool = False  # No-Intro, Redump, etc.
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

        if config_path and config_path.exists():
            self.load_from_file(config_path, download_directory_override)

        self.validate_config()
        self.write_to_file(config_path)
        self.print_config_overview()

    def print_config_overview(self) -> None:
        """Print the configuration overview."""
        print_green = Fore.GREEN + Back.BLACK
        print_red = Fore.RED + Back.BLACK

        def str_magenta(text: Path | str | list[str]) -> str:
            return f"{Fore.MAGENTA}{Back.BLACK}{text}{Style.RESET_ALL}"

        def will_will_not(*, condition: bool, thing: str) -> str:
            if condition:
                return f"{print_green}Will {thing}{Style.RESET_ALL}"
            return f"{print_red}Will NOT {thing}{Style.RESET_ALL}"

        msg = f"""
Configuration:
  Download Directory: {str_magenta(self.download_dir)}
  Resolved Myrinet URL: {str_magenta(f"{self.myrinet_url}/{str_magenta(self.myrinet_path)}")}
  {will_will_not(condition=self.create_and_use_system_directories, thing="create system directories")}
  {will_will_not(condition=self.skip_existing, thing="skip existing files")}
  {will_will_not(condition=self.verify_zips, thing="verify existing zips")}
  Systems:
    {"\n    ".join(self.systems)}
  System Allow List: {str_magenta(", ".join(self.system_allow_list) if self.system_allow_list else "<All>")}
  System Disallow List: {str_magenta(", ".join(self.system_disallow_list) if self.system_disallow_list else "<None>")}
  Game Allow List: {str_magenta(", ".join(self.game_allow_list) if self.game_allow_list else "<All>")}
  Game Disallow List: {str_magenta(", ".join(self.game_disallow_list) if self.game_disallow_list else "<None>")}"""

        logger.info(msg)
        time.sleep(3)  # Pause to allow the user to read the config overview

    def validate_config(self) -> None:
        """Validate the configuration values."""
        if not self.create_and_use_system_directories and len(self.systems) > 1:
            msg = "Cannot set 'create_and_use_system_directories' to True when multiple systems are specified."
            raise ValueError(msg)

        if not self.download_dir.exists():
            logger.warning(
                "Download directory '%s' does not exist. Creating it in 10 seconds.", self.download_dir.resolve()
            )
            time.sleep(10)
            self.download_dir.mkdir(parents=True, exist_ok=True)

    def load_from_file(self, config_path: Path, download_directory_override: Path | None = None) -> None:
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

        if download_directory_override:
            logger.info("Overriding download directory with '%s'", download_directory_override)
            self.download_dir = download_directory_override.expanduser().resolve()
        else:
            self.download_dir = Path(self.download_dir).expanduser().resolve()

    def write_to_file(self, config_path: Path | None) -> None:
        """Write configuration to a file."""
        if not config_path:
            config_path = Path("config.toml").expanduser().resolve()

        if not config_path.exists():
            config_path.touch()

        logger.debug("Writing configuration to '%s'", config_path)
        temp_dict = self.__dict__.copy()

        # Convert Path object to string for TOML serialization
        temp_dict["download_dir"] = str(self.download_dir)

        with config_path.open("w") as f:
            f.write(f"# Configuration file for {PROGRAM_NAME} v{__version__} {URL}\n")
            tomlkit.dump(temp_dict, f)
        logger.info("Configuration written to '%s'", config_path)

"""Config loading, setup, validating, writing."""

import json
from pathlib import Path
from typing import Self

import tomlkit
from colorama import Back, Fore, Style, init
from pydantic import BaseModel, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from . import PROGRAM_NAME, URL, __version__
from .helpers import wait_with_dots
from .logger import get_logger

logger = get_logger(__name__)
init(autoreset=True)


class MyrDLConfig(BaseModel):
    """Settings for the Myrient downloader."""

    myrient_url: str = "https://myrient.erista.me/files"
    myrient_path: str = "No-Intro"  # Database name, see the website
    skip_existing: bool = True
    verify_zips: bool = True  # Check existing zips are valid before skipping
    systems: list[str] = [
        "Nintendo - Nintendo Entertainment System (Headered)",
        "Nintendo - Super Nintendo Entertainment System",
    ]
    system_allow_list: list[str] = []
    system_disallow_list: list[str] = []
    game_allow_list: list[str] = ["(USA)"]
    game_disallow_list: list[str] = ["Demo", "BIOS", "(Proto)", "(Beta)", "(Program)"]

    # @model_validator(mode="after")
    # def validate_config(self) -> Self:
    #     """Validate the configuration values."""
    #     if not self.create_and_use_system_directories and len(self.systems) > 1:
    #         msg = "Cannot set 'create_and_use_system_directories' to True when multiple systems are specified."
    #         raise ValueError(msg)
    #     return self


class MyrDLConfigHandler(BaseSettings):
    """Settings loaded from a TOML file."""

    # Default values for our settings
    myrient_downloader: list[MyrDLConfig] = [MyrDLConfig()]
    download_dir: Path = Path.cwd() / "output"
    create_and_use_system_directories: bool = True  # System name, per the list
    create_and_use_database_directories: bool = False  # No-Intro, Redump, etc.

    config_path: Path = Path() / "config.toml"  # Default config path

    # Configure settings class
    model_config = SettingsConfigDict(
        env_prefix="APP_",  # environment variables with APP_ prefix will override settings
        env_nested_delimiter="__",  # APP_NESTED__NESTED_FIELD=value
        json_encoders={Path: str},
    )

    def __init__(self, config_path: Path, download_directory_override: Path | None = None) -> None:
        """Initialize settings and load from a TOML file if provided."""
        super().__init__()  # Initialize with default values first
        self.config_path = config_path

        self._load_from_toml()

        if download_directory_override:
            self.download_dir = download_directory_override.expanduser().resolve()

    @model_validator(mode="after")
    def validate_config(self) -> Self:
        """Validate the settings after initialization."""
        if not self.download_dir.exists():
            logger.warning(
                "Download directory '%s' does not exist. Creating it in 10 seconds.",
                self.download_dir.resolve(),
            )
            wait_with_dots(10)  # Wait for 10 seconds to give the user a chance to cancel
            self.download_dir.mkdir(parents=True, exist_ok=True)

        return self

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
Global Settings:
  Download Directory: {str_magenta(self.download_dir)}
  {will_will_not(condition=self.create_and_use_system_directories, thing="create system directories")}
  {will_will_not(condition=self.create_and_use_database_directories, thing="create database directories")}
"""

        for n, myr_downloader in enumerate(self.myrient_downloader):
            msg += f"""
Myrient Downloader {n + 1}:
  Resolved Myrinet URL: {str_magenta(f"{myr_downloader.myrient_url}/{str_magenta(myr_downloader.myrient_path)}")}
  {will_will_not(condition=myr_downloader.skip_existing, thing="skip existing files")}
  {will_will_not(condition=myr_downloader.verify_zips, thing="verify existing zips")}
  Systems:
    {"\n    ".join(myr_downloader.systems)}
  System Allow List: {str_magenta(", ".join(myr_downloader.system_allow_list) if myr_downloader.system_allow_list else "<All>")}
  System Disallow List: {str_magenta(", ".join(myr_downloader.system_disallow_list) if myr_downloader.system_disallow_list else "<None>")}
  Game Allow List: {str_magenta(", ".join(myr_downloader.game_allow_list) if myr_downloader.game_allow_list else "<All>")}
  Game Disallow List: {str_magenta(", ".join(myr_downloader.game_disallow_list) if myr_downloader.game_disallow_list else "<None>")}
"""
        logger.info(msg)
        wait_with_dots(5)  # Pause to allow the user to read the config overview

    def _load_from_toml(self) -> None:
        """Load settings from the TOML file specified in config_path."""
        if self.config_path.is_dir():
            msg = f"Config path '{self.config_path}' is a directory, not a file."
            raise ValueError(msg)

        if self.config_path.is_file():
            with self.config_path.open("r") as f:
                config_data = tomlkit.load(f)

            # Update our settings from the loaded data
            for key, value in config_data.items():
                if key == "myrient_downloader" and isinstance(value, list):
                    self.myrient_downloader = [
                        MyrDLConfig(**item) if isinstance(item, dict) else item for item in value
                    ]
                elif key == "download_dir":
                    self.download_dir = Path(value).expanduser().resolve()
                elif hasattr(self, key):
                    setattr(self, key, value)
                else:
                    logger.warning("Unknown config key '%s' in %s", key, self.config_path)

    def write_config(self) -> None:
        """Write the current settings to a TOML file."""
        with self.config_path.open("r") as f:
            existing_data = tomlkit.load(f)

        logger.info("Writing config to %s", self.config_path)
        config_data = json.loads(self.model_dump_json())  # This is how we make the object safe for tomlkit
        config_data.pop("config_path", None)  # Remove config_path from the data to be written

        # Write to the TOML file
        if not self.config_path.parent.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.config_path.exists():
            self.config_path.touch()

        new_file_content_str = f"# Configuration file for {PROGRAM_NAME} v{__version__} {URL}\n"
        new_file_content_str += tomlkit.dumps(config_data)

        if existing_data != config_data: # The new object will be valid, so we back up the old one
            backup_file = self.config_path.parent / f"{self.config_path.name}.bak"
            logger.warning("Validation has changed the config file, backing up the old one to %s", backup_file)
            with backup_file.open("w") as f:
                f.write(tomlkit.dumps(existing_data))

        with self.config_path.open("w") as f:
            f.write(new_file_content_str)

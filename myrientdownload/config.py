"""Config loading, setup, validating, writing."""

import json
import time
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

    myrinet_url: str = "https://myrient.erista.me/files"
    myrinet_path: str = "No-Intro"  # Database name, see the website
    download_dir: Path = Path.cwd() / "output"
    create_and_use_system_directories: bool = True  # System name, per the list
    create_and_use_database_directories: bool = False  # No-Intro, Redump, etc.
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

    @model_validator(mode="after")
    def validate_config(self) -> Self:
        """Validate the configuration values."""
        if not self.create_and_use_system_directories and len(self.systems) > 1:
            msg = "Cannot set 'create_and_use_system_directories' to True when multiple systems are specified."
            raise ValueError(msg)
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
        wait_with_dots(5)  # Pause to allow the user to read the config overview


class MyrDLConfigHandler(BaseSettings):
    """Settings loaded from a TOML file."""

    # Default values for our settings
    myrient: MyrDLConfig = MyrDLConfig()

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
            self.myrient.download_dir = download_directory_override.expanduser().resolve()

        self.myrient.print_config_overview()

    @model_validator(mode="after")
    def validate_config(self) -> Self:
        """Validate the settings after initialization."""
        if not self.myrient.download_dir.exists():
            logger.warning(
                "Download directory '%s' does not exist. Creating it in 10 seconds.",
                self.myrient.download_dir.resolve(),
            )
            wait_with_dots(10)  # Wait for 10 seconds to give the user a chance to cancel
            self.myrient.download_dir.mkdir(parents=True, exist_ok=True)
        return self

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
                if key == "myrient":
                    self.myrient = MyrDLConfig(**value)

    def get_config(self) -> MyrDLConfig:
        """Get the current settings."""
        return self.myrient

    def write_config(self) -> None:
        """Write the current settings to a TOML file."""
        logger.info("Writing config to %s", self.config_path)
        config_data = json.loads(self.model_dump_json())  # This is how we make the object safe for tomlkit
        config_data.pop("config_path", None)  # Remove config_path from the data to be written

        # Write to the TOML file
        if not self.config_path.parent.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with self.config_path.open("w") as f:
            f.write(f"# Configuration file for {PROGRAM_NAME} v{__version__} {URL}\n")
            tomlkit.dump(config_data, f)

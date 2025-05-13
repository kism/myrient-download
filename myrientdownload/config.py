"""Config loading, setup, validating, writing."""

import json
from pathlib import Path
from typing import Any

import tomlkit
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from .logger import get_logger

# Logging should be all done at INFO level or higher as the log level hasn't been set yet
# Modules should all setup logging like this so the log messages include the modules name.
logger = get_logger(__name__)


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


class MyrDLConfigHandler(BaseSettings):
    """Settings loaded from a TOML file."""

    # Default values for our settings
    myrient: MyrDLConfig = MyrDLConfig()

    config_path: Path = Path()

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

    def _load_from_toml(self) -> None:
        """Load settings from the TOML file specified in config_path."""
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
            tomlkit.dump(config_data, f)

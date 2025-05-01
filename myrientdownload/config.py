"""Handle loading and writing the configuration file."""

from pathlib import Path
from typing import TypedDict

import tomlkit

from .constants import DEFAULT_CONFIG
from .logger import get_logger

logger = get_logger(__name__)


class Config(TypedDict):
    """Configuration for the Myrient download script."""

    myrinet_url: str
    myrinet_path: str
    download_dir: Path
    skip_existing: bool
    systems: list[str]
    system_allow_list: list[str]
    system_disallow_list: list[str]
    game_allow_list: list[str]
    game_disallow_list: list[str]


def load_config(config_path_str: str) -> Config:
    """Load configuration from a JSON file."""
    config_path = Path(config_path_str).expanduser().resolve()

    if not config_path.exists():
        write_config(config_path, DEFAULT_CONFIG)

    with config_path.open() as f:
        config_dict = tomlkit.load(f)

    # Ensure download_dir is a Path object
    if "download_dir" in config_dict:
        config_dict["download_dir"] = Path(str(config_dict["download_dir"])).expanduser().resolve()

    for key in DEFAULT_CONFIG:
        if key not in config_dict:
            logger.warning("Missing key '%s' in configuration. Using default value.", key)
            config_dict[key] = DEFAULT_CONFIG[key]

    return Config(**config_dict)


def write_config(config_path: Path, config: Config) -> None:
    """Write configuration to a TOML file."""
    with config_path.open("w") as f:
        tomlkit.dump(config, f)

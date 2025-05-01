"""Handle loading and writing the configuration file."""

import json
from pathlib import Path

from .constants import DEFAULT_CONFIG
from .logger import get_logger

logger = get_logger(__name__)


def load_config(config_path_str: str) -> dict:
    """Load configuration from a JSON file."""
    config_path = Path(config_path_str).expanduser().resolve()

    if not config_path.exists():
        write_config(config_path, DEFAULT_CONFIG)

    with config_path.open() as f:
        return json.load(f)


def write_config(config_path: Path, config: dict) -> None:
    """Write configuration to a JSON file."""
    with config_path.open("w") as f:
        json.dump(config, f, indent=4)

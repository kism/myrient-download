import argparse
import shutil
from pathlib import Path

import pytest

from myrientdownload.config import MyrDLDownloaderConfig

TEST_CONFIGS_LOCATION = Path.cwd() / "tests" / "configs"


def pytest_configure():
    """Magic function to set module level variables."""
    pytest.TEST_CONFIGS_LOCATION = TEST_CONFIGS_LOCATION


@pytest.fixture
def myr_default_config(tmp_path, no_sleep) -> MyrDLDownloaderConfig:
    """Fixture for MyCoolObject."""
    return MyrDLDownloaderConfig()


@pytest.fixture
def no_sleep(monkeypatch):
    """Fixture to disable sleep."""
    monkeypatch.setattr("time.sleep", lambda x: None)


@pytest.fixture
def place_test_config():
    """Fixture that places a config in the tmp_path.

    Returns: a function to place a config in the tmp_path.
    """

    def _place_test_config(config_name, path):
        """Place config in tmp_path by name."""
        filepath = Path(pytest.TEST_CONFIGS_LOCATION) / config_name

        shutil.copyfile(filepath, Path(path) / "config.toml")

    return _place_test_config


@pytest.fixture
def no_argparse(monkeypatch, tmp_path):
    """Fixture to disable argparse."""

    config_path = tmp_path / "config.toml"

    mock_args = argparse.Namespace(log_level="INFO", config=config_path, directory=tmp_path)
    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", lambda self: mock_args)

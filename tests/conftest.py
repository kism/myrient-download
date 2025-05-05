import pytest

from myrientdownload.config import MyrDLConfig


@pytest.fixture
def myr_default_config(tmp_path, no_sleep) -> MyrDLConfig:
    """Fixture for MyCoolObject."""
    return MyrDLConfig()


@pytest.fixture
def no_sleep(monkeypatch):
    """Fixture to disable sleep."""
    monkeypatch.setattr("time.sleep", lambda x: None)

"""Test versioning."""

from pathlib import Path

import tomlkit

import myrientdownload


def test_version_pyproject():
    """Verify version in pyproject.toml matches package version."""
    pyproject_path = Path("pyproject.toml")
    with pyproject_path.open("rb") as f:
        pyproject_toml = tomlkit.load(f)
    assert pyproject_toml["project"]["version"] == myrientdownload.__version__


def test_version_lock():
    """Verify version in uv.lock matches package version."""
    lock_path = Path("uv.lock")
    with lock_path.open() as f:
        uv_lock = tomlkit.load(f)

    found_version = False
    for package in uv_lock["package"]:
        if package["name"] == "myrientdownload":
            assert package["version"] == myrientdownload.__version__
            found_version = True
            break

    assert found_version, "myrientdownload not found in uv.lock"

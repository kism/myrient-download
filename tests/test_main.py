import argparse

from myrientdownload.__main__ import print_program_info


def test_print_program_info(caplog):
    """Test the print_program_info function."""

    from myrientdownload import __version__

    with caplog.at_level("INFO"):
        print_program_info()

    assert __version__ in caplog.text


def test_main_no_download(caplog, tmp_path, place_test_config, no_argparse, no_sleep):
    """Test the main function without downloading files."""
    from myrientdownload.__main__ import main

    place_test_config("valid_no_systems.toml", tmp_path)

    with caplog.at_level("INFO"):
        main()

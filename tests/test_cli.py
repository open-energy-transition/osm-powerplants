"""Tests for CLI."""

import subprocess
import sys


def test_cli_version():
    """Test CLI version command."""
    from osm_powerplants import __version__

    result = subprocess.run(
        [sys.executable, "-m", "osm_powerplants.cli", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert __version__ in result.stdout


def test_cli_help():
    """Test CLI help command."""
    result = subprocess.run(
        [sys.executable, "-m", "osm_powerplants.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "process" in result.stdout
    assert "info" in result.stdout


def test_cli_info():
    """Test CLI info command."""
    result = subprocess.run(
        [sys.executable, "-m", "osm_powerplants.cli", "info"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Config file:" in result.stdout
    assert "Cache directory:" in result.stdout


def test_cli_process_help():
    """Test CLI process help."""
    result = subprocess.run(
        [sys.executable, "-m", "osm_powerplants.cli", "process", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--output" in result.stdout
    assert "--config" in result.stdout

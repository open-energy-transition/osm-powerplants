"""Integration tests (require network access)."""

import pytest


@pytest.mark.slow
def test_process_small_country():
    """Test full processing pipeline with a small country."""
    from osm_powerplants import get_cache_dir, get_config, process_units

    config = get_config()
    cache_dir = str(get_cache_dir(config))

    df = process_units(
        countries=["Luxembourg"],
        config=config,
        cache_dir=cache_dir,
    )

    assert len(df) > 0
    assert "projectID" in df.columns
    assert "Fueltype" in df.columns
    assert "Capacity" in df.columns


@pytest.mark.slow
def test_cli_process():
    """Test CLI process command."""
    import subprocess
    import sys
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        output_path = f.name

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "osm_powerplants.cli",
            "process",
            "Luxembourg",
            "-o",
            output_path,
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0
    # Logging goes to stderr
    assert "Saved" in result.stderr or "power plants" in result.stderr

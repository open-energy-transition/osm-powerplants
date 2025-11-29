# SPDX-FileCopyrightText: Contributors to osm-powerplants
#
# SPDX-License-Identifier: MIT

"""
Core configuration and path utilities for osm_powerplants.
"""

import logging
from pathlib import Path

import yaml
from platformdirs import user_cache_dir, user_config_dir

logger = logging.getLogger(__name__)

# Package directories
PACKAGE_DIR = Path(__file__).parent
CONFIG_DIR = user_config_dir("osm-powerplants")
CACHE_DIR = user_cache_dir("osm-powerplants")

# Ensure directories exist
Path(CONFIG_DIR).mkdir(parents=True, exist_ok=True)
Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)


def get_default_config_path() -> Path:
    """Get path to the default config file."""
    # Check multiple locations in order of priority:
    # 1. Project root (for development: src/osm_powerplants -> osm_powerplants -> config.yaml)
    pkg_config = PACKAGE_DIR.parent.parent / "config.yaml"
    if pkg_config.exists():
        return pkg_config

    # 2. One more level up (for editable installs)
    pkg_config_alt = PACKAGE_DIR.parent.parent.parent / "config.yaml"
    if pkg_config_alt.exists():
        return pkg_config_alt

    # 3. User config directory
    user_config = Path(CONFIG_DIR) / "config.yaml"
    if user_config.exists():
        return user_config

    # 4. Fallback to package directory (for bundled config)
    return PACKAGE_DIR / "config.yaml"


def get_config(filename: str | None = None) -> dict:
    """
    Load configuration from YAML file.

    Parameters
    ----------
    filename : str, optional
        Path to configuration file. If None, uses default location.

    Returns
    -------
    dict
        Configuration dictionary
    """
    if filename is not None:
        config_path = Path(filename)
    else:
        config_path = get_default_config_path()

    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}")
        return {}

    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    return config


def get_cache_dir(config: dict | None = None) -> Path:
    """
    Get cache directory path.

    Parameters
    ----------
    config : dict, optional
        Configuration with optional cache_dir override

    Returns
    -------
    Path
        Cache directory path
    """
    if config and config.get("cache_dir"):
        cache_dir = Path(config["cache_dir"]).expanduser()
    else:
        cache_dir = Path(CACHE_DIR)

    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir

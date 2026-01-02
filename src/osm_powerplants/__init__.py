# SPDX-FileCopyrightText: Contributors to osm-powerplants
# SPDX-License-Identifier: MIT

"""
OpenStreetMap (OSM) power plant data extraction and processing.

This package provides tools for extracting, processing, and analyzing
power plant data from OpenStreetMap.
"""

__version__ = "0.1.3"

from .core import get_cache_dir, get_config
from .interface import (
    process_countries,
    process_units,
    validate_countries,
)
from .models import Unit, Units

__all__ = [
    "__version__",
    "process_countries",
    "process_units",
    "validate_countries",
    "Unit",
    "Units",
    "get_config",
    "get_cache_dir",
]

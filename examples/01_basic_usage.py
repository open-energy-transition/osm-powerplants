#!/usr/bin/env python3
"""
Example 1: Basic Usage
======================

Extract power plant data from OpenStreetMap for a single country.
"""

from osm_powerplants import get_cache_dir, get_config, process_units

# Load configuration
config = get_config()
cache_dir = get_cache_dir(config)

# Process a small country (fast)
df = process_units(
    countries=["Luxembourg"],
    config=config,
    cache_dir=str(cache_dir),
)

# Display results
print(f"Found {len(df)} power plants in Luxembourg\n")
print(df[["Name", "Fueltype", "Technology", "Capacity"]].head(10).to_string())

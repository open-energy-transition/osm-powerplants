#!/usr/bin/env python3
"""
Example 1: Basic Usage
======================

Extract power plant data from OpenStreetMap for a single country.
"""

from osm_powerplants import get_cache_dir, get_config, process_countries_simple

# Load configuration
config = get_config()
cache_dir = get_cache_dir(config)

# Process a small country (fast)
df = process_countries_simple(
    countries=["Malta"],
    config=config,
    cache_dir=str(cache_dir),
)

# Display results
print(f"Found {len(df)} power plants in Malta\n")
print(df[["Name", "Fueltype", "Technology", "Capacity"]].to_string())

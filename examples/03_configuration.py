#!/usr/bin/env python3
"""
Example 3: Configuration Options
================================

Customize processing with different configuration options.
"""

from osm_powerplants import get_cache_dir, get_config, process_units

# Load and customize configuration
config = get_config()
cache_dir = get_cache_dir(config)

# Option 1: Strict data quality (require names)
config["missing_name_allowed"] = False
df_strict = process_units(
    countries=["Luxembourg"],
    config=config,
    cache_dir=str(cache_dir),
)
print(f"Strict mode (require names): {len(df_strict)} plants")

# Option 2: Permissive (allow missing names)
config["missing_name_allowed"] = True
df_permissive = process_units(
    countries=["Luxembourg"],
    config=config,
    cache_dir=str(cache_dir),
)
print(f"Permissive mode: {len(df_permissive)} plants")

# Option 3: Enable plant reconstruction from generators
config["units_reconstruction"]["enabled"] = True
config["units_reconstruction"]["min_generators_for_reconstruction"] = 2
df_reconstructed = process_units(
    countries=["Cyprus"],
    config=config,
    cache_dir=str(cache_dir),
)
print(f"With reconstruction (Cyprus): {len(df_reconstructed)} plants")

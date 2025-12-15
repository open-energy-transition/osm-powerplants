#!/usr/bin/env python3
"""
Example 2: Multiple Countries
=============================

Process multiple countries and analyze the results.
"""

from osm_powerplants import get_cache_dir, get_config, process_units

config = get_config()
cache_dir = get_cache_dir(config)

# Process multiple countries
df = process_units(
    countries=["Luxembourg", "Malta", "Cyprus"],
    config=config,
    cache_dir=str(cache_dir),
)

print(f"Total power plants: {len(df)}\n")

# Summary by country
print("=== By Country ===")
summary = (
    df.groupby("Country")
    .agg(Plants=("projectID", "count"), Capacity_MW=("Capacity", "sum"))
    .round(1)
)
print(summary.to_string())

# Summary by fuel type
print("\n=== By Fuel Type ===")
by_fuel = (
    df.groupby("Fueltype")
    .agg(Plants=("projectID", "count"), Capacity_MW=("Capacity", "sum"))
    .sort_values("Capacity_MW", ascending=False)
    .round(1)
)
print(by_fuel.to_string())

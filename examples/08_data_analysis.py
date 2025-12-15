#!/usr/bin/env python3
"""
Example 8: Data Analysis
========================

Analyze power plant data with pandas.
"""

from osm_powerplants import get_cache_dir, get_config, process_units

config = get_config()
cache_dir = get_cache_dir(config)

# Load data for a medium country
df = process_units(
    countries=["Portugal"],
    config=config,
    cache_dir=str(cache_dir),
)

print(f"Total plants: {len(df)}")
print(f"Total capacity: {df['Capacity'].sum():,.0f} MW\n")

# Capacity by fuel type
print("=== Capacity by Fuel Type ===")
by_fuel = (
    df.groupby("Fueltype")
    .agg(
        Count=("projectID", "count"),
        Total_MW=("Capacity", "sum"),
        Avg_MW=("Capacity", "mean"),
    )
    .sort_values("Total_MW", ascending=False)
    .round(1)
)
print(by_fuel.to_string())

# Technology distribution
print("\n=== Technology Distribution ===")
by_tech = df.groupby("Technology")["Capacity"].agg(["count", "sum"]).round(1)
by_tech.columns = ["Count", "Total_MW"]
print(by_tech.sort_values("Total_MW", ascending=False).to_string())

# Plants by commissioning decade
print("\n=== By Commissioning Decade ===")
df["Decade"] = (df["DateIn"] // 10 * 10).astype("Int64")
by_decade = df.groupby("Decade")["Capacity"].agg(["count", "sum"]).round(1)
by_decade.columns = ["Count", "Total_MW"]
print(by_decade.dropna().to_string())

# Data completeness
print("\n=== Data Completeness ===")
total = len(df)
print(f"Has name: {df['Name'].notna().sum()}/{total} ({df['Name'].notna().mean():.0%})")
print(
    f"Has capacity: {df['Capacity'].notna().sum()}/{total} ({df['Capacity'].notna().mean():.0%})"
)
print(
    f"Has date: {df['DateIn'].notna().sum()}/{total} ({df['DateIn'].notna().mean():.0%})"
)

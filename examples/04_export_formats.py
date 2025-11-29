#!/usr/bin/env python3
"""
Example 4: Export Formats
=========================

Export power plant data in different formats.
"""

from osm_powerplants import (
    Unit,
    Units,
    get_cache_dir,
    get_config,
    process_countries_simple,
)

config = get_config()
cache_dir = get_cache_dir(config)

df = process_countries_simple(
    countries=["Luxembourg"],
    config=config,
    cache_dir=str(cache_dir),
)

# Export to CSV
df.to_csv("luxembourg_plants.csv", index=False)
print("Saved: luxembourg_plants.csv")

# Export to JSON
df.to_json("luxembourg_plants.json", orient="records", indent=2)
print("Saved: luxembourg_plants.json")

# Export to GeoJSON (using Units class)
units = [
    Unit(
        projectID=row["projectID"],
        Name=row.get("Name"),
        Country=row["Country"],
        lat=row["lat"],
        lon=row["lon"],
        Fueltype=row.get("Fueltype"),
        Technology=row.get("Technology"),
        Capacity=row.get("Capacity"),
    )
    for _, row in df.iterrows()
]

units_collection = Units(units)
units_collection.save_geojson_report("luxembourg_plants.geojson")
print("Saved: luxembourg_plants.geojson")

# Show GeoJSON preview
geojson = units_collection.generate_geojson_report()
print(f"\nGeoJSON has {len(geojson['features'])} features")

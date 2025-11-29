#!/usr/bin/env python3
"""
Example 6: Regional Queries
===========================

Query raw OSM power elements in custom regions (bbox, radius).

Note: Regional queries return raw OSM element counts, not processed
power plants. Use process_countries_simple() for processed data.
"""

from osm_powerplants import get_cache_dir, get_config
from osm_powerplants.retrieval.regional import region_download

config = get_config()
cache_dir = str(get_cache_dir(config))

# Example 1: Circular region around a city
print("=== Radius Query: Valletta (Malta) 5km ===")
region = {
    "type": "radius",
    "name": "Valletta 5km",
    "center": [35.8989, 14.5146],
    "radius_km": 5,
}

try:
    result = region_download(regions=region, cache_dir=cache_dir)
    if result["success"]:
        data = result["results"]["Valletta 5km"]
        print("Raw OSM elements found:")
        print(f"  Plants: {data['plants_count']}")
        print(f"  Generators: {data['generators_count']}")
except Exception as e:
    print(f"Error (API may be busy): {type(e).__name__}")

# Example 2: Bounding box
print("\n=== Bounding Box Query: Luxembourg City ===")
bbox = {
    "type": "bbox",
    "name": "Luxembourg City",
    "bounds": [49.58, 6.10, 49.63, 6.15],
}

try:
    result = region_download(regions=bbox, cache_dir=cache_dir, download_type="plants")
    if result["success"]:
        data = result["results"]["Luxembourg City"]
        print(f"Raw plant elements: {data['plants_count']}")
except Exception as e:
    print(f"Error: {type(e).__name__}")

print("\n" + "=" * 50)
print("Note: Regional queries return raw OSM element counts.")
print("For processed power plant data, use:")
print("  process_countries_simple(['Malta'], config, cache_dir)")

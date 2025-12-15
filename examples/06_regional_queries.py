#!/usr/bin/env python3
"""
Example 6: Regional Queries
===========================

Query raw OSM power elements in custom regions (bbox, radius).

Note: Regional queries return raw OSM element counts, not processed
power plants. Use process_units() for processed data.
"""

from osm_powerplants import get_cache_dir, get_config
from osm_powerplants.retrieval.regional import region_download

config = get_config()
cache_dir = str(get_cache_dir(config))

# Example 1: Circular region around a wind park in Luxembourg
print("=== Radius Query: Kehmen Wind Park Area 10km ===")
region = {
    "type": "radius",
    "name": "Kehmen Area",
    "center": [49.889, 6.018],  # Near Wandpark Kehmen Heischent
    "radius_km": 10,
}

try:
    result = region_download(regions=region, cache_dir=cache_dir)
    if result["success"]:
        data = result["results"]["Kehmen Area"]
        print("Raw OSM elements found:")
        print(f"  Plants: {data['plants_count']}")
        print(f"  Generators: {data['generators_count']}")
except Exception as e:
    print(f"Error (API may be busy): {type(e).__name__}")

# Example 2: Bounding box covering multiple wind parks
print("\n=== Bounding Box Query: Luxembourg Wind Parks ===")
bbox = {
    "type": "bbox",
    "name": "Luxembourg Wind",
    "bounds": [49.50, 6.00, 49.95, 6.50],  # Covers several wind parks
}

try:
    result = region_download(regions=bbox, cache_dir=cache_dir, download_type="plants")
    if result["success"]:
        data = result["results"]["Luxembourg Wind"]
        print(f"Raw plant elements: {data['plants_count']}")
except Exception as e:
    print(f"Error: {type(e).__name__}")

print("\n" + "=" * 50)
print("Note: Regional queries return raw OSM element counts.")
print("For processed power plant data, use:")
print("  process_units(['Luxembourg'], config, cache_dir)")

#!/usr/bin/env python3
"""
Example 7: Cache Management
===========================

Understand and manage the caching system.
"""

import os
import time

from osm_powerplants import get_cache_dir, get_config, process_countries_simple

config = get_config()
cache_dir = get_cache_dir(config)

print(f"Cache directory: {cache_dir}\n")

# Show cache contents
print("Cache contents:")
for item in sorted(os.listdir(cache_dir)):
    path = cache_dir / item
    if path.is_file():
        size = path.stat().st_size / 1024
        print(f"  {item}: {size:.1f} KB")
    else:
        print(f"  {item}/ (directory)")

# First run: may download from API or use cache
print("\n=== First Run ===")
start = time.time()
df1 = process_countries_simple(
    countries=["Malta"],
    config=config,
    cache_dir=str(cache_dir),
)
print(f"Time: {time.time() - start:.2f}s, Plants: {len(df1)}")

# Second run: uses cache (fast)
print("\n=== Second Run (Cached) ===")
start = time.time()
df2 = process_countries_simple(
    countries=["Malta"],
    config=config,
    cache_dir=str(cache_dir),
)
print(f"Time: {time.time() - start:.2f}s, Plants: {len(df2)}")

# Show cache hit message
print("\nNote: Second run is faster because data is cached.")
print("Use config['force_refresh'] = True to re-download from OSM.")

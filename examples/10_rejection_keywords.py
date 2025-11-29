#!/usr/bin/env python3
"""
Example 10: Rejection Keyword Analysis
======================================

Identify problematic OSM tag values causing rejections.
Useful for targeted data quality improvements.
"""

from osm_powerplants import Units, get_cache_dir, get_config
from osm_powerplants.quality.rejection import RejectionTracker
from osm_powerplants.retrieval.client import OverpassAPIClient
from osm_powerplants.workflow import Workflow

config = get_config()
cache_dir = str(get_cache_dir(config))

# Strict settings to capture more rejections
config["missing_name_allowed"] = False
config["missing_technology_allowed"] = False

tracker = RejectionTracker()
units = Units()

with OverpassAPIClient(cache_dir=cache_dir) as client:
    workflow = Workflow(client, tracker, units, config)
    workflow.process_country_data("Malta")

# Get unique rejection reasons found
reasons = tracker.get_unique_rejection_reasons()
print(f"Rejection reasons found: {len(reasons)}\n")

# Analyze keywords for each reason
for reason in reasons:
    keywords = tracker.get_unique_keyword(reason)
    if keywords:
        print(f"{reason.value}:")
        for kw, count in keywords.items():
            print(f"  '{kw}': {count}")
        print()

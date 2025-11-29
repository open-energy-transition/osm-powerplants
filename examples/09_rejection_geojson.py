#!/usr/bin/env python3
"""
Example 9: Rejection GeoJSON Export
===================================

Export rejected elements as GeoJSON for visualization
in mapping tools (JOSM, iD editor, uMap, geojson.io).
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

# Export all rejections to single GeoJSON
tracker.save_geojson("malta_rejections.geojson")
print(f"Saved: malta_rejections.geojson ({tracker.get_total_count()} features)")

# Export separate files per rejection reason
tracker.save_geojson_by_reasons(".", prefix="malta")

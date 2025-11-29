#!/usr/bin/env python3
"""
Example 5: Rejection Analysis
=============================

Track why OSM elements are rejected during processing.
Useful for improving OSM data quality.
"""

from osm_powerplants import Units, get_cache_dir, get_config
from osm_powerplants.quality.rejection import RejectionTracker
from osm_powerplants.retrieval.client import OverpassAPIClient
from osm_powerplants.workflow import Workflow

config = get_config()
cache_dir = str(get_cache_dir(config))

# Strict configuration to see all issues
config["missing_name_allowed"] = False
config["missing_technology_allowed"] = False

# Create tracking objects
rejection_tracker = RejectionTracker()
units = Units()

# Process with rejection tracking
with OverpassAPIClient(cache_dir=cache_dir) as client:
    workflow = Workflow(client, rejection_tracker, units, config)
    workflow.process_country_data("Malta")

# Summary
print(f"Valid plants: {len(units)}")
print(f"Rejected elements: {rejection_tracker.get_total_count()}")

# Rejection breakdown
print("\n=== Rejection Reasons ===")
for reason, count in rejection_tracker.get_summary().items():
    print(f"  {reason}: {count}")

# Export detailed report
report = rejection_tracker.generate_report()
if not report.empty:
    report.to_csv("malta_rejections.csv", index=False)
    print("\nSaved detailed report: malta_rejections.csv")

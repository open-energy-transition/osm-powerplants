# Python API

## Basic usage

```python
from osm_powerplants import (
    process_units,
    get_config,
    get_cache_dir,
    validate_countries,
    Unit,
    Units,
)

config = get_config()
cache_dir = get_cache_dir(config)

df = process_units(
    countries=["Chile", "Greece"],
    config=config,
    cache_dir=str(cache_dir),
    output_path="plants.csv",           # optional
    rejected_output_path=None,          # optional — see Quality Tracking
)
```

## Capturing rejected elements

Pass `rejected_output_path` to get a CSV + sibling GeoJSON listing every
OSM element dropped during processing and the reason. Rejection data is
only populated on API fetches, so set `force_refresh=True` to force a
re-query when you need a complete report.

```python
config = get_config()
config["force_refresh"] = True

df = process_units(
    countries=["Kenya"],
    config=config,
    cache_dir=str(cache_dir),
    output_path="kenya.csv",
    rejected_output_path="kenya_rejected.csv",   # writes kenya_rejected.geojson too
)
```

See the [Quality Tracking](quality-tracking.md) guide for the list of
reason codes and examples of how to analyse the report.

## Configuration

```python
# Load and modify
config = get_config()
config["force_refresh"] = True
config["units_clustering"]["enabled"] = True

# Custom config file
config = get_config("/path/to/config.yaml")
```

## Country validation

```python
valid, codes = validate_countries(["Germany", "France"])
# codes = {"Germany": "DE", "France": "FR"}
```

## Working with Units

```python
from osm_powerplants import Units, Unit

units = Units()
units.add_unit(unit)

# Filter
solar = units.filter_by_fueltype("Solar")
chile = units.filter_by_country("Chile")

# Export
df = units.to_dataframe()
units.save_csv("output.csv")
units.save_geojson_report("output.geojson")
```

## Low-level API

For custom pipelines — e.g. running parsing against cached OSM elements without re-entering the `process_units` flow:

```python
from osm_powerplants.retrieval.client import OverpassAPIClient
from osm_powerplants.workflow import Workflow
from osm_powerplants.quality.rejection import RejectionTracker

with OverpassAPIClient(cache_dir=str(cache_dir)) as client:
    units = Units()
    tracker = RejectionTracker()
    workflow = Workflow(client, tracker, units, config)
    workflow.process_country_data("Malta")

    print(f"Units: {len(units)}")
    print(tracker.get_summary_string())
```

## With GeoPandas

```python
import geopandas as gpd

gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.lon, df.lat),
    crs="EPSG:4326",
)
gdf.to_file("plants.gpkg", driver="GPKG")
```

# Python API

## Basic Usage

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
    output_path="plants.csv",  # optional
)
```

## Configuration

```python
# Load and modify
config = get_config()
config["force_refresh"] = True
config["units_clustering"]["enabled"] = True

# Custom config file
config = get_config("/path/to/config.yaml")
```

## Country Validation

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

## Low-Level API

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
    crs="EPSG:4326"
)
gdf.to_file("plants.gpkg", driver="GPKG")
```

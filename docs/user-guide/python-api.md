# Python API

This guide covers the Python API for advanced usage and integration.

## Quick Reference

```python
from osm_powerplants import (
    process_countries,
    process_countries_simple,
    validate_countries,
    get_config,
    get_cache_dir,
    Unit,
    Units,
)
```

## Configuration

### Loading Configuration

```python
from osm_powerplants import get_config, get_cache_dir

# Load default configuration
config = get_config()

# Load custom configuration
config = get_config("/path/to/custom-config.yaml")

# Get cache directory
cache_dir = get_cache_dir(config)
print(f"Cache: {cache_dir}")
```

### Modifying Configuration at Runtime

```python
config = get_config()

# Override settings
config["force_refresh"] = True
config["plants_only"] = False
config["units_clustering"]["enabled"] = True
```

## Processing Countries

### Simple API

The simplest way to process countries:

```python
from osm_powerplants import process_countries_simple, get_config, get_cache_dir

config = get_config()
cache_dir = get_cache_dir(config)

df = process_countries_simple(
    countries=["Chile", "Greece", "Portugal"],
    config=config,
    cache_dir=str(cache_dir),
    output_path="power_plants.csv",  # Optional
)

print(f"Processed {len(df)} power plants")
print(df.head())
```

### Advanced API

For more control, use the full `process_countries` function:

```python
from osm_powerplants.interface import process_countries
from osm_powerplants import get_config, get_cache_dir
import os

config = get_config()
cache_dir = get_cache_dir(config)
csv_cache_path = os.path.join(str(cache_dir), "osm_data.csv")

# Define target columns
target_columns = [
    "projectID", "Name", "Country", "lat", "lon",
    "Fueltype", "Technology", "Set", "Capacity", "DateIn"
]

df = process_countries(
    countries=["Germany", "France"],
    csv_cache_path=csv_cache_path,
    cache_dir=str(cache_dir),
    update=False,  # Use cache if available
    osm_config=config,
    target_columns=target_columns,
    raw=False,  # Apply validation and standardization
)
```

### Validating Countries

Validate country names before processing:

```python
from osm_powerplants import validate_countries

# Returns (valid_countries, country_code_map)
valid, codes = validate_countries(["Germany", "France", "Germny"])
# Raises ValueError for invalid countries with suggestions
```

## Working with Units

### Unit Data Class

The `Unit` class represents a single power plant:

```python
from osm_powerplants import Unit

unit = Unit(
    projectID="OSM_plant:way/123456",
    Name="Solar Farm Alpha",
    Country="Chile",
    lat=-33.45,
    lon=-70.66,
    Fueltype="Solar",
    Technology="PV",
    Set="PP",
    Capacity=50.0,
    DateIn=2020,
)

# Convert to dictionary
data = unit.to_dict()
```

### Units Collection

The `Units` class manages collections of power plants:

```python
from osm_powerplants import Units, Unit

# Create empty collection
units = Units()

# Add units
units.add_unit(unit1)
units.add_units([unit2, unit3, unit4])

# Filter
solar_units = units.filter_by_fueltype("Solar")
chile_units = units.filter_by_country("Chile")
pv_units = units.filter_by_technology("PV")

# Statistics
stats = units.get_statistics()
print(f"Total capacity: {stats['total_capacity_mw']} MW")

# Convert to DataFrame
df = units.to_dataframe()

# Export
units.save_csv("output.csv")
units.save_geojson_report("output.geojson")
```

## Low-Level API

### Using the Overpass Client Directly

```python
from osm_powerplants.retrieval.client import OverpassAPIClient
from osm_powerplants import get_config, get_cache_dir

config = get_config()
cache_dir = get_cache_dir(config)

with OverpassAPIClient(cache_dir=str(cache_dir)) as client:
    # Count elements
    counts = client.count_country_elements("Malta")
    print(f"Plants: {counts['plants']}, Generators: {counts['generators']}")

    # Get raw data
    plants_data, generators_data = client.get_country_data(
        "Malta",
        force_refresh=False,
        plants_only=True,
    )

    print(f"Raw plant elements: {len(plants_data['elements'])}")
```

### Using the Workflow Directly

```python
from osm_powerplants.workflow import Workflow
from osm_powerplants.retrieval.client import OverpassAPIClient
from osm_powerplants.quality.rejection import RejectionTracker
from osm_powerplants import Units, get_config, get_cache_dir

config = get_config()
cache_dir = get_cache_dir(config)

with OverpassAPIClient(cache_dir=str(cache_dir)) as client:
    units = Units()
    tracker = RejectionTracker()

    workflow = Workflow(
        client=client,
        rejection_tracker=tracker,
        units=units,
        config=config,
    )

    # Process a country
    result_units, result_tracker = workflow.process_country_data("Malta")

    # Analyze rejections
    print(tracker.get_summary_string())

    # Get processed units
    print(f"Valid units: {len(result_units)}")
```

## Integration Examples

### With powerplantmatching

```python
import powerplantmatching as pm
from osm_powerplants import process_countries_simple, get_config, get_cache_dir

# Get OSM data
config = get_config()
osm_df = process_countries_simple(
    countries=["Germany"],
    config=config,
    cache_dir=str(get_cache_dir(config)),
)

# Combine with other sources in PPM
# (This requires OSM to be configured in PPM's config.yaml)
matched = pm.powerplants()
```

### With GeoPandas

```python
import geopandas as gpd
from osm_powerplants import process_countries_simple, get_config, get_cache_dir

config = get_config()
df = process_countries_simple(
    countries=["Spain"],
    config=config,
    cache_dir=str(get_cache_dir(config)),
)

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.lon, df.lat),
    crs="EPSG:4326"
)

# Save as GeoPackage
gdf.to_file("spain_power_plants.gpkg", driver="GPKG")
```

### Parallel Processing

```python
from concurrent.futures import ProcessPoolExecutor
from osm_powerplants import process_countries_simple, get_config, get_cache_dir
import pandas as pd

def process_country(country):
    config = get_config()
    cache_dir = get_cache_dir(config)
    return process_countries_simple(
        countries=[country],
        config=config,
        cache_dir=str(cache_dir),
    )

countries = ["Germany", "France", "Spain", "Italy", "Poland"]

# Note: Due to caching, parallel processing has limited benefits
# after the first run
with ProcessPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(process_country, countries))

df = pd.concat(results, ignore_index=True)
print(f"Total plants: {len(df)}")
```

## Error Handling

```python
from osm_powerplants import process_countries_simple, get_config, get_cache_dir

try:
    config = get_config()
    df = process_countries_simple(
        countries=["InvalidCountry"],
        config=config,
        cache_dir=str(get_cache_dir(config)),
    )
except ValueError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"Processing error: {e}")
```

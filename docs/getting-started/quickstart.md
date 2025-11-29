# Quick Start

This guide will get you extracting power plant data in under 5 minutes.

## Basic Usage

### Using the CLI

The simplest way to extract data is using the command-line interface:

```bash
# Process a single country
osm-powerplants process Malta -o malta.csv

# Process multiple countries
osm-powerplants process Chile Greece Portugal -o south_countries.csv

# Force refresh (ignore cache)
osm-powerplants process Germany --force-refresh -o germany.csv
```

### Using Python

```python
from osm_powerplants import process_countries_simple, get_config, get_cache_dir

# Load default configuration
config = get_config()
cache_dir = get_cache_dir(config)

# Process countries
df = process_countries_simple(
    countries=["Chile", "Greece"],
    config=config,
    cache_dir=str(cache_dir),
    output_path="power_plants.csv",  # Optional: save to file
)

# Explore the data
print(f"Total plants: {len(df)}")
print(f"Total capacity: {df['Capacity'].sum():,.0f} MW")
print(df.head())
```

## Understanding the Output

The output CSV contains standardized power plant data:

```csv
projectID,Name,Country,lat,lon,Fueltype,Technology,Set,Capacity,DateIn
OSM_plant:way/123,Solar Farm,Chile,-33.45,-70.66,Solar,PV,PP,50.0,2020
OSM_plant:relation/456,Wind Park,Greece,38.5,23.7,Wind,Onshore,PP,100.0,2018
```

### Column Descriptions

| Column | Type | Description |
|--------|------|-------------|
| `projectID` | string | Unique OSM-based identifier |
| `Name` | string | Power plant name (may be empty) |
| `Country` | string | Full country name |
| `lat`, `lon` | float | Geographic coordinates |
| `Fueltype` | string | Primary fuel type |
| `Technology` | string | Generation technology |
| `Set` | string | Plant category (PP, Store, CHP) |
| `Capacity` | float | Electrical capacity in MW |
| `DateIn` | int | Commissioning year |

### Valid Fuel Types

- `Nuclear`, `Hydro`, `Wind`, `Solar`
- `Natural Gas`, `Hard Coal`, `Lignite`, `Oil`
- `Solid Biomass`, `Biogas`, `Geothermal`, `Waste`, `Other`

### Valid Technologies

- **Solar**: `PV`, `CSP`
- **Wind**: `Onshore`, `Offshore`
- **Hydro**: `Run-Of-River`, `Reservoir`, `Pumped Storage`
- **Thermal**: `Steam Turbine`, `CCGT`, `OCGT`, `Combustion Engine`
- **Other**: `Marine`

## Analyzing the Data

```python
import pandas as pd

df = pd.read_csv("power_plants.csv")

# Summary by country
print(df.groupby("Country").agg({
    "projectID": "count",
    "Capacity": "sum"
}).rename(columns={"projectID": "Plants"}))

# Capacity by fuel type
print(df.groupby("Fueltype")["Capacity"].sum().sort_values(ascending=False))

# Filter specific technologies
solar = df[df["Fueltype"] == "Solar"]
hydro_storage = df[df["Technology"] == "Pumped Storage"]
```

## Next Steps

- [Configuration Guide](configuration.md) - Customize processing options
- [CLI Reference](../user-guide/cli.md) - Full command-line options
- [Python API](../user-guide/python-api.md) - Advanced Python usage
- [Caching](../user-guide/caching.md) - Understand the caching system

# Data Output

This guide explains the output format and data quality of OSM Power Plants.

## Output Columns

### Standard Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `projectID` | string | Unique identifier based on OSM element | `OSM_plant:way/123456` |
| `Name` | string | Power plant name (may be empty) | `Solar Farm Alpha` |
| `Country` | string | Full country name | `Chile` |
| `lat` | float | Latitude (WGS84) | `-33.4569` |
| `lon` | float | Longitude (WGS84) | `-70.6483` |
| `Fueltype` | string | Primary fuel type | `Solar` |
| `Technology` | string | Generation technology | `PV` |
| `Set` | string | Plant category | `PP` |
| `Capacity` | float | Electrical capacity in MW | `150.5` |
| `DateIn` | int | Commissioning year | `2020` |

### Project ID Format

The `projectID` follows this pattern:

```bash
OSM_plant:{element_type}/{osm_id}
```

Examples:

- `OSM_plant:node/123456` - Point element
- `OSM_plant:way/789012` - Area element
- `OSM_plant:relation/345678` - Complex relation

## Valid Values

### Fuel Types

| Fueltype | Description |
|----------|-------------|
| `Nuclear` | Nuclear power |
| `Hydro` | Hydroelectric |
| `Wind` | Wind power |
| `Solar` | Solar power |
| `Natural Gas` | Gas-fired |
| `Hard Coal` | Hard coal |
| `Lignite` | Brown coal |
| `Oil` | Oil-fired |
| `Solid Biomass` | Biomass |
| `Biogas` | Biogas |
| `Geothermal` | Geothermal |
| `Waste` | Waste-to-energy |
| `Other` | Marine, tidal, etc. |

### Technologies

| Technology | Typical Fueltypes |
|------------|-------------------|
| `PV` | Solar |
| `CSP` | Solar |
| `Onshore` | Wind |
| `Offshore` | Wind |
| `Run-Of-River` | Hydro |
| `Reservoir` | Hydro |
| `Pumped Storage` | Hydro |
| `Steam Turbine` | Coal, Nuclear, Biomass |
| `CCGT` | Natural Gas |
| `OCGT` | Natural Gas, Oil |
| `Combustion Engine` | Gas, Oil, Biogas |
| `Marine` | Tidal, Wave |

### Set Types

| Set | Description | Typical Technologies |
|-----|-------------|---------------------|
| `PP` | Power Plant | PV, Onshore, Run-Of-River, Steam Turbine |
| `Store` | Storage | Reservoir, Pumped Storage |
| `CHP` | Combined Heat & Power | (Not yet implemented) |

## Data Quality

### Capacity Sources

Capacity values come from different sources, in order of priority:

1. **Direct tag**: `plant:output:electricity` or `generator:output:electricity`
2. **Aggregated**: Sum of generator capacities within a plant relation
3. **Estimated**: Based on area (for solar) when enabled

### Missing Data

Some fields may be missing:

```python
import pandas as pd

df = pd.read_csv("output.csv")

# Check missing values
print(df.isnull().sum())

# Filter plants with capacity
df_with_capacity = df[df["Capacity"].notna()]

# Filter plants with names
df_named = df[df["Name"].notna() & (df["Name"] != "")]
```

### Rejection Statistics

During processing, the system tracks rejected elements:

```bash
Rejection Summary:
Total rejections: 333
----------------------------------------
Capacity placeholder value: 155 (46.5%)
Missing output tag: 127 (38.1%)
Missing technology tag: 27 (8.1%)
Missing source tag: 10 (3.0%)
```

Common rejection reasons:

| Reason | Description |
|--------|-------------|
| `Capacity placeholder value` | Capacity tag exists but has no real value |
| `Missing output tag` | No capacity information available |
| `Missing technology tag` | Cannot determine generation technology |
| `Missing source tag` | Cannot determine fuel type |
| `Within existing plant` | Generator already counted in plant |

## Export Formats

### CSV (Default)

```python
df.to_csv("output.csv", index=False)
```

### GeoJSON

```python
from osm_powerplants import Units

units = Units(unit_list)
units.save_geojson_report("output.geojson")
```

Output structure:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-70.66, -33.45]
      },
      "properties": {
        "name": "Solar Farm",
        "capacity_mw": 50.0,
        "fuel_type": "Solar"
      }
    }
  ]
}
```

### Excel

```python
df.to_excel("output.xlsx", index=False)
```

### Parquet

```python
df.to_parquet("output.parquet", index=False)
```

## Data Validation

### Checking Data Quality

```python
import pandas as pd

df = pd.read_csv("output.csv")

# Basic stats
print(f"Total plants: {len(df)}")
print(f"Total capacity: {df['Capacity'].sum():,.0f} MW")
print(f"Plants with capacity: {df['Capacity'].notna().sum()}")
print(f"Capacity coverage: {df['Capacity'].notna().mean():.1%}")

# By country
print(df.groupby("Country").agg({
    "projectID": "count",
    "Capacity": ["sum", "count"]
}))

# Check for duplicates
duplicates = df[df.duplicated(subset=["projectID"], keep=False)]
print(f"Duplicate IDs: {len(duplicates)}")
```

### Coordinate Validation

```python
# Check coordinate bounds
invalid_coords = df[
    (df["lat"] < -90) | (df["lat"] > 90) |
    (df["lon"] < -180) | (df["lon"] > 180)
]
print(f"Invalid coordinates: {len(invalid_coords)}")

# Check coordinates match country (rough check)
# This would require additional geocoding verification
```

## Comparison with Other Sources

The output format is compatible with [powerplantmatching](https://github.com/pypsa/powerplantmatching) and can be compared with:

- ENTSO-E data
- Global Power Plant Database
- National energy statistics

```python
# Example: Compare total capacity by fuel type
osm = pd.read_csv("osm_germany.csv")
reference = pd.read_csv("entsoe_germany.csv")

osm_totals = osm.groupby("Fueltype")["Capacity"].sum()
ref_totals = reference.groupby("Fueltype")["Capacity"].sum()

comparison = pd.DataFrame({
    "OSM": osm_totals,
    "Reference": ref_totals
})
comparison["Diff_%"] = (comparison["OSM"] / comparison["Reference"] - 1) * 100
print(comparison)
```

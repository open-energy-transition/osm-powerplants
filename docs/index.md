# OSM Power Plants

**Extract and process power plant data from OpenStreetMap**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## Overview

OSM Power Plants is a Python package for extracting, processing, and standardizing power plant data from [OpenStreetMap](https://www.openstreetmap.org/). It provides:

- **Comprehensive extraction** of power plants and generators from OSM
- **Intelligent parsing** of capacity, fuel type, technology, and commissioning dates
- **Multi-level caching** for efficient repeated queries
- **Data standardization** compatible with [powerplantmatching](https://github.com/pypsa/powerplantmatching)

## Quick Example

```python
from osm_powerplants import process_countries_simple, get_config, get_cache_dir

# Load configuration
config = get_config()
cache_dir = get_cache_dir(config)

# Process power plants for Chile and Greece
df = process_countries_simple(
    countries=["Chile", "Greece"],
    config=config,
    cache_dir=str(cache_dir),
    output_path="power_plants.csv",
)

print(f"Found {len(df)} power plants")
print(df.groupby("Fueltype")["Capacity"].sum())
```

Or use the CLI:

```bash
osm-powerplants process Chile Greece -o power_plants.csv
```

## Key Features

<!-- markdownlint-disable MD033 -->
<div class="grid cards" markdown>
<!-- markdownlint-enable MD033 -->

- :material-lightning-bolt:{ .lg .middle } **Fast Processing**

    ---

    Multi-level caching (API, units, CSV) enables rapid repeated queries

- :material-database:{ .lg .middle } **Rich Data**

    ---

    Extracts capacity, fuel type, technology, location, and commissioning dates

- :material-earth:{ .lg .middle } **Global Coverage**

    ---

    Process any country using ISO codes or full names

- :material-puzzle:{ .lg .middle } **PPM Compatible**

    ---

    Output format matches powerplantmatching for easy integration

</div>

## Data Output

The package produces standardized CSV output with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `projectID` | Unique identifier | `OSM_plant:way/123456` |
| `Name` | Power plant name | `Solar Farm Alpha` |
| `Country` | Country name | `Chile` |
| `lat`, `lon` | Coordinates | `-33.45`, `-70.66` |
| `Fueltype` | Primary fuel | `Solar`, `Wind`, `Hydro` |
| `Technology` | Generation technology | `PV`, `Onshore`, `Run-Of-River` |
| `Set` | Plant type | `PP`, `Store`, `CHP` |
| `Capacity` | Capacity in MW | `150.5` |
| `DateIn` | Commissioning year | `2020` |

## Installation

```bash
pip install osm-powerplants
```

See the [Installation Guide](getting-started/installation.md) for detailed instructions.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/open-energy-transition/osm-powerplants/blob/main/LICENSE) file for details.

## Acknowledgments

- Data sourced from [OpenStreetMap](https://www.openstreetmap.org/) contributors
- Inspired by [powerplantmatching](https://github.com/pypsa/powerplantmatching)
- Developed by [Open Energy Transition](https://openenergytransition.org/)

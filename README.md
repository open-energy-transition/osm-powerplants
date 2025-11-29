# OSM Power Plants

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**Extract and process power plant data from OpenStreetMap**

OSM Power Plants is a Python package for extracting, processing, and standardizing power plant data from [OpenStreetMap](https://www.openstreetmap.org/). It provides comprehensive extraction of power plants with intelligent parsing of capacity, fuel type, technology, and commissioning dates.

## Features

- 🌍 **Global Coverage**: Process any country using ISO codes or full names
- ⚡ **Fast Processing**: Multi-level caching for rapid repeated queries
- 📊 **Rich Data**: Extracts capacity, fuel type, technology, location, and dates
- 🔧 **Configurable**: Extensive YAML configuration for customization
- 🔌 **PPM Compatible**: Output format matches [powerplantmatching](https://github.com/pypsa/powerplantmatching)

## Installation

```bash
pip install osm-powerplants
```

## Quick Start

### Command Line

```bash
# Process countries and save to CSV
osm-powerplants process Germany France -o europe.csv

# Show configuration info
osm-powerplants info
```

### Python API

```python
from osm_powerplants import process_countries_simple, get_config, get_cache_dir

config = get_config()
cache_dir = get_cache_dir(config)

df = process_countries_simple(
    countries=["Chile", "Greece"],
    config=config,
    cache_dir=str(cache_dir),
    output_path="power_plants.csv",
)

print(f"Found {len(df)} power plants")
print(df.groupby("Fueltype")["Capacity"].sum())
```

## Output Format

| Column | Description | Example |
|--------|-------------|---------|
| `projectID` | Unique identifier | `OSM_plant:way/123456` |
| `Name` | Power plant name | `Solar Farm Alpha` |
| `Country` | Country name | `Chile` |
| `lat`, `lon` | Coordinates | `-33.45`, `-70.66` |
| `Fueltype` | Primary fuel | `Solar`, `Wind`, `Hydro` |
| `Technology` | Generation technology | `PV`, `Onshore`, `Run-Of-River` |
| `Set` | Plant type | `PP`, `Store` |
| `Capacity` | Capacity in MW | `150.5` |
| `DateIn` | Commissioning year | `2020` |

## Supported Fuel Types

Nuclear, Hydro, Wind, Solar, Natural Gas, Hard Coal, Lignite, Oil, Solid Biomass, Biogas, Geothermal, Waste, Other

## Documentation

Full documentation available at: <https://open-energy-transition.github.io/osm-powerplants>

- [Installation Guide](https://open-energy-transition.github.io/osm-powerplants/getting-started/installation/)
- [Quick Start](https://open-energy-transition.github.io/osm-powerplants/getting-started/quickstart/)
- [Configuration](https://open-energy-transition.github.io/osm-powerplants/getting-started/configuration/)
- [CLI Reference](https://open-energy-transition.github.io/osm-powerplants/user-guide/cli/)
- [Python API](https://open-energy-transition.github.io/osm-powerplants/user-guide/python-api/)

## Integration with powerplantmatching

OSM Power Plants can be used standalone or integrated with powerplantmatching:

```yaml
# powerplantmatching config.yaml
OSM:
  url: https://raw.githubusercontent.com/open-energy-transition/osm-powerplants/main/osm_data.csv
  fn: osm_data.csv
  reliability_score: 3
```

## Development

```bash
# Clone repository
git clone https://github.com/open-energy-transition/osm-powerplants.git
cd osm-powerplants

# Create virtual environment
uv venv .venv
source .venv/bin/activate

# Install with development dependencies
pip install -e ".[dev,docs]"

# Set up pre-commit hooks
pre-commit install

# Run tests
pytest

# Build documentation
mkdocs serve
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Data sourced from [OpenStreetMap](https://www.openstreetmap.org/) contributors
- Inspired by [powerplantmatching](https://github.com/pypsa/powerplantmatching)
- Developed by [Open Energy Transition](https://openenergytransition.org/)

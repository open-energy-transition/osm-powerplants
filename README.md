# OSM Power Plants

[![CI](https://github.com/open-energy-transition/osm-powerplants/actions/workflows/ci.yml/badge.svg)](https://github.com/open-energy-transition/osm-powerplants/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/osm-powerplants.svg)](https://badge.fury.io/py/osm-powerplants)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Extract power plant data from OpenStreetMap for energy system modeling.

## Installation

```bash
pip install osm-powerplants
```

## Quick Start

### Command Line

```bash
osm-powerplants process Germany France -o europe.csv
```

### Python API

```python
from osm_powerplants import process_units, get_config, get_cache_dir

df = process_units(
    countries=["Chile", "Greece"],
    config=get_config(),
    cache_dir=str(get_cache_dir(get_config())),
)
```

## Output Format

| Column | Description |
|--------|-------------|
| `projectID` | OSM-based identifier |
| `Name` | Plant name |
| `Country` | Country name |
| `lat`, `lon` | Coordinates |
| `Fueltype` | Solar, Wind, Hydro, Nuclear, Natural Gas, etc. |
| `Technology` | PV, Onshore, Run-Of-River, Steam Turbine, etc. |
| `Set` | PP (power plant), Store (storage) |
| `Capacity` | MW |
| `DateIn` | Commissioning year |

## Documentation

Full documentation: <https://open-energy-transition.github.io/osm-powerplants>

## Integration with powerplantmatching

This package provides OSM data for [powerplantmatching](https://github.com/PyPSA/powerplantmatching). The generated `osm_europe.csv` is automatically updated and consumed by powerplantmatching's matching pipeline.

## Development

```bash
git clone https://github.com/open-energy-transition/osm-powerplants.git
cd osm-powerplants
pip install -e ".[dev]"
pre-commit install
pytest
```

## Acknowledgments

This project is developed and maintained by [Open Energy Transition](https://openenergytransition.org/), a company dedicated to accelerating the global energy transition through open-source tools and data.

## License

MIT License - see [LICENSE](LICENSE) for details.

Data sourced from [OpenStreetMap](https://www.openstreetmap.org/) © OpenStreetMap contributors.

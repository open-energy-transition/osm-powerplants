# OSM Power Plants

[![CI](https://github.com/open-energy-transition/osm-powerplants/actions/workflows/ci.yml/badge.svg)](https://github.com/open-energy-transition/osm-powerplants/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Extract power plant data from OpenStreetMap.

## Installation

```bash
pip install osm-powerplants
```

## Quick Start

```bash
osm-powerplants process Germany France -o europe.csv
```

```python
from osm_powerplants import process_countries_simple, get_config, get_cache_dir

df = process_countries_simple(
    countries=["Chile", "Greece"],
    config=get_config(),
    cache_dir=str(get_cache_dir(get_config())),
)
```

## Output

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

Full docs: <https://open-energy-transition.github.io/osm-powerplants>

## Integration with powerplantmatching

This package provides OSM data for [powerplantmatching](https://github.com/PyPSA/powerplantmatching). The generated `osm_europe.csv` is automatically updated weekly and consumed by powerplantmatching's matching pipeline.

## Development

```bash
git clone https://github.com/open-energy-transition/osm-powerplants.git
cd osm-powerplants
pip install -e ".[dev]"
pre-commit install
pytest
```

## License

MIT License. Data from [OpenStreetMap](https://www.openstreetmap.org/) contributors.

Developed by [Open Energy Transition](https://openenergytransition.org/).

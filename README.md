# OSM Power Plants

[![CI](https://github.com/open-energy-transition/osm-powerplants/actions/workflows/ci.yml/badge.svg)](https://github.com/open-energy-transition/osm-powerplants/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/osm-powerplants.svg)](https://badge.fury.io/py/osm-powerplants)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Two tools in one package:

1. **Collect and parse** OpenStreetMap power-plant data into a clean, modelling-ready table (Fueltype, Technology, Capacity, coordinates…).
2. **Triage the OSM dataset itself** — every element that couldn't be resolved is emitted as a rejection report (CSV + GeoJSON), with a reason code and an OSM URL so contributors can fix the underlying tags.

## Installation

```bash
pip install osm-powerplants
```

## Extract plants

```bash
osm-powerplants process Germany France -o europe.csv
```

```python
from osm_powerplants import process_units, get_config, get_cache_dir

config = get_config()
df = process_units(
    countries=["Chile", "Greece"],
    config=config,
    cache_dir=str(get_cache_dir(config)),
    output_path="plants.csv",
)
```

## Triage OSM tags

`process_units` can also emit a rejection report that pinpoints what OSM needs in order to cover a country more completely:

```python
df = process_units(
    countries=["Kenya"],
    config={**config, "force_refresh": True},  # rejection data is only populated on API fetches
    cache_dir=str(get_cache_dir(config)),
    output_path="kenya.csv",
    rejected_output_path="kenya_rejected.csv",  # writes CSV + sibling .geojson
)
```

Every dropped element is recorded with its OSM URL, coordinates, and a reason code. The sibling `.geojson` loads straight into JOSM or QGIS as a triage layer. Dominant reasons:

| Reason | What it means |
|---|---|
| `Missing output tag` | Plant has `power=plant` but no `plant:output:electricity`. Very common on solar/geothermal farms. |
| `Capacity placeholder value` | Tag is a stub like `yes` instead of a number. |
| `Capacity regex no match` / `Capacity non-numeric` | Tag exists but cannot be parsed (unusual units, free-form text). |
| `Missing source tag` / `Missing technology tag` | Cannot classify the plant — can be relaxed with `missing_technology_allowed: True`. |
| `Element within existing plant geometry` | Generator polygon lies inside an already-processed plant (deduplication). |

## Output format

| Column | Description |
|---|---|
| `projectID` | OSM-based identifier |
| `Name` | Plant name |
| `Country` | Country name |
| `lat`, `lon` | WGS84 coordinates |
| `Fueltype` | Solar, Wind, Hydro, Nuclear, Natural Gas, etc. |
| `Technology` | PV, Onshore, Run-Of-River, Steam Turbine, etc. |
| `Set` | PP (power plant), Store (storage), CHP |
| `Capacity` | MW |
| `DateIn` | Commissioning year |

## Documentation

Full documentation: <https://open-energy-transition.github.io/osm-powerplants>

## Development

```bash
git clone https://github.com/open-energy-transition/osm-powerplants.git
cd osm-powerplants
pip install -e ".[dev]"
pre-commit install
pytest
```

## Acknowledgments

Developed and maintained by [Open Energy Transition](https://openenergytransition.org/).

## License

MIT License — see [LICENSE](LICENSE) for details.

Data sourced from [OpenStreetMap](https://www.openstreetmap.org/) © OpenStreetMap contributors.

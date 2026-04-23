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

## Why some plants are excluded

OSM is a crowd-sourced dataset, and many `power=plant` elements lack the
metadata needed to plug them into an energy system model. Every OSM
element that cannot be resolved into a usable unit is dropped from the
output and recorded in a rejection report. The dominant reasons are:

| Reason | What it means |
|---|---|
| `Missing output tag` | Plant has `power=plant` but no `plant:output:electricity` (and no source-specific capacity-estimation default in `config.yaml`). Very common on solar and geothermal farms. |
| `Capacity placeholder value` | `plant:output:electricity` is set to a stub like `yes` instead of a number. |
| `Capacity regex no match` / `Capacity non-numeric` | Capacity tag exists but cannot be parsed (unusual units, free-form text). |
| `Missing source tag` / `Missing technology tag` | Cannot classify the plant — these can be relaxed with `missing_technology_allowed: True` in config. |
| `Element within existing plant geometry` | A generator polygon lies inside an already-processed plant boundary (deduplication). |

If a country returns fewer plants than you expected from `overpass-turbo`,
set `rejected_output_path` to see exactly what was dropped and why:

```python
config = get_config()
config["force_refresh"] = True  # rejection data is only populated on API fetches

df = process_units(
    countries=["Kenya"],
    config=config,
    cache_dir=str(get_cache_dir(config)),
    output_path="kenya.csv",
    rejected_output_path="kenya_rejected.csv",  # writes CSV + .geojson
)
```

The CSV lists each rejection with the OSM URL, coordinates, and reason
code; the sibling GeoJSON can be loaded in JOSM or QGIS so OSM
contributors can triage the gaps directly.

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

## Global dataset

A ready-to-use global dataset, regenerated monthly by CI, lives at the repo root:

- [`osm_global.csv`](osm_global.csv) — merged plants for all 16 regions (~250 countries).
- [`osm_global_rejected_plants.csv`](osm_global_rejected_plants.csv) — features dropped by quality filters, with reason and coordinates.
- [`osm_global_rejected_plants.geojson`](osm_global_rejected_plants.geojson) — the same rejections as mappable points for OSM-contributor triage.

Per-region outputs (one triplet per region) live under [`datasets/`](datasets/). Region definitions are in [`src/osm_powerplants/regions.py`](src/osm_powerplants/regions.py).

The CI workflow ([`.github/workflows/data.yml`](.github/workflows/data.yml)) runs on the 1st of each month: one parallel job per region (uploads artifacts) followed by a merge job that commits the global outputs.

Local regeneration:
```bash
python scripts/extract_region.py --region europe --clear-cache
python scripts/merge_global.py
```

## Integration with powerplantmatching

This package provides OSM data for [powerplantmatching](https://github.com/PyPSA/powerplantmatching). `osm_global.csv` is consumed by PPM's matching pipeline. The evaluation that selected which countries should include OSM by default lives in [`evaluation/`](evaluation/) — see [`evaluation/osm_global_report.md`](evaluation/osm_global_report.md) for the methodology and findings.

> The legacy `osm_europe.csv` at the repo root is frozen: it is retained only while the current PPM config still points to it and will be removed after the PPM PR that re-points to `osm_global.csv` merges.

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

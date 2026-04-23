# OSM Power Plants

Two tools in one package:

1. **Collect and parse** OpenStreetMap power-plant data into a clean, modelling-ready table.
2. **Triage the OSM dataset itself** — every element that couldn't be resolved is emitted as a rejection report (CSV + GeoJSON) with a reason code and an OSM URL so contributors can fix the underlying tags.

## Quick Start

```bash
pip install osm-powerplants
osm-powerplants process Germany France -o plants.csv
```

```python
from osm_powerplants import process_units, get_config, get_cache_dir

config = get_config()
df = process_units(
    countries=["Chile", "Greece"],
    config=config,
    cache_dir=str(get_cache_dir(config)),
    output_path="plants.csv",
    rejected_output_path="plants_rejected.csv",  # optional — see Quality Tracking
)
```

## Output

| Column | Description |
|---|---|
| `projectID` | OSM-based identifier |
| `Name` | Plant name |
| `Country` | Country name |
| `lat`, `lon` | WGS84 coordinates |
| `Fueltype` | Solar, Wind, Hydro, Nuclear, Natural Gas, etc. |
| `Technology` | PV, Onshore, Run-Of-River, Steam Turbine, etc. |
| `Set` | PP, Store, CHP |
| `Capacity` | MW |
| `DateIn` | Commissioning year |

## Where to go next

- [Installation](getting-started/installation.md)
- [Quick Start](getting-started/quickstart.md)
- [Configuration](getting-started/configuration.md)
- [Quality Tracking](user-guide/quality-tracking.md) — the rejection-report half of the package
- [Python API](user-guide/python-api.md)
- [CLI Reference](user-guide/cli.md)

## License

MIT License. Data from [OpenStreetMap](https://www.openstreetmap.org/) contributors.

# OSM Power Plants

Extract power plant data from OpenStreetMap.

## Quick Start

```bash
pip install osm-powerplants
osm-powerplants process Germany France -o plants.csv
```

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

- [Installation](getting-started/installation.md)
- [Quick Start](getting-started/quickstart.md)
- [Configuration](getting-started/configuration.md)
- [CLI Reference](user-guide/cli.md)
- [Python API](user-guide/python-api.md)

## License

MIT License. Data from [OpenStreetMap](https://www.openstreetmap.org/) contributors.

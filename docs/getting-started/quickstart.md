# Quick Start

## File locations

```bash
osm-powerplants info
```

| Item | Linux | macOS | Windows |
|---|---|---|---|
| Config | `~/.config/osm-powerplants/` | `~/Library/Application Support/osm-powerplants/` | `%APPDATA%\osm-powerplants\` |
| Cache | `~/.cache/osm-powerplants/` | `~/Library/Caches/osm-powerplants/` | `%LOCALAPPDATA%\osm-powerplants\Cache\` |

## CLI

```bash
osm-powerplants process Germany France -o europe.csv
osm-powerplants process Chile --force-refresh -o chile.csv
```

## Python — extract plants

```python
from osm_powerplants import process_units, get_config, get_cache_dir

config = get_config()
df = process_units(
    countries=["Chile", "Greece"],
    config=config,
    cache_dir=str(get_cache_dir(config)),
    output_path="plants.csv",
)

print(df.groupby("Fueltype")["Capacity"].sum())
```

## Python — capture rejected elements

Pass `rejected_output_path` to get a CSV + sibling GeoJSON listing every
OSM element that was dropped and why. Useful for diagnosing why a
country came back short and for feeding triage targets back to OSM.

```python
config = get_config()
config["force_refresh"] = True  # rejection data only populated on API fetches

df = process_units(
    countries=["Kenya"],
    config=config,
    cache_dir=str(get_cache_dir(config)),
    output_path="kenya.csv",
    rejected_output_path="kenya_rejected.csv",  # also writes kenya_rejected.geojson
)
```

See the [Quality Tracking](../user-guide/quality-tracking.md) guide for
the list of reason codes and how to analyse the report.

## Valid values

**Fuel Types**: Nuclear, Hydro, Wind, Solar, Natural Gas, Hard Coal, Lignite, Oil, Solid Biomass, Biogas, Geothermal, Waste, Other

**Technologies**: PV, CSP, Onshore, Offshore, Run-Of-River, Reservoir, Pumped Storage, Steam Turbine, CCGT, OCGT, Combustion Engine, Marine

**Set Types**: PP (power plant), Store (storage), CHP (combined heat & power)

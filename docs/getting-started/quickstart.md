# Quick Start

## File Locations

```bash
osm-powerplants info
```

| Item | Linux | macOS | Windows |
|------|-------|-------|---------|
| Config | `~/.config/osm-powerplants/` | `~/Library/Application Support/osm-powerplants/` | `%APPDATA%\osm-powerplants\` |
| Cache | `~/.cache/osm-powerplants/` | `~/Library/Caches/osm-powerplants/` | `%LOCALAPPDATA%\osm-powerplants\Cache\` |

## CLI

```bash
osm-powerplants process Germany France -o europe.csv
osm-powerplants process Chile --force-refresh -o chile.csv
```

## Python

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

## Valid Values

**Fuel Types**: Nuclear, Hydro, Wind, Solar, Natural Gas, Hard Coal, Lignite, Oil, Solid Biomass, Biogas, Geothermal, Waste, Other

**Technologies**: PV, CSP, Onshore, Offshore, Run-Of-River, Reservoir, Pumped Storage, Steam Turbine, CCGT, OCGT, Combustion Engine, Marine

**Set Types**: PP (power plant), Store (storage), CHP (combined heat & power)

# Configuration

OSM Power Plants uses a YAML configuration file to control processing behavior.

## Configuration File Location

The package searches for `config.yaml` in the following order:

1. Project root directory (for development)
2. User config directory (`~/.config/osm-powerplants/config.yaml`)
3. Package directory (bundled defaults)

You can also specify a custom config file:

```bash
osm-powerplants process Germany -c /path/to/my-config.yaml
```

```python
from osm_powerplants import get_config
config = get_config("/path/to/my-config.yaml")
```

## Configuration Options

### Global Settings

```yaml
# Cache directory (null = auto-detect based on OS)
cache_dir: null
# cache_dir: /custom/path/to/cache

# Force re-download from API (ignore cache)
force_refresh: false

# Only process power=plant elements (skip generators)
plants_only: true

# Allow plants without names
missing_name_allowed: true

# Allow plants without technology tags
missing_technology_allowed: false

# Allow plants without start dates
missing_start_date_allowed: true
```

### Capacity Extraction

```yaml
capacity_extraction:
  enabled: true
  # Custom regex patterns (optional)
  # regex_patterns:
  #   - ^(\d+(?:\.\d+)?)([a-zA-Z]+(?:p|el|e)?)$
```

### Capacity Estimation

```yaml
capacity_estimation:
  enabled: false  # Estimate capacity from geometry
```

### Generator Clustering

```yaml
units_clustering:
  enabled: false  # Cluster nearby generators (solar/wind farms)
```

### Plant Reconstruction

```yaml
units_reconstruction:
  enabled: true  # Reconstruct plants from orphaned generators
  min_generators_for_reconstruction: 2
  name_similarity_threshold: 0.7
```

### Source Mapping

Maps OSM source tags to standardized fuel types:

```yaml
source_mapping:
  Nuclear: [nuclear, nuclear;oil]
  Solar: [solar, solar;battery, solar;wind]
  Wind: [wind, wind;solar]
  Hydro: [hydro, hydro;oil, hydro;solar]
  Natural Gas: [gas, gas;oil, gas;coal]
  Hard Coal: [coal, coal;gas, coal;biomass]
  # ... see full config for complete mapping
```

### Technology Mapping

Maps OSM technology tags to standardized technologies:

```yaml
technology_mapping:
  PV: [photovoltaic, solar_photovoltaic_panel, ground_mounted]
  Onshore: [horizontal_axis, vertical_axis, wind_turbine]
  Run-Of-River: [run-of-the-river, stream, francis_turbine]
  Reservoir: [water-storage, barrage]
  Pumped Storage: [water-pumped-storage]
  Steam Turbine: [steam_turbine, thermal, boiler]
  CCGT: [combined_cycle, ccpp]
  OCGT: [gas_turbine, open_cycle]
  # ... see full config for complete mapping
```

### Set Mapping

Maps technologies to plant types (PP, Store, CHP):

```yaml
set_mapping:
  Store:
    - Reservoir
    - Pumped Storage
    - Marine
  PP:
    - PV
    - CSP
    - Onshore
    - Offshore
    - Run-Of-River
    - Combustion Engine
    - OCGT
    - CCGT
    - Steam Turbine
  CHP: []  # Not implemented yet
```

### Source-Specific Configuration

Override settings for specific fuel types:

```yaml
sources:
  Solar:
    units_clustering:
      method: dbscan
      eps: 0.005
      min_samples: 2
    capacity_estimation:
      method: area_based
      efficiency: 150  # W/m²
  Wind:
    units_clustering:
      method: dbscan
      eps: 0.02
      min_samples: 2
```

### Overpass API Settings

```yaml
overpass_api:
  api_url: https://overpass-api.de/api/interpreter
  timeout: 1200  # seconds
  max_retries: 3
  retry_delay: 60  # seconds
  cache_size_gb: 12
  show_progress: true
```

### Omitted Countries

Countries that cannot be queried via Overpass API:

```yaml
omitted_countries: ["Kosovo"]
```

## Example: Custom Configuration

Create a minimal custom config for solar-only processing:

```yaml
# solar-only.yaml
force_refresh: false
plants_only: true
missing_technology_allowed: false

# Only keep solar-related sources
source_mapping:
  Solar: [solar, solar;battery, photovoltaic]

technology_mapping:
  PV: [photovoltaic, solar_photovoltaic_panel]
  CSP: [solar_thermal_collector]

overpass_api:
  timeout: 600
  show_progress: true
```

Use it:

```bash
osm-powerplants process Spain -c solar-only.yaml -o spain_solar.csv
```

## Environment Variables

Currently, no environment variables are supported. All configuration is done via the YAML file.

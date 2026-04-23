# Configuration

Config file location: `~/.config/osm-powerplants/config.yaml` (the package ships a default at `src/osm_powerplants/config.yaml`).

## Main options

```yaml
force_refresh: false          # Ignore cache, re-download
plants_only: true             # Skip standalone generators
missing_name_allowed: true    # Accept unnamed plants
missing_technology_allowed: true
missing_start_date_allowed: true
```

Relaxing a `missing_*_allowed` flag keeps plants in the output that would otherwise be rejected for that reason. Tighten them when you want a stricter dataset plus a richer rejection report (see [Quality Tracking](../user-guide/quality-tracking.md)).

## Capacity extraction

```yaml
capacity_extraction:
  enabled: true

capacity_estimation:
  enabled: false   # Estimate MW from geometry (e.g. solar area)
```

## Clustering & reconstruction

```yaml
units_clustering:
  enabled: false   # Group nearby generators

units_reconstruction:
  enabled: true    # Rebuild plants from orphaned generators
  min_generators_for_reconstruction: 2
  name_similarity_threshold: 0.7
```

## Source & technology mapping

Map OSM tag values to the package's standardized fuel/technology vocabulary:

```yaml
source_mapping:
  Solar: [solar, solar;battery, photovoltaic]
  Wind: [wind, wind;solar]
  Hydro: [hydro, hydro;oil, water]
  Natural Gas: [gas, gas;oil]
  # ... see config.yaml for the full list

technology_mapping:
  PV: [photovoltaic, solar_photovoltaic_panel]
  Onshore: [horizontal_axis, wind_turbine]
  Run-Of-River: [run-of-the-river, francis_turbine]
  # ...
```

Unknown tag values surface as `Missing source type` / `Missing technology type` rejections — a cue to either extend the mapping or fix the tag upstream in OSM.

## Overpass API

```yaml
overpass_api:
  api_url: https://overpass.private.coffee/api/interpreter
  timeout: 1800
  max_retries: 3
  retry_delay: 90
  cache_size_gb: 12
  show_progress: true
```

Every request carries an explicit `osm-powerplants/<version>` User-Agent header — public Overpass instances reject the default `python-requests/X` UA with HTTP 406.

## Omitted countries

```yaml
omitted_countries: ["Kosovo"]   # Not queryable via Overpass
```

## Custom config

```bash
osm-powerplants process Spain -c my-config.yaml -o spain.csv
```

```python
config = get_config("/path/to/my-config.yaml")
```

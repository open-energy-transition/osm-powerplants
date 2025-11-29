# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial release of osm-powerplants as standalone package
- CLI with `process` and `info` commands
- Python API for programmatic access
- Multi-level caching (CSV, Units, API)
- Plant reconstruction from orphaned generators
- Generator clustering for solar/wind farms
- Configuration via YAML file
- Support for all countries via ISO codes or names
- Comprehensive documentation with MkDocs Material

### Changed

- Extracted from powerplantmatching OSM module
- Switched to platformdirs for cross-platform cache locations
- Simplified configuration structure

## [0.1.0] - 2024-XX-XX

### Added

- Initial public release
- Core processing pipeline
- Overpass API client with retry logic
- Rejection tracking system
- GeoJSON export support

### Dependencies

- pandas >= 2.0
- numpy >= 1.24
- requests >= 2.28
- pycountry >= 22.3
- shapely >= 2.0
- diskcache >= 5.6
- tqdm >= 4.65
- scikit-learn >= 1.2
- platformdirs >= 3.0
- pyyaml >= 6.0

---

## Migration from powerplantmatching

If you were using the OSM module from powerplantmatching, here's how to migrate:

### Before (powerplantmatching)

```python
from powerplantmatching.osm import process_countries
# or
import powerplantmatching as pm
df = pm.data.OSM()
```

### After (osm-powerplants)

```python
from osm_powerplants import process_countries_simple, get_config, get_cache_dir

config = get_config()
df = process_countries_simple(
    countries=["Germany"],
    config=config,
    cache_dir=str(get_cache_dir(config)),
)
```

### Key Differences

1. **Standalone package**: No longer requires powerplantmatching
2. **Separate configuration**: Uses its own `config.yaml`
3. **Different cache location**: Uses platformdirs for OS-appropriate paths
4. **Simplified API**: `process_countries_simple()` for common use cases

### powerplantmatching Integration

powerplantmatching can still use OSM data by downloading the pre-generated CSV:

```yaml
# powerplantmatching config.yaml
OSM:
  url: https://raw.githubusercontent.com/open-energy-transition/osm-powerplants/main/osm_data.csv
  fn: osm_data.csv
```

Then use as before:

```python
import powerplantmatching as pm
df = pm.data.OSM()
```

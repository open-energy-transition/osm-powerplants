# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/), [Semantic Versioning](https://semver.org/)

## [Unreleased]

### Added

- Initial release as standalone package
- CLI: `process` and `info` commands
- Multi-level caching (CSV, Units, API)
- Plant reconstruction from orphaned generators
- Generator clustering for solar/wind farms
- Cross-platform paths via platformdirs

## [0.1.0]

Initial public release.

---

## Migration from powerplantmatching

### Before

```python
from powerplantmatching.osm import process_countries
```

### After

```python
from osm_powerplants import process_units, get_config, get_cache_dir

df = process_units(
    countries=["Germany"],
    config=get_config(),
    cache_dir=str(get_cache_dir(get_config())),
)
```

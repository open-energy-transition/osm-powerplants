# Changelog

See [CHANGELOG.md](https://github.com/open-energy-transition/osm-powerplants/blob/main/CHANGELOG.md) for the full changelog.

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

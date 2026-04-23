# CLI Reference

## Commands

### process

```bash
osm-powerplants process <countries> [options]
```

| Option | Description |
|---|---|
| `-o`, `--output` | Output CSV path (default: `osm_data.csv`) |
| `-c`, `--config` | Custom config file |
| `--force-refresh` | Ignore all cache, re-download from API |
| `--update` | Reprocess from API cache (skip CSV cache) |

```bash
osm-powerplants process Germany -o germany.csv
osm-powerplants process France Spain Italy -o europe.csv
osm-powerplants process DE FR ES -o countries.csv          # ISO codes
osm-powerplants process "United States" -o usa.csv         # quotes for spaces
```

!!! note "Rejection reports"
    The CLI currently emits accepted plants only. To also capture the
    rejection report (CSV + GeoJSON of dropped OSM elements), use the
    Python API with `rejected_output_path` — see
    [Quality Tracking](quality-tracking.md).

### info

```bash
osm-powerplants info
```

Shows config file path, cache directory, and current settings.

### --version

```bash
osm-powerplants --version
```

## Country names

Accepts full names, ISO-2, ISO-3, and common variations. Invalid names
produce suggestions:

```
❌ 'Germny'
   ℹ️  Did you mean: 'Germany', 'Armenia'
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Error |

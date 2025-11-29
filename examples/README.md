# Examples

Short, focused examples demonstrating OSM Power Plants features.

## Quick Start

```bash
cd examples
python 01_basic_usage.py
```

## Examples

| # | File | Description |
|---|------|-------------|
| 1 | `01_basic_usage.py` | Extract data for a single country |
| 2 | `02_multiple_countries.py` | Process multiple countries, aggregate results |
| 3 | `03_configuration.py` | Customize processing options |
| 4 | `04_export_formats.py` | Export to CSV, JSON, GeoJSON |
| 5 | `05_rejection_analysis.py` | Track rejected elements for OSM quality |
| 6 | `06_regional_queries.py` | Query by bbox, radius, or polygon |
| 7 | `07_cache_management.py` | Understand caching behavior |
| 8 | `08_data_analysis.py` | Analyze data with pandas |
| 9 | `09_rejection_geojson.py` | Export rejections as GeoJSON for mapping tools |
| 10 | `10_rejection_keywords.py` | Analyze problematic tag values |

## Running All Examples

```bash
for f in *.py; do echo "=== $f ===" && python "$f" && echo; done
```

## Notes

- Examples use small countries (Malta, Luxembourg, Monaco) for fast execution
- First run downloads from Overpass API; subsequent runs use cache
- Output files are created in the current directory

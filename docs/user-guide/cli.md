# CLI Reference

The `osm-powerplants` command-line interface provides easy access to power plant extraction.

## Commands

### `process`

Process OSM data for one or more countries.

```bash
osm-powerplants process <countries> [options]
```

#### Arguments

| Argument | Description |
|----------|-------------|
| `countries` | One or more country names or ISO codes |

#### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output CSV file path | `osm_data.csv` |
| `--config` | `-c` | Path to configuration file | Auto-detect |
| `--force-refresh` | | Ignore cache, download fresh data | `false` |

#### Examples

```bash
# Single country
osm-powerplants process Germany -o germany.csv

# Multiple countries
osm-powerplants process France Spain Italy -o southern_europe.csv

# Using ISO codes
osm-powerplants process DE FR ES -o countries.csv

# Mixed formats
osm-powerplants process Germany FR "United States" -o mixed.csv

# Force refresh
osm-powerplants process Portugal --force-refresh -o portugal_fresh.csv

# Custom config
osm-powerplants process Austria -c custom.yaml -o austria.csv
```

### `info`

Display configuration and cache information.

```bash
osm-powerplants info [options]
```

#### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--config` | `-c` | Path to configuration file |

#### Example

```bash
$ osm-powerplants info
Cache directory: /home/user/.cache/osm-powerplants
Config loaded: True
  - force_refresh: False
  - plants_only: True
```

### `--version`

Display version information.

```bash
$ osm-powerplants --version
osm-powerplants 0.1.0
```

### `--help`

Display help for any command.

```bash
osm-powerplants --help
osm-powerplants process --help
```

## Country Names

The CLI accepts various country name formats:

| Format | Example |
|--------|---------|
| Full name | `Germany`, `United States` |
| ISO 3166-1 alpha-2 | `DE`, `US` |
| ISO 3166-1 alpha-3 | `DEU`, `USA` |
| Common variations | `USA`, `UK`, `South Korea` |

### Handling Spaces

For countries with spaces, use quotes:

```bash
osm-powerplants process "United States" "United Kingdom" -o anglophone.csv
```

### Validation Errors

If a country name is invalid, the CLI provides helpful suggestions:

```bash
$ osm-powerplants process Germny
❌ Invalid country names detected: 1 out of 1 countries

Invalid entries:
  ❌ 'Germny'
     ℹ️  Did you mean: 'Germany', 'Armenia'

📝 Accepted formats:
  - Full name: 'Germany', 'United States'
  - ISO 3166-1 alpha-2: 'DE', 'US'
  - ISO 3166-1 alpha-3: 'DEU', 'USA'
  - Common names: 'USA', 'UK', 'South Korea'

⚠️  All countries must be valid before processing can begin.
```

## Output Format

The CLI outputs CSV files with the following columns:

```csv
projectID,Name,Country,lat,lon,Fueltype,Technology,Set,Capacity,DateIn
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (invalid arguments, processing failure, no data found) |

## Logging

The CLI outputs informative logs during processing:

```bash
2024-01-15 10:30:00 [INFO] Processing countries: ['Chile', 'Greece']
2024-01-15 10:30:00 [INFO] Cache directory: /home/user/.cache/osm-powerplants
2024-01-15 10:30:00 [INFO] ✅ Successfully validated all 2 countries
2024-01-15 10:30:05 [INFO] Fetching power plants for Chile
Downloading Chile: 100%|██████████| 966/966 [00:04<00:00, 207.88elements/s]
2024-01-15 10:30:25 [INFO] Processed 705 units for Chile
2024-01-15 10:30:50 [INFO] ✅ Successfully processed all 2 countries
2024-01-15 10:30:50 [INFO] Saved 785 power plants to output.csv
```

## Scripting Examples

### Batch Processing

```bash
#!/bin/bash
# process_europe.sh

COUNTRIES="Germany France Spain Italy Portugal Austria"
OUTPUT_DIR="./data"

mkdir -p $OUTPUT_DIR

for country in $COUNTRIES; do
    echo "Processing $country..."
    osm-powerplants process "$country" -o "$OUTPUT_DIR/${country,,}.csv"
done

echo "Done!"
```

### Combining with Other Tools

```bash
# Process and analyze
osm-powerplants process Germany -o germany.csv
cat germany.csv | csvstat  # requires csvkit

# Process and convert to JSON
osm-powerplants process Malta -o malta.csv
csvjson malta.csv > malta.json  # requires csvkit
```

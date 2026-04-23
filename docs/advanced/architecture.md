# Architecture

## Package structure

```
osm_powerplants/
├── cli.py           # Command-line interface
├── core.py          # Configuration, paths
├── interface.py     # High-level API (process_units, process_countries)
├── models.py        # Unit, Units, RejectionReason
├── workflow.py      # Processing orchestration
├── retrieval/       # Overpass API client, caching
├── parsing/         # OSM element → Unit
├── enhancement/     # Clustering, plant reconstruction
└── quality/         # RejectionTracker
```

## Data flow

```
Countries → Validate → Retrieve (cache/API) → Parse → Enhance → Validate → DataFrame
                                                   ↓
                                          RejectionTracker
```

1. **Validate** — check country names via `pycountry`.
2. **Retrieve** — walk the cache hierarchy, query Overpass when needed.
3. **Parse** — pull fuel type, technology, capacity from OSM tags.
4. **Enhance** — cluster nearby generators, reconstruct plants from orphaned generators.
5. **Validate** — ensure valid fuel types, technologies, sets.

Every element dropped along the way is recorded in the
`RejectionTracker`, which `process_units` can persist via
`rejected_output_path`.

## Key classes

- **`Unit`** — a single power plant with all attributes.
- **`Units`** — collection with filtering and export methods.
- **`Workflow`** — orchestrates the processing pipeline for a country.
- **`OverpassAPIClient`** — retries, caches, and talks to Overpass with an explicit User-Agent.
- **`RejectionTracker`** — records every failed element with a reason code; emits CSV and GeoJSON reports.

# Quality Tracking

OSM is crowd-sourced and uneven. Every `power=plant` element that
cannot be resolved into a usable unit — missing capacity, unparseable
tag, unknown source — is dropped from the output and recorded as a
rejection. You can surface those rejections alongside the accepted
plants to diagnose short results and to feed triage targets back to
OSM contributors.

## The easy path: `rejected_output_path`

`process_units` writes a CSV + sibling GeoJSON when `rejected_output_path`
is set. Rejection data is only populated on API fetches (cache hits
don't re-run the filter), so force a refresh when you need a full
report.

```python
from osm_powerplants import process_units, get_config, get_cache_dir

config = get_config()
config["force_refresh"] = True

df = process_units(
    countries=["Kenya"],
    config=config,
    cache_dir=str(get_cache_dir(config)),
    output_path="kenya.csv",
    rejected_output_path="kenya_rejected.csv",    # also writes kenya_rejected.geojson
)
```

The CSV lists each rejection with:

| Column | Description |
|---|---|
| `id` | `type/id` OSM identifier |
| `element_type` | `node`, `way`, `relation` |
| `country`, `lat`, `lon` | Location |
| `unit_type` | `plant` or `generator` |
| `reason` | One of the codes below |
| `keywords` | The offending tag value (e.g. `yes`, `photovoltaic`) |
| `details` | Free-text context (e.g. raw tag dict) |
| `url` | Direct link to the OSM element |

The GeoJSON has the same fields as feature properties and loads
directly into JOSM or QGIS as a triage layer.

## Rejection reasons

| Reason | What to fix in OSM |
|---|---|
| `Missing output tag` | Add `plant:output:electricity` (e.g. `50 MW`) |
| `Capacity placeholder value` | Replace stubs like `yes` with a real number |
| `Capacity regex no match` / `Capacity non-numeric` | Use a parseable format — number + unit |
| `Missing source tag` | Add `plant:source` |
| `Missing technology tag` | Add `plant:method` |
| `Missing source type` / `Missing technology type` | Extend `source_mapping` / `technology_mapping` in config, or normalise the OSM value |
| `Capacity placeholder value`, `Capacity zero` | Replace with an actual measurement |
| `Element within existing plant geometry` | Already counted — a generator polygon lies inside a parent plant |

## Analysis

```python
import pandas as pd

rej = pd.read_csv("kenya_rejected.csv")

# Top reasons
print(rej["reason"].value_counts())

# Plants only (filter out generators)
plants = rej[rej["unit_type"] == "plant"]
print(plants[["url", "reason", "details"]].head())
```

## Low-level: re-using a tracker

For custom pipelines, instantiate `RejectionTracker` directly and hand
it to a `Workflow`:

```python
from osm_powerplants import Units, get_config, get_cache_dir
from osm_powerplants.quality.rejection import RejectionTracker
from osm_powerplants.retrieval.client import OverpassAPIClient
from osm_powerplants.workflow import Workflow

config = get_config()
config["missing_name_allowed"] = False   # strict mode

tracker = RejectionTracker()
units = Units()

with OverpassAPIClient(cache_dir=str(get_cache_dir(config))) as client:
    workflow = Workflow(client, tracker, units, config)
    workflow.process_country_data("Malta")

print(tracker.get_summary_string())

# Slice by reason
from osm_powerplants.models import RejectionReason
missing = tracker.get_rejections_by_reason(RejectionReason.MISSING_OUTPUT_TAG)

# Export
tracker.generate_report().to_csv("rejections.csv", index=False)
tracker.save_geojson("rejections.geojson")
tracker.save_geojson_by_reasons("output/")   # one file per reason
```

## The feedback loop

```
osm-powerplants → rejection report → fix in JOSM → upload to OSM → re-run
       ↑                                                              │
       └──────────────────────────────────────────────────────────────┘
```

See the [Workshop](workshop.md) notebook for an end-to-end walkthrough.

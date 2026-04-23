# OSM contribution evaluation for powerplantmatching

This directory is a self-contained reviewer bundle for the report in [`osm_global_report.md`](osm_global_report.md) — the scripts and configs needed to regenerate the country-level OSM-contribution buckets that back the recommended powerplantmatching (PPM) config.

## Contents

| file | purpose |
|---|---|
| `osm_global_report.md` | Methodology, findings, and PR-ready recommendation. |
| `matching.py` | Runs PPM twice (with and without OSM) to measure OSM's delta. |
| `evaluate.py` | Classifies each country into five buckets against IRENA ELECSTAT. |
| `config.overlay.yaml` | Minimal PPM overlay used by `matching.py`. |
| `config.ppm_with_osm.yaml` | Recommended final PPM config — the proposed PR payload. |

Everything the extraction step needs lives in the repo root (`config.yaml`, `scripts/extract_region.py`, `scripts/merge_global.py`) because the monthly CI that refreshes `osm_global.csv` runs from there.

## Reproducing

```bash
# From the repo root:
uv venv .venv
uv pip install -e .
uv pip install powerplantmatching country_converter

# 1. Generate osm_global.csv (normally produced by the monthly CI in
#    .github/workflows/data.yml; this regenerates it locally)
for region in europe russia north_america central_america_caribbean \
              south_america northern_africa western_africa middle_africa \
              eastern_africa southern_africa western_asia central_asia \
              southern_asia southeastern_asia eastern_asia oceania; do
  .venv/bin/python scripts/extract_region.py --region "$region" --clear-cache
done
.venv/bin/python scripts/merge_global.py

# 2. Run PPM twice (~ 75 + 90 min on the reference machine)
.venv/bin/python evaluation/matching.py --countries all --skip osm_matching
.venv/bin/python evaluation/matching.py --countries all --skip no_osm

# 3. Classify countries into buckets → evaluation.csv + evaluation_by_fueltype.csv
.venv/bin/python evaluation/evaluate.py
```

Outputs land in `evaluation/matching/` (matched CSVs) and in `evaluation/` itself (`evaluation.csv`, `evaluation_by_fueltype.csv`).
Neither is committed — they're regenerated on demand.

For the numbers behind every table in the report, the evaluation CSVs are the source of truth after running step 3.

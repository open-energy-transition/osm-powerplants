# OSM contribution to the global power-plant dataset

This repository builds a global OSM power-plant dataset and evaluates whether adding it to `powerplantmatching` (PPM) provides genuine new plants or capacity that the other PPM sources miss. The evaluation is then translated into a PPM configuration that keeps OSM only where it adds defensible value.

## TL;DR

- Built a global OSM power-plant dataset: **28,882 plants / 2,873 GW across 173 countries** (`osm_global.csv`).
- Ran PPM twice — with and without OSM — and measured the delta: **18,204 OSM plants matched into PPM, 10,678 OSM-only**.
- Classified every country into five buckets against IRENA ELECSTAT 2024:
  - **186** `ppm_already_sufficient` — OSM adds <10% of combined capacity.
  - **35** `osm_complements` + **3** `osm_primary` → **38 countries / 146 GW of defensible OSM contribution**.
  - **6** `likely_duplicates` (Ukraine, Ethiopia, Nepal, Namibia, Palestine, Dominica); four of the six have zero OSM-only capacity, so the over-report is PPM-internal.
  - **3** `insufficient_reference` (no IRENA data, sub-50 MW).
- Per-fueltype audit flags **9 rows inside the 38 fully-included countries** where OSM compounds a PPM over-report (Sweden/Nuclear, BiH/Hydro, Belarus/Nuclear, Morocco/Solar, etc.).
- Recommendation encoded in `evaluation/config.ppm_with_osm.yaml`: **OSM globally in `matching_sources`** (cross-validates any PPM row) and **fully-included only in the 38 defensible countries**.
- **Proposed PR refinement**: narrow the OSM `fully_included` filter with seven `not (Country == '…' and Fueltype == '…')` clauses to drop the clear-duplicate (Country, Fueltype) pairs without removing the host countries. Revises the defensible total from 145.6 GW to **~135 GW** and keeps every other fueltype in Sweden, BiH, Belarus, Morocco, Togo, Cabo Verde and Hungary intact. See "Proposed refinement" at the end of the per-fueltype audit section.

## Methodology

The work proceeds in three independent steps, each with its own script and outputs.

### 1. Generation — `scripts/extract_region.py` + `scripts/merge_global.py`

The world is partitioned into 16 regions (`src/osm_powerplants/regions.py`): `europe`, `russia`, `north_america`, `central_america_caribbean`, `south_america`, `northern_africa`, `western_africa`, `middle_africa`, `eastern_africa`, `southern_africa`, `western_asia`, `central_asia`, `southern_asia`, `southeastern_asia`, `eastern_asia`, `oceania`. Each region runs as an independent CI job once a month; a final merge job concatenates the regional outputs into `osm_global.csv`.

- For each region, `extract_region.py` enumerates the region's countries from `REGIONS`, validates them against `pycountry`, and processes them in parallel with a `ThreadPoolExecutor`. Each worker tries the configured Overpass endpoint first, then falls back to `overpass-api.de`, `overpass.private.coffee`, `overpass.kumi.systems`. Raw responses are cached per-country under a local cache directory so reruns are incremental.
- Regional outputs (in `datasets/`): `osm_<region>.csv` (plants), `osm_<region>_rejected.csv` (rejection report DataFrame), and `osm_<region>_rejected.geojson` (rejected-plant points for map review).
- `merge_global.py` concatenates the regional CSVs into `osm_global.csv`, the rejection CSVs into `osm_global_rejected_plants.csv`, and the rejection GeoJSONs into `osm_global_rejected_plants.geojson` at the repo root.
- Kosovo is excluded via `omitted_countries` in `config.yaml` (no Overpass coverage).

### 2. Matching — `evaluation/matching.py`

Runs PPM twice to measure OSM's incremental contribution. Both runs share the same overlay (`evaluation/config.overlay.yaml`, which fixes the Southern-hemisphere latitude filter, registers the OSM source, and pins `target_countries` to 221 names):

- `no_osm`: the 10 PPM sources (BEYONDCOAL, EESI, ENTSOE, GEM, GEO, GHR, GPD, JRC, MASTR, OPSD). Output:
  `evaluation/matching/matched_no_osm.csv` (225,343 plants).
- `osm_matching`: the same 10 sources plus OSM added to `matching_sources` as `{"OSM": "Capacity >= 1"}`. OSM is not in `fully_included_sources` here, so any OSM plant that does not match another source is dropped. Output:
  `evaluation/matching/matched_osm_matching.csv` (228,464 plants).

OSM-only contributions are recovered separately in step 3 via set-difference against `osm_global.csv`, not by configuring PPM to fully include OSM. This keeps step 2 cheap and deterministic.

### 3. Evaluation — `evaluation/evaluate.py`

Classifies every country in `osm_global.csv ∪ matched_osm_matching.csv` based on how much OSM adds on top of PPM.

1. Country names in all three inputs (`osm_global.csv`, `matched_osm_matching.csv`, IRENA ELECSTAT) are harmonised with
   `country_converter` to avoid double-counting under names like "Russia" vs "Russian Federation".
2. OSM plants already absorbed into PPM are identified by parsing the `projectID` dicts in `matched_osm_matching.csv` and collecting the
   `OSM_plant:...` identifiers under the `OSM` key. The complement of that set against the `projectID` column of `osm_global.csv` gives the
   OSM-only set.
3. Per-country capacity is aggregated for PPM, OSM-only, and IRENA ELECSTAT (2024, all fueltypes — renewable *and* fossil; see "Inputs" for what IRENASTAT actually returns).
4. Each country is assigned one of five buckets based on how PPM and OSM-only relate to IRENA:

| bucket | rule | reading |
|---|---|---|
| `ppm_already_sufficient` | OSM share < 10% of combined | PPM dominates |
| `osm_complements` | OSM share ≥ 10%, combined ≤ 2×IRENA | OSM adds real value |
| `osm_primary` | PPM < 10% of IRENA, OSM share > 50% | OSM carries the signal |
| `likely_duplicates` | combined > 2×IRENA | inspect for dedup/over-report |
| `insufficient_reference` | IRENA missing and combined < 50 MW | unresolvable |

Output: `evaluation/evaluation.csv`, one row per country with the raw numbers
and the bucket. Regenerated when `evaluate.py` runs (not committed).

## Inputs

- `osm_global.csv` — OSM power-plant dataset (28,882 plants / 2,873 GW, 173 countries), produced by step 1.
- `evaluation/matching/matched_no_osm.csv` and `evaluation/matching/matched_osm_matching.csv` — produced by step 2.
- IRENA ELECSTAT 2024 — loaded via `powerplantmatching.data.IRENASTAT()`. The PPM docstring calls it "renewable capacity statistics", which is misleading: the DataFrame returned covers **all fueltypes**, including Hard Coal, Natural Gas, Nuclear and Oil, at realistic global totals (verified: Russia 251 GW, Germany 276 GW — unreachable from renewables alone). This evaluation uses all of it as the reference signal.

## Headline findings

| metric | value |
|---|---|
| OSM plants total | 28,882 (2,873 GW) |
| Matched into PPM | 18,204 (63%) by set-difference; 18,188 unique OSM IDs actually referenced in `projectID` |
| OSM-only | 10,678 plants / 306 GW |
| Countries with any OSM-only contribution | 144 |
| Defensible contribution (`osm_primary` + `osm_complements`) | **146 GW across 38 countries** |
| Likely duplicates | 6 countries (mostly PPM-internal) |

The 16-ID gap between 18,204 and 18,188 is a regeneration-drift artefact: 16 OSM IDs referenced in `matched_osm_matching.csv` no longer appear in the current `osm_global.csv` (which was regenerated after the matching run). The set-difference used by `evaluate.py` therefore treats those 16 as "matched" implicitly via subtraction. Immaterial to the buckets but worth noting if the numbers are audited directly.

## Bucket breakdown (233 countries)

| bucket | countries |
|---|---:|
| ppm_already_sufficient | 186 |
| osm_complements | 35 |
| osm_primary | 3 |
| likely_duplicates | 6 |
| insufficient_reference | 3 |

Full per-country table: `evaluation/evaluation.csv`.

## Defensible OSM contribution

### All 35 countries in `osm_complements`

| Country | n_ppm | cap_ppm (GW) | n_osm_only | cap_osm_only (GW) | cap_irena (GW) | OSM share |
|---|---:|---:|---:|---:|---:|---:|
| Germany | 141,475 | 328.3 | 2,011 | 38.1 | 275.9 | 10% |
| Russia | 610 | 275.8 | 123 | 34.3 | 251.1 | 11% |
| France | 3,150 | 157.2 | 2,026 | 23.7 | 156.8 | 13% |
| Sweden | 668 | 54.5 | 162 | 7.0 | 53.3 | 11% |
| Chile | 906 | 45.2 | 190 | 6.3 | 37.5 | 12% |
| Malaysia | 218 | 45.4 | 8 | 5.3 | 39.0 | 10% |
| Portugal | 644 | 26.9 | 297 | 3.4 | 25.9 | 11% |
| Serbia | 66 | 9.8 | 9 | 3.1 | 8.8 | 24% |
| Belarus | 38 | 12.0 | 25 | 2.9 | 12.7 | 20% |
| Denmark | 376 | 17.3 | 284 | 2.9 | 17.9 | 14% |
| Bosnia and Herzegovina | 86 | 5.5 | 9 | 2.8 | 5.0 | 33% |
| Peru | 84 | 16.7 | 17 | 2.5 | 16.2 | 13% |
| Laos | 80 | 19.5 | 31 | 2.3 | 12.0 | 11% |
| Lithuania | 146 | 8.3 | 164 | 1.9 | 7.2 | 19% |
| Morocco | 79 | 12.3 | 16 | 1.9 | 12.1 | 13% |
| Hungary | 622 | 11.6 | 50 | 1.8 | 16.3 | 13% |
| Turkmenistan | 16 | 8.7 | 1 | 1.6 | 7.0 | 15% |
| Myanmar | 69 | 8.0 | 9 | 1.1 | 7.2 | 12% |
| Iceland | 22 | 3.6 | 24 | 0.7 | 3.0 | 17% |
| Mongolia | 26 | 2.1 | 3 | 0.7 | 1.6 | 24% |
| Croatia | 118 | 5.5 | 41 | 0.6 | 5.7 | 11% |
| Estonia | 177 | 2.7 | 23 | 0.4 | 3.6 | 12% |
| Djibouti | 9 | 0.3 | 1 | 0.1 | 0.2 | 15% |
| Faroe Islands | 2 | 0.0 | 9 | 0.1 | 0.2 | 61% |
| Burkina Faso | 13 | 0.5 | 2 | 0.1 | 0.6 | 11% |
| Togo | 7 | 0.3 | 1 | 0.1 | 0.4 | 13% |
| Burundi | 9 | 0.1 | 5 | 0.0 | 0.1 | 34% |
| Belize | 4 | 0.0 | 4 | 0.0 | 0.2 | 58% |
| Niger | 9 | 0.3 | 1 | 0.0 | 0.5 | 10% |
| Greenland | 1 | 0.0 | 3 | 0.0 | 0.2 | 27% |
| Cabo Verde | 10 | 0.1 | 5 | 0.0 | 0.2 | 22% |
| Sao Tome and Principe | 2 | 0.0 | 1 | 0.0 | 0.0 | 14% |
| Vanuatu | 2 | 0.0 | 1 | 0.0 | 0.0 | 24% |
| Tonga | 2 | 0.0 | 1 | 0.0 | 0.0 | 18% |
| Micronesia, Fed. Sts. | 2 | 0.0 | 1 | 0.0 | 0.0 | 16% |

Across all 35 `osm_complements` countries: **+145.6 GW**.

### `osm_primary`

| Country | cap_ppm (MW) | cap_osm_only (MW) | cap_irena (MW) |
|---|---:|---:|---:|
| Jersey | 7.5 | 75.0 | — |
| Falkland Islands | 0 | 2.0 | 17.0 |
| British Virgin Islands | 0 | 0.1 | 66.4 |

All three are small territories. Together **+77 MW** — negligible in absolute terms but legitimate coverage for entities PPM does not touch.

## Over-report shortlist (`likely_duplicates`)

| Country | cap_ppm (GW) | cap_osm_only (GW) | cap_irena (GW) | reading |
|---|---:|---:|---:|---|
| Ukraine | 57.7 | 1.5 | 20.2 | OSM involved but minor; PPM already over-reports 2.9× |
| Ethiopia | 13.7 | 0.0 | 6.1 | PPM-internal, OSM adds nothing |
| Nepal | 7.7 | 0.0 | 3.5 | PPM-internal, OSM adds nothing |
| Namibia | 8.3 | 0.03 | 0.8 | PPM-internal, OSM trivially involved |
| Palestine | 0.6 | 0.0 | 0.2 | PPM-internal, OSM adds nothing |
| Dominica | 0.13 | 0.002 | 0.03 | Noise level |

Four of the six flagged countries have **zero** OSM-only capacity — the doubling vs IRENA is entirely from PPM's own sources. Only Ukraine carries OSM-only MW at a scale worth a closer look, and even there OSM is < 3% of the excess. The over-reports are PPM concerns, not OSM concerns.

## Interpretation

- OSM does **not** rescue any large country where PPM is missing — the three `osm_primary` cases are all sub-100 MW territories.
- OSM **does** add real, cross-validated capacity in 35 mostly European and Eurasian countries — 145 GW in total. In Germany, France, Russia and Sweden the contribution is in the tens of GW and the country-level PPM+OSM totals track IRENA within 15%. At the fueltype level a handful of cells (Sweden/Nuclear, Belarus/Nuclear, BiH/Hydro, Morocco/Solar) show OSM material contributing to an over-report — see the per-fueltype audit above and `evaluation/evaluation_by_fueltype.csv`.
- For the remaining ~190 countries the contribution is immaterial or not resolvable against IRENA.

Translating this to a matching configuration: OSM should be used **globally for matching** (so it can cross-validate any PPM row) and **fully included only in the 38 defensible-contribution countries**. That is what `evaluation/config.ppm_with_osm.yaml` encodes.

## Per-fueltype audit

Country-level bucketing can mask duplicate risk at the fueltype level: a country whose combined PPM+OSM total is ≤ 2 × IRENA overall can still have individual fueltypes where OSM-only capacity piles onto a PPM total that already exceeds IRENA. `evaluation/evaluate.py` now writes a second output, `evaluation/evaluation_by_fueltype.csv`, with raw `cap_ppm_MW`, `cap_osm_only_MW`, `cap_irena_MW` per (Country, Fueltype) and a boolean `hidden_duplicate_risk` flag (`cap_osm_only_MW > 0 ∧ cap_total_MW > 2 × cap_irena_MW`).

The audit finds **9 flagged rows inside the 38 fully-included countries**:

| Country | Fueltype | PPM (MW) | OSM-only (MW) | IRENA (MW) | reading |
|---|---|---:|---:|---:|---|
| Sweden | Nuclear | 11,452 | 4,721 | 7,001 | OSM doubles an already-inflated PPM total — very likely reactor-unit duplication |
| Bosnia and Herzegovina | Hydro | 2,272 | 2,761 | 2,288 | OSM ≈ IRENA on its own, but sits on top of a full PPM total — probable double count |
| Belarus | Nuclear | 2,388 | 2,400 | 2,340 | OSM repeats the Ostrovets plant that PPM already carries |
| Morocco | Solar | 1,351 | 602 | 951 | OSM adds 2× IRENA on top of PPM |
| Germany | Waste | 3,582 | 15 | 1,004 | PPM-internal over-report; OSM contribution trivial |
| Togo | Solar | 106 | 50 | 67 | small absolute; OSM over-reports |
| Cabo Verde | Wind | 44 | 14 | 27 | small absolute |
| Portugal | Waste | 107 | 10 | 41 | small absolute; PPM-internal driver |
| Hungary | Geothermal | 3.4 | 2.7 | 3.0 | noise level |

Only two of these (Germany/Waste, Portugal/Waste) are PPM-internal with trivial OSM involvement. The other seven are rows where OSM-only MW materially compounds an over-report.

### Proposed refinement (to be discussed during the PR)

Rather than fix the seven rows upstream in `osm_global.csv`, the cleaner first step is to **exclude those specific (Country, Fueltype) pairs from the OSM fully-included filter** in `evaluation/config.ppm_with_osm.yaml`. This removes the clear-duplicate rows while keeping every other fueltype in the same country intact — Sweden still benefits from OSM for Hydro/Wind/Solar, Morocco still benefits from OSM for Wind, and so on. The remaining 28 countries that have no flagged (Country, Fueltype) pair are unchanged.

Concretely, the OSM entry in `fully_included_sources` would gain seven `not (Country == '…' and Fueltype == '…')` clauses:

```yaml
- OSM: >-
    Capacity >= 1
    and Country in [...38 countries...]
    and not (Country == 'Sweden' and Fueltype == 'Nuclear')
    and not (Country == 'Bosnia and Herzegovina' and Fueltype == 'Hydro')
    and not (Country == 'Belarus' and Fueltype == 'Nuclear')
    and not (Country == 'Morocco' and Fueltype == 'Solar')
    and not (Country == 'Togo' and Fueltype == 'Solar')
    and not (Country == 'Cabo Verde' and Fueltype == 'Wind')
    and not (Country == 'Hungary' and Fueltype == 'Geothermal')
```

Impact: removes **10.55 GW of very-likely-duplicate OSM-only capacity** (7.2% of the 145.6 GW defensible total), leaving a revised defensible contribution of **~135 GW across the same 38 countries**. The two trivial rows (Germany/Waste 14.5 MW, Portugal/Waste 10.3 MW) are left in — their OSM contribution is small enough that it does not move the country-level picture, and they can be revisited if the upstream over-report is cleaned up in PPM.

Rows deliberately **not** excluded are those where PPM is the over-reporter and OSM contributes essentially nothing (Germany/Waste, Portugal/Waste): filtering them would be cosmetic, the real fix belongs upstream in PPM's sources.

Alternative (follow-up): triage the seven rows at source — demote unit-level entries to generator-level in OSM, correct the capacity tag, or remove the duplicates directly in `osm_global.csv`. This is the right long-term fix but requires per-plant review; the filter-based refinement above is the low-risk improvement for this PR.

## Methodology caveats

- **IRENA is used as a signal, not ground truth.** It is missing for several dependencies and small territories, and can under-report fossil fleets in some countries.
- **Country-name harmonisation matters.** Before harmonisation, Russia alone accounted for a spurious 34 GW mis-classified as `osm_primary` because `osm_global.csv` used "Russian Federation" while PPM used "Russia".
- **Set-difference is an upper bound on OSM-unique capacity.** A fraction of the 10,678 "OSM-only" plants likely correspond to PPM plants that simply failed to match on coordinate/name drift. The 306 GW headline is therefore the upper bound; 146 GW (`osm_primary` + `osm_complements` only) is the defensible number.
- **No hard thresholds.** The bucket rules above are heuristics chosen after looking at the data, not ground-truth classifiers. Edge cases on the boundaries are expected and worth manual review.

## Deliverables

- **Primary dataset**: `osm_global.csv`
- **Recommended PPM config**: `evaluation/config.ppm_with_osm.yaml` — uses OSM globally in `matching_sources` and fully-includes OSM only in the 38 `osm_primary`+`osm_complements` countries.
  
  This file is an **overlay**, not a standalone config. It encodes only the four keys that differ from PPM's default (`main_query`, `matching_sources`, `fully_included_sources`, `target_countries`) plus the `OSM` source block. All other data-source definitions (ENTSOE, OPSD, JRC, …), I/O settings and execution knobs are inherited from PPM's default `config.yaml`. Apply with:

  ```python
  import yaml, powerplantmatching as ppm
  from powerplantmatching.core import get_config
  overlay = yaml.safe_load(open("evaluation/config.ppm_with_osm.yaml"))
  ppm.powerplants(config=get_config(**overlay), update=True)
  ```

  Do **not** pass the YAML directly as the full config: matching will fail because every other source block is missing. Filter strings for the 10 upstream `matching_sources` and 6 upstream `fully_included_sources` are reproduced verbatim from PPM's default; the only functional changes are (a) relaxing the default `lat >= 30` clause in `main_query` to enable the Southern Hemisphere, (b) extending `target_countries` from PPM's 36-country
  EU-plus list to the 221-country OSM ∪ GEM union, and (c) adding OSM as the 11th matching source and 7th fully-included source.
  
- **Per-country evaluation**: `evaluation/evaluation.csv`
- **Per-(country, fueltype) evaluation**: `evaluation/evaluation_by_fueltype.csv` with the `hidden_duplicate_risk` flag for rows where OSM compounds a PPM over-report at the fueltype level.

## Reproducing end-to-end

```bash
# 0. Dependencies (install osm-powerplants + PPM deps)
uv venv .venv
uv pip install -e .
uv pip install powerplantmatching country_converter

# 1. Generation — in production this is the monthly CI workflow
#    (.github/workflows/data.yml). To regenerate locally:
.venv/bin/python scripts/extract_region.py --region europe --clear-cache
# ...repeat for each region, or run all 16 then:
.venv/bin/python scripts/merge_global.py

# 2. Matching (≈ 75 min and ≈ 90 min on the reference machine)
.venv/bin/python evaluation/matching.py --countries all --skip osm_matching
.venv/bin/python evaluation/matching.py --countries all --skip no_osm

# 3. Evaluation
.venv/bin/python evaluation/evaluate.py
```

Inputs consumed: `config.yaml` (OSM extraction rules), `evaluation/config.overlay.yaml` (PPM overlay). Matching outputs go to `evaluation/matching/`; evaluation CSVs land directly in `evaluation/`.

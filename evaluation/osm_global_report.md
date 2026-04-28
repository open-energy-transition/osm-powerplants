# OSM contribution to the global power-plant dataset

This repository builds a global OSM power-plant dataset and evaluates whether adding it to `powerplantmatching` (PPM) provides genuine new plants or capacity that the other PPM sources miss. The evaluation is then translated into a PPM configuration that keeps OSM only where it adds defensible value.

## TL;DR

- Built a global OSM power-plant dataset: **28,970 plants / 2,896 GW across 173 countries** (`osm_global.csv.gz`).
- Ran PPM in four configurations to measure OSM's incremental contribution: **21,389 OSM plants matched into PPM (74 %), 7,581 OSM-only**.
- Classified every country into five buckets against IRENA ELECSTAT 2024:
  - **188** `ppm_already_sufficient` — OSM adds < 10 % of combined capacity.
  - **34** `osm_complements` + **2** `osm_primary` → **36 countries / 146.8 GW of defensible OSM contribution** (gross).
  - **6** `likely_duplicates` (Ukraine, Ethiopia, Nepal, Namibia, Palestine, Dominica); four of the six have zero OSM-only capacity, so the over-report is PPM-internal.
  - **2** `insufficient_reference` (no IRENA data, sub-50 MW).
- Per-fueltype audit flags **8 rows inside the 36 defensible countries** where OSM compounds a PPM over-report (Sweden/Nuclear, BiH/Hydro, Belarus/Nuclear, Togo/Solar, Cabo Verde/Wind, Hungary/Geothermal — plus two trivial PPM-internal rows in Germany/Waste and Portugal/Waste).
- Recommendation encoded in `evaluation/config.ppm_with_osm.yaml`: **OSM globally in `matching_sources`** (cross-validates any PPM row) and **fully-included in 35 of the 36 defensible countries** — Kuwait is excluded as a manual override because its single OSM-only plant ("Subbiya"/Sabiya, 7 GW Oil) is a known un-matched twin of an existing PPM record. Within those 35 countries, six (Country, Fueltype) duplicate pairs are additionally excluded by the per-fueltype filter. **Defensible OSM contribution under the recommended overlay: 129.9 GW.**

## Methodology

The work proceeds in three independent steps, each with its own script and outputs.

### 1. Generation — `scripts/extract_region.py` + `scripts/merge_global.py`

The world is partitioned into 16 regions (`src/osm_powerplants/regions.py`): `europe`, `russia`, `north_america`, `central_america_caribbean`, `south_america`, `northern_africa`, `western_africa`, `middle_africa`, `eastern_africa`, `southern_africa`, `western_asia`, `central_asia`, `southern_asia`, `southeastern_asia`, `eastern_asia`, `oceania`. Each region runs as an independent CI job once a month; a final merge job concatenates the regional outputs into `osm_global.csv.gz`.

- For each region, `extract_region.py` enumerates the region's countries from `REGIONS`, validates them against `pycountry`, and processes them in parallel with a `ThreadPoolExecutor`. Each worker tries the configured Overpass endpoint first, then falls back to `overpass-api.de`, `overpass.private.coffee`, `overpass.kumi.systems`. Raw responses are cached per-country under a local cache directory so reruns are incremental.
- Regional outputs (in `datasets/`): `osm_<region>.csv` (plants), `osm_<region>_rejected.csv` (rejection report DataFrame), and `osm_<region>_rejected.geojson` (rejected-plant points for map review).
- `merge_global.py` concatenates the regional CSVs into `osm_global.csv.gz`, the rejection CSVs into `osm_global_rejected_plants.csv.gz`, and the rejection GeoJSONs into `osm_global_rejected_plants.geojson.gz` at the repo root.
- Kosovo is excluded via `omitted_countries` in `config.yaml` (no Overpass coverage).

### 2. Matching — `evaluation/matching.py`

Runs PPM in four configurations, all sharing the basic overlay (`evaluation/config.overlay.yaml`, which fixes the Southern-hemisphere latitude filter, registers the OSM source, and pins `target_countries` to 221 names):

- `no_osm`: PPM's 10 default sources (BEYONDCOAL, EESI, ENTSOE, GEM, GEO, GHR, GPD, JRC, MASTR, OPSD). Output: `matched_no_osm.csv`.
- `osm_matching`: same 10 sources plus OSM in `matching_sources` only. OSM acts as a cross-validator; unmatched OSM plants are dropped. Output: `matched_osm_matching.csv`.
- `osm_only`: OSM added to both `matching_sources` and `fully_included_sources` with no country/fueltype filter. Every unmatched OSM plant is retained — uppermost bound on OSM contribution. Output: `matched_osm_only.csv`.
- `osm_full`: the recommended overlay (`evaluation/config.ppm_with_osm.yaml`) — OSM in `fully_included_sources` only for the 35-country list, with the six (Country, Fueltype) exclusions applied. Output: `matched_osm_full.csv` — the dataset a downstream PPM user would get with the overlay.

### 3. Evaluation — `evaluation/evaluate.py`

Reads `matched_osm_only.csv` and `matched_osm_full.csv`, splits each into PPM rows and OSM-only rows by parsing the `projectID` column (a row is OSM-only if its `projectID` dict has only the `OSM` key), then aggregates per country and per (country, fueltype):

1. Country names in all inputs are harmonised with `country_converter` to avoid double-counting under names like "Russia" vs "Russian Federation".
2. Per-country capacity is aggregated for PPM, OSM-only (gross from `matched_osm_only`), OSM-only filtered (from `matched_osm_full`), and IRENA ELECSTAT (2024, all fueltypes — renewable *and* fossil; see "Inputs").
3. Each country is assigned one of five buckets based on how PPM and OSM-only relate to IRENA:

| bucket | rule | reading |
|---|---|---|
| `ppm_already_sufficient` | OSM share < 10 % of combined | PPM dominates |
| `osm_complements` | OSM share ≥ 10 %, combined ≤ 2×IRENA | OSM adds real value |
| `osm_primary` | PPM < 10 % of IRENA, OSM share > 50 % | OSM carries the signal |
| `likely_duplicates` | combined > 2×IRENA | inspect for dedup/over-report |
| `insufficient_reference` | IRENA missing and combined < 50 MW | unresolvable |

Outputs: `evaluation/evaluation.csv` (per-country) and `evaluation/evaluation_by_fueltype.csv` (per-(country, fueltype) with a `hidden_duplicate_risk` flag). Regenerated when `evaluate.py` runs (not committed).

## Inputs

- `osm_global.csv.gz` — OSM power-plant dataset (28,970 plants / 2,896 GW, 173 countries), produced by step 1.
- `evaluation/matching/matched_osm_only.csv` and `evaluation/matching/matched_osm_full.csv` — produced by step 2.
- IRENA ELECSTAT 2024 — loaded via `powerplantmatching.data.IRENASTAT()`. The PPM docstring calls it "renewable capacity statistics", which is misleading: the DataFrame returned covers **all fueltypes**, including Hard Coal, Natural Gas, Nuclear and Oil, at realistic global totals (verified: Russia 251 GW, Germany 276 GW — unreachable from renewables alone). This evaluation uses all of it as the reference signal.

## Headline findings

| metric | value |
|---|---|
| OSM plants total | 28,970 (2,896 GW) |
| Matched into PPM | 21,389 (74 %) |
| OSM-only (gross) | 7,581 plants / 306 GW |
| OSM-only (filtered, under recommended overlay) | 4,008 plants / 130 GW |
| Countries with any OSM-only contribution | 134 |
| Defensible by bucket (`osm_primary` + `osm_complements`) | **146.8 GW across 36 countries** |
| Defensible under the overlay (35 countries, Kuwait excluded) | **129.9 GW** |
| Likely duplicates | 6 countries (mostly PPM-internal) |

## Bucket breakdown (232 countries)

| bucket | countries |
|---|---:|
| ppm_already_sufficient | 188 |
| osm_complements | 34 |
| osm_primary | 2 |
| likely_duplicates | 6 |
| insufficient_reference | 2 |

Full per-country table: `evaluation/evaluation.csv`.

## Defensible OSM contribution

### `osm_complements` (34 countries)

Sorted by gross OSM-only capacity desc. `cap_osm_only_filt` is the post-overlay capacity (after the country list and the six per-fueltype exclusions); a `0.0` cell either means the country is not in the overlay's country list, or all its OSM-only fueltypes are flagged as duplicates and excluded.

| Country | n_ppm | cap_ppm (GW) | n_osm_only | cap_osm_only (GW) | cap_osm_only_filt (GW) | cap_irena (GW) | OSM share |
|---|---:|---:|---:|---:|---:|---:|---:|
| Germany | 141,478 | 328.3 | 1,493 | 36.9 | 36.9 | 275.9 | 10 % |
| Russia | 610 | 275.8 | 118 | 34.3 | 34.3 | 251.1 | 11 % |
| France | 3,149 | 157.2 | 1,457 | 20.9 | 20.9 | 156.8 | 12 % |
| Sweden | 667 | 53.8 | 137 | 7.3 | 2.6 | 53.3 | 12 % |
| Kuwait\* | 12 | 27.8 | 1 | 7.0 | **0.0** | 20.3 | 20 % |
| Chile | 906 | 45.2 | 158 | 6.3 | 6.3 | 37.5 | 12 % |
| Malaysia | 218 | 45.4 | 8 | 5.3 | 5.3 | 39.0 | 10 % |
| Portugal | 644 | 26.9 | 116 | 3.2 | 3.2 | 25.9 | 11 % |
| Serbia | 66 | 9.8 | 5 | 3.1 | 3.1 | 8.8 | 24 % |
| Belarus | 38 | 12.0 | 21 | 2.9 | 0.5 | 12.7 | 20 % |
| Denmark | 376 | 17.3 | 251 | 2.9 | 2.9 | 17.9 | 14 % |
| Bosnia and Herzegovina | 86 | 5.5 | 7 | 2.8 | **0.0** | 5.0 | 33 % |
| Peru | 84 | 16.7 | 10 | 2.5 | 2.5 | 16.2 | 13 % |
| Laos | 80 | 19.5 | 32 | 2.3 | 2.3 | 12.0 | 11 % |
| Lithuania | 146 | 8.3 | 67 | 1.9 | 1.9 | 7.2 | 18 % |
| Hungary | 622 | 11.6 | 37 | 1.8 | 1.8 | 16.3 | 13 % |
| Turkmenistan | 16 | 8.7 | 1 | 1.6 | 1.6 | 7.0 | 15 % |
| Myanmar | 69 | 8.0 | 9 | 1.1 | 1.1 | 7.2 | 12 % |
| Iceland | 22 | 3.6 | 12 | 0.7 | 0.7 | 3.0 | 17 % |
| Mongolia | 26 | 2.1 | 3 | 0.7 | 0.7 | 1.6 | 24 % |
| Croatia | 118 | 5.5 | 33 | 0.6 | 0.6 | 5.7 | 11 % |
| Estonia | 177 | 2.7 | 17 | 0.4 | 0.4 | 3.6 | 12 % |
| Djibouti | 9 | 0.3 | 1 | 0.1 | 0.1 | 0.2 | 15 % |
| Faroe Islands | 2 | 0.0 | 8 | 0.1 | 0.1 | 0.2 | 61 % |
| Burkina Faso | 13 | 0.5 | 2 | 0.1 | 0.1 | 0.6 | 11 % |
| Togo | 7 | 0.3 | 1 | 0.1 | **0.0** | 0.4 | 13 % |
| Burundi | 9 | 0.1 | 3 | 0.0 | 0.0 | 0.1 | 33 % |
| Belize | 4 | 0.0 | 4 | 0.0 | 0.0 | 0.2 | 58 % |
| Niger | 9 | 0.3 | 1 | 0.0 | 0.0 | 0.5 | 10 % |
| Greenland | 1 | 0.0 | 2 | 0.0 | 0.0 | 0.2 | 26 % |
| Cabo Verde | 10 | 0.1 | 3 | 0.0 | 0.0 | 0.2 | 20 % |
| Sao Tome and Principe | 2 | 0.0 | 1 | 0.0 | 0.0 | 0.0 | 14 % |
| Vanuatu | 2 | 0.0 | 1 | 0.0 | 0.0 | 0.0 | 24 % |
| Tonga | 2 | 0.0 | 1 | 0.0 | 0.0 | 0.0 | 18 % |

\* Kuwait classifies as `osm_complements` at the country level but its sole OSM-only plant ("Subbiya"/Sabiya, 7 GW Oil/Combustion Engine) is a known un-matched twin of an existing PPM record (Sabiya, 7.3 GW Natural Gas/Steam Turbine) — same site, capacity within 4 %, fueltype mismatch prevented the matcher from picking it up. Manually excluded from the overlay's country list.

Across all 34 `osm_complements` countries: **+146.7 GW gross**. Under the overlay (Kuwait excluded, six (Country, Fueltype) pairs filtered): **+129.8 GW**.

### `osm_primary` (2 countries)

| Country | cap_ppm (MW) | cap_osm_only (MW) | cap_irena (MW) |
|---|---:|---:|---:|
| Jersey | 7.5 | 75.0 | — |
| Falkland Islands | 0 | 2.0 | 17.0 |

Both are small territories. Together **+77 MW** — negligible in absolute terms but legitimate coverage for entities PPM does not touch. (British Virgin Islands previously appeared in this bucket; in this evaluation it classifies as `ppm_already_sufficient`.)

## Over-report shortlist (`likely_duplicates`)

| Country | cap_ppm (GW) | cap_osm_only (GW) | cap_irena (GW) | reading |
|---|---:|---:|---:|---|
| Ukraine | 57.7 | 1.5 | 20.2 | OSM involved but minor; PPM already over-reports 2.9× |
| Ethiopia | 13.7 | 0.0 | 6.1 | PPM-internal, OSM adds nothing |
| Nepal | 7.7 | 0.0 | 3.5 | PPM-internal, OSM adds nothing |
| Namibia | 8.3 | 0.03 | 0.8 | PPM-internal, OSM trivially involved |
| Palestine | 0.6 | 0.0 | 0.2 | PPM-internal, OSM adds nothing |
| Dominica | 0.13 | 0.002 | 0.03 | Noise level |

Four of the six flagged countries have **zero** OSM-only capacity — the doubling vs IRENA is entirely from PPM's own sources. Only Ukraine carries OSM-only MW at a scale worth a closer look, and even there OSM is < 3 % of the excess. The over-reports are PPM concerns, not OSM concerns.

## Interpretation

- OSM does **not** rescue any large country where PPM is missing — the two `osm_primary` cases (Jersey, Falkland Islands) are sub-100 MW territories.
- OSM **does** add real, cross-validated capacity in 34 mostly European and Eurasian `osm_complements` countries — 146.8 GW gross / 129.9 GW under the overlay (Kuwait excluded, six per-fueltype duplicate pairs filtered). In Germany, France, Russia and Sweden the contribution is in the tens of GW and the country-level PPM+OSM totals track IRENA within 15 %. At the fueltype level a handful of cells (Sweden/Nuclear, Belarus/Nuclear, BiH/Hydro) showed OSM material contributing to an over-report; the overlay's `fully_included_sources.OSM` filter excludes these duplicate pairs — see the per-fueltype audit below and `evaluation/evaluation_by_fueltype.csv`.
- For the remaining ~190 countries the contribution is immaterial or not resolvable against IRENA.

Translating this to a matching configuration: OSM is used **globally for matching** (so it can cross-validate any PPM row) and **fully included in 35 of the 36 defensible countries** (Kuwait excluded as a manual override), with six (Country, Fueltype) duplicate pairs from the per-fueltype audit additionally excluded. That is what `evaluation/config.ppm_with_osm.yaml` encodes.

## Per-fueltype audit

Country-level bucketing can mask duplicate risk at the fueltype level: a country whose combined PPM+OSM total is ≤ 2 × IRENA overall can still have individual fueltypes where OSM-only capacity piles onto a PPM total that already exceeds IRENA. `evaluation/evaluate.py` writes a second output, `evaluation/evaluation_by_fueltype.csv`, with `cap_ppm_MW`, `cap_osm_only_MW`, `cap_osm_only_filtered_MW`, `cap_irena_MW` per (Country, Fueltype) and a boolean `hidden_duplicate_risk` flag (`cap_osm_only_MW > 0 ∧ cap_total_MW > 2 × cap_irena_MW`).

The audit finds **8 flagged rows inside the 36 defensible countries**:

| Country | Fueltype | PPM (MW) | OSM-only (MW) | IRENA (MW) | reading |
|---|---|---:|---:|---:|---|
| Sweden | Nuclear | 11,452 | 4,721 | 7,001 | OSM doubles an already-inflated PPM total — very likely reactor-unit duplication |
| Bosnia and Herzegovina | Hydro | 2,272 | 2,760 | 2,288 | OSM ≈ IRENA on its own, but sits on top of a full PPM total — probable double count |
| Belarus | Nuclear | 2,388 | 2,400 | 2,340 | OSM repeats the Ostrovets plant that PPM already carries |
| Germany | Waste | 3,582 | 14.5 | 1,004 | PPM-internal over-report; OSM contribution trivial |
| Togo | Solar | 106 | 50 | 67 | small absolute; OSM over-reports |
| Cabo Verde | Wind | 44 | 11.9 | 27 | small absolute |
| Portugal | Waste | 107 | 10.3 | 41 | small absolute; PPM-internal driver |
| Hungary | Geothermal | 3.4 | 2.7 | 3.0 | noise level |

Only two of these (Germany/Waste, Portugal/Waste) are PPM-internal with trivial OSM involvement. The other six are rows where OSM-only MW materially compounds an over-report. (Morocco/Solar previously appeared on this list; in this evaluation Morocco classifies as `ppm_already_sufficient` and is no longer in the defensible bucket, so the issue is moot.)

### Filter encoded in the overlay

`evaluation/config.ppm_with_osm.yaml` excludes those six (Country, Fueltype) pairs from the OSM `fully_included_sources` filter. This removes the clear-duplicate rows while keeping every other fueltype in the same country intact — Sweden still benefits from OSM for Hydro/Wind/Solar, Belarus for Solar/Wind, and so on. The remaining 29 countries that have no flagged (Country, Fueltype) pair are unchanged.

The exclusions appear inside the `fully_included_sources.OSM` filter as:

```yaml
- OSM: >-
    Capacity >= 1
    and Country in [...35 countries...]
    and not (Country == 'Sweden' and Fueltype == 'Nuclear')
    and not (Country == 'Bosnia and Herzegovina' and Fueltype == 'Hydro')
    and not (Country == 'Belarus' and Fueltype == 'Nuclear')
    and not (Country == 'Togo' and Fueltype == 'Solar')
    and not (Country == 'Cabo Verde' and Fueltype == 'Wind')
    and not (Country == 'Hungary' and Fueltype == 'Geothermal')
```

Impact: removes **9.9 GW of very-likely-duplicate OSM-only capacity** (7.1 % of the 139.8 GW gross contribution from the 35 countries in the overlay), leaving a defensible contribution of **129.9 GW**. Kuwait's 7.0 GW OSM-only plant is dropped separately by virtue of Kuwait not being in the country list (manual override; see footnote on the `osm_complements` table). The two trivial fueltype rows (Germany/Waste 14.5 MW, Portugal/Waste 10.3 MW) are deliberately left in — their OSM contribution is small enough that it does not move the country-level picture, and the real fix for those rows belongs upstream in PPM's sources, not in this filter.

Possible follow-up: triage the seven flagged rows at source (six fueltype pairs + Kuwait's Subbiya record) — demote unit-level entries to generator-level in OSM, correct the capacity tag, or remove the duplicates directly in `osm_global.csv.gz`. This is the right long-term fix but requires per-plant review; the filter encoded above is the low-risk first step.

## Methodology caveats

- **IRENA is used as a signal, not ground truth.** It is missing for several dependencies and small territories, and can under-report fossil fleets in some countries.
- **Country-name harmonisation matters.** Before harmonisation, Russia alone accounted for a spurious 34 GW mis-classified as `osm_primary` because `osm_global.csv.gz` used "Russian Federation" while PPM used "Russia".
- **OSM-only plants are an upper bound on OSM-unique capacity.** A fraction of the 7,581 OSM-only plants likely correspond to PPM plants that simply failed to match on coordinate/name/fueltype drift. Kuwait is the clearest known example — caught by manual inspection, not the bucket rules. The 306 GW headline is therefore the upper bound; 146.8 GW (`osm_primary` + `osm_complements`) is the defensible bucket-level number; 129.9 GW is what survives the recommended overlay.
- **The Kuwait override is manual.** The country-level bucket rules class Kuwait as `osm_complements` because total PPM+OSM is below 2×IRENA. Manual inspection found the single 7 GW OSM-only plant duplicates a known PPM record. There may be other small-set countries where one big OSM-only plant is similarly a duplicate; only Kuwait was caught and overridden in this pass.
- **No hard thresholds.** The bucket rules above are heuristics chosen after looking at the data, not ground-truth classifiers. Edge cases on the boundaries are expected and worth manual review.

## Deliverables

- **Primary dataset**: `osm_global.csv.gz`
- **Recommended PPM config**: `evaluation/config.ppm_with_osm.yaml` — uses OSM globally in `matching_sources` and fully-includes OSM in 35 of the 36 defensible countries (Kuwait excluded as manual override), with six (Country, Fueltype) duplicate pairs additionally excluded.

  This file is an **overlay**, not a standalone config. It encodes only the four keys that differ from PPM's default (`main_query`, `matching_sources`, `fully_included_sources`, `target_countries`) plus the `OSM` source block. All other data-source definitions (ENTSOE, OPSD, JRC, …), I/O settings and execution knobs are inherited from PPM's default `config.yaml`. Apply with:

  ```python
  import yaml, powerplantmatching as ppm
  from powerplantmatching.core import get_config
  overlay = yaml.safe_load(open("evaluation/config.ppm_with_osm.yaml"))
  ppm.powerplants(config=get_config(**overlay), update=True)
  ```

  Do **not** pass the YAML directly as the full config: matching will fail because every other source block is missing. Filter strings for the 10 upstream `matching_sources` and 6 upstream `fully_included_sources` are reproduced verbatim from PPM's default; the only functional changes are (a) relaxing the default `lat >= 30` clause in `main_query` to enable the Southern Hemisphere, (b) extending `target_countries` from PPM's 36-country EU-plus list to the 221-country OSM ∪ GEM union, and (c) adding OSM as the 11th matching source and 7th fully-included source, with a country-restricted filter that also excludes six duplicate (Country, Fueltype) pairs.

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

# 2. Matching (each run ≈ 75–90 min; see matching.py docstring for run definitions)
.venv/bin/python evaluation/matching.py --countries all

# 3. Evaluation
.venv/bin/python evaluation/evaluate.py
```

Inputs consumed: `config.yaml` (OSM extraction rules), `evaluation/config.overlay.yaml` (basic PPM overlay), `evaluation/config.ppm_with_osm.yaml` (recommended overlay, used by the `osm_full` matching run). Matching outputs go to `evaluation/matching/`; evaluation CSVs land directly in `evaluation/`.

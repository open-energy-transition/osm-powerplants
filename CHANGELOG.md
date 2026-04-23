# Changelog

## Unreleased

### Features

* Global dataset pipeline: weekly Europe-only extraction replaced with a monthly global extraction split across 16 regions (`src/osm_powerplants/regions.py`). Matrix CI job per region uploads artifacts; a merge job concatenates into `osm_global.csv` + `osm_global_rejected_plants.csv` + `osm_global_rejected_plants.geojson` at the repo root, with per-region outputs preserved under `datasets/`.
* `scripts/extract_region.py` replaces `scripts/extract_europe.py`: parallelizes countries with fallback Overpass endpoints and writes the rejection report in both CSV and GeoJSON form per region.
* `scripts/merge_global.py` combines regional outputs into global ones.
* `evaluation/`: reviewer bundle (report, PPM matching + evaluation scripts, recommended PPM overlay) used to decide which countries should have OSM fully included in PPM.

### Changes

* Default `config.yaml` now enables `missing_technology_allowed`, adds a Battery mapping, extends CSP technology patterns, and points to the `overpass.private.coffee` endpoint with a longer timeout/retry — absorbed from the previous sibling `config.global.yaml`.
* Legacy root `osm_europe.csv` is frozen and retained for back-compat with the current PPM config; it will be removed once the PPM PR that re-points to `osm_global.csv` merges.

## [0.1.4](https://github.com/open-energy-transition/osm-powerplants/releases/tag/v0.1.4) (2026-04-15)

### Features

* Use alternative Overpass endpoint (`overpass.private.coffee`) for improved availability
* Workshop notebook with Colab launch button

### Bug Fixes

* Detect Overpass resource-limit errors disguised as HTTP 200 responses (PR #4)
* Raise `OverpassAPIError` on exhausted retries instead of returning a silent empty response (PR #4)

### Changes

* Demo country switched from Malta to Colombia
* Tests no longer pin hardcoded version strings

## [0.1.3](https://github.com/open-energy-transition/osm-powerplants/releases/tag/v0.1.3) (2026-01-02)

### Bug Fixes

* CLI `--version` now uses dynamic version from `__version__`

## [0.1.2](https://github.com/open-energy-transition/osm-powerplants/releases/tag/v0.1.2) (2026-01-02)

### Bug Fixes

* Sync `__version__` with pyproject.toml

## [0.1.1](https://github.com/open-energy-transition/osm-powerplants/releases/tag/v0.1.1) (2026-01-02)

### Changes

* Simplified CI workflow - removed Release Please, single main branch
* Skip slow integration tests by default (require external Overpass API)
* Added manual PyPI publish workflow

## 0.1.0 (2025-12-16)


### Features

* initial release v0.1.0 ([9535bb2](https://github.com/open-energy-transition/osm-powerplants/commit/9535bb210cee1389a4b1c31dd757cbe8021a91c8))


### Bug Fixes

* add .nojekyll to disable Jekyll processing ([1650831](https://github.com/open-energy-transition/osm-powerplants/commit/1650831aaedc408fb0beda5eb6126f16282c454f))
* force-add osm_europe.csv to bypass .gitignore in CI ([871556d](https://github.com/open-energy-transition/osm-powerplants/commit/871556dc855aef2d27819ee9d310609ed70cae24))
* page url with underscore ([724b218](https://github.com/open-energy-transition/osm-powerplants/commit/724b218c8d51cf4dfc4b8c67a0136b43afb767c7))
* update repo URLs from osm-powerplants to osm_powerplants ([a154ee4](https://github.com/open-energy-transition/osm-powerplants/commit/a154ee4829f85253a110507dc7604dd4d5527961))


### Documentation

* add PyPI publishing instructions to contributing guide ([f3910af](https://github.com/open-energy-transition/osm-powerplants/commit/f3910afaca90cddecfffdb441ea361800449febf))
* update URLs to use hyphenated repo name (osm-powerplants) ([9f4619b](https://github.com/open-energy-transition/osm-powerplants/commit/9f4619b45452bfcc853ad3a36a9e838de5ffa34e))

## [0.1.0](https://github.com/open-energy-transition/osm-powerplants/releases/tag/v0.1.0) (2024-12-15)

Initial public release.

### Features

* CLI with `process` and `info` commands
* Multi-level caching (CSV, Units, API)
* Plant reconstruction from orphaned generators
* Generator clustering for solar/wind farms
* Cross-platform paths via platformdirs
* Rejection tracking with 27 categorized reasons
* GeoJSON export for JOSM/iD editor integration

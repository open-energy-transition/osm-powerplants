#!/usr/bin/env python3
"""Run powerplantmatching for a set of countries in four OSM configurations.

Runs:
  no_osm        - OSM excluded from matching sources
  osm_matching  - OSM in matching_sources only
  osm_only      - OSM in matching_sources and fully_included_sources, no filter
  osm_full      - recommended overlay (config.ppm_with_osm.yaml: 38-country
                  list and seven-pair fueltype exclusions)

Each run writes evaluation/matching/matched_<label>.csv.

Usage:
    python evaluation/matching.py                        # sample (10 countries)
    python evaluation/matching.py --countries all        # full global run
    python evaluation/matching.py --countries "Germany,France"
    python evaluation/matching.py --skip no_osm          # resume after run 1
"""

import argparse
import shutil
from pathlib import Path

import yaml
import powerplantmatching as ppm
from powerplantmatching.core import _data_in, get_config

EVAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVAL_DIR.parent
CONFIG_OVERLAY = EVAL_DIR / "config.overlay.yaml"
CONFIG_PPM_WITH_OSM = EVAL_DIR / "config.ppm_with_osm.yaml"
MATCHING_DIR = EVAL_DIR / "matching"
OSM_CSV = REPO_ROOT / "osm_global.csv.gz"

SAMPLE_COUNTRIES = [
    "Luxembourg", "Malta", "Iceland", "Cyprus", "Estonia",
    "Latvia", "Lithuania", "Slovenia", "Croatia", "Montenegro",
]


def _install_osm() -> None:
    dest = Path(_data_in("osm_global.csv.gz"))
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_symlink() or dest.exists():
        dest.unlink()
    shutil.copy2(OSM_CSV, dest)


def _run(label: str, config: dict) -> None:
    df = ppm.powerplants(config=config, update=True)
    df.to_csv(MATCHING_DIR / f"matched_{label}.csv")


def main(countries: list[str] | None, skip: set[str] = frozenset()) -> None:
    MATCHING_DIR.mkdir(parents=True, exist_ok=True)

    with CONFIG_OVERLAY.open() as f:
        overlay = yaml.safe_load(f)
    with CONFIG_PPM_WITH_OSM.open() as f:
        recommended = yaml.safe_load(f)

    overlay_base = {
        k: overlay[k] for k in ("main_query", "OSM") if k in overlay
    }
    overlay_countries = overlay.get("target_countries")

    default = get_config(**overlay_base)
    base_matching = default["matching_sources"]
    base_fully = default["fully_included_sources"]

    osm_matching_entry = {"OSM": "Capacity >= 1"}

    target = countries if countries is not None else overlay_countries
    extra = {"target_countries": target} if target is not None else {}

    runs = [
        ("no_osm", get_config(
            **overlay_base,
            matching_sources=base_matching,
            fully_included_sources=base_fully,
            **extra,
        )),
        ("osm_matching", get_config(
            **overlay_base,
            matching_sources=base_matching + [osm_matching_entry],
            fully_included_sources=base_fully,
            **extra,
        )),
        ("osm_only", get_config(
            **overlay_base,
            matching_sources=base_matching + [osm_matching_entry],
            fully_included_sources=base_fully + [osm_matching_entry],
            **extra,
        )),
        ("osm_full", get_config(
            **overlay_base,
            matching_sources=recommended["matching_sources"],
            fully_included_sources=recommended["fully_included_sources"],
            **extra,
        )),
    ]

    needs_osm = {"osm_matching", "osm_only", "osm_full"}
    osm_installed = False
    for label, config in runs:
        if label in skip:
            continue
        if label in needs_osm and not osm_installed:
            _install_osm()
            osm_installed = True
        _run(label, config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--countries",
        default="sample",
        help="'sample' (default, 10 countries), 'all' (overlay list), or comma-separated names",
    )
    parser.add_argument(
        "--skip",
        default="",
        help="comma-separated run labels to skip (e.g. 'no_osm')",
    )
    args = parser.parse_args()

    if args.countries == "all":
        countries = None
    elif args.countries == "sample":
        countries = SAMPLE_COUNTRIES
    else:
        countries = [c.strip() for c in args.countries.split(",")]

    main(countries, skip={s.strip() for s in args.skip.split(",") if s.strip()})

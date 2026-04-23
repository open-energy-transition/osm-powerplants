#!/usr/bin/env python3
# SPDX-FileCopyrightText: Contributors to osm-powerplants
#
# SPDX-License-Identifier: MIT

"""
Extract OSM power plants for a single named region.

Produces three outputs alongside the CSV (paths derived from ``-o``):

    <output>.csv                 — plants (via Units.to_dataframe)
    <output>_rejected.csv        — RejectionTracker.generate_report()
    <output>_rejected.geojson    — RejectionTracker.save_geojson()

Countries within a region are fetched in parallel across Overpass endpoints,
with per-country cache subdirectories so workers never clobber each other.
If the primary endpoint rejects a country (timeout, resource limit), the
worker falls back to the remaining mirrors before giving up.

Usage:
    python scripts/extract_region.py --region europe
    python scripts/extract_region.py --region oceania --clear-cache
    python scripts/extract_region.py --region southeastern_asia \\
        -o datasets/osm_southeastern_asia.csv --workers 8
"""

import argparse
import logging
import shutil
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from osm_powerplants import Units, get_cache_dir, get_config
from osm_powerplants.interface import validate_countries
from osm_powerplants.quality.rejection import RejectionTracker
from osm_powerplants.regions import REGIONS, get_region
from osm_powerplants.retrieval.client import OverpassAPIClient, OverpassAPIError
from osm_powerplants.workflow import Workflow

FALLBACK_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

logger = logging.getLogger("extract_region")


def clear_cache(cache_dir: Path) -> None:
    if cache_dir.exists():
        logger.info(f"clearing cache: {cache_dir}")
        shutil.rmtree(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)


def build_endpoint_list(configured_url: str | None) -> list[str]:
    endpoints = [configured_url] if configured_url else []
    endpoints += [e for e in FALLBACK_ENDPOINTS if e != configured_url]
    return endpoints


def process_country(
    name: str,
    iso: str,
    config: dict,
    cache_root: Path,
) -> tuple[Units, RejectionTracker]:
    """Fetch one country, trying fallback endpoints if primary fails."""
    api_cfg = config.get("overpass_api", {})
    country_cache = cache_root / iso
    country_cache.mkdir(parents=True, exist_ok=True)

    configured_url = api_cfg.get("api_url")
    last_exc: Exception = RuntimeError("no endpoints")
    for endpoint in build_endpoint_list(configured_url):
        try:
            tracker = RejectionTracker()
            units = Units()
            with OverpassAPIClient(
                cache_dir=str(country_cache),
                api_url=endpoint,
                timeout=api_cfg.get("timeout", 1800),
                max_retries=api_cfg.get("max_retries", 5),
                retry_delay=api_cfg.get("retry_delay", 90),
                show_progress=api_cfg.get("show_progress", False),
            ) as client:
                Workflow(
                    client=client,
                    rejection_tracker=tracker,
                    units=units,
                    config={**config, "cache_dir": str(country_cache)},
                ).process_country_data(name)
            return units, tracker
        except OverpassAPIError as e:
            logger.warning(f"  {iso}: {endpoint} failed ({e}) — trying next")
            last_exc = e
    raise last_exc


def _worker(name: str, iso: str, config: dict, cache_root: Path):
    units, tracker = process_country(name, iso, config, cache_root)
    logger.info(f"{iso} ({name}): {len(units)} plants, {tracker.get_total_count()} rejections")
    return units, tracker


def merge_tracker(target: RejectionTracker, source: RejectionTracker) -> None:
    """Append all rejected elements from ``source`` into ``target``.

    RejectionTracker has no native merge method; this replicates the
    manual dict-append pattern used historically in extract_europe.py.
    """
    for rej_list in source.rejected_elements.values():
        for rej in rej_list:
            target.rejected_elements.setdefault(rej.id, []).append(rej)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--region",
        required=True,
        choices=sorted(REGIONS),
        help="region key (see osm_powerplants.regions.REGIONS)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="output CSV path (default: datasets/osm_<region>.csv)",
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="wipe the OSM cache before processing",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="parallel Overpass workers (default: 4)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    output_csv = Path(args.output) if args.output else Path("datasets") / f"osm_{args.region}.csv"
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    rejected_csv = output_csv.with_name(f"{output_csv.stem}_rejected.csv")
    rejected_geojson = output_csv.with_name(f"{output_csv.stem}_rejected.geojson")

    config = get_config()
    cache_dir = Path(get_cache_dir(config))
    if args.clear_cache:
        clear_cache(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    country_names = get_region(args.region)
    valid_countries, country_codes = validate_countries(
        country_names, config.get("omitted_countries", [])
    )
    logger.info(
        f"region={args.region} countries={len(valid_countries)} "
        f"cache={cache_dir} output={output_csv}"
    )

    all_units = Units()
    all_rejections = RejectionTracker()
    failed: list[tuple[str, str, str]] = []

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(_worker, name, country_codes[name], config, cache_dir): name
            for name in valid_countries
        }
        for future in as_completed(futures):
            name = futures[future]
            iso = country_codes[name]
            try:
                units, tracker = future.result()
                for unit in units:
                    all_units.add_unit(unit)
                merge_tracker(all_rejections, tracker)
            except Exception as e:
                logger.error(f"FAIL {iso} ({name}): {e}")
                logger.debug(traceback.format_exc())
                failed.append((iso, name, str(e)))

    df = all_units.to_dataframe()
    df.to_csv(output_csv, index=False)
    logger.info(f"wrote {len(df)} plants → {output_csv}")

    # Rejections CSV (may be empty)
    rej_df = all_rejections.generate_report()
    rej_df.to_csv(rejected_csv, index=False)
    logger.info(f"wrote {len(rej_df)} rejected rows → {rejected_csv}")

    # Rejections GeoJSON (only rows with coordinates)
    all_rejections.save_geojson(str(rejected_geojson))

    print()
    print(f"region:    {args.region}")
    print(f"countries: {len(valid_countries)} processed, {len(failed)} failed")
    print(f"plants:    {len(df):,}")
    if "Capacity" in df.columns and not df.empty:
        total_mw = df["Capacity"].sum()
        print(f"capacity:  {total_mw:,.0f} MW ({total_mw / 1000:,.1f} GW)")
    print(f"rejected:  {all_rejections.get_total_count():,}")

    if failed:
        # Partial-failure is expected (transient Overpass mirror issues on
        # individual countries). Surface the list prominently but still
        # exit 0: the region CSV is usable and the CI artifact should
        # upload. The next monthly run picks up the missed countries.
        print("\nfailed countries (will retry next run):")
        for iso, name, err in failed:
            print(f"  {iso}  {name}: {err}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

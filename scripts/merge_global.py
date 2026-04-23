#!/usr/bin/env python3
# SPDX-FileCopyrightText: Contributors to osm-powerplants
#
# SPDX-License-Identifier: MIT

"""
Merge all regional datasets into a single global dataset.

Inputs (all under ``datasets/``):
    osm_<region>.csv                 — per-region plants
    osm_<region>_rejected.csv        — per-region rejection report
    osm_<region>_rejected.geojson    — per-region rejected plants on map

Outputs (all at repo root):
    osm_global.csv                        — concatenated plants
    osm_global_rejected_plants.csv        — concatenated rejection report
    osm_global_rejected_plants.geojson    — merged FeatureCollection

The frozen root-level ``osm_europe.csv`` is intentionally untouched — it is
retained for back-compat with the current PPM config until the PPM PR that
repoints to ``osm_global.csv`` merges.

Usage:
    python scripts/merge_global.py
    python scripts/merge_global.py --datasets-dir datasets --output-dir .
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import pandas as pd

logger = logging.getLogger("merge_global")


def _plant_csvs(datasets_dir: Path) -> list[Path]:
    # plants CSVs are osm_<region>.csv; exclude *_rejected.csv
    return sorted(
        p for p in datasets_dir.glob("osm_*.csv")
        if not p.stem.endswith("_rejected")
    )


def _rejected_csvs(datasets_dir: Path) -> list[Path]:
    return sorted(datasets_dir.glob("osm_*_rejected.csv"))


def _rejected_geojsons(datasets_dir: Path) -> list[Path]:
    return sorted(datasets_dir.glob("osm_*_rejected.geojson"))


def merge_csvs(paths: list[Path], output: Path, label: str) -> int:
    if not paths:
        logger.warning(f"no {label} CSVs found")
        output.write_text("")
        return 0
    frames = []
    for p in paths:
        if p.stat().st_size == 0:
            continue
        try:
            df = pd.read_csv(p)
        except pd.errors.EmptyDataError:
            continue
        if not df.empty:
            frames.append(df)
    if not frames:
        logger.warning(f"all {label} CSVs were empty")
        output.write_text("")
        return 0
    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(output, index=False)
    logger.info(f"{label}: merged {len(frames)} files → {output} ({len(combined)} rows)")
    return len(combined)


def merge_geojsons(paths: list[Path], output: Path) -> int:
    features: list[dict] = []
    files_with_features = 0
    for p in paths:
        try:
            data = json.loads(p.read_text())
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f"skipping {p}: {e}")
            continue
        region_features = data.get("features", [])
        if region_features:
            features.extend(region_features)
            files_with_features += 1
    merged = {"type": "FeatureCollection", "features": features}
    with output.open("w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False)
    logger.info(
        f"rejected geojson: merged {files_with_features} files → {output} "
        f"({len(features)} features)"
    )
    return len(features)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--datasets-dir",
        default="datasets",
        help="directory containing per-region outputs (default: datasets)",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="directory for global outputs (default: repo root)",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    datasets_dir = Path(args.datasets_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not datasets_dir.is_dir():
        logger.error(f"datasets directory not found: {datasets_dir}")
        return 2

    plant_paths = _plant_csvs(datasets_dir)
    rejected_csv_paths = _rejected_csvs(datasets_dir)
    rejected_geojson_paths = _rejected_geojsons(datasets_dir)

    logger.info(
        f"inputs: {len(plant_paths)} plant CSVs, "
        f"{len(rejected_csv_paths)} rejection CSVs, "
        f"{len(rejected_geojson_paths)} rejection GeoJSONs"
    )

    plants = merge_csvs(plant_paths, output_dir / "osm_global.csv", "plants")
    rejected = merge_csvs(
        rejected_csv_paths,
        output_dir / "osm_global_rejected_plants.csv",
        "rejected",
    )
    rejected_geom = merge_geojsons(
        rejected_geojson_paths,
        output_dir / "osm_global_rejected_plants.geojson",
    )

    print()
    print(f"plants:             {plants:,}")
    print(f"rejected (csv):     {rejected:,}")
    print(f"rejected (geojson): {rejected_geom:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

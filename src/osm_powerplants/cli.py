# SPDX-FileCopyrightText: Contributors to osm-powerplants
#
# SPDX-License-Identifier: MIT

"""
Command-line interface for osm-powerplants.
"""

import argparse
import logging
import sys

from . import __version__
from .core import get_cache_dir, get_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="osm-powerplants",
        description="Extract power plant data from OpenStreetMap",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Process command
    process_parser = subparsers.add_parser(
        "process",
        help="Process OSM data for countries",
    )
    process_parser.add_argument(
        "countries",
        nargs="+",
        help="Countries to process (names or ISO codes)",
    )
    process_parser.add_argument(
        "-o",
        "--output",
        default="osm_data.csv",
        help="Output CSV file (default: osm_data.csv)",
    )
    process_parser.add_argument(
        "-c",
        "--config",
        help="Path to config file",
    )
    process_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force refresh from API (ignore all cache)",
    )
    process_parser.add_argument(
        "--update",
        action="store_true",
        help="Reprocess from API cache (skip CSV cache)",
    )

    # Info command
    info_parser = subparsers.add_parser(
        "info",
        help="Show configuration info",
    )
    info_parser.add_argument(
        "-c",
        "--config",
        help="Path to config file",
    )

    args = parser.parse_args()

    if args.command == "process":
        run_process(args)
    elif args.command == "info":
        run_info(args)
    else:
        parser.print_help()
        sys.exit(1)


def run_process(args):
    """Run the process command."""
    import os

    from .interface import process_countries

    config = get_config(args.config)
    cache_dir = get_cache_dir(config)
    csv_cache_path = os.path.join(str(cache_dir), "osm_data.csv")

    if args.force_refresh:
        config["force_refresh"] = True

    logger.info(f"Processing countries: {args.countries}")
    logger.info(f"Cache directory: {cache_dir}")

    try:
        df = process_countries(
            countries=args.countries,
            csv_cache_path=csv_cache_path,
            cache_dir=str(cache_dir),
            update=args.update,
            osm_config=config,
        )

        if df.empty:
            logger.warning("No data found for specified countries")
            sys.exit(1)

        df.to_csv(args.output, index=False)
        logger.info(f"Saved {len(df)} power plants to {args.output}")

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        sys.exit(1)


def run_info(args):
    """Run the info command."""
    from .core import get_default_config_path

    config = get_config(args.config)
    cache_dir = get_cache_dir(config)
    config_path = args.config or get_default_config_path()

    print(f"Config file: {config_path}")
    print(f"Cache directory: {cache_dir}")
    print(f"Config loaded: {bool(config)}")
    if config:
        print(f"  - force_refresh: {config.get('force_refresh', False)}")
        print(f"  - plants_only: {config.get('plants_only', True)}")


if __name__ == "__main__":
    main()

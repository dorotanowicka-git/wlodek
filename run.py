#!/usr/bin/env python3
"""CLI entry point for the AdTech segment proposal pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Ensure the repo root is on sys.path when run directly
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import run


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AdTech daily segment proposal pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                          # run for today
  python run.py --date 2025-06-01        # backfill a specific date
  python run.py --dry-run                # analyse but don't write files
  python run.py --vertical gaming --vertical crypto  # add extra verticals
  python run.py --output-dir /tmp/segs   # override output directory
  python run.py --config custom.yaml     # use a different config file
""",
    )
    parser.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        default=None,
        help="Run date (default: today UTC).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch signals and run analysis but do not write output files.",
    )
    parser.add_argument(
        "--vertical",
        dest="verticals",
        action="append",
        metavar="VERTICAL",
        default=None,
        help="Add extra advertiser vertical (repeatable).",
    )
    parser.add_argument(
        "--output-dir",
        metavar="DIR",
        default=None,
        help="Override the output directory from config.",
    )
    parser.add_argument(
        "--config",
        metavar="FILE",
        default="config.yaml",
        help="Path to the YAML config file (default: config.yaml).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    count = run(
        config_path=args.config,
        run_date=args.date,
        dry_run=args.dry_run,
        extra_verticals=args.verticals,
        output_dir=args.output_dir,
    )
    sys.exit(0 if count >= 0 else 1)


if __name__ == "__main__":
    main()

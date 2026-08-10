#!/usr/bin/env python3
"""Recompute and byte-compare the 504-row exactness-aware menu audit."""

from __future__ import annotations

import argparse
import concurrent.futures
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
RANGES = tuple((start, start + 63) for start in range(0, 504, 63))
EXCEPTIONS = ((154, 155), (365, 366))


def run(temporary, start, stop, bound):
    output = temporary / f"bound-{bound}-{start}-{stop}.json"
    subprocess.run(
        [
            sys.executable,
            str(HERE / "search_starved_exactness_menus.py"),
            "--bound", str(bound),
            "--start", str(start),
            "--stop", str(stop),
            "--timeout-ms", "30000",
            "--output", str(output),
        ],
        check=True,
    )
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--expected",
        type=Path,
        default=HERE / "starved_exactness_menu_audit.json",
    )
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="starved-exactness-menus-") as name:
        temporary = Path(name)
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            bound_one = list(
                pool.map(lambda interval: run(temporary, *interval, 1), RANGES)
            )
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            exceptions = list(
                pool.map(lambda interval: run(temporary, *interval, 2), EXCEPTIONS)
            )
        regenerated = temporary / "merged.json"
        subprocess.run(
            [
                sys.executable,
                str(HERE / "merge_starved_exactness_menus.py"),
                "--bound-one-shards", *map(str, bound_one),
                "--exception-shards", *map(str, exceptions),
                "--output", str(regenerated),
            ],
            check=True,
        )
        if regenerated.read_bytes() != args.expected.read_bytes():
            raise SystemExit("regenerated starved exactness-menu audit differs")
    print("PASS: starved_exactness_menu_audit.json byte-reproduces")


if __name__ == "__main__":
    main()

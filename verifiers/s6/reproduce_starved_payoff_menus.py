#!/usr/bin/env python3
"""Recompute bounded shards and byte-compare the starved payoff-menu audit."""

from __future__ import annotations

import argparse
import concurrent.futures
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
RANGES = ((0, 71), (71, 142), (142, 212), (212, 282))


def run(temporary, side, start, stop, filters=()):
    output = temporary / f"{side}-{start}-{stop}.json"
    command = [
        sys.executable,
        str(HERE / "search_starved_payoff_menus.py"),
        "--bound", "2",
        "--side", side,
        "--start", str(start),
        "--stop", str(stop),
        "--timeout-ms", "30000",
    ]
    if filters:
        command.extend(["--filter-min-sat-shards", *map(str, filters)])
    command.extend(["--output", str(output)])
    subprocess.run(command, check=True)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--expected", type=Path, default=HERE / "starved_payoff_menu_audit.json"
    )
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="starved-payoff-menus-") as name:
        temporary = Path(name)
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            minimum = list(pool.map(lambda interval: run(temporary, "min", *interval), RANGES))
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            maximum = list(
                pool.map(
                    lambda interval: run(temporary, "max", *interval, filters=minimum),
                    RANGES,
                )
            )
        regenerated = temporary / "merged.json"
        subprocess.run(
            [
                sys.executable,
                str(HERE / "merge_starved_payoff_menus.py"),
                "--min-shards", *map(str, minimum),
                "--max-shards", *map(str, maximum),
                "--output", str(regenerated),
            ],
            check=True,
        )
        if regenerated.read_bytes() != args.expected.read_bytes():
            raise SystemExit("regenerated starved payoff-menu audit differs")
    print("PASS: starved_payoff_menu_audit.json byte-reproduces")


if __name__ == "__main__":
    main()

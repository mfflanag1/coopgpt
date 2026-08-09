#!/usr/bin/env python3
"""Recompute and merge the complete Lmin dependency audit in bounded shards."""

from __future__ import annotations

import argparse
import concurrent.futures
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
RANGES = {
    "critical": ((0, 225), (225, 450), (450, 675), (675, 901)),
    "direction": ((0, 80), (80, 160), (160, 240), (240, 322)),
    "menu": ((0, 25), (25, 50), (50, 75), (75, 97)),
}


def run(command):
    return subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    ).stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if args.workers <= 0:
        raise ValueError("workers must be positive")
    with tempfile.TemporaryDirectory(prefix="positive-lmin-layers-") as temporary:
        root = Path(temporary)
        jobs = []
        shards = []
        for section, ranges in RANGES.items():
            for start, stop in ranges:
                shard = root / f"{section}-{start}-{stop}.json"
                shards.append(shard)
                jobs.append(
                    [
                        sys.executable,
                        str(HERE / "audit_positive_lmin_handover_layers.py"),
                        "--section",
                        section,
                        "--start",
                        str(start),
                        "--stop",
                        str(stop),
                        "--output",
                        str(shard),
                    ]
                )
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            for output in pool.map(run, jobs):
                print(output, flush=True)
        merge = [
            sys.executable,
            str(HERE / "merge_positive_lmin_handover_layers.py"),
            *map(str, shards),
            "--output",
            str(args.output),
        ]
        print(run(merge))


if __name__ == "__main__":
    main()

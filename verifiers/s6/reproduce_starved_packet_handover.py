#!/usr/bin/env python3
"""Recompute four bounded shards and byte-compare the starved handover audit."""

from __future__ import annotations

import argparse
import concurrent.futures
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
RANGES = ((0, 126), (126, 252), (252, 378), (378, 504))


def run_shard(temporary: Path, start: int, stop: int):
    output = temporary / f"shard-{start}-{stop}.json"
    subprocess.run(
        [
            sys.executable,
            str(HERE / "audit_starved_packet_handover.py"),
            "--start",
            str(start),
            "--stop",
            str(stop),
            "--output",
            str(output),
        ],
        check=True,
    )
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--expected",
        type=Path,
        default=HERE / "starved_packet_handover_audit.json",
    )
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="starved-packet-handover-") as name:
        temporary = Path(name)
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            shards = list(
                pool.map(
                    lambda interval: run_shard(temporary, *interval),
                    RANGES,
                )
            )
        regenerated = temporary / "merged.json"
        subprocess.run(
            [
                sys.executable,
                str(HERE / "merge_starved_packet_handover.py"),
                *map(str, shards),
                "--output",
                str(regenerated),
            ],
            check=True,
        )
        if regenerated.read_bytes() != args.expected.read_bytes():
            raise SystemExit("regenerated starved packet handover differs")
    print("PASS: starved_packet_handover_audit.json byte-reproduces")


if __name__ == "__main__":
    main()

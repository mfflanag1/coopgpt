#!/usr/bin/env python3
"""Recompute and byte-compare the starved payoff-direction discovery audit."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--expected",
        type=Path,
        default=HERE / "starved_refinement_direction_audit.json",
    )
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="starved-direction-") as temporary:
        regenerated = Path(temporary) / "audit.json"
        subprocess.run(
            [
                sys.executable,
                str(HERE / "audit_starved_refinement_direction.py"),
                "--output",
                str(regenerated),
            ],
            check=True,
        )
        if regenerated.read_bytes() != args.expected.read_bytes():
            raise SystemExit("regenerated starved direction audit differs")
    print("PASS: starved_refinement_direction_audit.json byte-reproduces")


if __name__ == "__main__":
    main()

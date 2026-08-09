#!/usr/bin/env python3
"""Recompute and byte-compare the Lmin direction-pattern mapping audit."""

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
        default=HERE / "positive_lmin_direction_patterns_audit.json",
    )
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="lmin-direction-patterns-") as temporary:
        regenerated = Path(temporary) / "audit.json"
        subprocess.run(
            [
                sys.executable,
                str(HERE / "audit_positive_lmin_direction_patterns.py"),
                "--output",
                str(regenerated),
            ],
            check=True,
        )
        if regenerated.read_bytes() != args.expected.read_bytes():
            raise SystemExit("regenerated direction-pattern audit differs")
    print("PASS: positive_lmin_direction_patterns_audit.json byte-reproduces")


if __name__ == "__main__":
    main()

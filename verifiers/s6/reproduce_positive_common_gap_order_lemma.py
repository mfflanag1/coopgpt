#!/usr/bin/env python3
"""Recompute and byte-compare the common-gap order-lemma map."""

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
        default=HERE / "positive_common_gap_order_lemma_audit.json",
    )
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="common-gap-order-") as temporary:
        regenerated = Path(temporary) / "audit.json"
        subprocess.run(
            [
                sys.executable,
                str(HERE / "audit_positive_common_gap_order_lemma.py"),
                "--output",
                str(regenerated),
            ],
            check=True,
        )
        if regenerated.read_bytes() != args.expected.read_bytes():
            raise SystemExit("regenerated common-gap order audit differs")
    print("PASS: positive_common_gap_order_lemma_audit.json byte-reproduces")


if __name__ == "__main__":
    main()

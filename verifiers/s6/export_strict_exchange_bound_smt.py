#!/usr/bin/env python3
"""Freeze one strict-distance sign-count case as exact SMT-LIB."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from export_core_closure_smt import qf_lra_smt2  # noqa: E402
from minimize_equality_exchange_directions import rebuilt_solver_from_row  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit = json.loads((HERE / "strict_exchange_direction_cores.json").read_text())
    matches = [row for row in audit["rows"] if row["case"] == args.case]
    if len(matches) != 1:
        raise ValueError(f"expected one strict audit row for {args.case!r}")
    args.output.write_text(qf_lra_smt2(rebuilt_solver_from_row(matches[0])))


if __name__ == "__main__":
    main()

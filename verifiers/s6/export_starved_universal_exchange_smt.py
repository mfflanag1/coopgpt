#!/usr/bin/env python3
"""Freeze one table-free starved exchange branch as exact SMT-LIB."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from audit_starved_universal_exchange_lemma import abstract_solver  # noqa: E402
from export_core_closure_smt import qf_lra_smt2  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--side", choices=("min", "max"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    solver, *_ = abstract_solver(args.side, 0)
    args.output.write_text(qf_lra_smt2(solver))


if __name__ == "__main__":
    main()

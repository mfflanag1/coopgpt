#!/usr/bin/env python3
"""Freeze one abstract Lmin single-direction pattern as exact SMT-LIB."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from audit_positive_lmin_direction_patterns import abstract_solver  # noqa: E402
from export_core_closure_smt import qf_lra_smt2  # noqa: E402


def load_case(case: str, source: Path):
    payload = json.loads(source.read_text())
    matches = [item for item in payload["proof_cases"] if item["case"] == case]
    if len(matches) != 1:
        raise ValueError(f"expected one proof case named {case!r}")
    return matches[0]


def build(case: str, source: Path):
    item = load_case(case, source)
    key = (
        tuple(item["roles"]),
        tuple(item["direction"]),
        tuple(item["common_pair_positions"]),
    )
    x_relations = tuple(
        tuple(relation[1:]) for relation in item["relations"] if relation[0] == "x"
    )
    z_relations = tuple(
        tuple(relation[1:]) for relation in item["relations"] if relation[0] == "z"
    )
    return abstract_solver(key, x_relations, z_relations)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument(
        "--source",
        type=Path,
        default=HERE / "positive_lmin_direction_patterns_audit.json",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(qf_lra_smt2(build(args.case, args.source)))


if __name__ == "__main__":
    main()

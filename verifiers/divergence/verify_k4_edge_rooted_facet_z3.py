#!/usr/bin/env python3
"""Independent exact-LRA replay of the first K4-edge rooted facet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import z3


SUPPORT = (1, 15, 51, 85, 105)


def exceptional_feasible(exceptional: int) -> bool:
    weights = [z3.Real(f"w_{exceptional}_{index}") for index in range(len(SUPPORT))]
    rho = z3.Real(f"rho_{exceptional}")
    solver = z3.Solver()
    solver.add(*(weight >= 0 for weight in weights))
    for player in range(7):
        solver.add(
            z3.Sum(
                *[
                    weight * ((coalition >> player) & 1)
                    for coalition, weight in zip(SUPPORT, weights)
                ]
            )
            == rho + ((exceptional >> player) & 1)
        )
    status = solver.check()
    if status == z3.unknown:
        raise AssertionError("exact-LRA facet replay returned unknown")
    return status == z3.sat


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    feasible = [coalition for coalition in range(1, 128) if exceptional_feasible(coalition)]
    expected = list(SUPPORT) + [127]
    if feasible != expected:
        raise AssertionError({"independent exceptional-set classification changed": feasible})
    report = {
        "status": "independent exact-LRA K4-edge rooted facet replay passed",
        "z3_version": z3.get_version_string(),
        "support": list(SUPPORT),
        "candidate_exceptional_sets": 127,
        "feasible_exceptional_sets": feasible,
        "unsupported_proper_candidates_proved_infeasible": 121,
        "new_proper_exceptional_sets": 0,
        "classification": "indecomposable exact-cone facet",
        "scope": (
            "independent exceptional-set feasibility formulation for the first "
            "seven-player member; the dimension-free graph case analysis is primary"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

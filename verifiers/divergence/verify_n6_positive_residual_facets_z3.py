#!/usr/bin/env python3
"""Independent exact-LRA replay of the five n=6 residual facet orbits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import z3


SUPPORTS = (
    (1, 3, 5, 9, 17, 33),
    (1, 3, 5, 9, 49),
    (1, 3, 5, 25, 41, 49),
    (1, 3, 5, 25, 41, 51),
    (1, 3, 13, 53, 57),
)


def feasible(support: tuple[int, ...], exceptional: int, orbit: int) -> bool:
    weights = [z3.Real(f"w_{orbit}_{exceptional}_{i}") for i in range(len(support))]
    rho = z3.Real(f"rho_{orbit}_{exceptional}")
    solver = z3.Solver()
    solver.add(*(weight >= 0 for weight in weights))
    for player in range(6):
        solver.add(
            z3.Sum(
                *[
                    weight * ((coalition >> player) & 1)
                    for coalition, weight in zip(support, weights)
                ]
            )
            == rho + ((exceptional >> player) & 1)
        )
    status = solver.check()
    if status == z3.unknown:
        raise AssertionError("exact-LRA orbit replay returned unknown")
    return status == z3.sat


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rows = []
    total_infeasible = 0
    for orbit, support in enumerate(SUPPORTS):
        feasible_sets = [
            coalition for coalition in range(1, 64) if feasible(support, coalition, orbit)
        ]
        expected = sorted((*support, 63))
        if feasible_sets != expected:
            raise AssertionError(
                {"orbit": orbit, "unexpected feasible exceptional sets": feasible_sets}
            )
        infeasible = 62 - len(support)
        total_infeasible += infeasible
        rows.append(
            {
                "support": list(support),
                "feasible_exceptional_sets": feasible_sets,
                "unsupported_proper_candidates_proved_infeasible": infeasible,
            }
        )
    report = {
        "status": "independent exact-LRA n=6 residual facet-orbit replay passed",
        "z3_version": z3.get_version_string(),
        "facet_orbits": len(rows),
        "unsupported_proper_candidates_proved_infeasible": total_infeasible,
        "new_proper_exceptional_sets": 0,
        "rows": rows,
        "scope": (
            "independent exceptional-set feasibility formulation for the five "
            "finite atlas orbits; not a six-player domain classification"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

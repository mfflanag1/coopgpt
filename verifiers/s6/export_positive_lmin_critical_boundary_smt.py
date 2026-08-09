#!/usr/bin/env python3
"""Freeze eight globally Lmin-ordered critical-boundary lemmas as SMT-LIB."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from export_core_closure_smt import qf_lra_smt2  # noqa: E402


# (global Lmin role word, common excluded-player positions, Lmax relation)
CASES = {
    "nnpppr-low": (("N", "N", "P", "P", "P", "R"), (2, 3), ("le", 2, 5)),
    "nnpppr-outer": (("N", "N", "P", "P", "P", "R"), (2, 4), ("eq", 4, 5)),
    "nnpppr-high": (("N", "N", "P", "P", "P", "R"), (3, 4), ("eq", 4, 5)),
    "npnppr-low": (("N", "P", "N", "P", "P", "R"), (1, 3), ("le", 3, 5)),
    "npnppr-outer": (("N", "P", "N", "P", "P", "R"), (1, 4), ("eq", 4, 5)),
    "npnppr-high": (("N", "P", "N", "P", "P", "R"), (3, 4), ("eq", 4, 5)),
    "nppnpr-outer": (("N", "P", "P", "N", "P", "R"), (1, 4), ("eq", 4, 5)),
    "nppnpr-high": (("N", "P", "P", "N", "P", "R"), (2, 4), ("eq", 4, 5)),
}


def point_sum(point, players):
    return z3.Sum(*[point[player] for player in players])


def build(case: str) -> z3.Solver:
    roles, common_pair, relation = CASES[case]
    solver = z3.Solver()
    x = [z3.Real(f"lmin_boundary_x_{i}") for i in range(6)]
    z = [z3.Real(f"lmin_boundary_z_{i}") for i in range(6)]
    solver.add(
        z3.Sum(x) == 1,
        z3.Sum(z) == 1,
        x[0] >= 0,
        z[0] >= 0,
        *[x[i] <= x[i + 1] for i in range(5)],
    )
    for player, role in enumerate(roles):
        solver.add(x[player] >= z[player] if role in ("N", "R") else z[player] >= x[player])
    operator, first, second = relation
    solver.add(z[first] == z[second] if operator == "eq" else z[first] <= z[second])

    middle = tuple(player for player, role in enumerate(roles) if role == "P")
    rich = roles.index("R")
    triples = {
        excluded: tuple(player for player in middle if player != excluded) + (rich,)
        for excluded in middle
    }
    for excluded in middle:
        solver.add(
            point_sum(z, triples[excluded]) >= point_sum(x, triples[excluded])
        )
    for excluded in common_pair:
        solver.add(
            point_sum(z, triples[excluded]) == point_sum(x, triples[excluded])
        )
    for zero in range(6):
        witness = [z3.Real(f"lmin_boundary_q_{zero}_{i}") for i in range(6)]
        solver.add(
            z3.Sum(witness) == 1,
            witness[zero] == 0,
            *[coordinate >= 0 for coordinate in witness],
        )
        for excluded in middle:
            solver.add(
                point_sum(witness, triples[excluded])
                >= point_sum(x, triples[excluded])
            )
    positive = [player for player, role in enumerate(roles) if role in ("N", "R")]
    distance = 2 * z3.Sum(*[x[player] - z[player] for player in positive])
    solver.add(distance > z3.RealVal("2/3"))
    return solver


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=tuple(CASES), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(qf_lra_smt2(build(args.case)))


if __name__ == "__main__":
    main()

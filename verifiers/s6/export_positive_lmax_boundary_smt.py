#!/usr/bin/env python3
"""Freeze one abstract distance-sensitive Lmax blocker lemma as SMT-LIB."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from export_core_closure_smt import qf_lra_smt2  # noqa: E402


# Roles: 0=n (decreased poor), 1=j, 2=n' (increased poor),
# 3=k, 4=l, 5=r.  Players j,k are the common excluded-player pair.
CASES = {
    "n-l": (0, 4),
    "n-j-k-r": (0, 1, 3, 5),
    "n-j-l-r": (0, 1, 4, 5),
    "n-k-l-r": (0, 3, 4, 5),
}


def point_sum(point, players):
    return z3.Sum(*[point[player] for player in players])


def build(case: str) -> z3.Solver:
    coalition = CASES[case]
    solver = z3.Solver()
    x = [z3.Real(f"boundary_x_{i}") for i in range(6)]
    z = [z3.Real(f"boundary_z_{i}") for i in range(6)]
    solver.add(
        z3.Sum(x) == 1,
        z3.Sum(z) == 1,
        x[0] >= 0,
        z[0] >= 0,
        x[0] <= x[1],
        x[1] <= x[2],
        x[2] <= x[3],
        x[3] <= x[4],
        x[4] <= x[5],
        z[2] <= z[0],
        z[0] <= z[1],
        z[1] <= z[5],
        z[5] <= z[3],
        z[3] == z[4],
        x[0] >= z[0],
        z[1] >= x[1],
        x[2] >= z[2],
        z[3] >= x[3],
        z[4] >= x[4],
        x[5] >= z[5],
    )
    middle = (1, 3, 4)
    rich = 5
    for excluded in (1, 3):
        triple = tuple(player for player in middle if player != excluded) + (rich,)
        solver.add(point_sum(z, triple) == point_sum(x, triple))

    witnesses = []
    for zero in range(6):
        witness = [z3.Real(f"boundary_q_{zero}_{i}") for i in range(6)]
        witnesses.append(witness)
        solver.add(
            z3.Sum(witness) == 1,
            witness[zero] == 0,
            *[coordinate >= 0 for coordinate in witness],
        )
    for excluded in middle:
        triple = tuple(player for player in middle if player != excluded) + (rich,)
        for witness in witnesses:
            solver.add(point_sum(witness, triple) >= point_sum(x, triple))

    solver.add(
        point_sum(x, coalition) >= point_sum(z, coalition),
        *[
            point_sum(witness, coalition) >= point_sum(z, coalition)
            for witness in witnesses
        ],
    )
    distance = 2 * ((x[0] - z[0]) + (x[2] - z[2]) + (x[5] - z[5]))
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

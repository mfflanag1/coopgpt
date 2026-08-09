#!/usr/bin/env python3
"""Freeze the abstract 16-row Lmax critical-boundary lemma as SMT-LIB."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from export_core_closure_smt import qf_lra_smt2  # noqa: E402


def point_sum(point, players):
    return z3.Sum(*[point[player] for player in players])


def build() -> z3.Solver:
    # Roles: 0,1 are poor; 2,3 are the common excluded-player pair;
    # 4 is the third P player; 5 is rich.
    solver = z3.Solver()
    x = [z3.Real(f"critical_boundary_x_{i}") for i in range(6)]
    z = [z3.Real(f"critical_boundary_z_{i}") for i in range(6)]
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
        z[0] <= z[2],
        z[1] <= z[2],
        z[2] <= z[5],
        z[5] <= z[3],
        z[3] == z[4],
        x[0] >= z[0],
        x[1] >= z[1],
        z[2] >= x[2],
        z[3] >= x[3],
        z[4] >= x[4],
        x[5] >= z[5],
    )
    middle = (2, 3, 4)
    rich = 5
    for excluded in (2, 3):
        triple = tuple(player for player in middle if player != excluded) + (rich,)
        solver.add(point_sum(z, triple) == point_sum(x, triple))

    witnesses = []
    for zero in range(6):
        witness = [z3.Real(f"critical_boundary_q_{zero}_{i}") for i in range(6)]
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

    distance = 2 * ((x[0] - z[0]) + (x[1] - z[1]) + (x[5] - z[5]))
    solver.add(distance > z3.RealVal("2/3"))
    return solver


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(qf_lra_smt2(build()))


if __name__ == "__main__":
    main()

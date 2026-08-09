#!/usr/bin/env python3
"""Classify the positive profile's coarse-or-one-split critical residue.

The human critical-residue theorem forces all three P-pair-plus-r triples to
be Lmin-tight and at least two to be common.  On the eleven hand-net survivors
with at most one additional stratum, those conditions, the r-singleton
witness, and the strict cross-cell signs inherited from the canonical pair
eliminate nine types.  Two Lmin-split types remain, and one explicit
Lmin-improving direction eliminates each.  The accepted full-staged generator
encoding is checked as a control.

This is a proof-discovery and finite-reduction audit.  Its Z3 UNSAT verdicts
are not independently checked proof objects, and the one-split neighborhood
does not cover simultaneous splits.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import nsix  # noqa: E402
from audit_equality_refinement_neighborhood import (  # noqa: E402
    COARSE_TYPES,
    contiguous_groups,
    refines,
)
from core_closure_pipeline import pipeline2_generator_normal_form  # noqa: E402


N = 6
POSITIVE = COARSE_TYPES[1]


def q(value):
    return z3.RealVal(f"{value.numerator}/{value.denominator}")


def point_sum(point, players):
    terms = [point[i] for i in players]
    return z3.Sum(terms) if terms else z3.RealVal(0)


def critical_solver(index, configuration):
    r = tuple(configuration[0])
    c = tuple(configuration[1])
    table = tuple(tuple(row) for row in configuration[2])
    solver = z3.Solver()
    lmin_levels, lmax_levels = nsix.levels(N, r, c, solver)
    cell = nsix.layout(N, r, c, table)
    x = [lmin_levels[cell[i][0]] for i in range(N)]
    z = [lmax_levels[cell[i][1]] for i in range(N)]

    row_groups = contiguous_groups(r, POSITIVE["lmin"])
    column_groups = contiguous_groups(c, POSITIVE["lmax"])
    P = [
        i
        for i, (row, column) in enumerate(cell)
        if row in row_groups[0] and column in column_groups[1]
    ]
    poor = [
        i
        for i, (row, column) in enumerate(cell)
        if row in row_groups[0] and column in column_groups[0]
    ]
    rich = [
        i
        for i, (row, column) in enumerate(cell)
        if row in row_groups[1] and column in column_groups[1]
    ]
    assert len(poor) == 2 and len(P) == 3 and len(rich) == 1
    rich = rich[0]

    # These signs are strict at the canonical pair and therefore persist in
    # the first-crossing neighborhood.  A refinement table alone does not
    # encode them; omitting them admits remote, irrelevant SAT points.
    solver.add(*[x[i] > z[i] for i in poor])
    solver.add(*[z[i] > x[i] for i in P])
    solver.add(x[rich] > z[rich])

    witness = [z3.Real(f"critical_q_{index}_{i}") for i in range(N)]
    solver.add(
        z3.Sum(witness) == 1,
        witness[rich] == 0,
        *[coordinate >= 0 for coordinate in witness],
    )
    triples = []
    for excluded in P:
        triple = tuple(i for i in P if i != excluded) + (rich,)
        triples.append(triple)
        # Every triple is Lmin-tight, so every core witness and Lmax dominate
        # its Lmin sum.
        solver.add(point_sum(witness, triple) >= point_sum(x, triple))
        solver.add(point_sum(z, triple) >= point_sum(x, triple))

    # At least two triples are common tight.
    solver.add(
        z3.Or(
            *[
                z3.And(
                    *[
                        point_sum(z, triples[k]) == point_sum(x, triples[k])
                        for k in pair
                    ]
                )
                for pair in ((0, 1), (0, 2), (1, 2))
            ]
        )
    )
    distance = z3.Sum(
        *[
            table[row][column]
            * z3.Abs(lmin_levels[row] - lmax_levels[column])
            for row in range(len(r))
            for column in range(len(c))
            if table[row][column]
        ]
    )
    solver.add(distance > q(F(2, 3)))
    return solver, {
        "P_players": P,
        "poor_players": poor,
        "rich_player": rich,
        "triple_masks": [sum(1 << i for i in triple) for triple in triples],
    }


def direction_blocker_verdict(index, configuration, direction):
    solver, _ = critical_solver(index, configuration)
    r = tuple(configuration[0])
    c = tuple(configuration[1])
    table = tuple(tuple(row) for row in configuration[2])
    cell = nsix.layout(N, r, c, table)
    x = [z3.Real(f"m{cell[i][0]}") for i in range(N)]
    z = [z3.Real(f"M{cell[i][1]}") for i in range(N)]
    witness = [z3.Real(f"critical_q_{index}_{i}") for i in range(N)]
    blockers = []
    for coalition in range(1, (1 << N) - 1):
        if sum(direction[i] for i in range(N) if coalition >> i & 1) >= 0:
            continue
        players = tuple(i for i in range(N) if coalition >> i & 1)
        blockers.append(
            z3.And(
                point_sum(z, players) >= point_sum(x, players),
                point_sum(witness, players) >= point_sum(x, players),
            )
        )
    solver.add(z3.Or(*blockers))
    return solver.check()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--triage", type=Path, default=HERE / "triage32.json")
    args = parser.parse_args()

    triage = json.loads(args.triage.read_text())
    rows = []
    for index, configuration in enumerate(triage["survivors"]):
        r = tuple(configuration[0])
        c = tuple(configuration[1])
        table = tuple(tuple(row) for row in configuration[2])
        if not refines(r, c, table, POSITIVE):
            continue
        if (len(r) - 2) + (len(c) - 2) > 1:
            continue

        critical, labels = critical_solver(index, configuration)
        critical_verdict = critical.check()
        full = pipeline2_generator_normal_form(
            N, r, c, table, F(2, 3), fail=True
        )["solver"]
        full_verdict = full.check()
        assert full_verdict == z3.unsat
        row = {
                "survivor_index": index,
                "configuration": configuration,
                **labels,
                "critical_triples_plus_exactness": str(critical_verdict),
                "full_staged_generator_system": str(full_verdict),
                "requires_lmin_optimality_beyond_critical_algebra": (
                    critical_verdict == z3.sat
                ),
            }
        direction = {
            1442: (0, 1, 1, -1, 1, -2),
            2268: (0, 1, 1, 1, -1, -2),
        }.get(index)
        if direction is not None:
            direction_verdict = direction_blocker_verdict(
                index, configuration, direction
            )
            assert direction_verdict == z3.unsat
            row["explicit_lmin_improving_direction"] = direction
            row["eligible_negative_blocker_verdict"] = str(direction_verdict)
        rows.append(row)

    assert len(rows) == 11
    residual = [
        row
        for row in rows
        if row["requires_lmin_optimality_beyond_critical_algebra"]
    ]
    assert [row["survivor_index"] for row in residual] == [1442, 2268]
    report = {
        "status": (
            "exact one-split finite reduction; solver evidence, not independent "
            "proof objects and not a simultaneous-split theorem"
        ),
        "coarse_type": POSITIVE["name"],
        "coarse_or_one_split_hand_net_survivors": len(rows),
        "eliminated_by_critical_triples_and_exactness": sum(
            row["critical_triples_plus_exactness"] == "unsat" for row in rows
        ),
        "critical_algebra_residual_count": len(residual),
        "critical_algebra_residual_indices": [
            row["survivor_index"] for row in residual
        ],
        "eliminated_by_explicit_lmin_directions": 2,
        "unresolved_after_explicit_directions": 0,
        "rows": rows,
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

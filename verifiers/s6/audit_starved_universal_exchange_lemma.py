#!/usr/bin/env python3
"""Test a table-free exactness-aware exchange lemma for the starved profile."""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path

import z3


N_PLAYERS = (0, 1)
P_PLAYERS = (2, 3)
R_PLAYERS = (4, 5)
SHAPES = (
    (-1, 0, 0, 0, 0, 1),
    (-1, -1, 0, 0, 1, 1),
    (-1, -1, -1, 0, 1, 2),
)


def point_sum(point, players):
    return z3.Sum(*[point[player] for player in players])


def direction_family():
    return tuple(sorted({item for shape in SHAPES for item in itertools.permutations(shape)}))


def lex_improves(point, direction, side):
    if side == "min":
        pivots = []
        for pivot, value in enumerate(direction):
            if value <= 0:
                continue
            pivots.append(
                z3.And(
                    *[
                        point[player] >= point[pivot]
                        for player, coefficient in enumerate(direction)
                        if coefficient != 0
                    ],
                    *[
                        point[player] > point[pivot]
                        for player, coefficient in enumerate(direction)
                        if coefficient < 0
                    ],
                )
            )
        return z3.Or(*pivots)
    pivots = []
    for pivot, value in enumerate(direction):
        if value >= 0:
            continue
        pivots.append(
            z3.And(
                *[
                    point[player] <= point[pivot]
                    for player, coefficient in enumerate(direction)
                    if coefficient != 0
                ],
                *[
                    point[player] < point[pivot]
                    for player, coefficient in enumerate(direction)
                    if coefficient > 0
                ],
            )
        )
    return z3.Or(*pivots)


def blocker_formula(x, z, witnesses, direction, side):
    reference = x if side == "min" else z
    comparison = z if side == "min" else x
    blockers = []
    for mask in range(1, (1 << 6) - 1):
        players = tuple(player for player in range(6) if mask >> player & 1)
        if sum(direction[player] for player in players) >= 0:
            continue
        blockers.append(
            z3.And(
                point_sum(comparison, players) >= point_sum(reference, players),
                *[
                    point_sum(witness, players) >= point_sum(reference, players)
                    for witness in witnesses
                ],
            )
        )
    return z3.Or(*blockers)


def abstract_solver(side, timeout_ms):
    solver = z3.Solver()
    solver.set(timeout=timeout_ms)
    x = [z3.Real(f"starved_universal_x_{player}") for player in range(6)]
    z = [z3.Real(f"starved_universal_z_{player}") for player in range(6)]
    solver.add(
        z3.Sum(*x) == 1,
        z3.Sum(*z) == 1,
        *[coordinate >= 0 for coordinate in x + z],
        *[x[player] > z[player] for player in N_PLAYERS + R_PLAYERS],
        *[z[player] > x[player] for player in P_PLAYERS],
        *[x[low] < x[rich] for low in N_PLAYERS + P_PLAYERS for rich in R_PLAYERS],
        *[z[poor] < z[high] for poor in N_PLAYERS for high in P_PLAYERS + R_PLAYERS],
        x[R_PLAYERS[0]] == x[R_PLAYERS[1]],
    )
    # Dimension-free selection anchors already used by the hand net: Lmax has
    # no singleton top stratum; some Lmax-top player reaches the top level at
    # x; and some Lmin-bottom player is no higher at z than the Lmin floor.
    solver.add(
        z3.Or(
            *[
                z3.And(
                    z[first] == z[second],
                    *[z[first] >= z[player] for player in range(6)],
                )
                for first in range(6)
                for second in range(first + 1, 6)
            ]
        ),
        z3.Or(
            *[
                z3.And(
                    *[z[player] >= z[other] for other in range(6)],
                    x[player] >= z[player],
                )
                for player in range(6)
            ]
        ),
        z3.Or(
            *[
                z3.And(
                    *[x[player] <= x[other] for other in range(6)],
                    z[player] <= x[player],
                )
                for player in range(6)
            ]
        ),
    )
    lmax_branch = z3.Or(
        *[
            z3.And(*[z[rich] < z[poor] for poor in P_PLAYERS])
            for rich in R_PLAYERS
        ]
    )
    solver.add(lmax_branch if side == "max" else z3.Not(lmax_branch))
    solver.add(
        2 * point_sum([x[player] - z[player] for player in range(6)], N_PLAYERS + R_PLAYERS)
        > z3.RealVal("2/3")
    )
    witnesses = []
    for zero in range(6):
        witness = [
            z3.Real(f"starved_universal_q_{zero}_{player}") for player in range(6)
        ]
        solver.add(
            z3.Sum(*witness) == 1,
            witness[zero] == 0,
            *[coordinate >= 0 for coordinate in witness],
        )
        witnesses.append(witness)

    directions = direction_family()
    point = x if side == "min" else z
    for direction in directions:
        solver.add(
            z3.Implies(
                lex_improves(point, direction, side),
                blocker_formula(x, z, witnesses, direction, side),
            )
        )
    opposite = "max" if side == "min" else "min"
    opposite_point = z if opposite == "max" else x
    for direction in sorted(set(itertools.permutations(SHAPES[0]))):
        solver.add(
            z3.Implies(
                lex_improves(opposite_point, direction, opposite),
                blocker_formula(x, z, witnesses, direction, opposite),
            )
        )
    return solver, x, z, witnesses, directions


def rational(model, value):
    rendered = model.eval(value, model_completion=True)
    return rendered.as_fraction().__str__() if z3.is_rational_value(rendered) else str(rendered)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout-ms", type=int, default=120_000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = []
    for side in ("min", "max"):
        solver, x, z, witnesses, directions = abstract_solver(side, args.timeout_ms)
        verdict = solver.check()
        row = {
            "side": side,
            "verdict": str(verdict),
            "direction_count": len(directions),
            "direction_shape_count": len(SHAPES),
        }
        if verdict == z3.sat:
            model = solver.model()
            row["model"] = {
                "x": [rational(model, value) for value in x],
                "z": [rational(model, value) for value in z],
                "witnesses": [
                    [rational(model, value) for value in witness]
                    for witness in witnesses
                ],
            }
        rows.append(row)
    payload = {
        "schema": "starved-universal-exchange-lemma-audit-v1",
        "scope": "table-free exact QF_LRA discovery audit; not proof objects",
        "roles": {"N": list(N_PLAYERS), "P": list(P_PLAYERS), "R": list(R_PLAYERS)},
        "direction_shapes": [list(shape) for shape in SHAPES],
        "premises": [
            "starved coarse role signs and strict coarse gaps",
            "the two coarse-rich players remain tied at Lmin",
            "Lmax top stratum has at least two players",
            "Lmax-top cross anchor and Lmin-bottom cross anchor",
            "six singleton-zero nonnegative efficiency witnesses",
            "opposite-side one-for-one exchange blockers",
            "selected-side blockers for every lex-improving shape permutation",
            "distance strictly greater than 2/3",
        ],
        "verdict_summary": dict(sorted(Counter(row["verdict"] for row in rows).items())),
        "rows": rows,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

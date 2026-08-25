#!/usr/bin/env python3
"""Discovery-only n=7 exactness-aware exchange relaxation for the overlap frontier.

SAT models are allocation/witness relaxations, not games.  UNSAT is a
necessary-system exclusion for the selected sign-count cell and direction
menu.  This file is deliberately outside the repository until its scientific
status is clear.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter
from pathlib import Path

import z3


N = 7


def point_sum(point, players):
    return z3.Sum(*[point[player] for player in players])


def primitive(direction):
    divisor = 0
    for value in direction:
        divisor = math.gcd(divisor, abs(value))
    return divisor == 1


def direction_pool(bound, max_support=None):
    rows = []
    for direction in itertools.product(range(-bound, bound + 1), repeat=N):
        support = sum(value != 0 for value in direction)
        if sum(direction) or not support or not primitive(direction):
            continue
        if max_support is not None and support > max_support:
            continue
        rows.append(direction)
    return tuple(
        sorted(
            rows,
            key=lambda row: (
                sum(abs(value) for value in row),
                max(abs(value) for value in row),
                sum(value != 0 for value in row),
                row,
            ),
        )
    )


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


def blocker_atoms(solver, x, z, witnesses, side):
    """Name each coalition's necessary blocker condition once.

    The unshared DNF repeats eight identical comparison inequalities in every
    exchange implication.  Exact Boolean definitions preserve the formula but
    make the n=7 instance much smaller for the SMT solver.
    """
    reference = x if side == "min" else z
    comparison = z if side == "min" else x
    atoms = {}
    for mask in range(1, (1 << N) - 1):
        players = tuple(player for player in range(N) if mask >> player & 1)
        atom = z3.Bool(f"n7_exchange_blocker_{side}_{mask}")
        solver.add(
            atom
            == z3.And(
                point_sum(comparison, players) >= point_sum(reference, players),
                *[
                    point_sum(witness, players) >= point_sum(reference, players)
                    for witness in witnesses
                ],
            )
        )
        atoms[mask] = atom
    return atoms


def blocker_formula(atoms, direction):
    return z3.Or(
        *[
            atom
            for mask, atom in atoms.items()
            if sum(direction[player] for player in range(N) if mask >> player & 1) < 0
        ]
    )


def selection_anchors(solver, x, z):
    # Exact selectors imply: Lmax has at least two top players; some Lmax-top
    # player is not a strict gainer; and some Lmin-bottom player is not a
    # strict loser.  These are the dimension-free anchor lemmas used at n=6.
    solver.add(
        z3.Or(
            *[
                z3.And(
                    z[first] == z[second],
                    *[z[first] >= z[player] for player in range(N)],
                )
                for first in range(N)
                for second in range(first + 1, N)
            ]
        ),
        z3.Or(
            *[
                z3.And(
                    *[z[player] >= z[other] for other in range(N)],
                    x[player] >= z[player],
                )
                for player in range(N)
            ]
        ),
        z3.Or(
            *[
                z3.And(
                    *[x[player] <= x[other] for other in range(N)],
                    z[player] <= x[player],
                )
                for player in range(N)
            ]
        ),
    )


def build(positive_count, negative_count, bound, max_support, timeout_ms):
    tie_count = N - positive_count - negative_count
    positive = tuple(range(positive_count))
    negative = tuple(range(positive_count, positive_count + negative_count))
    tied = tuple(range(positive_count + negative_count, N))
    solver = z3.SolverFor("QF_LRA")
    solver.set(timeout=timeout_ms)
    x = [z3.Real(f"n7_exchange_x_{player}") for player in range(N)]
    z = [z3.Real(f"n7_exchange_z_{player}") for player in range(N)]
    solver.add(
        z3.Sum(*x) == 1,
        z3.Sum(*z) == 1,
        *[coordinate >= 0 for coordinate in x + z],
        *[x[player] > z[player] for player in positive],
        *[z[player] > x[player] for player in negative],
        *[x[player] == z[player] for player in tied],
        2 * z3.Sum(*[x[player] - z[player] for player in positive])
        > z3.RealVal("5/6"),
    )
    selection_anchors(solver, x, z)
    witnesses = []
    for zero in range(N):
        witness = [z3.Real(f"n7_exchange_q_{zero}_{player}") for player in range(N)]
        solver.add(
            z3.Sum(*witness) == 1,
            witness[zero] == 0,
            *[coordinate >= 0 for coordinate in witness],
        )
        witnesses.append(witness)
    directions = direction_pool(bound, max_support)
    atoms_by_side = {
        side: blocker_atoms(solver, x, z, witnesses, side)
        for side in ("min", "max")
    }
    for side, point in (("min", x), ("max", z)):
        for direction in directions:
            solver.add(
                z3.Implies(
                    lex_improves(point, direction, side),
                    blocker_formula(atoms_by_side[side], direction),
                )
            )
    return solver, x, z, witnesses, directions, tie_count, atoms_by_side


def rational(model, value):
    rendered = model.eval(value, model_completion=True)
    return str(rendered.as_fraction()) if z3.is_rational_value(rendered) else str(rendered)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bound", type=int, default=1)
    parser.add_argument("--max-support", type=int)
    parser.add_argument("--timeout-ms", type=int, default=60_000)
    parser.add_argument("--positive-count", type=int)
    parser.add_argument("--negative-count", type=int)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--menu-json",
        type=Path,
        help="seed side-specific implications from a prior row's active_extra_menu",
    )
    parser.add_argument(
        "--extra-direction",
        action="append",
        default=[],
        help="side:comma-separated integer direction; repeatable",
    )
    parser.add_argument(
        "--cegar-full",
        action="store_true",
        help="start from max-support menu and add violated full bound menu in batches",
    )
    parser.add_argument("--cegar-rounds", type=int, default=50)
    args = parser.parse_args()
    cases = []
    for positive in range(1, N):
        for negative in range(1, N + 1 - positive):
            if args.positive_count is not None and positive != args.positive_count:
                continue
            if args.negative_count is not None and negative != args.negative_count:
                continue
            cases.append((positive, negative))
    rows = []
    for positive, negative in cases:
        solver, x, z, witnesses, directions, ties, atoms_by_side = build(
            positive, negative, args.bound, args.max_support, args.timeout_ms
        )
        seeded_menu = []
        if args.menu_json:
            prior = json.loads(args.menu_json.read_text())
            seeded_menu.extend(prior["rows"][0].get("active_extra_menu", []))
        for rendered in args.extra_direction:
            side, values = rendered.split(":", 1)
            seeded_menu.append(
                {"side": side, "direction": [int(value) for value in values.split(",")]}
            )
        for item in seeded_menu:
            side = item["side"]
            direction = tuple(item["direction"])
            point = x if side == "min" else z
            solver.add(
                z3.Implies(
                    lex_improves(point, direction, side),
                    blocker_formula(atoms_by_side[side], direction),
                )
            )
        full_directions = direction_pool(args.bound, None)
        active = {(side, direction) for side in ("min", "max") for direction in directions}
        active.update((item["side"], tuple(item["direction"])) for item in seeded_menu)
        cegar_log = []
        verdict = solver.check()
        if args.cegar_full:
            if args.max_support is None:
                parser.error("--cegar-full requires --max-support")
            for round_index in range(args.cegar_rounds):
                covered_full = sum(
                    (side, direction) in active
                    for side in ("min", "max")
                    for direction in full_directions
                )
                if verdict != z3.sat or covered_full == 2 * len(full_directions):
                    break
                model = solver.model()
                violated = []
                for side, point in (("min", x), ("max", z)):
                    for direction in full_directions:
                        if (side, direction) in active:
                            continue
                        improves = z3.is_true(
                            model.eval(lex_improves(point, direction, side), model_completion=True)
                        )
                        blocked = z3.is_true(
                            model.eval(
                                blocker_formula(atoms_by_side[side], direction),
                                model_completion=True,
                            )
                        )
                        if improves and not blocked:
                            violated.append((side, direction))
                cegar_log.append(
                    {
                        "round": round_index,
                        "active_implication_count": len(active),
                        "violated_implication_count": len(violated),
                    }
                )
                if not violated:
                    break
                for side, direction in violated:
                    point = x if side == "min" else z
                    solver.add(
                        z3.Implies(
                            lex_improves(point, direction, side),
                            blocker_formula(atoms_by_side[side], direction),
                        )
                    )
                    active.add((side, direction))
                verdict = solver.check()
        row = {
            "case": f"p{positive}_n{negative}_t{ties}",
            "positive_count": positive,
            "negative_count": negative,
            "tie_count": ties,
            "direction_count_per_side": len(directions),
            "verdict": str(verdict),
            "reason_unknown": solver.reason_unknown() if verdict == z3.unknown else None,
            "cegar_log": cegar_log,
            "active_implication_count": len(active),
            "active_extra_menu": [
                {"side": side, "direction": list(direction)}
                for side, direction in sorted(active)
                if direction not in directions
            ],
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
        print(f"{row['case']}: {verdict}", flush=True)
    payload = {
        "schema": "n7-exactness-aware-exchange-relaxation-scratch-v1",
        "scope": "necessary QF_LRA relaxation; SAT rows are not games",
        "threshold": "distance > 5/6 at total 1",
        "bound": args.bound,
        "max_support": args.max_support,
        "case_count": len(rows),
        "verdict_summary": dict(sorted(Counter(row["verdict"] for row in rows).items())),
        "rows": rows,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

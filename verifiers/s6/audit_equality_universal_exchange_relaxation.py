#!/usr/bin/env python3
"""Probe table-free exactness-aware exchange constraints at distance 2/3."""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from audit_starved_universal_exchange_lemma import (  # noqa: E402
    blocker_formula,
    lex_improves,
)
from search_positive_handover_directions import direction_pool  # noqa: E402


COEFFICIENT_TWO_SHAPE = (-1, -1, -1, 0, 1, 2)


def exchange_directions(bound, extra_coefficient_two):
    directions = set(direction_pool(bound))
    if extra_coefficient_two:
        directions.update(itertools.permutations(COEFFICIENT_TWO_SHAPE))
    return tuple(sorted(directions))


def canonical_equality_formula(x, z, positive_count, negative_count):
    positive = tuple(range(positive_count))
    negative = tuple(range(positive_count, positive_count + negative_count))
    alternatives = []
    if (positive_count, negative_count) == (3, 3):
        for rich in positive:
            alternatives.append(
                z3.And(
                    x[rich] == z3.RealVal("4/9"),
                    z[rich] == z3.RealVal("2/9"),
                    *[
                        z3.And(x[player] == z3.RealVal("1/9"), z[player] == z3.RealVal("1/18"))
                        for player in positive
                        if player != rich
                    ],
                    *[
                        z3.And(x[player] == z3.RealVal("1/9"), z[player] == z3.RealVal("2/9"))
                        for player in negative
                    ],
                )
            )
    elif (positive_count, negative_count) == (4, 2):
        for rich in itertools.combinations(positive, 2):
            rich = set(rich)
            alternatives.append(
                z3.And(
                    *[
                        z3.And(
                            x[player] == z3.RealVal("1/3"),
                            z[player] == z3.RealVal("1/4"),
                        )
                        for player in rich
                    ],
                    *[
                        z3.And(
                            x[player] == z3.RealVal("1/12"),
                            z[player] == 0,
                        )
                        for player in positive
                        if player not in rich
                    ],
                    *[
                        z3.And(
                            x[player] == z3.RealVal("1/12"),
                            z[player] == z3.RealVal("1/4"),
                        )
                        for player in negative
                    ],
                )
            )
    return z3.Or(*alternatives) if alternatives else z3.BoolVal(False)


def selection_anchors(solver, x, z):
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


def top_triple_formula(x, z, witnesses):
    alternatives = []
    for triple in itertools.combinations(range(6), 3):
        alternatives.append(
            z3.And(
                z[triple[0]] == z[triple[1]],
                z[triple[0]] == z[triple[2]],
                *[z[triple[0]] >= z[player] for player in range(6)],
                z3.Sum(*[x[player] for player in triple])
                >= z3.Sum(*[z[player] for player in triple]),
                *[
                    z3.Sum(*[witness[player] for player in triple])
                    >= z3.Sum(*[z[player] for player in triple])
                    for witness in witnesses
                ],
            )
        )
    return z3.Or(*alternatives)


def build(
    positive_count,
    negative_count,
    bound,
    extra_coefficient_two,
    require_top_triple,
    forbid_top_triple,
    exclude_canonical,
    timeout_ms,
    distance_relation="eq",
):
    tie_count = 6 - positive_count - negative_count
    solver = z3.Solver()
    solver.set(timeout=timeout_ms)
    x = [z3.Real(f"equality_exchange_x_{player}") for player in range(6)]
    z = [z3.Real(f"equality_exchange_z_{player}") for player in range(6)]
    positive = tuple(range(positive_count))
    negative = tuple(range(positive_count, positive_count + negative_count))
    tied = tuple(range(positive_count + negative_count, 6))
    distance_left = 2 * z3.Sum(
        *[x[player] - z[player] for player in positive]
    )
    distance_right = z3.RealVal("2/3")
    if distance_relation == "eq":
        distance_constraint = distance_left == distance_right
    elif distance_relation == "gt":
        distance_constraint = distance_left > distance_right
    else:
        raise ValueError(distance_relation)
    solver.add(
        z3.Sum(*x) == 1,
        z3.Sum(*z) == 1,
        *[coordinate >= 0 for coordinate in x + z],
        *[x[player] > z[player] for player in positive],
        *[z[player] > x[player] for player in negative],
        *[x[player] == z[player] for player in tied],
        distance_constraint,
    )
    if exclude_canonical:
        solver.add(z3.Not(canonical_equality_formula(x, z, positive_count, negative_count)))
    selection_anchors(solver, x, z)
    witnesses = []
    for zero in range(6):
        witness = [
            z3.Real(f"equality_exchange_q_{zero}_{player}") for player in range(6)
        ]
        solver.add(
            z3.Sum(*witness) == 1,
            witness[zero] == 0,
            *[coordinate >= 0 for coordinate in witness],
        )
        witnesses.append(witness)
    if require_top_triple:
        solver.add(top_triple_formula(x, z, witnesses))
    if forbid_top_triple:
        solver.add(z3.Not(top_triple_formula(x, z, witnesses)))
    directions = exchange_directions(bound, extra_coefficient_two)
    for side, point in (("min", x), ("max", z)):
        for direction in directions:
            solver.add(
                z3.Implies(
                    lex_improves(point, direction, side),
                    blocker_formula(x, z, witnesses, direction, side),
                )
            )
    return solver, x, z, witnesses, len(directions), tie_count


def rational(model, value):
    rendered = model.eval(value, model_completion=True)
    if z3.is_rational_value(rendered):
        return str(rendered.as_fraction())
    return str(rendered)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bound", type=int, default=1)
    parser.add_argument("--timeout-ms", type=int, default=120_000)
    parser.add_argument("--include-ties", action="store_true")
    parser.add_argument("--extra-coefficient-two", action="store_true")
    parser.add_argument("--require-top-triple", action="store_true")
    parser.add_argument("--forbid-top-triple", action="store_true")
    parser.add_argument("--exclude-canonical", action="store_true")
    parser.add_argument("--positive-count", type=int)
    parser.add_argument("--negative-count", type=int)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--distance-relation", choices=("eq", "gt"), default="eq")
    args = parser.parse_args()
    if args.require_top_triple and args.forbid_top_triple:
        parser.error("--require-top-triple and --forbid-top-triple are incompatible")
    triples = []
    for positive in range(1, 6):
        for negative in range(1, 7 - positive):
            ties = 6 - positive - negative
            if ties and not args.include_ties:
                continue
            if args.positive_count is not None and positive != args.positive_count:
                continue
            if args.negative_count is not None and negative != args.negative_count:
                continue
            triples.append((positive, negative))
    rows = []
    for positive, negative in triples:
        solver, x, z, witnesses, direction_count, ties = build(
            positive,
            negative,
            args.bound,
            args.extra_coefficient_two,
            args.require_top_triple,
            args.forbid_top_triple,
            args.exclude_canonical,
            args.timeout_ms,
            args.distance_relation,
        )
        verdict = solver.check()
        row = {
            "positive_count": positive,
            "negative_count": negative,
            "tie_count": ties,
            "direction_count_per_side": direction_count,
            "verdict": str(verdict),
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
        "schema": "equality-universal-exchange-relaxation-v1",
        "scope": "table-free exact QF_LRA relaxation; SAT rows are not games",
        "bound": args.bound,
        "include_ties": args.include_ties,
        "extra_coefficient_two": args.extra_coefficient_two,
        "require_top_triple": args.require_top_triple,
        "forbid_top_triple": args.forbid_top_triple,
        "exclude_canonical": args.exclude_canonical,
        "distance_relation": args.distance_relation,
        "verdict_summary": dict(sorted(Counter(row["verdict"] for row in rows).items())),
        "rows": rows,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

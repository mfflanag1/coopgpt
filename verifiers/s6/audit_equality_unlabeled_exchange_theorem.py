#!/usr/bin/env python3
"""Test two unlabeled table-free formulas for the equality classification."""

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

from audit_equality_universal_exchange_relaxation import (  # noqa: E402
    selection_anchors,
    top_triple_formula,
)
from audit_starved_universal_exchange_lemma import blocker_formula, lex_improves  # noqa: E402
from search_positive_handover_directions import direction_pool  # noqa: E402


STARVED_PAIRS = (
    ("1/12", "0"),
    ("1/12", "0"),
    ("1/12", "1/4"),
    ("1/12", "1/4"),
    ("1/3", "1/4"),
    ("1/3", "1/4"),
)
POSITIVE_PAIRS = (
    ("1/9", "1/18"),
    ("1/9", "1/18"),
    ("1/9", "2/9"),
    ("1/9", "2/9"),
    ("1/9", "2/9"),
    ("4/9", "2/9"),
)


def canonical_formula(x, z):
    alternatives = []
    for profile in (STARVED_PAIRS, POSITIVE_PAIRS):
        for assignment in sorted(set(itertools.permutations(profile))):
            alternatives.append(
                z3.And(
                    *[
                        z3.And(
                            x[player] == z3.RealVal(pair[0]),
                            z[player] == z3.RealVal(pair[1]),
                        )
                        for player, pair in enumerate(assignment)
                    ]
                )
            )
    return z3.Or(*alternatives), len(alternatives)


def build(mode, timeout_ms):
    solver = z3.Solver()
    solver.set(timeout=timeout_ms)
    x = [z3.Real(f"equality_unlabeled_x_{player}") for player in range(6)]
    z = [z3.Real(f"equality_unlabeled_z_{player}") for player in range(6)]
    solver.add(
        z3.Sum(*x) == 1,
        z3.Sum(*z) == 1,
        *[coordinate >= 0 for coordinate in x + z],
        z3.Sum(*[z3.Abs(x[player] - z[player]) for player in range(6)])
        == z3.RealVal("2/3"),
    )
    selection_anchors(solver, x, z)
    witnesses = []
    for zero in range(6):
        witness = [
            z3.Real(f"equality_unlabeled_q_{zero}_{player}") for player in range(6)
        ]
        solver.add(
            z3.Sum(*witness) == 1,
            witness[zero] == 0,
            *[coordinate >= 0 for coordinate in witness],
        )
        witnesses.append(witness)
    anchor = top_triple_formula(x, z, witnesses)
    canonical, canonical_assignment_count = canonical_formula(x, z)
    if mode == "no-eligible-top-triple":
        solver.add(z3.Not(anchor))
    elif mode == "noncanonical-with-eligible-top-triple":
        solver.add(anchor, z3.Not(canonical))
    else:
        raise ValueError(mode)

    directions = direction_pool(2)
    for side, point in (("min", x), ("max", z)):
        for direction in directions:
            solver.add(
                z3.Implies(
                    lex_improves(point, direction, side),
                    blocker_formula(x, z, witnesses, direction, side),
                )
            )
    return solver, x, z, witnesses, len(directions), canonical_assignment_count


def rational(model, value):
    rendered = model.eval(value, model_completion=True)
    return str(rendered.as_fraction()) if z3.is_rational_value(rendered) else str(rendered)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout-ms", type=int, default=300_000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = []
    for mode in ("no-eligible-top-triple", "noncanonical-with-eligible-top-triple"):
        solver, x, z, witnesses, direction_count, assignment_count = build(
            mode, args.timeout_ms
        )
        verdict = solver.check()
        row = {
            "mode": mode,
            "verdict": str(verdict),
            "direction_count_per_side": direction_count,
            "canonical_assignment_count": assignment_count,
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
        "schema": "equality-unlabeled-exchange-theorem-audit-v1",
        "scope": "table-free exact QF_LRA discovery audit; not proof objects",
        "timeout_ms_per_mode": args.timeout_ms,
        "verdict_summary": dict(sorted(Counter(row["verdict"] for row in rows).items())),
        "rows": rows,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

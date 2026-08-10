#!/usr/bin/env python3
"""Separately formulate the two coefficient-two strict-bound cases.

This is a differential reconstruction of ``p2_n3_t1`` and ``p3_n3_t0``.
It deliberately imports none of the production encoder, lex-predicate,
blocker, direction-pool, minimizer, or SMT serializer code.  The only shared
input is the frozen retained direction menu, treated as theorem data.  All
logical assertions are rebuilt below with different variable names and a
separately written first-affected-level predicate.

The script emits standalone SMT-LIB and a JSON audit.  SAT of the base system
is checked as a nonvacuity control before the menu implications are added.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
CASES = {"p2_n3_t1": (2, 3, 1, 14), "p3_n3_t0": (3, 3, 0, 71)}


def vector_sum(vector, players):
    terms = [vector[player] for player in players]
    if len(terms) == 1:
        return terms[0]
    return z3.Sum(terms)


def disjoin(formulas):
    if not formulas:
        return z3.BoolVal(False)
    if len(formulas) == 1:
        return formulas[0]
    return z3.Or(*formulas)


def first_affected_improves(point, direction, side):
    """Direct first-affected-payoff-level test, written independently.

    On the min side, a positive entry witnesses the lowest affected level,
    all other affected players are weakly above it, and every negative entry
    is strictly above it.  The max-side statement is the order dual.
    """
    candidates = []
    if side == "min":
        for pivot, coefficient in enumerate(direction):
            if coefficient <= 0:
                continue
            candidates.append(
                z3.And(
                    *[
                        point[pivot] <= point[player]
                        for player, value in enumerate(direction)
                        if value != 0
                    ],
                    *[
                        point[pivot] < point[player]
                        for player, value in enumerate(direction)
                        if value < 0
                    ],
                )
            )
    elif side == "max":
        for pivot, coefficient in enumerate(direction):
            if coefficient >= 0:
                continue
            candidates.append(
                z3.And(
                    *[
                        point[pivot] >= point[player]
                        for player, value in enumerate(direction)
                        if value != 0
                    ],
                    *[
                        point[pivot] > point[player]
                        for player, value in enumerate(direction)
                        if value > 0
                    ],
                )
            )
    else:
        raise ValueError(side)
    return disjoin(candidates)


def eligible_negative_cut(x, z, witnesses, direction, side):
    """Necessary exactness blocker, reconstructed subset by subset."""
    selected = x if side == "min" else z
    opposite = z if side == "min" else x
    alternatives = []
    for mask in range(1, 63):
        players = tuple(i for i in range(6) if mask & (1 << i))
        if sum(direction[i] for i in players) >= 0:
            continue
        selected_sum = vector_sum(selected, players)
        alternatives.append(
            z3.And(
                vector_sum(opposite, players) >= selected_sum,
                *[
                    vector_sum(witness, players) >= selected_sum
                    for witness in witnesses
                ],
            )
        )
    if not alternatives:
        raise AssertionError("an efficiency-preserving nonzero direction has no negative cut")
    return disjoin(alternatives)


def add_anchors(solver, x, z):
    # Written as the negation of a unique-top alternative, rather than the
    # production encoder's positive tied-top disjunction.
    solver.add(
        z3.Not(
            z3.Or(
                *[
                    z3.And(*[z[i] > z[j] for j in range(6) if j != i])
                    for i in range(6)
                ]
            )
        )
    )
    solver.add(
        z3.Or(
            *[
                z3.And(
                    *[z[i] >= z[j] for j in range(6)],
                    x[i] >= z[i],
                )
                for i in range(6)
            ]
        )
    )
    solver.add(
        z3.Or(
            *[
                z3.And(
                    *[x[i] <= x[j] for j in range(6)],
                    z[i] <= x[i],
                )
                for i in range(6)
            ]
        )
    )


def load_menu(case):
    payload = json.loads((HERE / "strict_exchange_direction_cores.json").read_text())
    rows = [row for row in payload["rows"] if row["case"] == case]
    if len(rows) != 1:
        raise AssertionError(f"expected one menu for {case}")
    row = rows[0]
    expected = CASES[case][3]
    menu = tuple(
        (item["side"], tuple(int(value) for value in item["direction"]))
        for item in row["retained_menu"]
    )
    if len(menu) != expected or len(set(menu)) != expected:
        raise AssertionError(f"unexpected or duplicate retained menu for {case}")
    for side, direction in menu:
        if side not in ("min", "max"):
            raise AssertionError(side)
        if len(direction) != 6 or sum(direction) != 0:
            raise AssertionError(direction)
        if max(map(abs, direction)) > 2 or not any(direction):
            raise AssertionError(direction)
    return menu


def build_case(case, include_menu):
    positive_count, negative_count, tie_count, _ = CASES[case]
    x = [z3.Real(f"ind_{case}_x{i}") for i in range(6)]
    z = [z3.Real(f"ind_{case}_z{i}") for i in range(6)]
    solver = z3.Solver()
    solver.add(z3.Sum(x) == 1, z3.Sum(z) == 1)
    solver.add(*[coordinate >= 0 for coordinate in x + z])
    positives = range(positive_count)
    negatives = range(positive_count, positive_count + negative_count)
    ties = range(positive_count + negative_count, 6)
    solver.add(*[x[i] > z[i] for i in positives])
    solver.add(*[x[i] < z[i] for i in negatives])
    solver.add(*[x[i] == z[i] for i in ties])
    solver.add(2 * z3.Sum([x[i] - z[i] for i in positives]) > z3.RealVal("2/3"))
    add_anchors(solver, x, z)

    witnesses = []
    for missing in range(6):
        witness = [z3.Real(f"ind_{case}_q{missing}_{i}") for i in range(6)]
        solver.add(z3.Sum(witness) == 1, witness[missing] == 0)
        solver.add(*[coordinate >= 0 for coordinate in witness])
        witnesses.append(witness)

    menu = load_menu(case)
    if include_menu:
        for side, direction in menu:
            point = x if side == "min" else z
            solver.add(
                z3.Implies(
                    first_affected_improves(point, direction, side),
                    eligible_negative_cut(x, z, witnesses, direction, side),
                )
            )
    return solver, menu, (positive_count, negative_count, tie_count)


def standalone_smt2(solver):
    return "(set-logic QF_LRA)\n" + solver.sexpr() + "\n(check-sat)\n"


def sha256_text(text):
    return hashlib.sha256(text.encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=HERE / "independent_bound_two")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for case in CASES:
        base, menu, counts = build_case(case, include_menu=False)
        base_verdict = base.check()
        if base_verdict != z3.sat:
            raise AssertionError(f"{case} base system is unexpectedly {base_verdict}")

        full, _, _ = build_case(case, include_menu=True)
        full_verdict = full.check()
        if full_verdict != z3.unsat:
            raise AssertionError(f"{case} independent reconstruction is {full_verdict}")
        rendered = standalone_smt2(full)
        formula = args.output_dir / f"{case}.smt2"
        formula.write_text(rendered)
        rows.append(
            {
                "case": case,
                "sign_counts": list(counts),
                "retained_direction_count": len(menu),
                "base_without_direction_implications": str(base_verdict),
                "independent_formula_verdict": str(full_verdict),
                "formula": f"{args.output_dir.name}/{case}.smt2",
                "formula_bytes": len(rendered.encode()),
                "formula_sha256": sha256_text(rendered),
            }
        )

    report = {
        "schema": "independent-bound-two-reconstruction-v1",
        "status": "PASS",
        "independence": (
            "No production encoder, predicate, blocker, direction-pool, minimizer, "
            "or serializer code is imported; only the frozen retained menus are shared data."
        ),
        "z3_version": z3.get_version_string(),
        "rows": rows,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    target = args.report or args.output_dir / "audit.json"
    target.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

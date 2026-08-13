#!/usr/bin/env python3
"""Exact LRA audit of the four noncommon four-role edge transitions.

This is a structural discovery/audit tool.  It asks whether an arbitrary
four-role interval--pair-slab core can have distinct weighted Lmin and Lmax
on each canonical active-edge incidence from (FEC4).  The selectors are
specified by the quantified max-min/min-max fairness conditions, without a
guessed payoff stratum.  Unit-role singleton minima are attained, as required
by objective A; attainment of all other coalition bounds is relaxed.

An UNSAT answer is a theorem for the displayed fixed weight row and incidence
cell.  A SAT answer is only a relaxed-core witness and must be exactified and
independently recomputed before it can refute an exact-game statement.
"""

from __future__ import annotations

import argparse
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from verify_common_two_finite_z3 import core_formula, fairness_formula


PAIR_ROLES = ((0, 1), (0, 2), (0, 3))
TYPES = {
    "I": ((0, "L"), (1, "U")),
    "II": ((0, "L"), (2, "L")),
    "III": ((0, "U"), (1, "U")),
    "IV": ((0, "U"), (2, "L")),
}


def add(*terms: str) -> str:
    return terms[0] if len(terms) == 1 else f"(+ {' '.join(terms)})"


def pair(prefix: str, index: int) -> str:
    return add(*(f"{prefix}{role}" for role in PAIR_ROLES[index]))


def compositions(total: int):
    for a in range(1, total - 2):
        for b in range(1, total - a - 1):
            for c in range(1, total - a - b):
                yield (a, b, c, total - a - b - c)


def endpoint_options():
    return tuple(
        tuple(zip(pairs, endpoints))
        for pairs in itertools.combinations(range(3), 2)
        for endpoints in itertools.product(("L", "U"), repeat=2)
    )


def pair_box_formula(prefix):
    coordinates = [f"{prefix}{role}" for role in range(4)]
    clauses = [f"(= {add(*coordinates)} 1)"]
    clauses.extend(
        f"(and (<= L{j} {pair(prefix, j)}) (<= {pair(prefix, j)} U{j}))"
        for j in range(3)
    )
    return f"(and {' '.join(clauses)})"


def restricted_fairness_formula(selector_prefix, weights, mode, trigger_roles):
    """The selected trigger-role clauses of max-min/min-max fairness."""

    clauses = []
    for role in trigger_roles:
        weight = weights[role]
        y_value = f"y{role}" if weight == 1 else f"(/ y{role} {weight})"
        selected = (
            f"{selector_prefix}{role}"
            if weight == 1
            else f"(/ {selector_prefix}{role} {weight})"
        )
        if mode == "min":
            trigger = f"(> {y_value} {selected})"
        else:
            trigger = f"(< {y_value} {selected})"
        repairs = []
        for j in range(4):
            selected_j = (
                f"{selector_prefix}{j}"
                if weights[j] == 1
                else f"(/ {selector_prefix}{j} {weights[j]})"
            )
            y_j = f"y{j}" if weights[j] == 1 else f"(/ y{j} {weights[j]})"
            if mode == "min":
                repairs.append(
                    f"(and (<= {selected_j} {selected}) (< {y_j} {selected_j}))"
                )
            else:
                repairs.append(
                    f"(and (>= {selected_j} {selected}) (> {y_j} {selected_j}))"
                )
        clauses.append(f"(=> {trigger} (or {' '.join(repairs)}))")
    return "true" if not clauses else f"(and {' '.join(clauses)})"


def build_query(
    weights,
    transition: str | None,
    timeout_ms: int,
    pairwise_only=False,
    x_choice=None,
    z_choice=None,
    pair_box_only=False,
    one_full_selector=None,
    min_trigger_roles=(0, 1, 2, 3),
    max_trigger_roles=(0, 1, 2, 3),
) -> str:
    lines = [
        "(set-logic LRA)",
        "(set-option :produce-models true)",
        f"(set-option :timeout {timeout_ms})",
    ]
    for stem in ("lo", "hi"):
        for role in range(4):
            lines.append(f"(declare-const {stem}{role} Real)")
    for stem in ("L", "U"):
        for index in range(3):
            lines.append(f"(declare-const {stem}{index} Real)")
    for prefix in ("x", "z"):
        for role in range(4):
            lines.append(f"(declare-const {prefix}{role} Real)")

    lines.append(
        "(assert (and "
        + " ".join(
            f"(<= 0 lo{i}) (<= lo{i} hi{i}) (<= hi{i} 1)"
            for i in range(4)
        )
        + " "
        + " ".join(
            f"(<= 0 L{j}) (<= L{j} U{j}) (<= U{j} 1)"
            for j in range(3)
        )
        + "))"
    )
    for role, weight in enumerate(weights):
        if weight == 1:
            lines.append(f"(assert (= lo{role} 0))")
    selected_core_formula = pair_box_formula if pair_box_only else core_formula
    lines.append(f"(assert {selected_core_formula('x')})")
    lines.append(f"(assert {selected_core_formula('z')})")

    for witness, attained_role in enumerate(
        role for role, weight in enumerate(weights) if weight == 1
    ):
        for role in range(4):
            lines.append(f"(declare-const w{witness}{role} Real)")
        lines.append(f"(assert {selected_core_formula(f'w{witness}')})")
        lines.append(f"(assert (= w{witness}{attained_role} 0))")

    min_formula = restricted_fairness_formula(
        "x", weights, "min", min_trigger_roles
    )
    max_formula = restricted_fairness_formula(
        "z", weights, "max", max_trigger_roles
    )
    min_at_z = min_formula.replace("y", "z")
    max_at_x = max_formula.replace("y", "x")
    y_core = selected_core_formula("y")
    if pairwise_only or one_full_selector == "max":
        lines.append(f"(assert {min_at_z})")
    else:
        lines.append(
            f"(assert (forall ({' '.join(f'(y{i} Real)' for i in range(4))}) "
            f"(=> {y_core} {min_formula})))"
        )
    if pairwise_only or one_full_selector == "min":
        lines.append(f"(assert {max_at_x})")
    else:
        lines.append(
            f"(assert (forall ({' '.join(f'(y{i} Real)' for i in range(4))}) "
            f"(=> {y_core} {max_formula})))"
        )

    if x_choice is not None:
        for index, endpoint in x_choice:
            lines.append(f"(assert (= {pair('x', index)} {endpoint}{index}))")
        for index, endpoint in z_choice:
            lines.append(f"(assert (= {pair('z', index)} {endpoint}{index}))")

        # Count actual, not merely selected, shared endpoint equalities.  This
        # prevents an apparent noncommon cell from collapsing into the
        # already proved common-two branch through extra active endpoints.
        common = []
        for index in range(3):
            common.append(
                f"(or (and (= {pair('x', index)} L{index}) "
                f"(= {pair('z', index)} L{index})) "
                f"(and (= {pair('x', index)} U{index}) "
                f"(= {pair('z', index)} U{index})))"
            )
        lines.append(
            "(assert (and "
            + " ".join(
                f"(not (and {common[i]} {common[j]}))"
                for i, j in itertools.combinations(range(3), 2)
            )
            + "))"
        )
    else:
        # Canonical orientation used only for the inexpensive diagnostic
        # cells.  It is not a substitute for --all-incidences.
        lines.append(f"(assert (= {pair('x', 0)} L0))")
        lines.append(f"(assert (= {pair('x', 1)} L1))")
        for index, endpoint in TYPES[transition]:
            lines.append(f"(assert (= {pair('z', index)} {endpoint}{index}))")

    # Exclude collapse into the already closed common-two incidence.  Strict
    # widths are imposed exactly where the named transition reverses an
    # endpoint.  Extra third-flat activity remains allowed.
    if x_choice is not None:
        pass
    elif transition == "I":
        lines.append("(assert (< L1 U1))")
        lines.append(f"(assert (> {pair('z', 2)} L2))")
        lines.append(f"(assert (> {pair('x', 2)} L2))")
        lines.append(f"(assert (< {pair('z', 2)} U2))")
        lines.append(f"(assert (< {pair('x', 2)} U2))")
    elif transition == "II":
        lines.append(f"(assert (> {pair('z', 1)} L1))")
        lines.append(f"(assert (> {pair('x', 2)} L2))")
    elif transition == "III":
        lines.append("(assert (< L0 U0))")
        lines.append("(assert (< L1 U1))")
    elif transition == "IV":
        lines.append("(assert (< L0 U0))")
        lines.append(f"(assert (> {pair('z', 1)} L1))")

    lines.append(f"(assert (or {' '.join(f'(not (= x{i} z{i}))' for i in range(4))}))")
    lines.append("(check-sat-using (then qe2 smt))")
    lines.append("(get-model)")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--z3", default="z3")
    parser.add_argument("--min-n", type=int, default=4)
    parser.add_argument("--max-n", type=int, default=9)
    parser.add_argument("--weights", help="one ordered four-weight row")
    parser.add_argument("--types", default="I,II,III,IV")
    parser.add_argument("--timeout-ms", type=int, default=30000)
    parser.add_argument("--pairwise-only", action="store_true")
    parser.add_argument("--pair-box-only", action="store_true")
    parser.add_argument("--one-full-selector", choices=("min", "max"))
    parser.add_argument("--min-trigger-roles", default="0,1,2,3")
    parser.add_argument("--max-trigger-roles", default="0,1,2,3")
    parser.add_argument("--all-incidences", action="store_true")
    parser.add_argument("--x-cell", type=int)
    parser.add_argument("--z-cell", type=int)
    parser.add_argument("--stop-on-sat", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = (
        [tuple(map(int, args.weights.split(",")))]
        if args.weights
        else [
            row
            for n in range(args.min_n, args.max_n + 1)
            for row in compositions(n)
        ]
    )
    transitions = tuple(args.types.split(","))
    if args.all_incidences:
        x_options = endpoint_options()
        z_options = endpoint_options()
        if args.x_cell is not None:
            x_options = (x_options[args.x_cell],)
        if args.z_cell is not None:
            z_options = (z_options[args.z_cell],)
        cells = tuple(itertools.product(x_options, z_options))
    else:
        cells = tuple((transition, None) for transition in transitions)
    results = []
    min_trigger_roles = tuple(
        int(role) for role in args.min_trigger_roles.split(",") if role != ""
    )
    max_trigger_roles = tuple(
        int(role) for role in args.max_trigger_roles.split(",") if role != ""
    )
    counts = {"sat": 0, "unsat": 0, "unknown": 0}
    stop = False
    for weights in rows:
        for cell in cells:
            if args.all_incidences:
                x_choice, z_choice = cell
                transition = None
            else:
                transition, _ = cell
                x_choice = z_choice = None
            query = build_query(
                weights,
                transition,
                args.timeout_ms,
                pairwise_only=args.pairwise_only,
                x_choice=x_choice,
                z_choice=z_choice,
                pair_box_only=args.pair_box_only,
                one_full_selector=args.one_full_selector,
                min_trigger_roles=min_trigger_roles,
                max_trigger_roles=max_trigger_roles,
            )
            with tempfile.NamedTemporaryFile(
                "w", suffix=".smt2", delete=False
            ) as handle:
                handle.write(query)
                path = Path(handle.name)
            completed = subprocess.run(
                [args.z3, str(path)],
                capture_output=True,
                text=True,
                timeout=args.timeout_ms / 1000 + 30,
                check=False,
            )
            path.unlink(missing_ok=True)
            status = completed.stdout.splitlines()[0] if completed.stdout else "unknown"
            if status not in counts:
                status = "unknown"
            counts[status] += 1
            row = {
                "weights": list(weights),
                "n": sum(weights),
                "transition": transition,
                "x_active_endpoints": (
                    [list(item) for item in x_choice] if x_choice else None
                ),
                "z_active_endpoints": (
                    [list(item) for item in z_choice] if z_choice else None
                ),
                "status": status,
            }
            if status == "sat":
                row["model"] = completed.stdout
            if completed.returncode != 0 or status == "unknown":
                row["stderr"] = completed.stderr
            results.append(row)
            print(
                json.dumps(
                    {
                        "cell": len(results),
                        "weights": list(weights),
                        "transition": transition,
                        "status": status,
                    }
                ),
                flush=True,
            )
            if status == "sat" and args.stop_on_sat:
                stop = True
                break
        if stop:
            break
    report = {
        "status": "fixed-weight noncommon transition audit",
        "evidence_class": "quantified exact linear-real arithmetic",
        "scope": (
            "structural existence in the interval--pair-slab relaxation with "
            "all required zero unit-singleton witnesses; "
            + (
                "only mutual selector fairness tested; "
                if args.pairwise_only
                else "full quantified selector fairness tested; "
            )
            + "SAT requires exact-game replay"
        ),
        "counts": counts,
        "results": results,
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(json.dumps({"counts": counts, "cells": len(results)}, indent=2))


if __name__ == "__main__":
    main()

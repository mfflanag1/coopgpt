#!/usr/bin/env python3
"""Exact quantified-LRA audit of the finite common-two-flat residue.

The unrestricted endowed-seesaw theorem leaves six ordered weight rows at
atomic sizes 6,...,9.  This verifier represents an arbitrary nonnegative
four-role core by four coordinate intervals and three complementary pair-sum
slabs.  It retains the exactness witnesses attaining every zero unit-role
singleton and deliberately relaxes attainment of the other bounds.  Weighted
Lmin and Lmax are defined by the equivalent max-min/min-max fairness
conditions, universally quantified over the core; no selector stratum, dual
support, or active coordinate face is assumed.

For each remaining weight row Z3 is asked for a target-violating relaxed core
whose two selectors share endpoints of at least two pair slabs.  An unsat
answer is a computer-assisted finite theorem, subordinate to the human
large-n common-face argument.  The encoding is independently formulated
from the staged rational LP verifier.
"""

from __future__ import annotations

import argparse
import itertools
import json
import subprocess
import tempfile
from fractions import Fraction as F
from pathlib import Path


ROWS_P_R_Q_B = (
    (1, 2, 1, 2),
    (1, 3, 1, 1),
    (1, 3, 1, 2),
    (1, 4, 1, 1),
    (1, 5, 1, 1),
    (1, 6, 1, 1),
)


def atomic_target(n):
    return F(4 * n, n * n - (n % 2))


def smt_fraction(value):
    value = F(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"(/ {value.numerator} {value.denominator})"


def add(*terms):
    if len(terms) == 1:
        return terms[0]
    return f"(+ {' '.join(terms)})"


def ratio(role_term, weight):
    return role_term if weight == 1 else f"(/ {role_term} {weight})"


def fairness_formula(selector_prefix, weights, mode):
    """Max-min or min-max fairness, equivalent to the weighted lex selector."""

    clauses = []
    for role, weight in enumerate(weights):
        y_value = ratio(f"y{role}", weight)
        selected = ratio(f"{selector_prefix}{role}", weight)
        if mode == "min":
            trigger = f"(> {y_value} {selected})"
            repairs = [
                f"(and (<= {ratio(f'{selector_prefix}{j}', weights[j])} {selected}) "
                f"(< {ratio(f'y{j}', weights[j])} {ratio(f'{selector_prefix}{j}', weights[j])}))"
                for j in range(4)
            ]
        else:
            trigger = f"(< {y_value} {selected})"
            repairs = [
                f"(and (>= {ratio(f'{selector_prefix}{j}', weights[j])} {selected}) "
                f"(> {ratio(f'y{j}', weights[j])} {ratio(f'{selector_prefix}{j}', weights[j])}))"
                for j in range(4)
            ]
        clauses.append(f"(=> {trigger} (or {' '.join(repairs)}))")
    return f"(and {' '.join(clauses)})"


def core_formula(prefix):
    coordinates = [f"{prefix}{role}" for role in range(4)]
    pair_terms = (
        add(coordinates[0], coordinates[1]),
        add(coordinates[0], coordinates[2]),
        add(coordinates[0], coordinates[3]),
    )
    clauses = [f"(= {add(*coordinates)} 1)"]
    clauses.extend(
        f"(and (<= lo{role} {coordinate}) (<= {coordinate} hi{role}))"
        for role, coordinate in enumerate(coordinates)
    )
    clauses.extend(
        f"(and (<= L{j} {term}) (<= {term} U{j}))"
        for j, term in enumerate(pair_terms)
    )
    return f"(and {' '.join(clauses)})"


def build_query(weights, common_choice=None, overlap_signs=None, timeout_ms=300000):
    n = sum(weights)
    lines = [
        "(set-logic LRA)",
        "(set-option :produce-models true)",
        f"(set-option :timeout {timeout_ms})",
    ]
    for stem in ("lo", "hi"):
        for role in range(4):
            lines.append(f"(declare-const {stem}{role} Real)")
    for stem in ("L", "U"):
        for pair in range(3):
            lines.append(f"(declare-const {stem}{pair} Real)")
    for prefix in ("x", "z"):
        for role in range(4):
            lines.append(f"(declare-const {prefix}{role} Real)")

    # Nonnegative characteristic function after normalizing v(R)=1.
    lines.append(
        "(assert (and "
        + " ".join(f"(<= 0 lo{i}) (<= lo{i} hi{i}) (<= hi{i} 1)" for i in range(4))
        + " "
        + " ".join(f"(<= 0 L{j}) (<= L{j} U{j}) (<= U{j} 1)" for j in range(3))
        + "))"
    )
    for role, weight in enumerate(weights):
        if weight == 1:
            lines.append(f"(assert (= lo{role} 0))")
    lines.append(f"(assert {core_formula('x')})")
    lines.append(f"(assert {core_formula('z')})")

    # Every objective-A game has a core witness attaining each zero
    # unit-role singleton.  Omitting all other attainment constraints makes
    # this a relaxation, so unsatisfiability remains a valid theorem.
    unit_roles = [role for role, weight in enumerate(weights) if weight == 1]
    for witness, attained_role in enumerate(unit_roles):
        for role in range(4):
            lines.append(f"(declare-const w{witness}{role} Real)")
        lines.append(f"(assert {core_formula(f'w{witness}')})")
        lines.append(f"(assert (= w{witness}{attained_role} 0))")

    pair_roles = ((0, 1), (0, 2), (0, 3))

    # Max-min and min-max fairness are equivalent to the repeated-player
    # leximin and leximax selectors on a compact convex core.
    min_fair = fairness_formula("x", weights, "min")
    max_fair = fairness_formula("z", weights, "max")
    y_core = core_formula("y")
    lines.append(
        f"(assert (forall ({' '.join(f'(y{i} Real)' for i in range(4))}) "
        f"(=> {y_core} {min_fair})))"
    )
    lines.append(
        f"(assert (forall ({' '.join(f'(y{i} Real)' for i in range(4))}) "
        f"(=> {y_core} {max_fair})))"
    )

    # At least two of the three pair coordinates have the same endpoint at
    # both selectors.  Extra common endpoints are allowed.
    common = []
    for pair, roles in enumerate(pair_roles):
        xpair = add(*(f"x{role}" for role in roles))
        zpair = add(*(f"z{role}" for role in roles))
        common.append(
            f"(or (and (= {xpair} L{pair}) (= {zpair} L{pair})) "
            f"(and (= {xpair} U{pair}) (= {zpair} U{pair})))"
        )
    if common_choice is None:
        lines.append(
            f"(assert (or (and {common[0]} {common[1]}) "
            f"(and {common[0]} {common[2]}) (and {common[1]} {common[2]})))"
        )
    else:
        for pair, endpoint in common_choice:
            roles = pair_roles[pair]
            xpair = add(*(f"x{role}" for role in roles))
            zpair = add(*(f"z{role}" for role in roles))
            lines.append(f"(assert (= {xpair} {endpoint}{pair}))")
            lines.append(f"(assert (= {zpair} {endpoint}{pair}))")

    if overlap_signs is None:
        overlap_terms = [f"(ite (<= x{i} z{i}) x{i} z{i})" for i in range(4)]
    else:
        overlap_terms = []
        for role, x_is_minimum in enumerate(overlap_signs):
            if x_is_minimum:
                lines.append(f"(assert (<= x{role} z{role}))")
                overlap_terms.append(f"x{role}")
            else:
                lines.append(f"(assert (<= z{role} x{role}))")
                overlap_terms.append(f"z{role}")
    overlap = add(*overlap_terms)
    lines.append(f"(assert (< {overlap} {smt_fraction(atomic_target(n))}))")
    lines.append("(check-sat-using (then qe2 smt))")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--z3", default="z3")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--keep-smt2", type=Path)
    parser.add_argument("--only-row", help="optional p,r,q,b row")
    parser.add_argument("--timeout-ms", type=int, default=30000)
    args = parser.parse_args()
    selected_rows = ROWS_P_R_Q_B
    if args.only_row:
        selected = tuple(map(int, args.only_row.split(",")))
        if selected not in ROWS_P_R_Q_B:
            parser.error("--only-row is not one of the six finite rows")
        selected_rows = (selected,)
    results = []
    for row in selected_rows:
        # The common-line coordinate order is (p,q,r,b).
        weights = (row[0], row[2], row[1], row[3])
        counts = {"unsat": 0, "sat": 0, "unknown": 0}
        configurations = []
        for pair_choice in itertools.combinations(range(3), 2):
            for endpoints in itertools.product(("L", "U"), repeat=2):
                common_choice = tuple(zip(pair_choice, endpoints))
                for signs in itertools.product((False, True), repeat=4):
                    query = build_query(
                        weights,
                        common_choice,
                        signs,
                        args.timeout_ms,
                    )
                    with tempfile.NamedTemporaryFile(
                        "w", suffix=".smt2", delete=False
                    ) as handle:
                        handle.write(query)
                        query_path = Path(handle.name)
                    if args.keep_smt2:
                        args.keep_smt2.mkdir(parents=True, exist_ok=True)
                        name = (
                            "common_two_"
                            + "_".join(map(str, row))
                            + "_"
                            + "_".join(f"{pair}{endpoint}" for pair, endpoint in common_choice)
                            + "_"
                            + "".join("x" if sign else "z" for sign in signs)
                            + ".smt2"
                        )
                        (args.keep_smt2 / name).write_text(query)
                    completed = subprocess.run(
                        [args.z3, str(query_path)],
                        check=False,
                        capture_output=True,
                        text=True,
                        timeout=(args.timeout_ms / 1000) + 30,
                    )
                    query_path.unlink(missing_ok=True)
                    first = (
                        completed.stdout.splitlines()[0]
                        if completed.stdout
                        else "no-output"
                    )
                    counts[first] = counts.get(first, 0) + 1
                    if completed.returncode != 0 or first not in {"unsat", "sat"}:
                        raise RuntimeError(
                            (
                                row,
                                common_choice,
                                signs,
                                completed.returncode,
                                completed.stdout,
                                completed.stderr,
                            )
                        )
                    if first == "sat":
                        raise AssertionError(
                            (
                                "target-violating common-two core",
                                row,
                                common_choice,
                                signs,
                                completed.stdout,
                            )
                        )
                    configurations.append(
                        {
                            "common_endpoints": [list(item) for item in common_choice],
                            "overlap_minimum_from_x": list(signs),
                            "z3_status": first,
                        }
                    )
        results.append(
            {
                "weights_p_r_q_b": list(row),
                "line_order_weights_p_q_r_b": list(weights),
                "atomic_target": str(atomic_target(sum(row))),
                "endpoint_orientation_cells": 12,
                "overlap_sign_cells_per_orientation": 16,
                "configurations_checked": len(configurations),
                "status_counts": counts,
            }
        )
    report = {
        "status": "finite common-two exact-core target theorem verified by quantified LRA",
        "encoding": (
            "four coordinate intervals plus three complementary pair slabs; "
            "every zero unit singleton attained and all other exactness "
            "attainment constraints relaxed; quantified max-min/min-max "
            "fairness definitions of weighted Lmin and Lmax"
        ),
        "rows": results,
        "scope": (
            "computer-assisted finite closure of the six relaxed rows left by "
            "the human unrestricted common-face theorem; does not cover "
            "noncommon edge transitions"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Exact controls for eliminating the common singleton witness.

The human rooted-hinge projection theorem replaces the witness ``w^r`` by
all rooted fractional Lmin-support packing inequalities.  Common-hinge rows
already identify ``x(S)=z(S)``, so the apparent second colour is redundant.
This verifier
uses an exact cutting-plane formulation of that projection and compares its
minimum with the existing direct one-witness LP on every maximum-overlap root
of five hostile branches and two sharp-family orientations.

The two formulations share the fixed labelled branch data, but their
witness-feasibility components are independently formulated.  Agreement on
these seven branches is a control, not proof of the human projection theorem
or of the all-n hybrid-overlap conjecture.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from exactlp import exact_linprog  # noqa: E402

from verify_labelled_branch_duals import (  # noqa: E402
    CASES,
    branch_system,
    one_witness_minimum,
)


def master_without_witness(system):
    """Keep x,z rows and their direct tightness comparisons."""
    n = system["n"]
    columns = list(range(2 * n))
    inequality_rows = []
    for k, label in enumerate(system["inequality_labels"]):
        if label[0] == "nonnegative" and label[1] >= 2:
            continue
        if label[0] == "tight" and label[3] >= 2:
            continue
        inequality_rows.append(k)
    equality_rows = []
    for k, label in enumerate(system["equality_labels"]):
        if label[0] == "total" and label[1] >= 2:
            continue
        if label[0] == "witness_zero":
            continue
        equality_rows.append(k)
    return {
        "objective": [system["objective"][j] for j in columns],
        "aub": [
            [system["inequalities"][k][j] for j in columns]
            for k in inequality_rows
        ],
        "bub": [system["inequality_rhs"][k] for k in inequality_rows],
        "aeq": [
            [system["equalities"][k][j] for j in columns]
            for k in equality_rows
        ],
        "beq": [system["equality_rhs"][k] for k in equality_rows],
    }


def separator(coalitions, n, root, x):
    """Maximize the projected rooted-hinge inequality at fixed x,z."""
    width = len(coalitions)
    aub, bub = [], []
    for player in range(n):
        if player == root:
            continue
        aub.append([F(int(coalition >> player & 1)) for coalition in coalitions])
        bub.append(F(1))
    for variable in range(width):
        row = [F(0)] * width
        row[variable] = F(-1)
        aub.append(row)
        bub.append(F(0))
    objective = []
    for coalition in coalitions:
        objective.append(
            -sum((x[i] for i in range(n) if coalition >> i & 1), F(0))
        )
    status, negative_value, weights = exact_linprog(objective, aub, bub)
    if status != "optimal":
        raise AssertionError(f"rooted-hinge separator is {status}")
    return -negative_value, weights


def projected_minimum(case, root):
    common = tuple(sorted(set(case["support_x"]).intersection(case["support_z"])))
    reduced_case = dict(case)
    reduced_case["support_z"] = common
    system = branch_system(reduced_case)
    n = system["n"]
    master = master_without_witness(system)
    coalitions = tuple(case["support_x"])
    cuts = []

    for _iteration in range(256):
        status, optimum, solution = exact_linprog(
            master["objective"],
            master["aub"],
            master["bub"],
            master["aeq"],
            master["beq"],
        )
        if status != "optimal":
            raise AssertionError(f"projected master is {status}")
        x = solution[:n]
        violation, weights = separator(coalitions, n, root, x)
        if violation <= 1:
            return optimum, cuts

        support = tuple(k for k, weight in enumerate(weights) if weight > 0)
        if len(support) > n - 1:
            raise AssertionError("extreme rooted-hinge packing exceeds support bound")
        row = [F(0)] * (2 * n)
        for weight, coalition in zip(weights, coalitions):
            if weight == 0:
                continue
            for player in range(n):
                if coalition >> player & 1:
                    row[player] += weight
        master["aub"].append(row)
        master["bub"].append(F(1))
        cuts.append(
            {
                "violated_value": str(violation),
                "support": [
                    {
                        "coalition": coalitions[k],
                        "weight": str(weights[k]),
                    }
                    for k in support
                ],
            }
        )
    raise AssertionError("rooted-hinge cutting plane did not terminate")


def audit_case(case0):
    case = dict(case0)
    common = tuple(sorted(set(case["support_x"]).intersection(case["support_z"])))
    case["support_z"] = common
    system = branch_system(case)
    n = system["n"]
    coordinate_overlap = tuple(min(case["x"][i], case["z"][i]) for i in range(n))
    roots = tuple(
        i for i, value in enumerate(coordinate_overlap)
        if value == max(coordinate_overlap)
    )
    rows = []
    for root in roots:
        projected, cuts = projected_minimum(case0, root)
        direct = one_witness_minimum(system, root)
        if projected != direct:
            raise AssertionError(
                {
                    "case": case["name"],
                    "root": root,
                    "projected": str(projected),
                    "direct": str(direct),
                }
            )
        rows.append(
            {
                "root": root,
                "projected_minimum": str(projected),
                "direct_witness_minimum": str(direct),
                "cut_count": len(cuts),
                "maximum_cut_support": max(
                    (len(cut["support"]) for cut in cuts), default=0
                ),
                "cuts": cuts,
            }
        )
    return {
        "name": case["name"],
        "n": n,
        "lmin_support": list(case["support_x"]),
        "common_hinge_support": list(common),
        "maximum_overlap_roots": list(roots),
        "roots": rows,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {
        "status": "exact rooted-hinge projection controls",
        "human_theorem_audited": (
            "after common rows identify x(S)=z(S), eliminating a singleton-zero "
            "witness gives all rooted fractional Lmin-support packing inequalities; "
            "extreme packings use at most n-1 rows"
        ),
        "scope": (
            "maximum-overlap roots of five hostile fixed branches and two sharp "
            "orientations; exact controls only, not an all-n proof"
        ),
        "cases": [audit_case(case) for case in CASES],
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

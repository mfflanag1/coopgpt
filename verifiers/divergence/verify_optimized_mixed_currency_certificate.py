#!/usr/bin/env python3
"""Solver-free exact certificate for the hardest n=7 spectral branch.

The certificate is a literal nonnegative slack decomposition of
O-3/4.  It turns the previously solver-returned root-3 optimum into a short
human-checkable proof and records how witness, cross-hinge, and order
currencies pay the branch deficit.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_lmax_overcover import coalition_sum  # noqa: E402
from verify_labelled_branch_duals import CASES, branch_system  # noqa: E402


CASE = CASES[0]
N = 7
ROOT = 3
ALLOWED = {0, 1, 2 + ROOT}

INEQUALITY_WEIGHTS = {
    ("nonnegative", 1, 2): F(1),
    ("nonnegative", 5, 2): F(1, 2),
    ("nonnegative", 5, 5): F(1, 4),
    ("nonnegative", 5, 6): F(1, 4),
    ("tight", "x", 26, 5): F(1, 4),
    ("tight", "x", 57, 5): F(1, 4),
    ("tight", "z", 52, 0): F(5, 4),
    ("tight", "z", 57, 0): F(1, 2),
    ("tight", "z", 75, 5): F(1, 4),
    ("stratum_order", 0, 4, 0): F(3, 4),
    ("stratum_order", 1, 4, 5): F(1, 2),
    ("stratum_order", 1, 5, 1): F(1),
}
EQUALITY_WEIGHTS = {
    ("total", 1): F(5, 4),
    ("total", 5): F(-1, 2),
    ("witness_zero", 3): F(-1, 4),
    ("stratum_equal", 0, 1, 2): F(-5, 4),
    ("stratum_equal", 0, 4, 5): F(-1, 2),
    ("stratum_equal", 1, 0, 3): F(1, 2),
}
PRIMAL = (
    F(5, 32), F(1, 16), F(1, 16), F(11, 32), F(5, 32), F(5, 32), F(1, 16),
    F(7, 32), F(3, 16), F(0), F(7, 32), F(3, 16), F(3, 16), F(0),
    F(7, 16), F(3, 16), F(0), F(0), F(3, 8), F(0), F(0),
)


def restricted_system():
    system = branch_system(CASE)
    columns = [generator * N + player for generator in sorted(ALLOWED) for player in range(N)]
    inequality_rows = []
    for k, label in enumerate(system["inequality_labels"]):
        if label[0] == "nonnegative" and label[1] not in ALLOWED:
            continue
        if label[0] == "tight" and label[3] not in ALLOWED:
            continue
        inequality_rows.append(k)
    equality_rows = []
    for k, label in enumerate(system["equality_labels"]):
        if label[0] == "total" and label[1] not in ALLOWED:
            continue
        if label[0] == "witness_zero" and label[1] != ROOT:
            continue
        equality_rows.append(k)
    return {
        "inequalities": [
            [system["inequalities"][k][j] for j in columns] for k in inequality_rows
        ],
        "inequality_rhs": [system["inequality_rhs"][k] for k in inequality_rows],
        "inequality_labels": [system["inequality_labels"][k] for k in inequality_rows],
        "equalities": [
            [system["equalities"][k][j] for j in columns] for k in equality_rows
        ],
        "equality_rhs": [system["equality_rhs"][k] for k in equality_rows],
        "equality_labels": [system["equality_labels"][k] for k in equality_rows],
        "objective": [system["objective"][j] for j in columns],
    }


def audit_certificate():
    system = restricted_system()
    for row, rhs in zip(system["inequalities"], system["inequality_rhs"]):
        if sum((a * b for a, b in zip(row, PRIMAL)), F(0)) > rhs:
            raise AssertionError("displayed rooted primal is infeasible")
    for row, rhs in zip(system["equalities"], system["equality_rhs"]):
        if sum((a * b for a, b in zip(row, PRIMAL)), F(0)) != rhs:
            raise AssertionError("displayed rooted primal violates a branch equality")
    primal_value = sum((a * b for a, b in zip(system["objective"], PRIMAL)), F(0))
    if primal_value != F(3, 4):
        raise AssertionError("displayed rooted primal objective changed")

    nu = [INEQUALITY_WEIGHTS.get(label, F(0)) for label in system["inequality_labels"]]
    pi = [EQUALITY_WEIGHTS.get(label, F(0)) for label in system["equality_labels"]]
    if set(INEQUALITY_WEIGHTS) - set(system["inequality_labels"]):
        raise AssertionError("hard-coded inequality label disappeared")
    if set(EQUALITY_WEIGHTS) - set(system["equality_labels"]):
        raise AssertionError("hard-coded equality label disappeared")
    for coordinate, objective_coefficient in enumerate(system["objective"]):
        lhs = -sum(
            (weight * row[coordinate] for weight, row in zip(nu, system["inequalities"])),
            F(0),
        )
        lhs += sum(
            (weight * row[coordinate] for weight, row in zip(pi, system["equalities"])),
            F(0),
        )
        if lhs != objective_coefficient:
            raise AssertionError(("dual stationarity", coordinate, lhs, objective_coefficient))
    dual_value = sum(
        (weight * rhs for weight, rhs in zip(pi, system["equality_rhs"])), F(0)
    ) - sum(
        (weight * rhs for weight, rhs in zip(nu, system["inequality_rhs"])), F(0)
    )
    if dual_value != primal_value:
        raise AssertionError("primal/dual values differ")
    return system, nu, primal_value


def audit_actual_slacks(system, nu):
    total = sum(map(F, CASE["g"]), F(0))
    x = tuple(q / total for q in CASE["x"])
    z = tuple(q / total for q in CASE["z"])
    # h has zero at the distinguished root and is an actual core witness.
    witness = tuple(F(q, total) for q in CASE["h"])
    actual = x + z + witness
    slacks = []
    for label, weight, row, rhs in zip(
        system["inequality_labels"], nu, system["inequalities"], system["inequality_rhs"]
    ):
        if not weight:
            continue
        slack = rhs - sum((a * b for a, b in zip(row, actual)), F(0))
        if slack < 0:
            raise AssertionError(("actual branch slack is negative", label, slack))
        slacks.append({"label": list(label), "weight": str(weight), "slack": str(slack)})
    objective = sum((a * b for a, b in zip(system["objective"], actual)), F(0))
    weighted_slack = sum(
        (F(row["weight"]) * F(row["slack"]) for row in slacks), F(0)
    )
    if objective - F(3, 4) != weighted_slack:
        raise AssertionError("slack decomposition does not recover the actual margin")
    return objective, weighted_slack, slacks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    system, nu, optimum = audit_certificate()
    actual, margin, slacks = audit_actual_slacks(system, nu)
    report = {
        "status": "solver-free exact mixed-currency certificate",
        "case": CASE["name"],
        "root": ROOT,
        "human_identity": "O-3/4 is the displayed nonnegative weighted slack sum",
        "rooted_relaxation_optimum": str(optimum),
        "rooted_primal": {
            "lmin": [str(q) for q in PRIMAL[:N]],
            "lmax": [str(q) for q in PRIMAL[N:2 * N]],
            "witness": [str(q) for q in PRIMAL[2 * N:]],
        },
        "dual_nonzero_inequalities": len(INEQUALITY_WEIGHTS),
        "dual_nonzero_equalities": len(EQUALITY_WEIGHTS),
        "actual_overlap_ratio": str(actual),
        "actual_margin_above_three_quarters": str(margin),
        "weighted_slacks_at_actual_control": slacks,
        "scope": (
            "one fixed labelled n=7 branch; the human slack identity proves the "
            "branch bound, but does not establish universal root selection"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

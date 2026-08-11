#!/usr/bin/env python3
"""Exact hostile audit of the over-cover-to-pair-lift coupling.

For every maximum-overlap Lmax root in the archived hostile controls, this
script solves two rational linear programs.

``deleted_load`` minimizes the largest nonroot alpha-coordinate among all
normalized Lmax top over-covers.  This is the root-specific normalization in
the human over-cover-to-pair-lift theorem; its returned support need not be
Lmin-tight.

``common_leader`` restricts the over-cover to coalitions tight at both Lmin
and Lmax and maximizes

    alpha_root - max_{i != root} alpha_i.

Thus a positive optimum is an exact certificate that the theorem produces a
positive-root pair lift, while a nonpositive optimum rules out that premise
for *every* common normalized top over-cover at the fixed game and root.

All returned witnesses are checked directly with Fraction arithmetic.  The
finite controls test the premises of the human theorem; they are not evidence
for the universal hybrid-overlap conjecture.  The coefficient-two output also
checks the rooted-pair gauge quotient and its two-facet decomposition.
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

from audit_lmax_overcover import coalition_sum  # noqa: E402
from verify_labelled_branch_duals import CASES  # noqa: E402
from verify_rooted_hinge_projection import (  # noqa: E402
    NEUTRAL_CASE,
    decomposition_witnesses,
    matrix_rank,
)


CONTROL_CASES = CASES + (NEUTRAL_CASE,)


def characteristic_function(case):
    g = tuple(map(F, case["g"]))
    h = tuple(map(F, case["h"]))
    n = len(g)
    return tuple(
        min(coalition_sum(g, coalition), coalition_sum(h, coalition))
        for coalition in range(1 << n)
    )


def tight_support(values, point):
    full = (1 << len(point)) - 1
    return tuple(
        coalition
        for coalition in range(1, full)
        if coalition_sum(point, coalition) == values[coalition]
    )


def maximum_overlap_roots(x, z):
    maximum = max(z)
    return tuple(i for i, value in enumerate(z) if value == maximum and x[i] >= maximum)


def solve_overcover(values, x, z, root, support, objective_mode):
    """Return an exact normalized top over-cover on ``support``.

    In deleted-load mode the last variable is theta and the objective is to
    minimize it subject to alpha_i <= theta off the root.  In common-leader
    mode the same epigraph is used and theta-alpha_root is minimized, i.e.
    the strict-root gap alpha_root-theta is maximized.
    """
    n = len(z)
    maximum = max(z)
    top = tuple(i for i, value in enumerate(z) if value == maximum)
    m = len(support)
    eta_index = m
    alpha_index = {player: m + 1 + j for j, player in enumerate(top)}
    theta_index = m + 1 + len(top)
    width = theta_index + 1

    equalities, equality_rhs = [], []
    for player in range(n):
        row = [F(0)] * width
        for j, coalition in enumerate(support):
            row[j] = F((coalition >> player) & 1)
        row[eta_index] = -1
        if player in alpha_index:
            row[alpha_index[player]] = -1
        equalities.append(row)
        equality_rhs.append(F(0))
    row = [F(0)] * width
    for player in top:
        row[alpha_index[player]] = 1
    equalities.append(row)
    equality_rhs.append(F(1))

    inequalities, inequality_rhs = [], []
    for variable in range(width):
        row = [F(0)] * width
        row[variable] = -1
        inequalities.append(row)
        inequality_rhs.append(F(0))
    for player in range(n):
        if player == root:
            continue
        row = [F(0)] * width
        if player in alpha_index:
            row[alpha_index[player]] = 1
        row[theta_index] = -1
        inequalities.append(row)
        inequality_rhs.append(F(0))

    objective = [F(0)] * width
    objective[theta_index] = 1
    if objective_mode == "common_leader":
        objective[alpha_index[root]] = -1
    elif objective_mode != "deleted_load":
        raise ValueError(objective_mode)

    status, objective_value, solution = exact_linprog(
        objective, inequalities, inequality_rhs, equalities, equality_rhs
    )
    if status != "optimal":
        return {"status": status}

    lambdas = tuple(solution[j] for j in range(m))
    eta = solution[eta_index]
    alpha = tuple(
        solution[alpha_index[player]] if player in alpha_index else F(0)
        for player in range(n)
    )
    theta_minus = solution[theta_index]
    if theta_minus != max(alpha[i] for i in range(n) if i != root):
        raise AssertionError("nonroot epigraph is not tight")
    if sum(alpha, F(0)) != 1 or any(value < 0 for value in lambdas + alpha):
        raise AssertionError("invalid normalized over-cover signs")
    if eta < 0 or theta_minus < 0:
        raise AssertionError("invalid eta or deleted load")
    for player in range(n):
        load = sum(
            (lambdas[j] for j, coalition in enumerate(support) if coalition >> player & 1),
            F(0),
        )
        if load != eta + alpha[player]:
            raise AssertionError("over-cover incidence identity failed")
    if objective_mode == "deleted_load" and objective_value != theta_minus:
        raise AssertionError("deleted-load objective orientation failed")
    leader_gap = alpha[root] - theta_minus
    if objective_mode == "common_leader" and objective_value != -leader_gap:
        raise AssertionError("common-leader objective orientation failed")

    positive = tuple(
        (coalition, lambdas[j])
        for j, coalition in enumerate(support)
        if lambdas[j] > 0
    )
    common = set(tight_support(values, x)).intersection(tight_support(values, z))
    result = {
        "status": "optimal",
        "eta": str(eta),
        "alpha": [str(value) for value in alpha],
        "theta_minus": str(theta_minus),
        "leader_gap": str(leader_gap),
        "support": [coalition for coalition, _weight in positive],
        "weights": [str(weight) for _coalition, weight in positive],
        "support_is_common": all(coalition in common for coalition, _weight in positive),
    }

    if result["support_is_common"] and eta + theta_minus > 0:
        result["pair_lift"] = audit_pair_lift(
            values, x, z, root, positive, eta, alpha, theta_minus
        )
    return result


def audit_pair_lift(values, x, z, root, positive, eta, alpha, theta_minus):
    """Check the theorem's normalized packing and its two exact slacks."""
    n = len(x)
    full = (1 << n) - 1
    theta = eta + theta_minus
    u = tuple((coalition, weight / theta) for coalition, weight in positive)
    loads = [
        sum((weight for coalition, weight in u if coalition >> player & 1), F(0))
        for player in range(n)
    ]
    if any(loads[i] > 1 for i in range(n) if i != root):
        raise AssertionError("normalized support is not a rooted packing")
    delta = (alpha[root] - theta_minus) / theta
    deficits = [F(0) if i == root else (theta_minus - alpha[i]) / theta for i in range(n)]
    if delta != loads[root] - 1:
        raise AssertionError("root advantage formula failed")
    if any(deficits[i] != 1 - loads[i] for i in range(n) if i != root):
        raise AssertionError("deficit formula failed")

    root_mask = 1 << root
    coefficient = delta + sum(deficits, F(0))
    incidence_loads = [F(0)] * n
    for coalition, weight in u:
        for player in range(n):
            incidence_loads[player] += weight * F((coalition >> player) & 1)
    for i in range(n):
        if i == root or deficits[i] == 0:
            continue
        pair = root_mask | (1 << i)
        for player in range(n):
            incidence_loads[player] += deficits[i] * F((pair >> player) & 1)
    incidence_loads[root] -= coefficient
    if incidence_loads != [F(1)] * n:
        raise AssertionError("pair-lift incidence identity failed")

    slacks = []
    scaled_slacks = []
    for point in (x, z):
        slack = values[full]
        slack -= sum((weight * values[coalition] for coalition, weight in u), F(0))
        slack -= sum(
            (
                deficits[i] * values[root_mask | (1 << i)]
                for i in range(n)
                if i != root
            ),
            F(0),
        )
        slack += coefficient * values[root_mask]
        slacks.append(slack)
        scaled = sum(
            ((theta_minus - alpha[i]) * point[i] for i in range(n) if i != root),
            F(0),
        )
        scaled -= (alpha[root] - theta_minus) * point[root]
        scaled -= sum(
            (
                (theta_minus - alpha[i]) * values[root_mask | (1 << i)]
                for i in range(n)
                if i != root
            ),
            F(0),
        )
        if scaled != theta * slack:
            raise AssertionError("scaled pair-lift slack formula failed")
        scaled_slacks.append(scaled)
    if slacks[0] != slacks[1]:
        raise AssertionError("common pair-lift slacks differ")
    difference_lhs = sum(
        (
            (theta_minus - alpha[i]) * (x[i] - z[i])
            for i in range(n)
            if i != root
        ),
        F(0),
    )
    difference_rhs = (alpha[root] - theta_minus) * (x[root] - z[root])
    if difference_lhs != difference_rhs:
        raise AssertionError("pair-lift tangent balance failed")
    return {
        "theta": str(theta),
        "root_advantage": str(delta),
        "deficits": [str(value) for value in deficits],
        "pair_lift_slack_x": str(slacks[0]),
        "pair_lift_slack_z": str(slacks[1]),
        "scaled_slack_x": str(scaled_slacks[0]),
        "scaled_slack_z": str(scaled_slacks[1]),
        "difference_identity_lhs": str(difference_lhs),
        "difference_identity_rhs": str(difference_rhs),
    }


def pair_lift_coefficients(n, root, coalition_weights):
    """Form the merged rooted-pair lift of one rooted packing."""
    loads = [F(0)] * n
    coefficients = {}
    for coalition, weight in coalition_weights:
        if weight == 0:
            continue
        coefficients[coalition] = coefficients.get(coalition, F(0)) + weight
        for player in range(n):
            if coalition >> player & 1:
                loads[player] += weight
    deficits = [F(0) if i == root else F(1) - loads[i] for i in range(n)]
    if any(value < 0 for value in deficits):
        raise AssertionError("not a rooted packing")
    delta = loads[root] - 1
    root_mask = 1 << root
    for player in range(n):
        if player == root or deficits[player] == 0:
            continue
        pair = root_mask | (1 << player)
        coefficients[pair] = coefficients.get(pair, F(0)) + deficits[player]
    coefficients[root_mask] = coefficients.get(root_mask, F(0)) - delta - sum(
        deficits, F(0)
    )
    return {
        coalition: coefficient
        for coalition, coefficient in coefficients.items()
        if coefficient
    }


def coefficient_two_pair_gauge_audit():
    """Exact quotient and facet decomposition of the strict common packet."""
    case = next(
        row for row in CASES if row["name"] == "coefficient_two_congestion_failure"
    )
    values = characteristic_function(case)
    n, root = 7, 3
    aggregate_packing = ((24, F(1, 2)), (44, F(1, 2)), (79, F(1, 2)))
    reduced_packing = ((44, F(1, 2)), (79, F(1, 2)))
    aggregate = pair_lift_coefficients(n, root, aggregate_packing)
    reduced = pair_lift_coefficients(n, root, reduced_packing)
    if aggregate != reduced:
        raise AssertionError("root-pair gauge deletion changed the lifted row")

    facets = []
    component_coefficients = []
    for coalition in (44, 79):
        coefficients = pair_lift_coefficients(n, root, ((coalition, F(1)),))
        support = tuple(sorted(coefficients))
        if matrix_rank(support, n) != len(support):
            raise AssertionError("coefficient-two component is not support-minimal")
        decompositions = decomposition_witnesses(support, n)
        if decompositions:
            raise AssertionError("coefficient-two component is decomposable")
        slack = values[(1 << n) - 1] - sum(
            (
                coefficient * values[mask]
                for mask, coefficient in coefficients.items()
            ),
            F(0),
        )
        if slack != 0:
            raise AssertionError("coefficient-two component facet is not active")
        component_coefficients.append(coefficients)
        facets.append(
            {
                "packing_vertex": [{"coalition": coalition, "weight": "1"}],
                "coefficients": [
                    {"coalition": mask, "coefficient": str(coefficients[mask])}
                    for mask in support
                ],
                "support_size": len(support),
                "incidence_rank": matrix_rank(support, n),
                "decomposition_count": 0,
                "indecomposable": True,
                "exact_cone_facet": True,
                "game_inequality_slack": "0",
            }
        )
    averaged = {
        mask: (component_coefficients[0].get(mask, F(0)) + component_coefficients[1].get(mask, F(0))) / 2
        for mask in set(component_coefficients[0]).union(component_coefficients[1])
    }
    averaged = {mask: coefficient for mask, coefficient in averaged.items() if coefficient}
    if averaged != aggregate:
        raise AssertionError("two-facet average does not recover the aggregate row")
    return {
        "root": root,
        "strict_common_overcover_normalized_packing": [
            {"coalition": coalition, "weight": str(weight)}
            for coalition, weight in aggregate_packing
        ],
        "root_pair_gauge_coalition": 24,
        "gauge_deleted_packing": [
            {"coalition": coalition, "weight": str(weight)}
            for coalition, weight in reduced_packing
        ],
        "lift_unchanged_by_gauge_deletion": True,
        "aggregate_coefficients": [
            {"coalition": mask, "coefficient": str(aggregate[mask])}
            for mask in sorted(aggregate)
        ],
        "facet_decomposition_weights": ["1/2", "1/2"],
        "distinct_active_facets": facets,
        "displayed_facet_count": 2,
    }


def audit_case(case):
    values = characteristic_function(case)
    x, z = tuple(map(F, case["x"])), tuple(map(F, case["z"]))
    z_tight = tight_support(values, z)
    common = tuple(sorted(set(z_tight).intersection(tight_support(values, x))))
    roots = maximum_overlap_roots(x, z)
    if not roots:
        raise AssertionError(f"{case['name']} has no maximum-overlap root")
    return {
        "name": case["name"],
        "n": len(x),
        "maximum_overlap_roots": list(roots),
        "z_tight_count": len(z_tight),
        "common_tight_count": len(common),
        "roots": [
            {
                "root": root,
                "deleted_load": solve_overcover(
                    values, x, z, root, z_tight, "deleted_load"
                ),
                "common_leader": solve_overcover(
                    values, x, z, root, common, "common_leader"
                ),
            }
            for root in roots
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = {
        "status": (
            "exact hostile premise audit; finite controls are not an all-n proof"
        ),
        "cases": [audit_case(case) for case in CONTROL_CASES],
        "coefficient_two_pair_gauge_and_facet_decomposition": (
            coefficient_two_pair_gauge_audit()
        ),
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()

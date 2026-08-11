#!/usr/bin/env python3
"""Exact audit of common-support deficiency and pair-lift surplus absorption.

For a normalized Lmax top over-cover, the hinge surplus

    epsilon = alpha.Lmin - max(Lmax)

is exactly the weighted Lmin slack of its z-tight coalition support.  This
script solves the minimum-surplus over-cover LP and its player-price dual.  A
zero optimum is equivalent to the existence of a common Lmin/Lmax-tight
over-cover.

For every Lmax-top root it then forms the over-cover's rooted pair lift.  Its
scaled exact-cone slack is kappa_r, while its Lmin-side pair-floor expression
has slack kappa_r-epsilon.  Thus kappa_r >= epsilon is the exact condition
under which that noncommon pair lift absorbs its own hinge surplus.

The identities are human linear algebra.  Archive counts are finite hostile
evidence only and do not prove root existence or the hybrid-overlap theorem.
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

from audit_lmax_overcover import (  # noqa: E402
    coalition_sum,
    records,
    spectral_bound,
    top_certificate,
)
from audit_overcover_pair_lift_coupling import (  # noqa: E402
    CONTROL_CASES,
    characteristic_function,
)


NULL_PADDED_SOURCE = COOPGAMES / "verifiers/s5close/completeness3.json"


def minimum_surplus_certificate(values, x, z):
    """Solve the common-support deficiency primal and player-price dual."""
    n = len(x)
    full = (1 << n) - 1
    maximum = max(z)
    top = tuple(i for i, value in enumerate(z) if value == maximum)
    tight = tuple(
        coalition
        for coalition in range(1, full)
        if coalition_sum(z, coalition) == values[coalition]
    )
    slacks = tuple(
        coalition_sum(x, coalition) - values[coalition]
        for coalition in tight
    )
    if any(value < 0 for value in slacks):
        raise AssertionError("Lmin violates a coalition constraint")

    m = len(tight)
    eta_index = m
    alpha_index = {player: m + 1 + j for j, player in enumerate(top)}
    width = m + 1 + len(top)
    equalities, equality_rhs = [], []
    for player in range(n):
        row = [F(0)] * width
        for j, coalition in enumerate(tight):
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
    objective = list(slacks) + [F(0)] * (1 + len(top))
    status, epsilon_star, solution = exact_linprog(
        objective, inequalities, inequality_rhs, equalities, equality_rhs
    )
    if status != "optimal":
        raise RuntimeError(f"minimum-surplus primal is {status}")
    lambdas = tuple(solution[j] for j in range(m))
    eta = solution[eta_index]
    alpha = tuple(
        solution[alpha_index[player]] if player in alpha_index else F(0)
        for player in range(n)
    )
    positive = tuple(
        (coalition, lambdas[j])
        for j, coalition in enumerate(tight)
        if lambdas[j] > 0
    )
    if sum(alpha, F(0)) != 1 or eta < 0:
        raise AssertionError("minimum-surplus primal normalization failed")
    if any(value < 0 for value in lambdas + alpha):
        raise AssertionError("minimum-surplus primal sign failed")
    for player in range(n):
        load = sum(
            (
                weight
                for coalition, weight in positive
                if coalition >> player & 1
            ),
            F(0),
        )
        if load != eta + alpha[player]:
            raise AssertionError("minimum-surplus primal incidence failed")
    if epsilon_star != sum(
        (
            weight * slacks[tight.index(coalition)]
            for coalition, weight in positive
        ),
        F(0),
    ):
        raise AssertionError("minimum-surplus primal objective mismatch")
    if epsilon_star != sum((alpha[i] * x[i] for i in range(n)), F(0)) - maximum:
        raise AssertionError("minimum-surplus hinge identity failed")

    # Dual: max t subject to y(S)<=slack_x(S), y(N)>=0, t<=y_i on top.
    t_index = n
    dual_width = n + 1
    dual_inequalities, dual_rhs = [], []
    for coalition, slack in zip(tight, slacks):
        row = [F((coalition >> player) & 1) for player in range(n)] + [F(0)]
        dual_inequalities.append(row)
        dual_rhs.append(slack)
    dual_inequalities.append([F(-1)] * n + [F(0)])
    dual_rhs.append(F(0))
    for player in top:
        row = [F(0)] * dual_width
        row[player] = -1
        row[t_index] = 1
        dual_inequalities.append(row)
        dual_rhs.append(F(0))
    dual_objective = [F(0)] * dual_width
    dual_objective[t_index] = -1
    dual_status, negative_t, dual_solution = exact_linprog(
        dual_objective, dual_inequalities, dual_rhs
    )
    if dual_status != "optimal" or -negative_t != epsilon_star:
        raise AssertionError("minimum-surplus strong duality failed")
    y = tuple(dual_solution[:n])
    t = dual_solution[t_index]
    if t != epsilon_star or sum(y, F(0)) < 0:
        raise AssertionError("minimum-surplus dual sign or objective failed")
    if any(coalition_sum(y, coalition) > slack for coalition, slack in zip(tight, slacks)):
        raise AssertionError("minimum-surplus dual coalition price failed")
    if any(y[player] < t for player in top):
        raise AssertionError("minimum-surplus dual top price failed")
    if any(
        coalition_sum(y, coalition) != slacks[j]
        for j, (coalition, weight) in enumerate(zip(tight, lambdas))
        if weight > 0
    ):
        raise AssertionError("positive coalition misses dual complementarity")
    if eta > 0 and sum(y, F(0)) != 0:
        raise AssertionError("positive eta misses dual complementarity")
    if any(alpha[player] > 0 and y[player] != t for player in top):
        raise AssertionError("positive alpha misses dual complementarity")

    common_support = all(coalition_sum(x, coalition) == values[coalition] for coalition, _ in positive)
    if (epsilon_star == 0) != common_support:
        raise AssertionError("zero deficiency/common-support equivalence failed")
    return {
        "epsilon_star": epsilon_star,
        "eta": eta,
        "alpha": alpha,
        "support": tuple(coalition for coalition, _weight in positive),
        "weights": tuple(weight for _coalition, weight in positive),
        "common_overcover_exists": epsilon_star == 0,
        "dual_y": y,
        "dual_t": t,
    }


def best_scaled_spectral_anchor(values, x, z):
    """Maximize the exact capped top-anchor excess after perspective scaling."""
    n = len(x)
    full = (1 << n) - 1
    minimum = min(x)
    maximum = max(z)
    top = tuple(i for i, value in enumerate(z) if value == maximum)
    tight = tuple(
        coalition
        for coalition in range(1, full)
        if coalition_sum(z, coalition) == values[coalition]
    )
    m = len(tight)
    eta_index = m
    u_index = {player: m + 1 + j for j, player in enumerate(top)}
    width = m + 1 + len(top)
    equalities, equality_rhs = [], []
    for player in range(n):
        row = [F(0)] * width
        for j, coalition in enumerate(tight):
            row[j] = F((coalition >> player) & 1)
        row[eta_index] = -1
        if player in u_index:
            row[u_index[player]] = -1
        equalities.append(row)
        equality_rhs.append(F(0))
    inequalities, inequality_rhs = [], []
    for variable in range(width):
        row = [F(0)] * width
        row[variable] = -1
        inequalities.append(row)
        inequality_rhs.append(F(0))
    for player in top:
        row = [F(0)] * width
        row[u_index[player]] = 1
        inequalities.append(row)
        inequality_rhs.append(F(1))
    objective = [F(0)] * width
    for player in top:
        objective[u_index[player]] = -(x[player] - minimum)
    status, negative_excess, solution = exact_linprog(
        objective, inequalities, inequality_rhs, equalities, equality_rhs
    )
    if status != "optimal":
        raise RuntimeError(f"best scaled spectral anchor is {status}")
    excess = -negative_excess
    scaled_alpha = tuple(
        solution[u_index[player]] if player in u_index else F(0)
        for player in range(n)
    )
    scale = sum(scaled_alpha, F(0))
    if excess <= 0 or scale <= 0 or max(scaled_alpha) != 1:
        raise AssertionError("best positive anchor did not saturate its cap")
    theta = 1 / scale
    alpha = tuple(value / scale for value in scaled_alpha)
    epsilon = sum((alpha[i] * x[i] for i in range(n)), F(0)) - maximum
    if excess != (maximum + epsilon - minimum) / theta:
        raise AssertionError("scaled spectral objective identity failed")
    bound = spectral_bound(x, z, theta, epsilon)
    support = tuple(tight[j] for j in range(m) if solution[j] > 0)
    return {
        "required_excess": excess,
        "theta": theta,
        "epsilon": epsilon,
        "alpha": alpha,
        "support": support,
        "spectral_overlap_bound": bound,
    }


def absorption_rows(values, x, z, certificate):
    """Check every scaled pair-lift defect identity for one over-cover."""
    n = len(x)
    total = sum(x, F(0))
    maximum = max(z)
    alpha = certificate["alpha"]
    eta = certificate["eta"]
    epsilon = sum((alpha[i] * x[i] for i in range(n)), F(0)) - maximum
    support = certificate["support"]
    weights = certificate["weights"]
    if epsilon != sum(
        (
            weight * (coalition_sum(x, coalition) - values[coalition])
            for coalition, weight in zip(support, weights)
        ),
        F(0),
    ):
        raise AssertionError("hinge surplus/support identity failed")
    top = tuple(i for i, value in enumerate(z) if value == maximum)
    rows = []
    for root in top:
        theta_minus = max(alpha[i] for i in range(n) if i != root)
        theta = eta + theta_minus
        if theta <= 0:
            raise AssertionError("positive Lmax level has zero rooted normalization")
        deficits = [F(0) if i == root else theta_minus - alpha[i] for i in range(n)]
        leader = alpha[root] - theta_minus
        kappa = theta_minus * total - maximum - sum(
            (
                deficits[i] * values[(1 << root) | (1 << i)]
                for i in range(n)
                if i != root
            ),
            F(0),
        )
        z_slack = sum((deficits[i] * z[i] for i in range(n) if i != root), F(0))
        z_slack -= leader * z[root]
        z_slack -= sum(
            (
                deficits[i] * values[(1 << root) | (1 << i)]
                for i in range(n)
                if i != root
            ),
            F(0),
        )
        x_slack = sum((deficits[i] * x[i] for i in range(n) if i != root), F(0))
        x_slack -= leader * x[root]
        x_slack -= sum(
            (
                deficits[i] * values[(1 << root) | (1 << i)]
                for i in range(n)
                if i != root
            ),
            F(0),
        )
        if kappa < 0 or z_slack != kappa or x_slack != kappa - epsilon:
            raise AssertionError("surplus-absorption slack identity failed")
        difference_lhs = sum(
            (deficits[i] * (x[i] - z[i]) for i in range(n) if i != root),
            F(0),
        )
        difference_rhs = leader * (x[root] - z[root]) - epsilon
        if difference_lhs != difference_rhs:
            raise AssertionError("defective tangent identity failed")
        rows.append(
            {
                "root": root,
                "theta_minus": str(theta_minus),
                "leader_gap": str(leader),
                "pair_lift_exact_cone_slack_kappa": str(kappa),
                "hinge_surplus_epsilon": str(epsilon),
                "lmin_pair_floor_slack": str(x_slack),
                "absorbs_surplus": kappa >= epsilon,
                "defective_tangent_lhs": str(difference_lhs),
                "defective_tangent_rhs": str(difference_rhs),
            }
        )
    return epsilon, rows


def audit_record(source, trail, values, x, z):
    certificate = top_certificate(values, z)
    minimum = minimum_surplus_certificate(values, x, z)
    epsilon, roots = absorption_rows(values, x, z, certificate)
    return {
        "source": str(source),
        "trail": trail,
        "n": len(x),
        "dispersion_theta": str(certificate["theta"]),
        "dispersion_certificate_surplus": str(epsilon),
        "minimum_surplus": str(minimum["epsilon_star"]),
        "dispersion_certificate_is_surplus_optimal": epsilon == minimum["epsilon_star"],
        "common_overcover_exists": minimum["common_overcover_exists"],
        "some_top_root_absorbs_surplus": any(row["absorbs_surplus"] for row in roots),
        "roots": roots,
    }


def fixed_controls():
    rows = []
    for case in CONTROL_CASES:
        values = characteristic_function(case)
        x, z = tuple(map(F, case["x"])), tuple(map(F, case["z"]))
        row = audit_record(case["name"], "$", values, x, z)
        minimum = minimum_surplus_certificate(values, x, z)
        row["minimum_surplus_primal"] = {
            "eta": str(minimum["eta"]),
            "alpha": [str(value) for value in minimum["alpha"]],
            "support": list(minimum["support"]),
            "weights": [str(value) for value in minimum["weights"]],
        }
        row["minimum_surplus_dual"] = {
            "t": str(minimum["dual_t"]),
            "y": [str(value) for value in minimum["dual_y"]],
        }
        anchor = best_scaled_spectral_anchor(values, x, z)
        total = sum(x, F(0))
        n = len(x)
        target = F(4 * n, n * n - (n % 2)) * total
        row["best_single_anchor_spectral_bound"] = {
            "required_excess": str(anchor["required_excess"]),
            "theta": str(anchor["theta"]),
            "epsilon": str(anchor["epsilon"]),
            "alpha": [str(value) for value in anchor["alpha"]],
            "support": list(anchor["support"]),
            "overlap_bound": str(anchor["spectral_overlap_bound"]),
            "hybrid_target": str(target),
            "closes_target": anchor["spectral_overlap_bound"] >= target,
        }
        rows.append(row)
    source = json.loads(NULL_PADDED_SOURCE.read_text())[3]["audit"]
    old_values = tuple(F(value) for value in source["v"])
    old_x = tuple(F(value) for value in source["Lmin"])
    old_z = tuple(F(value) for value in source["Lmax"])
    padded_values = tuple(old_values[coalition & 31] for coalition in range(64))
    padded_x = old_x + (F(0),)
    padded_z = old_z + (F(0),)
    padded = audit_record(
        "null_padded_five_player_absorption_counterexample",
        "$",
        padded_values,
        padded_x,
        padded_z,
    )
    padded["construction"] = {
        "source": str(NULL_PADDED_SOURCE.relative_to(COOPGAMES)),
        "source_trail": "$[3].audit",
        "new_null_player": 5,
        "lmin": [str(value) for value in padded_x],
        "lmax": [str(value) for value in padded_z],
        "overlap": str(sum((min(a, b) for a, b in zip(padded_x, padded_z)), F(0))),
        "n6_hybrid_target": "2/3",
        "does_not_challenge_hybrid_target": (
            sum((min(a, b) for a, b in zip(padded_x, padded_z)), F(0)) >= F(2, 3)
        ),
        "selection_preservation_reason": (
            "the padded core forces the null payoff to zero and is affinely "
            "identical to the source core on the original players"
        ),
    }
    if padded["some_top_root_absorbs_surplus"]:
        raise AssertionError("null-padded negative control unexpectedly absorbs surplus")
    if padded["minimum_surplus"] != "3/112":
        raise AssertionError("null-padded deficiency changed")
    rows.append(padded)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--n", type=int, default=6)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    files = []
    for path in args.paths:
        files.extend(sorted(path.rglob("*.json")) if path.is_dir() else [path])
    rows = []
    for source in files:
        try:
            data = json.loads(source.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        for source, trail, values, x, z in records(data, source):
            if len(x) != args.n or sum(x, F(0)) != sum(z, F(0)) or sum(x, F(0)) <= 0:
                continue
            rows.append(audit_record(source, trail, values, x, z))
    controls = fixed_controls()
    report = {
        "status": "exact deficiency and surplus-absorption audit; finite evidence only",
        "human_identities_audited": [
            "minimum surplus = common-support deficiency",
            "minimum-surplus player-price dual",
            "kappa_z = exact-cone pair-lift slack",
            "kappa_x = kappa_z - epsilon",
            "defective tangent identity",
        ],
        "archive_summary": {
            "n": args.n,
            "record_count": len(rows),
            "positive_minimum_surplus": sum(not row["common_overcover_exists"] for row in rows),
            "dispersion_certificate_surplus_optimal": sum(row["dispersion_certificate_is_surplus_optimal"] for row in rows),
            "some_top_root_absorbs_surplus": sum(row["some_top_root_absorbs_surplus"] for row in rows),
            "absorption_failures": [row for row in rows if not row["some_top_root_absorbs_surplus"]],
        },
        "archive_records": rows,
        "fixed_controls": controls,
        "scope": "archive and fixed controls do not prove universal root existence or the hybrid bound",
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()

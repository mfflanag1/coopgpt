#!/usr/bin/env python3
"""Exact audit of the paired first-stage dispersion conjectures.

theta_plus minimizes max(alpha_i) over Lmax top over-covers.  theta_minus
minimizes max(beta_i) over Lmin bottom under-covers.  The candidate bridge is

    overlap/T >= theta_plus + theta_minus,
    1/theta_plus + 1/theta_minus <= n.

Both identities are sharp on G(p,k).  This script tests archived pairs only;
passing would be discovery evidence, while any failure is a rigorous
counterexample to the stated first-stage formulation.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from audit_lmax_overcover import coalition_sum, records, top_certificate

import sys

COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))
from exactlp import exact_linprog  # noqa: E402


def bottom_certificate(v: tuple[F, ...], x: tuple[F, ...]) -> dict:
    n = len(x)
    full = (1 << n) - 1
    total = sum(x, F(0))
    minimum = min(x)
    bottom = tuple(i for i, value in enumerate(x) if value == minimum)
    tight = tuple(
        coalition
        for coalition in range(1, full)
        if coalition_sum(x, coalition) == v[coalition]
    )

    # Variables: gamma[tight], xi, beta[bottom], theta.  All are constrained
    # nonnegative; the incidence identity is gamma-load=xi*1-beta.
    m = len(tight)
    xi_index = m
    beta_index = {player: m + 1 + j for j, player in enumerate(bottom)}
    theta_index = m + 1 + len(bottom)
    width = theta_index + 1

    equalities = []
    equality_rhs = []
    for player in range(n):
        row = [F(0)] * width
        for j, coalition in enumerate(tight):
            row[j] = F(int(bool(coalition >> player & 1)))
        row[xi_index] = F(-1)
        if player in beta_index:
            row[beta_index[player]] = F(1)
        equalities.append(row)
        equality_rhs.append(F(0))
    row = [F(0)] * width
    for player in bottom:
        row[beta_index[player]] = F(1)
    equalities.append(row)
    equality_rhs.append(F(1))

    inequalities = []
    inequality_rhs = []
    for variable in range(width):
        row = [F(0)] * width
        row[variable] = F(-1)
        inequalities.append(row)
        inequality_rhs.append(F(0))
    for player in bottom:
        row = [F(0)] * width
        row[beta_index[player]] = F(1)
        row[theta_index] = F(-1)
        inequalities.append(row)
        inequality_rhs.append(F(0))

    objective = [F(0)] * width
    objective[theta_index] = F(1)
    status, theta, solution = exact_linprog(
        objective, inequalities, inequality_rhs, equalities, equality_rhs
    )
    if status != "optimal":
        raise RuntimeError(f"bottom certificate LP returned {status}")

    gammas = tuple(solution[j] for j in range(m))
    xi = solution[xi_index]
    beta = tuple(
        solution[beta_index[player]] if player in beta_index else F(0)
        for player in range(n)
    )
    if theta <= 0 or xi < 0 or any(value < 0 for value in gammas + beta):
        raise AssertionError("bottom certificate has an invalid sign")
    if sum(beta, F(0)) != 1 or theta != max(beta):
        raise AssertionError("bottom dispersion normalization failed")
    for player in range(n):
        load = sum(
            (gammas[j] for j, coalition in enumerate(tight) if coalition >> player & 1),
            F(0),
        )
        if load != xi - beta[player]:
            raise AssertionError("bottom incidence identity failed")
    dual_value = xi * total - sum(
        (weight * v[coalition] for weight, coalition in zip(gammas, tight)),
        F(0),
    )
    if dual_value != minimum:
        raise AssertionError("bottom certificate does not attain the Lmin floor")
    return {"theta": theta, "xi": xi, "beta": beta}


def compatible_optimal_packing(v, x, z, theta_plus, theta_minus):
    """Choose both dispersion-optimal certificates with normalized loads <=1."""
    n = len(x)
    full = (1 << n) - 1
    top = tuple(i for i, value in enumerate(z) if value == max(z))
    bottom = tuple(i for i, value in enumerate(x) if value == min(x))
    z_tight = tuple(
        coalition for coalition in range(1, full)
        if coalition_sum(z, coalition) == v[coalition]
    )
    x_tight = tuple(
        coalition for coalition in range(1, full)
        if coalition_sum(x, coalition) == v[coalition]
    )
    mz = len(z_tight)
    eta = mz
    alpha = {player: mz + 1 + j for j, player in enumerate(top)}
    gamma0 = mz + 1 + len(top)
    xi = gamma0 + len(x_tight)
    beta = {player: xi + 1 + j for j, player in enumerate(bottom)}
    width = xi + 1 + len(bottom)

    equalities = []
    rhs = []
    for player in range(n):
        row = [F(0)] * width
        for j, coalition in enumerate(z_tight):
            row[j] = F(int(bool(coalition >> player & 1)))
        row[eta] = F(-1)
        if player in alpha:
            row[alpha[player]] = F(-1)
        equalities.append(row)
        rhs.append(F(0))
    row = [F(0)] * width
    for player in top:
        row[alpha[player]] = F(1)
    equalities.append(row)
    rhs.append(F(1))
    for player in range(n):
        row = [F(0)] * width
        for j, coalition in enumerate(x_tight):
            row[gamma0 + j] = F(int(bool(coalition >> player & 1)))
        row[xi] = F(-1)
        if player in beta:
            row[beta[player]] = F(1)
        equalities.append(row)
        rhs.append(F(0))
    row = [F(0)] * width
    for player in bottom:
        row[beta[player]] = F(1)
    equalities.append(row)
    rhs.append(F(1))

    inequalities = []
    irhs = []
    for variable in range(width):
        row = [F(0)] * width
        row[variable] = F(-1)
        inequalities.append(row)
        irhs.append(F(0))
    for player in top:
        row = [F(0)] * width
        row[alpha[player]] = F(1)
        inequalities.append(row)
        irhs.append(theta_plus)
    for player in bottom:
        row = [F(0)] * width
        row[beta[player]] = F(1)
        inequalities.append(row)
        irhs.append(theta_minus)
    for player in range(n):
        row = [F(0)] * width
        if player in alpha:
            row[alpha[player]] = 1 / theta_plus
        if player in beta:
            row[beta[player]] = 1 / theta_minus
        inequalities.append(row)
        irhs.append(F(1))

    status, _value, solution = exact_linprog(
        [F(0)] * width, inequalities, irhs, equalities, rhs
    )
    if status != "optimal":
        return None
    packed_alpha = tuple(
        solution[alpha[player]] if player in alpha else F(0) for player in range(n)
    )
    packed_beta = tuple(
        solution[beta[player]] if player in beta else F(0) for player in range(n)
    )
    return packed_alpha, packed_beta


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--n", type=int, default=6)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    files = []
    for path in args.paths:
        files.extend(sorted(path.rglob("*.json")) if path.is_dir() else [path])

    rows = []
    overlap_failure_count = 0
    overlap_failure_representatives = {}
    reciprocal_failures = []
    surplus_budget_failures = []
    pointwise_packing_failures = []
    compatible_packing_failures = []
    repaired_independent_packings = 0
    equality_rows = []
    for source in files:
        try:
            data = json.loads(source.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        for source, trail, v, x, z in records(data, source):
            if len(x) != args.n or sum(x, F(0)) != sum(z, F(0)) or sum(x, F(0)) <= 0:
                continue
            plus_certificate = top_certificate(v, z)
            minus_certificate = bottom_certificate(v, x)
            plus = plus_certificate["theta"]
            minus = minus_certificate["theta"]
            total = sum(x, F(0))
            overlap = sum((min(a, b) for a, b in zip(x, z)), F(0))
            minimum = min(x)
            maximum = max(z)
            delta = maximum - minimum
            plus_surplus = sum(
                (plus_certificate["alpha"][i] * x[i] for i in range(len(x))),
                F(0),
            ) - maximum
            minus_surplus = minimum - sum(
                (minus_certificate["beta"][i] * z[i] for i in range(len(x))),
                F(0),
            )
            row = {
                "source": str(source),
                "trail": trail,
                "theta_plus": str(plus),
                "theta_minus": str(minus),
                "theta_sum": str(plus + minus),
                "reciprocal_sum": str(1 / plus + 1 / minus),
                "overlap_ratio": str(overlap / total),
                "hinge_surpluses": [str(plus_surplus), str(minus_surplus)],
            }
            rows.append(row)
            if overlap / total < plus + minus:
                overlap_failure_count += 1
                key = (plus, minus)
                old = overlap_failure_representatives.get(key)
                if old is None or F(row["overlap_ratio"]) < F(old["overlap_ratio"]):
                    overlap_failure_representatives[key] = row
            if 1 / plus + 1 / minus > len(x):
                reciprocal_failures.append(row)
            if delta > 0:
                plus_budget = (total - len(x) * minimum) / (delta + plus_surplus)
                minus_budget = (len(x) * maximum - total) / (delta + minus_surplus)
                if 1 / plus > plus_budget or 1 / minus > minus_budget:
                    failed = dict(row)
                    failed["surplus_budget_rhs"] = [
                        str(plus_budget), str(minus_budget)
                    ]
                    surplus_budget_failures.append(failed)
            packing_loads = [
                plus_certificate["alpha"][i] / plus
                + minus_certificate["beta"][i] / minus
                for i in range(len(x))
            ]
            if max(packing_loads) > 1:
                failed = dict(row)
                failed["normalized_coordinate_loads"] = [
                    str(value) for value in packing_loads
                ]
                pointwise_packing_failures.append(failed)
                compatible = compatible_optimal_packing(v, x, z, plus, minus)
                if compatible is None:
                    compatible_packing_failures.append(failed)
                else:
                    repaired_independent_packings += 1
            if overlap == F(2, 3) * total:
                equality_rows.append(row)

    report = {
        "status": "exact archived-pair audit; not exhaustive proof evidence",
        "n": args.n,
        "records": len(rows),
        "paired_overlap_failure_count": overlap_failure_count,
        "paired_overlap_failure_representatives": list(
            overlap_failure_representatives.values()
        ),
        "reciprocal_sum_failures": reciprocal_failures,
        "surplus_dispersion_budget_failures": surplus_budget_failures,
        "pointwise_packing_failure_count": len(pointwise_packing_failures),
        "pointwise_packing_failure_examples": pointwise_packing_failures[:12],
        "independent_packings_repaired_by_joint_choice": repaired_independent_packings,
        "compatible_optimal_packing_failures": compatible_packing_failures,
        "candidate_equality_rows": equality_rows,
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

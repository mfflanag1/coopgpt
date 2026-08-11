#!/usr/bin/env python3
"""Independent Z3 replay of the root-specific over-cover optima.

The primary audit uses the project's exact rational LP implementation.  This
script reconstructs the two over-cover systems directly in Z3's exact linear
rational arithmetic.  For each recorded optimum it separately checks
feasibility at the claimed value and unsatisfiability of every strictly better
value.  For recorded common-support infeasibility it checks the unoptimized
system itself.  It also independently applies the exceptional-set
decomposition test to the two coefficient-two pair-lift facets.  Agreement is
a finite cross-check, not a proof of the human over-cover-to-pair-lift theorem
or the all-n hybrid bound.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import z3

from audit_lmax_overcover import coalition_sum
from audit_overcover_pair_lift_coupling import (
    CONTROL_CASES,
    characteristic_function,
    maximum_overlap_roots,
    tight_support,
)


HERE = Path(__file__).resolve().parent


def rational(value):
    value = F(value)
    return z3.Q(value.numerator, value.denominator)


def system(values, z, root, support, mode, prefix):
    n = len(z)
    maximum = max(z)
    top = tuple(i for i, value in enumerate(z) if value == maximum)
    lambdas = [z3.Real(f"{prefix}_lambda_{j}") for j in range(len(support))]
    eta = z3.Real(f"{prefix}_eta")
    alpha = {
        player: z3.Real(f"{prefix}_alpha_{player}") for player in top
    }
    theta = z3.Real(f"{prefix}_theta")
    constraints = [eta >= 0, theta >= 0]
    constraints.extend(weight >= 0 for weight in lambdas)
    constraints.extend(value >= 0 for value in alpha.values())
    constraints.append(z3.Sum(list(alpha.values())) == 1)
    for player in range(n):
        load = z3.Sum(
            [
                weight
                for coalition, weight in zip(support, lambdas)
                if coalition >> player & 1
            ]
        )
        constraints.append(load == eta + alpha.get(player, 0))
        if player != root:
            constraints.append(alpha.get(player, 0) <= theta)
    objective = theta
    if mode == "common_leader":
        objective = theta - alpha[root]
    elif mode != "deleted_load":
        raise ValueError(mode)
    return constraints, objective


def verify_optimum(values, z, root, support, mode, record, prefix):
    constraints, objective = system(values, z, root, support, mode, prefix)
    solver = z3.Solver()
    solver.add(*constraints)
    if record["status"] == "infeasible":
        if solver.check() != z3.unsat:
            raise AssertionError((prefix, "expected infeasible"))
        return {
            "status": "infeasible",
            "z3_base_system": "unsat",
            "agreement": True,
        }
    if record["status"] != "optimal":
        raise AssertionError((prefix, record["status"]))
    optimum = (
        F(record["theta_minus"])
        if mode == "deleted_load"
        else -F(record["leader_gap"])
    )
    solver.push()
    solver.add(objective == rational(optimum))
    if solver.check() != z3.sat:
        raise AssertionError((prefix, "claimed optimum is infeasible"))
    solver.pop()
    solver.add(objective < rational(optimum))
    if solver.check() != z3.unsat:
        raise AssertionError((prefix, "strictly better solution exists"))
    return {
        "status": "optimal",
        "objective": str(optimum),
        "z3_at_claimed_value": "sat",
        "z3_strictly_better": "unsat",
        "agreement": True,
    }


def decomposition_count(n, support):
    """Independent exceptional-set test for a min-semi-balanced support."""
    full = (1 << n) - 1
    count = 0
    for exceptional in range(1, full):
        if exceptional in support:
            continue
        solver = z3.Solver()
        weights = [
            z3.Real(f"facet_{exceptional}_weight_{j}")
            for j in range(len(support))
        ]
        common = z3.Real(f"facet_{exceptional}_common")
        solver.add(*(weight >= 0 for weight in weights))
        for player in range(n):
            load = z3.Sum(
                [
                    weight
                    for coalition, weight in zip(support, weights)
                    if coalition >> player & 1
                ]
            )
            solver.add(
                load - (1 if exceptional >> player & 1 else 0) == common
            )
        count += solver.check() == z3.sat
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", type=Path, default=HERE / "overcover_pair_lift_coupling.json"
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    primary = json.loads(args.input.read_text())
    primary_by_name = {case["name"]: case for case in primary["cases"]}
    rows = []
    for case in CONTROL_CASES:
        values = characteristic_function(case)
        x, z = tuple(map(F, case["x"])), tuple(map(F, case["z"]))
        z_tight = tight_support(values, z)
        common = tuple(sorted(set(z_tight).intersection(tight_support(values, x))))
        expected = primary_by_name[case["name"]]
        expected_by_root = {row["root"]: row for row in expected["roots"]}
        roots = maximum_overlap_roots(x, z)
        if tuple(expected["maximum_overlap_roots"]) != roots:
            raise AssertionError((case["name"], "root mismatch"))
        for root in roots:
            record = expected_by_root[root]
            deleted = verify_optimum(
                values,
                z,
                root,
                z_tight,
                "deleted_load",
                record["deleted_load"],
                f"{case['name']}_{root}_deleted",
            )
            leader = verify_optimum(
                values,
                z,
                root,
                common,
                "common_leader",
                record["common_leader"],
                f"{case['name']}_{root}_common",
            )
            rows.append(
                {
                    "case": case["name"],
                    "root": root,
                    "deleted_load": deleted,
                    "common_leader": leader,
                }
            )
    coefficient_facets = []
    decomposition = primary["coefficient_two_pair_gauge_and_facet_decomposition"]
    for number, facet in enumerate(decomposition["distinct_active_facets"], start=1):
        support = tuple(row["coalition"] for row in facet["coefficients"])
        count = decomposition_count(7, support)
        if count != facet["decomposition_count"]:
            raise AssertionError(("coefficient_two_facet", number, count))
        coefficient_facets.append(
            {
                "facet": number,
                "support": list(support),
                "z3_decomposition_count": count,
                "exact_lp_decomposition_count": facet["decomposition_count"],
                "indecomposable_agreement": count == 0,
            }
        )
    report = {
        "status": "independent Z3 exact-LRA replay",
        "all_optima_and_infeasibilities_agree": all(
            row[mode]["agreement"]
            for row in rows
            for mode in ("deleted_load", "common_leader")
        ),
        "scope": "finite hostile controls; not an all-n proof",
        "roots": rows,
        "coefficient_two_pair_lift_facets": coefficient_facets,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

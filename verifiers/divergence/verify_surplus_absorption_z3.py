#!/usr/bin/env python3
"""Independent Z3 replay of minimum common-support deficiencies.

The primary surplus-absorption audit uses the project's exact rational LP.
For each named hostile control and the null-padded negative control, this
script independently reconstructs the minimum-surplus over-cover constraints
in Z3 exact linear arithmetic.  It checks feasibility at the recorded value
and unsatisfiability of every strictly smaller value.

This is a finite solver cross-check.  The deficiency dual and pair-lift slack
identities are human theorems; universal surplus-absorbing root existence is
explicitly false without the positive-floor/null-player reduction.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import z3

from audit_lmax_overcover import coalition_sum
from audit_overcover_pair_lift_coupling import CONTROL_CASES, characteristic_function
from audit_surplus_absorption import NULL_PADDED_SOURCE


HERE = Path(__file__).resolve().parent


def rational(value):
    value = F(value)
    return z3.Q(value.numerator, value.denominator)


def padded_control():
    source = json.loads(NULL_PADDED_SOURCE.read_text())[3]["audit"]
    old_values = tuple(F(value) for value in source["v"])
    values = tuple(old_values[coalition & 31] for coalition in range(64))
    x = tuple(F(value) for value in source["Lmin"]) + (F(0),)
    z = tuple(F(value) for value in source["Lmax"]) + (F(0),)
    return values, x, z


def fixed_inputs():
    rows = []
    for case in CONTROL_CASES:
        rows.append(
            (
                case["name"],
                characteristic_function(case),
                tuple(map(F, case["x"])),
                tuple(map(F, case["z"])),
            )
        )
    rows.append(
        (
            "null_padded_five_player_absorption_counterexample",
            *padded_control(),
        )
    )
    return rows


def verify_minimum(name, values, x, z, expected):
    n = len(x)
    full = (1 << n) - 1
    maximum = max(z)
    top = tuple(i for i, value in enumerate(z) if value == maximum)
    tight = tuple(
        coalition
        for coalition in range(1, full)
        if coalition_sum(z, coalition) == values[coalition]
    )
    lambdas = [z3.Real(f"{name}_lambda_{j}") for j in range(len(tight))]
    eta = z3.Real(f"{name}_eta")
    alpha = {player: z3.Real(f"{name}_alpha_{player}") for player in top}
    constraints = [eta >= 0]
    constraints.extend(weight >= 0 for weight in lambdas)
    constraints.extend(value >= 0 for value in alpha.values())
    constraints.append(z3.Sum(list(alpha.values())) == 1)
    for player in range(n):
        load = z3.Sum(
            [
                weight
                for coalition, weight in zip(tight, lambdas)
                if coalition >> player & 1
            ]
        )
        constraints.append(load == eta + alpha.get(player, 0))
    objective = z3.Sum(
        [
            weight * rational(coalition_sum(x, coalition) - values[coalition])
            for coalition, weight in zip(tight, lambdas)
        ]
    )
    solver = z3.Solver()
    solver.add(*constraints)
    solver.push()
    solver.add(objective == rational(expected))
    if solver.check() != z3.sat:
        raise AssertionError((name, "reported minimum is infeasible"))
    solver.pop()
    solver.add(objective < rational(expected))
    if solver.check() != z3.unsat:
        raise AssertionError((name, "strictly smaller surplus is feasible"))
    return {
        "name": name,
        "minimum_surplus": str(expected),
        "z3_at_reported_value": "sat",
        "z3_strictly_smaller": "unsat",
        "agreement": True,
    }


def verify_best_anchor(name, values, x, z, expected):
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
    lambdas = [z3.Real(f"{name}_anchor_lambda_{j}") for j in range(len(tight))]
    eta = z3.Real(f"{name}_anchor_eta")
    scaled_alpha = {
        player: z3.Real(f"{name}_anchor_u_{player}") for player in top
    }
    constraints = [eta >= 0]
    constraints.extend(weight >= 0 for weight in lambdas)
    constraints.extend(value >= 0 for value in scaled_alpha.values())
    constraints.extend(value <= 1 for value in scaled_alpha.values())
    for player in range(n):
        load = z3.Sum(
            [
                weight
                for coalition, weight in zip(tight, lambdas)
                if coalition >> player & 1
            ]
        )
        constraints.append(load == eta + scaled_alpha.get(player, 0))
    objective = z3.Sum(
        [
            scaled_alpha[player] * rational(x[player] - minimum)
            for player in top
        ]
    )
    solver = z3.Solver()
    solver.add(*constraints)
    solver.push()
    solver.add(objective == rational(expected))
    if solver.check() != z3.sat:
        raise AssertionError((name, "reported anchor optimum is infeasible"))
    solver.pop()
    solver.add(objective > rational(expected))
    if solver.check() != z3.unsat:
        raise AssertionError((name, "strictly better anchor is feasible"))
    return {
        "required_excess": str(expected),
        "z3_at_reported_value": "sat",
        "z3_strictly_larger": "unsat",
        "agreement": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", type=Path, default=HERE / "surplus_absorption_audit.json"
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    primary = json.loads(args.input.read_text())
    expected_rows = {row["source"]: row for row in primary["fixed_controls"]}
    rows = []
    for name, values, x, z in fixed_inputs():
        record = expected_rows[name]
        row = verify_minimum(name, values, x, z, F(record["minimum_surplus"]))
        if "best_single_anchor_spectral_bound" in record:
            row["best_scaled_anchor"] = verify_best_anchor(
                name,
                values,
                x,
                z,
                F(record["best_single_anchor_spectral_bound"]["required_excess"]),
            )
        rows.append(row)
    report = {
        "status": "independent Z3 exact-LRA minimum-surplus replay",
        "all_fixed_controls_agree": all(row["agreement"] for row in rows),
        "controls": rows,
        "scope": "finite solver cross-check; not a universal absorption theorem",
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

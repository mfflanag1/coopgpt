"""Test whether endpoint exactness neutralizes an enumerated Farkas circuit.

The input is a circuit payload produced by ``minimize_both_sensitive_support``.
For every proper coalition of every game, the LP includes a core allocation
tight at that coalition.  A rationally verified feasible solution with a
negative circuit margin is therefore an exact three-game counterexample, not a
balancedness-only screen.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.optimize import linprog


def rationalize(values, denominator=1_000_000):
    return [F(float(value)).limit_denominator(denominator) for value in values]


def analyze(payload, circuit_index, violation):
    n = int(payload.get("n", 6))
    A = int(payload.get("A_mask", 3))
    B = int(payload.get("B_mask", 12))
    detail = payload["circuits"][circuit_index - 1]
    grand = (1 << n) - 1
    proper = tuple(range(1, grand))
    d_A = len(proper)
    d_B = d_A + 1
    witness_offset = d_B + 1

    def worth_index(coalition):
        return coalition - 1

    def witness_index(game, tight, player):
        return witness_offset + ((game * len(proper) + tight - 1) * n + player)

    def bump_index(game, coalition):
        if game == 1 and coalition == A:
            return d_A
        if game == 2 and coalition == B:
            return d_B
        return None

    variable_count = witness_offset + 3 * len(proper) * n
    objective = np.zeros(variable_count)
    core_rows = []
    core_weights = []
    for meta, weight in zip(detail["active_rows"], detail["circuit_weights"]):
        if meta[0] != "core":
            continue
        game, coalition = int(meta[1]), int(meta[2])
        weight = F(weight)
        core_rows.append((game, coalition))
        core_weights.append(weight)
        objective[worth_index(coalition)] -= float(weight)
        bump = bump_index(game, coalition)
        if bump is not None:
            objective[bump] -= float(weight)

    efficiency_total = sum(F(value) for value in detail["efficiency_weights"])
    A_ub, b_ub, A_eq, b_eq = [], [], [], []
    for game in range(3):
        for tight in proper:
            efficiency = np.zeros(variable_count)
            for player in range(n):
                efficiency[witness_index(game, tight, player)] = 1
            A_eq.append(efficiency)
            b_eq.append(1)

            for coalition in proper:
                core = np.zeros(variable_count)
                core[worth_index(coalition)] = 1
                bump = bump_index(game, coalition)
                if bump is not None:
                    core[bump] = 1
                for player in range(n):
                    if coalition >> player & 1:
                        core[witness_index(game, tight, player)] = -1
                A_ub.append(core)
                b_ub.append(0)

            tightness = np.zeros(variable_count)
            for player in range(n):
                if tight >> player & 1:
                    tightness[witness_index(game, tight, player)] = 1
            tightness[worth_index(tight)] = -1
            bump = bump_index(game, tight)
            if bump is not None:
                tightness[bump] = -1
            A_eq.append(tightness)
            b_eq.append(0)

    if violation > 0:
        A_ub.append(objective.copy())
        b_ub.append(-float(efficiency_total + violation))

    bounds = [(None, None)] * variable_count
    bounds[d_A] = (0, None)
    bounds[d_B] = (0, None)
    result = linprog(
        np.zeros(variable_count) if violation > 0 else objective,
        A_ub=np.asarray(A_ub), b_ub=np.asarray(b_ub),
        A_eq=np.asarray(A_eq), b_eq=np.asarray(b_eq),
        bounds=bounds, method="highs",
    )
    if not result.success:
        return {
            "status": "no violating exact triple found",
            "solver_status": result.message,
            "n": n,
            "A_mask": A,
            "B_mask": B,
            "circuit_index": circuit_index,
            "required_violation": str(violation),
        }

    solution = rationalize(result.x)
    primal_exact = True
    for row, rhs in zip(A_ub, b_ub):
        lhs = sum(F(int(coefficient)) * value
                  for coefficient, value in zip(row, solution) if coefficient)
        primal_exact &= lhs <= F(float(rhs)).limit_denominator(1_000_000)
    for row, rhs in zip(A_eq, b_eq):
        lhs = sum(F(int(coefficient)) * value
                  for coefficient, value in zip(row, solution) if coefficient)
        primal_exact &= lhs == F(int(rhs))

    supported = sum(
        weight * (solution[worth_index(coalition)]
                  + (solution[bump_index(game, coalition)]
                     if bump_index(game, coalition) is not None else 0))
        for (game, coalition), weight in zip(core_rows, core_weights)
    )
    margin = efficiency_total - supported
    primal_exact &= solution[d_A] >= 0 and solution[d_B] >= 0

    dual_payload = None
    dual_exact = False
    if violation == 0:
        y = {
            index: F(float(value)).limit_denominator(1_000_000)
            for index, value in enumerate(result.ineqlin.marginals)
            if abs(value) > 1e-9
        }
        beta = {
            index: F(float(value)).limit_denominator(1_000_000)
            for index, value in enumerate(result.eqlin.marginals)
            if abs(value) > 1e-9
        }
        lower = {
            index: F(float(value)).limit_denominator(1_000_000)
            for index, value in enumerate(result.lower.marginals)
            if abs(value) > 1e-9
        }
        combined = [F(0)] * variable_count
        for index, multiplier in y.items():
            for column, coefficient in enumerate(A_ub[index]):
                if coefficient:
                    combined[column] += multiplier * F(int(coefficient))
        for index, multiplier in beta.items():
            for column, coefficient in enumerate(A_eq[index]):
                if coefficient:
                    combined[column] += multiplier * F(int(coefficient))
        for index, multiplier in lower.items():
            combined[index] += multiplier
        exact_objective = [F(0)] * variable_count
        for (game, coalition), weight in zip(core_rows, core_weights):
            exact_objective[worth_index(coalition)] -= weight
            bump = bump_index(game, coalition)
            if bump is not None:
                exact_objective[bump] -= weight
        dual_bound = (
            sum(y[index] * F(float(b_ub[index])).limit_denominator(1_000_000)
                for index in y)
            + sum(beta[index] * F(int(b_eq[index])) for index in beta)
        )
        dual_exact = (
            all(value <= 0 for value in y.values())
            and all(value >= 0 for value in lower.values())
            and set(lower).issubset({d_A, d_B})
            and combined == exact_objective
            and dual_bound == -efficiency_total
        )
        dual_payload = {
            "coefficient_identity_exact": dual_exact,
            "dual_bound": str(dual_bound),
            "nonzero_core_witness_inequality_multipliers": {
                str(index): str(value) for index, value in y.items()
            },
            "decoded_core_witness_inequalities": [
                {
                    "game": index // (len(proper) ** 2),
                    "tight_coalition":
                        (index % (len(proper) ** 2)) // len(proper) + 1,
                    "core_coalition": index % len(proper) + 1,
                    "multiplier": str(value),
                }
                for index, value in y.items()
            ],
            "nonzero_efficiency_tightness_multipliers": {
                str(index): str(value) for index, value in beta.items()
            },
            "decoded_efficiency_tightness_multipliers": [
                {
                    "game": (index // 2) // len(proper),
                    "tight_coalition": (index // 2) % len(proper) + 1,
                    "kind": "efficiency" if index % 2 == 0 else "tightness",
                    "multiplier": str(value),
                }
                for index, value in beta.items()
            ],
            "bump_nonnegativity_multipliers": {
                ("A" if index == d_A else "B"): str(value)
                for index, value in lower.items()
            },
        }

    counterexample_exact = primal_exact and margin < 0
    endpoint_bound_exact = primal_exact and margin == 0 and dual_exact
    return {
        "status": (
            "EXACT THREE-GAME COUNTEREXAMPLE VERIFIED"
            if counterexample_exact else
            "EXACT ENDPOINT BOUND VERIFIED"
            if endpoint_bound_exact else
            "floating candidate failed rational verification"
        ),
        "n": n,
        "A_mask": A,
        "B_mask": B,
        "circuit_index": circuit_index,
        "required_violation": str(violation),
        "exact_rational_verification": counterexample_exact or endpoint_bound_exact,
        "primal_exact_rational_verification": primal_exact,
        "bumps": {"A": str(solution[d_A]), "B": str(solution[d_B])},
        "circuit_margin": str(margin),
        "exact_dual": dual_payload,
        "base_values": {
            str(coalition): str(solution[worth_index(coalition)])
            for coalition in proper
        },
        "exactness_witnesses": [
            [
                [str(solution[witness_index(game, tight, player)])
                 for player in range(n)]
                for tight in proper
            ]
            for game in range(3)
        ],
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--circuit-index", type=int, default=1)
    parser.add_argument("--violation", type=F, default=F(1, 10))
    parser.add_argument("--n", type=int)
    parser.add_argument("--A", type=lambda value: int(value, 0))
    parser.add_argument("--B", type=lambda value: int(value, 0))
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    payload = json.loads(args.input.read_text())
    if args.n is not None:
        payload["n"] = args.n
    if args.A is not None:
        payload["A_mask"] = args.A
    if args.B is not None:
        payload["B_mask"] = args.B
    result = analyze(payload, args.circuit_index, args.violation)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")

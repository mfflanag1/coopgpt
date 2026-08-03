"""Compute the exact generalized recoloring capacity for one witness U."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.optimize import linprog


def rat(value):
    return F(float(value)).limit_denominator(1_000_000)


def analyze(payload, circuit_index, U, exclude_base=False,
            zero_total_defect=False):
    n, A, B = payload["n"], payload["A_mask"], payload["B_mask"]
    grand = (1 << n) - 1
    assert 0 < U < grand
    detail = payload["circuits"][circuit_index - 1]
    aggregate = defaultdict(F)
    required_A = required_B = F(0)
    for meta, raw_weight in zip(detail["active_rows"], detail["circuit_weights"]):
        if meta[0] != "core":
            continue
        game, coalition = int(meta[1]), int(meta[2])
        weight = F(raw_weight)
        aggregate[coalition] += weight
        if game == 1 and coalition == A:
            required_A += weight
        if game == 2 and coalition == B:
            required_B += weight
    coalitions = tuple(sorted(set(aggregate) | {U}))

    variables = [(game, coalition) for game in range(3) for coalition in coalitions]
    position = {key: index for index, key in enumerate(variables)}
    alpha_offset = len(variables)
    delta_offset = alpha_offset + 3
    sigma = delta_offset + 3
    variable_count = sigma + 1
    objective = np.zeros(variable_count)
    objective[sigma] = -1

    A_eq, b_eq, eq_meta = [], [], []
    for coalition in coalitions:
        row = np.zeros(variable_count)
        for game in range(3):
            row[position[(game, coalition)]] = 1
            if coalition == U:
                row[delta_offset + game] = -1
        A_eq.append(row)
        b_eq.append(float(aggregate[coalition]))
        eq_meta.append(("aggregate", coalition))
    for game in range(3):
        for player in range(n):
            row = np.zeros(variable_count)
            for coalition in coalitions:
                if coalition >> player & 1:
                    row[position[(game, coalition)]] = 1
            row[alpha_offset + game] = -1
            if U >> player & 1:
                row[delta_offset + game] = -1
            A_eq.append(row)
            b_eq.append(0)
            eq_meta.append(("coverage", game, player))
    efficiency_total = sum(F(value) for value in detail["efficiency_weights"])
    row = np.zeros(variable_count)
    row[alpha_offset:alpha_offset + 3] = 1
    A_eq.append(row)
    b_eq.append(float(efficiency_total))
    eq_meta.append(("efficiency",))
    efficiency_index = len(A_eq) - 1
    if zero_total_defect:
        row = np.zeros(variable_count)
        row[delta_offset:delta_offset + 3] = 1
        A_eq.append(row)
        b_eq.append(0)
        eq_meta.append(("zero-total-defect",))

    A_ub, b_ub = [], []
    for game, arm, required in ((1, A, required_A), (2, B, required_B)):
        row = np.zeros(variable_count)
        row[position[(game, arm)]] = -1
        if U == arm:
            row[delta_offset + game] = 1
        row[sigma] = float(required)
        A_ub.append(row)
        b_ub.append(0)

    bounds = []
    for game, _coalition in variables:
        bounds.append((0, 0) if exclude_base and game == 0 else (0, None))
    bounds.extend([
        (0, 0) if exclude_base and game == 0 else (None, None)
        for game in range(3)
    ])
    bounds.extend([
        (0, 0) if exclude_base and game == 0 else (None, None)
        for game in range(3)
    ])
    bounds.append((None, None))
    result = linprog(
        objective, A_ub=np.asarray(A_ub), b_ub=np.asarray(b_ub),
        A_eq=np.asarray(A_eq), b_eq=np.asarray(b_eq),
        bounds=bounds, method="highs",
    )
    if not result.success:
        return {
            "status": result.message,
            "n": n, "A_mask": A, "B_mask": B,
            "circuit_index": circuit_index, "tight_coalition": U,
        }

    solution = [rat(value) for value in result.x]
    capacity = solution[sigma]
    primal_exact = all(
        sum(F(int(a)) * x for a, x in zip(row, solution) if a) == rat(rhs)
        for row, rhs in zip(A_eq, b_eq)
    ) and all(
        sum(F(int(a)) * x for a, x in zip(row, solution) if a) <= rat(rhs)
        for row, rhs in zip(A_ub, b_ub)
    ) and all(
        (lower_bound is None or value >= lower_bound)
        and (upper_bound is None or value <= upper_bound)
        for value, (lower_bound, upper_bound) in zip(solution, bounds)
    )

    y = [rat(value) for value in result.ineqlin.marginals]
    gamma = [rat(value) for value in result.eqlin.marginals]
    lower = [rat(value) for value in result.lower.marginals]
    upper = [rat(value) for value in result.upper.marginals]
    combined = [F(0)] * variable_count
    for multiplier, row in zip(y, A_ub):
        for column, coefficient in enumerate(row):
            if coefficient:
                combined[column] += multiplier * F(int(coefficient))
    for multiplier, row in zip(gamma, A_eq):
        for column, coefficient in enumerate(row):
            if coefficient:
                combined[column] += multiplier * F(int(coefficient))
    for column, multiplier in enumerate(lower):
        combined[column] += multiplier
    for column, multiplier in enumerate(upper):
        combined[column] += multiplier
    target = [F(0)] * variable_count
    target[sigma] = -1
    dual_value = sum(multiplier * rat(rhs) for multiplier, rhs in zip(gamma, b_eq))
    dual_exact = (
        all(value <= 0 for value in y)
        and all(value >= 0 for value in lower)
        and all(value <= 0 for value in upper)
        and all(not value or bounds[index][0] is not None
                for index, value in enumerate(lower))
        and all(not value or bounds[index][1] is not None
                for index, value in enumerate(upper))
        and combined == target
        and dual_value == -capacity
    )

    blocks = []
    for game in range(3):
        collection = {
            str(coalition): str(solution[position[(game, coalition)]])
            for coalition in coalitions
            if solution[position[(game, coalition)]]
        }
        if collection:
            blocks.append({
                "game": game,
                "tight_coalition": U,
                "alpha": str(solution[alpha_offset + game]),
                "delta": str(solution[delta_offset + game]),
                "collection": collection,
            })
    return {
        "status": "exact single-witness capacity certificate",
        "n": n, "A_mask": A, "B_mask": B,
        "circuit_index": circuit_index,
        "tight_coalition": U,
        "exclude_base": exclude_base,
        "zero_total_defect": zero_total_defect,
        "capacity": str(capacity),
        "repairs_full_bumps": capacity >= 1,
        "primal_exact": primal_exact,
        "dual_exact": dual_exact,
        "dual_bound": str(dual_value),
        "retention_duals": {"A": str(y[0]), "B": str(y[1])},
        "blocks": blocks,
        "dual": {
            "coalition_prices": {
                str(coalition): str(gamma[index])
                for index, coalition in enumerate(coalitions)
                if gamma[index]
            },
            "game_player_potentials": [
                [
                    str(gamma[len(coalitions) + game * n + player])
                    for player in range(n)
                ]
                for game in range(3)
            ],
            "efficiency_multiplier": str(gamma[efficiency_index]),
            "equality_multipliers": {
                str(meta): str(value)
                for meta, value in zip(eq_meta, gamma) if value
            },
        },
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--circuit-index", type=int, required=True)
    parser.add_argument("--U", type=lambda value: int(value, 0), required=True)
    parser.add_argument("--exclude-base", action="store_true")
    parser.add_argument("--zero-total-defect", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = analyze(
        json.loads(args.input.read_text()), args.circuit_index, args.U,
        exclude_base=args.exclude_base,
        zero_total_defect=args.zero_total_defect,
    )
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")

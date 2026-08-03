"""Exact reduced two-color recoloring and fixed-witness box capacities."""
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


def circuit_data(payload, circuit_index):
    n, A, B = payload["n"], payload["A_mask"], payload["B_mask"]
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
    return n, A, B, aggregate, required_A, required_B


def analyze(payload, circuit_index, U=None):
    n, A, B, aggregate, required_A, required_B = circuit_data(
        payload, circuit_index
    )
    grand = (1 << n) - 1
    if U is not None:
        assert 0 < U < grand
    coalitions = tuple(sorted(set(aggregate) | ({U} if U is not None else set())))
    position = {coalition: index for index, coalition in enumerate(coalitions)}
    alpha = len(coalitions)
    delta = alpha + 1 if U is not None else None
    sigma = alpha + (2 if U is not None else 1)
    variable_count = sigma + 1

    objective = np.zeros(variable_count)
    objective[sigma] = -1

    A_eq, b_eq = [], []
    for player in range(n):
        row = np.zeros(variable_count)
        for coalition in coalitions:
            if coalition >> player & 1:
                row[position[coalition]] = 1
        row[alpha] = -1
        if U is not None and U >> player & 1:
            row[delta] = -1
        A_eq.append(row)
        b_eq.append(0)

    A_ub, b_ub = [], []
    row = np.zeros(variable_count)
    row[position[A]] = -1
    if U == A:
        row[delta] = 1
    row[sigma] = float(required_A)
    A_ub.append(row)
    b_ub.append(0)

    row = np.zeros(variable_count)
    row[position[B]] = 1
    if U == B:
        row[delta] = -1
    row[sigma] = float(required_B)
    A_ub.append(row)
    b_ub.append(float(aggregate[B]))

    bounds = [(0, float(aggregate[coalition])) for coalition in coalitions]
    bounds.extend([(None, None)] * (variable_count - len(coalitions)))
    result = linprog(
        objective,
        A_ub=np.asarray(A_ub), b_ub=np.asarray(b_ub),
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
    exact_bounds = [
        (F(0), aggregate[coalition]) for coalition in coalitions
    ] + [(None, None)] * (variable_count - len(coalitions))
    primal_exact = all(
        sum(F(int(a)) * x for a, x in zip(row, solution) if a) == rat(rhs)
        for row, rhs in zip(A_eq, b_eq)
    ) and all(
        sum(F(int(a)) * x for a, x in zip(row, solution) if a) <= rat(rhs)
        for row, rhs in zip(A_ub, b_ub)
    ) and all(
        (lower_bound is None or value >= lower_bound)
        and (upper_bound is None or value <= upper_bound)
        for value, (lower_bound, upper_bound) in zip(solution, exact_bounds)
    )

    y = [rat(value) for value in result.ineqlin.marginals]
    gamma = [rat(value) for value in result.eqlin.marginals]
    lower = [rat(value) for value in result.lower.marginals]
    upper = [rat(value) for value in result.upper.marginals]
    combined = [F(0)] * variable_count
    for multiplier, row in zip(y, A_ub):
        for column, coefficient in enumerate(row):
            if coefficient:
                combined[column] += multiplier * rat(coefficient)
    for multiplier, row in zip(gamma, A_eq):
        for column, coefficient in enumerate(row):
            if coefficient:
                combined[column] += multiplier * rat(coefficient)
    for column, multiplier in enumerate(lower):
        combined[column] += multiplier
    for column, multiplier in enumerate(upper):
        combined[column] += multiplier
    target = [F(0)] * variable_count
    target[sigma] = -1
    dual_value = sum(multiplier * rat(rhs) for multiplier, rhs in zip(y, b_ub))
    dual_value += sum(
        multiplier * upper_bound
        for multiplier, (_lower_bound, upper_bound) in zip(upper, exact_bounds)
        if upper_bound is not None
    )
    dual_exact = (
        all(value <= 0 for value in y)
        and all(value >= 0 for value in lower)
        and all(value <= 0 for value in upper)
        and all(not value or exact_bounds[index][0] is not None
                for index, value in enumerate(lower))
        and all(not value or exact_bounds[index][1] is not None
                for index, value in enumerate(upper))
        and combined == target
        and dual_value == -capacity
    )

    maximum = max(gamma)
    minimum = min(gamma)
    return {
        "status": "exact reduced two-color capacity certificate",
        "n": n, "A_mask": A, "B_mask": B,
        "circuit_index": circuit_index, "tight_coalition": U,
        "capacity": str(capacity),
        "repairs_full_bumps": capacity >= 1,
        "primal_exact": primal_exact,
        "dual_exact": dual_exact,
        "dual_bound": str(dual_value),
        "retention_duals": {"A": str(y[0]), "B": str(y[1])},
        "player_potential": [str(value) for value in gamma],
        "potential_sum": str(sum(gamma, F(0))),
        "potential_on_witness": (
            str(sum(value for player, value in enumerate(gamma)
                    if U >> player & 1))
            if U is not None else None
        ),
        "maximum_set": sum(
            1 << player for player, value in enumerate(gamma)
            if value == maximum
        ),
        "minimum_set": sum(
            1 << player for player, value in enumerate(gamma)
            if value == minimum
        ),
        "alpha": str(solution[alpha]),
        "delta": str(solution[delta]) if U is not None else None,
        "subcollection": {
            str(coalition): str(solution[position[coalition]])
            for coalition in coalitions if solution[position[coalition]]
        },
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--circuit-index", type=int, required=True)
    parser.add_argument("--U", type=lambda value: int(value, 0))
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = analyze(
        json.loads(args.input.read_text()), args.circuit_index, args.U
    )
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")

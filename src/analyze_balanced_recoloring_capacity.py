"""Compute and exactly certify a circuit's balanced-recoloring capacity."""
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


def capacity(n, A, B, detail):
    aggregate = defaultdict(F)
    required = {"A": F(0), "B": F(0)}
    for meta, raw_weight in zip(detail["active_rows"], detail["circuit_weights"]):
        if meta[0] != "core":
            continue
        game, coalition = int(meta[1]), int(meta[2])
        weight = F(raw_weight)
        aggregate[coalition] += weight
        if game == 1 and coalition == A:
            required["A"] += weight
        if game == 2 and coalition == B:
            required["B"] += weight

    coalitions = sorted(aggregate)
    variables = [(game, coalition) for game in range(3) for coalition in coalitions]
    position = {key: index for index, key in enumerate(variables)}
    beta = len(variables)
    rho = beta + 3
    variable_count = rho + 1
    objective = np.zeros(variable_count)
    objective[rho] = -1

    A_eq, b_eq = [], []
    for coalition in coalitions:
        row = np.zeros(variable_count)
        for game in range(3):
            row[position[(game, coalition)]] = 1
        A_eq.append(row)
        b_eq.append(float(aggregate[coalition]))
    for game in range(3):
        for player in range(n):
            row = np.zeros(variable_count)
            for coalition in coalitions:
                if coalition >> player & 1:
                    row[position[(game, coalition)]] = 1
            row[beta + game] = -1
            A_eq.append(row)
            b_eq.append(0)

    A_ub, b_ub = [], []
    for game, coalition, label in ((1, A, "A"), (2, B, "B")):
        row = np.zeros(variable_count)
        row[position[(game, coalition)]] = -1
        row[rho] = float(required[label])
        A_ub.append(row)
        b_ub.append(0)

    bounds = [(0, None)] * (beta + 3) + [(None, None)]
    result = linprog(
        objective, A_ub=np.asarray(A_ub), b_ub=np.asarray(b_ub),
        A_eq=np.asarray(A_eq), b_eq=np.asarray(b_eq),
        bounds=bounds, method="highs",
    )
    if not result.success:
        return {"status": result.message}

    solution = [rat(value) for value in result.x]
    exact_capacity = solution[rho]
    a_ratio = aggregate[A] / required["A"]
    b_ratio = aggregate[B] / required["B"]
    mixture_bound = a_ratio * b_ratio / (a_ratio + b_ratio)
    primal_exact = True
    for row, rhs in zip(A_eq, b_eq):
        primal_exact &= sum(F(int(a)) * x for a, x in zip(row, solution)) == rat(rhs)
    for row, rhs in zip(A_ub, b_ub):
        primal_exact &= sum(F(int(a)) * x for a, x in zip(row, solution)) <= rat(rhs)

    y = [rat(value) for value in result.ineqlin.marginals]
    gamma = [rat(value) for value in result.eqlin.marginals]
    lower = [rat(value) for value in result.lower.marginals]
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
    target = [F(0)] * variable_count
    target[rho] = -1
    dual_value = sum(multiplier * rat(rhs) for multiplier, rhs in zip(gamma, b_eq))
    dual_exact = (
        all(value <= 0 for value in y)
        and all(value >= 0 for value in lower)
        and combined == target
        and dual_value == -exact_capacity
    )

    coalition_duals = gamma[:len(coalitions)]
    balance_duals = gamma[len(coalitions):]

    recoloring = [
        {
            "game": game,
            "coalition": coalition,
            "weight": str(solution[position[(game, coalition)]])
        }
        for game, coalition in variables
        if solution[position[(game, coalition)]]
    ]
    return {
        "status": "exact recoloring-capacity certificate",
        "capacity": str(exact_capacity),
        "aggregate_bump_masses": {
            "A": str(aggregate[A]), "B": str(aggregate[B])
        },
        "aggregate_to_distinguished_ratios": {
            "A": str(a_ratio), "B": str(b_ratio)
        },
        "two_color_mixture_lower_bound": str(mixture_bound),
        "mixture_bound_sharp": exact_capacity == mixture_bound,
        "full_recoloring": exact_capacity >= 1,
        "primal_exact": primal_exact,
        "dual_exact": dual_exact,
        "dual_obstruction": {
            "retention_multipliers": {
                "A": str(y[0]), "B": str(y[1])
            },
            "coalition_prices": {
                str(coalition): str(value)
                for coalition, value in zip(coalitions, coalition_duals)
                if value
            },
            "game_player_potentials": [
                [str(balance_duals[game * n + player])
                 for player in range(n)]
                for game in range(3)
            ],
        },
        "required_bump_masses": {key: str(value) for key, value in required.items()},
        "recoloring": recoloring,
    }


def analyze(payload):
    n, A, B = payload["n"], payload["A_mask"], payload["B_mask"]
    details = payload.get("circuits")
    if details is None:
        details = [detail for batch in payload["batches"]
                   for detail in batch["circuits"]]
    return {
        "n": n,
        "A_mask": A,
        "B_mask": B,
        "circuits": [
            {"circuit_index": index, **capacity(n, A, B, detail)}
            for index, detail in enumerate(details, 1)
        ],
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = analyze(json.loads(args.input.read_text()))
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")

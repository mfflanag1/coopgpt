"""Alternating search over the universal totally-balanced slack cone.

For canonical ``S={1,...,m}``, normalize every carrier difference to at
least one.  A slack vector s represents a totally balanced game ``v=-s``
with reference core point zero exactly when every subgame T has a payoff
vector tight at T and feasible for all U subset T.  This is a linear cone.

For fixed s, eta has a slack-linear dual whose coalition degrees are one
higher on P than on S.  Alternating the two LP blocks searches a much broader
class than finite-generator exact-game screens and directly probes the
dimension-free fractional-cover conjecture suggested by the n=5 proof.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix


def members(mask, n):
    return [player + 1 for player in range(n) if mask >> player & 1]


def proper_coalitions(n):
    return list(range(1, (1 << n) - 1))


def build_balanced_cone(n, s_size, witness_mode="subgame"):
    if witness_mode not in {"subgame", "global"}:
        raise ValueError(witness_mode)
    full = (1 << n) - 1
    target = (1 << s_size) - 1
    proper = proper_coalitions(n)
    slack_count = 1 << n
    witness_offset = {
        coalition: slack_count + index * n
        for index, coalition in enumerate(proper)
    }
    variable_count = slack_count + len(proper) * n
    witness_pairs = [
        (tight, coalition)
        for tight in proper
        for coalition in proper
        if witness_mode == "global" or coalition & ~tight == 0
    ]
    carrier_subsets = [
        coalition for coalition in range(1, target) if coalition != target
    ]

    inequality_count = slack_count + len(witness_pairs) + len(carrier_subsets)
    A_ub = lil_matrix((inequality_count, variable_count), dtype=float)
    b_ub = np.zeros(inequality_count)
    inequality_names = []
    row = 0
    for coalition in range(1 << n):
        A_ub[row, coalition] = -1
        inequality_names.append(f"slack_nonnegative:{coalition}")
        row += 1
    for tight, coalition in witness_pairs:
        offset = witness_offset[tight]
        for player in range(n):
            if coalition >> player & 1:
                A_ub[row, offset + player] = -1
        A_ub[row, coalition] = -1
        inequality_names.append(f"subgame_core:{tight}:{coalition}")
        row += 1
    outside = full ^ target
    for coalition in carrier_subsets:
        A_ub[row, outside | coalition] = -1
        A_ub[row, coalition] = 1
        b_ub[row] = -1
        inequality_names.append(f"carrier:{coalition}")
        row += 1
    assert row == inequality_count

    equality_count = 2 + len(proper) * (2 if witness_mode == "global" else 1)
    A_eq = lil_matrix((equality_count, variable_count), dtype=float)
    b_eq = np.zeros(equality_count)
    equality_names = []
    row = 0
    A_eq[row, 0] = 1
    equality_names.append("slack_empty")
    row += 1
    A_eq[row, full] = 1
    equality_names.append("slack_grand")
    row += 1
    for tight in proper:
        offset = witness_offset[tight]
        if witness_mode == "global":
            for player in range(n):
                A_eq[row, offset + player] = 1
            equality_names.append(f"efficiency:{tight}")
            row += 1
        for player in range(n):
            if tight >> player & 1:
                A_eq[row, offset + player] = 1
        A_eq[row, tight] = 1
        equality_names.append(f"subgame_tight:{tight}")
        row += 1
    assert row == equality_count
    return {
        "n": n,
        "s_size": s_size,
        "target": target,
        "proper": proper,
        "objective": np.zeros(variable_count),
        "A_ub": A_ub.tocsr(),
        "b_ub": b_ub,
        "A_eq": A_eq.tocsr(),
        "b_eq": b_eq,
        "bounds": [(None, None)] * variable_count,
        "inequality_names": inequality_names,
        "equality_names": equality_names,
    }


def eta_dual(n, s_size, costs):
    proper = proper_coalitions(n)
    coalition_count = len(proper)
    w_offset = coalition_count
    rho_index = w_offset + s_size
    variable_count = rho_index + 1
    objective = np.zeros(variable_count)
    for index, coalition in enumerate(proper):
        objective[index] = costs[coalition]
    A_eq = np.zeros((n, variable_count))
    b_eq = np.zeros(n)
    for index, coalition in enumerate(proper):
        for player in range(n):
            if coalition >> player & 1:
                A_eq[player, index] = 1
    for player in range(s_size):
        A_eq[player, w_offset + player] = 1
        A_eq[player, rho_index] = -1
    for player in range(s_size, n):
        A_eq[player, rho_index] = -1
        b_eq[player] = 1
    result = linprog(
        objective,
        A_eq=A_eq,
        b_eq=b_eq,
        bounds=[(0, None)] * variable_count,
        method="highs",
    )
    if not result.success:
        raise RuntimeError(result.message)
    lambdas = np.zeros(1 << n)
    for index, coalition in enumerate(proper):
        lambdas[coalition] = result.x[index]
    return float(result.fun), lambdas, result.x


def minimize_cone(template, slack_objective):
    objective = np.zeros_like(template["objective"])
    objective[: 1 << template["n"]] = slack_objective
    result = linprog(
        objective,
        A_ub=template["A_ub"],
        b_ub=template["b_ub"],
        A_eq=template["A_eq"],
        b_eq=template["b_eq"],
        bounds=template["bounds"],
        method="highs",
    )
    if not result.success:
        raise RuntimeError(result.message)
    return float(result.fun), result.x[: 1 << template["n"]]


def random_dual_vertex(n, s_size, rng):
    costs = np.zeros(1 << n)
    for coalition in proper_coalitions(n):
        costs[coalition] = rng.uniform(0.05, 10.0)
    _, lambdas, _ = eta_dual(n, s_size, costs)
    return lambdas


def run(n, s_size, restarts, iterations, seed, witness_mode):
    rng = random.Random(seed)
    template = build_balanced_cone(n, s_size, witness_mode=witness_mode)
    best = None
    histories = []
    for restart in range(restarts):
        lambdas = random_dual_vertex(n, s_size, rng)
        seen = set()
        history = []
        for iteration in range(iterations):
            fixed_cost, slacks = minimize_cone(template, lambdas)
            eta, next_lambdas, dual_point = eta_dual(n, s_size, slacks)
            signature = tuple(
                (coalition, round(next_lambdas[coalition], 10))
                for coalition in template["proper"]
                if next_lambdas[coalition] > 1e-8
            )
            record = {
                "restart": restart,
                "iteration": iteration,
                "fixed_dual_cost": fixed_cost,
                "eta_over_gamma_upper": eta,
                "dual_support": [
                    {
                        "coalition": members(coalition, n),
                        "coefficient": float(next_lambdas[coalition]),
                    }
                    for coalition in template["proper"]
                    if next_lambdas[coalition] > 1e-8
                ],
                "rho": float(dual_point[-1]),
                "nonzero_slacks": {
                    str(members(mask, n)): float(value)
                    for mask, value in enumerate(slacks)
                    if abs(value) > 1e-8
                },
            }
            history.append({
                "iteration": iteration,
                "fixed_dual_cost": fixed_cost,
                "eta": eta,
                "dual_support_size": len(signature),
            })
            if best is None or eta < best[0]:
                best = (eta, record)
            if eta < 1 - 1e-8 or signature in seen:
                break
            seen.add(signature)
            lambdas = next_lambdas
        histories.append(history)
        if best is not None and best[0] < 1 - 1e-8:
            break
    return {
        "status": f"alternating universal {witness_mode}-witness cone carrier search",
        "n": n,
        "S_size": s_size,
        "P_size": n - s_size,
        "normalization": "all carrier differences >= 1",
        "witness_mode": witness_mode,
        "restarts_requested": restarts,
        "iterations_per_restart": iterations,
        "seed": seed,
        "cone_variable_count": len(template["objective"]),
        "cone_inequality_count": template["A_ub"].shape[0],
        "cone_equality_count": template["A_eq"].shape[0],
        "carrier_bound_violated": best is not None and best[0] < 1 - 1e-8,
        "best": None if best is None else best[1],
        "histories": histories,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=6)
    parser.add_argument("--s-size", type=int, default=3)
    parser.add_argument("--restarts", type=int, default=100)
    parser.add_argument("--iterations", type=int, default=15)
    parser.add_argument("--seed", type=int, default=20261102)
    parser.add_argument(
        "--witness-mode",
        choices=("subgame", "global"),
        default="subgame",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 2 <= args.s_size < args.n:
        raise ValueError("require 2 <= |S| < n")
    payload = run(
        args.n,
        args.s_size,
        args.restarts,
        args.iterations,
        args.seed,
        args.witness_mode,
    )
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({key: value for key, value in payload.items() if key != "histories"}, indent=2))


if __name__ == "__main__":
    main()

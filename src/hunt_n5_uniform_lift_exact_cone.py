"""Universal LP for the first open quantitative-carrier case.

Normalize ``N={1,2,3,p,q}``, ``S={1,2,3}``, ``psi=0`` and
``gamma_S(psi) >= 1``.  Write the exact game as ``v(A)=-s(A)``.  Exactness
is encoded linearly: for every proper nonempty coalition T there is a
translated core point d^T tight at T.

For the explicit uniform displacement (1/3,1/3,1/3,*,*) the only
potentially nonautomatic constraints reduce to

    s({p,i}) + s({q,i}) >= 1/3,  i in S.

This program minimizes the left side.  An optimum below 1/3 is an exact
five-player counterexample to the uniform lift; a dual lower bound of 1/3
proves the remaining 3+2 case.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix


N = 5
FULL = (1 << N) - 1
S = 0b00111
P = FULL ^ S
PROPER = list(range(1, FULL))


def coalition_sum_row(matrix, row_index, offset, mask, coefficient):
    for player in range(N):
        if mask >> player & 1:
            matrix[row_index, offset + player] += coefficient


def build_lp(target_player=0, witness_mode="global"):
    if witness_mode not in {"global", "subgame"}:
        raise ValueError(witness_mode)
    slack_count = 1 << N
    witness_offset = {
        coalition: slack_count + index * N
        for index, coalition in enumerate(PROPER)
    }
    variable_count = slack_count + len(PROPER) * N

    witness_pairs = [
        (tight, coalition)
        for tight in PROPER
        for coalition in PROPER
        if witness_mode == "global" or coalition & ~tight == 0
    ]
    inequality_count = slack_count + len(witness_pairs) + 6
    A_ub = lil_matrix((inequality_count, variable_count), dtype=float)
    b_ub = np.zeros(inequality_count)
    inequality_names = []
    row_index = 0

    # s(A) >= 0, so psi=0 is itself a core point.
    for coalition in range(1 << N):
        A_ub[row_index, coalition] = -1
        inequality_names.append(f"slack_nonnegative:{coalition}")
        row_index += 1

    # Every witness d^T is core feasible at every proper coalition U.
    for tight, coalition in witness_pairs:
        offset = witness_offset[tight]
        for player in range(N):
            if coalition >> player & 1:
                A_ub[row_index, offset + player] = -1
        A_ub[row_index, coalition] = -1
        inequality_names.append(f"core:{tight}:{coalition}")
        row_index += 1

    # s(P union C)-s(C) >= 1 for every nonempty proper C subset S.
    carrier_subsets = [mask for mask in range(1, S + 1) if mask & ~S == 0 and mask != S]
    for coalition in carrier_subsets:
        A_ub[row_index, P | coalition] = -1
        A_ub[row_index, coalition] = 1
        b_ub[row_index] = -1
        inequality_names.append(f"carrier:{coalition}")
        row_index += 1
    assert row_index == inequality_count

    equality_count = 2 + 2 * len(PROPER)
    A_eq = lil_matrix((equality_count, variable_count), dtype=float)
    b_eq = np.zeros(equality_count)
    equality_names = []
    row_index = 0
    A_eq[row_index, 0] = 1
    equality_names.append("slack_empty")
    row_index += 1
    A_eq[row_index, FULL] = 1
    equality_names.append("slack_grand")
    row_index += 1
    for tight in PROPER:
        offset = witness_offset[tight]
        for player in range(N):
            A_eq[row_index, offset + player] = 1
        equality_names.append(f"efficiency:{tight}")
        row_index += 1
        coalition_sum_row(A_eq, row_index, offset, tight, 1)
        A_eq[row_index, tight] = 1
        equality_names.append(f"tight:{tight}")
        row_index += 1
    assert row_index == equality_count

    objective = np.zeros(variable_count)
    p, q = 3, 4
    objective[(1 << p) | (1 << target_player)] = 1
    objective[(1 << q) | (1 << target_player)] = 1
    bounds = [(None, None)] * variable_count
    return {
        "objective": objective,
        "A_ub": A_ub.tocsr(),
        "b_ub": b_ub,
        "A_eq": A_eq.tocsr(),
        "b_eq": b_eq,
        "bounds": bounds,
        "inequality_names": inequality_names,
        "equality_names": equality_names,
        "witness_offset": witness_offset,
    }


def members(mask):
    return [player + 1 for player in range(N) if mask >> player & 1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-player", type=int, default=1, choices=(1, 2, 3))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    target_player = args.target_player - 1
    lp = build_lp(target_player)
    result = linprog(
        lp["objective"],
        A_ub=lp["A_ub"],
        b_ub=lp["b_ub"],
        A_eq=lp["A_eq"],
        b_eq=lp["b_eq"],
        bounds=lp["bounds"],
        method="highs",
    )
    payload = {
        "status": result.message,
        "success": bool(result.success),
        "target_player": target_player + 1,
        "objective": None if result.fun is None else float(result.fun),
        "uniform_threshold": 1 / 3,
        "variable_count": len(lp["objective"]),
        "inequality_count": lp["A_ub"].shape[0],
        "equality_count": lp["A_eq"].shape[0],
    }
    if result.success:
        slacks = result.x[: 1 << N]
        payload["nonzero_slacks"] = {
            str(members(mask)): float(value)
            for mask, value in enumerate(slacks)
            if abs(value) > 1e-8
        }
        payload["carrier_differences"] = {
            str(members(mask)): float(slacks[P | mask] - slacks[mask])
            for mask in range(1, S + 1)
            if mask & ~S == 0 and mask != S
        }
        payload["dual_inequality_support"] = [
            {
                "constraint": lp["inequality_names"][index],
                "multiplier": float(-value),
            }
            for index, value in enumerate(result.ineqlin.marginals)
            if abs(value) > 1e-8
        ]
        payload["dual_equality_support"] = [
            {
                "constraint": lp["equality_names"][index],
                "multiplier": float(value),
            }
            for index, value in enumerate(result.eqlin.marginals)
            if abs(value) > 1e-8
        ]
    output = args.output or (
        Path(__file__).resolve().parents[1]
        / "results"
        / "n5_uniform_lift_exact_cone.json"
    )
    output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

"""Targeted positive-circuit search for the three-game Farkas cone.

After eliminating the three free efficiency multipliers, the nonnegative
Farkas cone is {lambda >= 0 : D lambda = 0}, with rank 3(n-1).  Its extreme
rays are support-minimal positive circuits.  This search samples fundamental
circuits from random full-rank bases that contain the A-bump column and tests
whether adjoining the B-bump column produces an all-positive dependence.

Unlike random objectives on the normalized cone, this directly targets a
both-sensitive extreme ray.  Failure to find one is discovery evidence, not
an enumeration theorem.  Any hit is exactified with SymPy and checked to have
one-dimensional nullspace and strictly positive coefficients.
"""
from __future__ import annotations

import argparse
import json
import random
from fractions import Fraction as F

import numpy as np
import sympy as sp

from family_infeasible import build_constraints
from mine_family_farkas_rays import ray_invariants
from tugame import Game


def eliminated_matrix(n, A, B):
    zero = Game(n, [F(0)] * (1 << n))
    variable_count, inequalities, _, equalities, _, rowmeta = build_constraints(
        [zero, zero, zero], [(0, 1, A), (0, 2, B)]
    )
    columns = len(inequalities)
    rows = []
    reference = n - 1
    for game in range(3):
        for player in range(n - 1):
            rows.append(
                [
                    inequalities[column][game * n + player]
                    - inequalities[column][game * n + reference]
                    for column in range(columns)
                ]
            )
    return np.asarray(rows, dtype=float), inequalities, equalities, rowmeta


def exactify_support(matrix, support):
    exact = sp.Matrix(np.asarray(matrix[:, support], dtype=int).tolist())
    nullspace = exact.nullspace()
    if len(nullspace) != 1:
        return None
    vector = nullspace[0]
    if all(value < 0 for value in vector):
        vector = -vector
    if not all(value > 0 for value in vector):
        return None
    common = sp.ilcm(*[value.q for value in vector])
    integers = [int(value * common) for value in vector]
    divisor = abs(sp.igcd(*integers))
    return [value // divisor for value in integers]


def full_ray(weights, support, inequalities, equalities, n):
    lambdas = [0] * len(inequalities)
    for column, weight in zip(support, weights):
        lambdas[column] = weight
    efficiencies = []
    for game in range(3):
        stationarity = sum(
            lambdas[row] * inequalities[row][game * n]
            for row in range(len(inequalities))
        )
        efficiencies.append(-stationarity)
        for player in range(1, n):
            check = sum(
                lambdas[row] * inequalities[row][game * n + player]
                for row in range(len(inequalities))
            )
            assert check == stationarity
    return lambdas + efficiencies


def search(n, A, B, trials, seed):
    matrix, inequalities, equalities, rowmeta = eliminated_matrix(n, A, B)
    rank = int(np.linalg.matrix_rank(matrix))
    bump_A = rowmeta.index(("core", 1, A))
    bump_B = rowmeta.index(("core", 2, B))
    candidates = [
        column
        for column in range(matrix.shape[1])
        if column not in (bump_A, bump_B)
    ]
    rng = random.Random(seed)
    full_rank_bases = 0
    for trial in range(trials):
        basis = [bump_A] + rng.sample(candidates, rank - 1)
        basis_matrix = matrix[:, basis]
        if np.linalg.matrix_rank(basis_matrix) < rank:
            continue
        full_rank_bases += 1
        coefficients = np.linalg.solve(basis_matrix, matrix[:, bump_B])
        # Bx=e gives the dependence -x on the basis and +1 on bump_B.
        if coefficients[0] >= -1e-8 or np.any(coefficients > 1e-8):
            continue
        numerical_weights = [-value for value in coefficients] + [1.0]
        numerical_support = basis + [bump_B]
        support = [
            column
            for column, weight in zip(numerical_support, numerical_weights)
            if weight > 1e-8
        ]
        weights = exactify_support(matrix, support)
        if weights is None:
            continue
        ray = full_ray(weights, support, inequalities, equalities, n)
        invariants = ray_invariants(ray, rowmeta, n, A, B, (1 << n) - 1)
        assert set(invariants["bump_sensitivity"]) == {"A", "B"}
        return {
            "found": True,
            "trial": trial,
            "full_rank_bases": full_rank_bases,
            "rank": rank,
            "support_nullity": 1,
            "ray": invariants,
        }
    return {
        "found": False,
        "trials": trials,
        "full_rank_bases": full_rank_bases,
        "rank": rank,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5)
    parser.add_argument("--A", type=lambda value: int(value, 0), default=0b00011)
    parser.add_argument("--B", type=lambda value: int(value, 0), default=0b01100)
    parser.add_argument("--trials", type=int, default=100000)
    parser.add_argument("--seed", type=int, default=20260801)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    payload = {
        "status": "targeted fundamental-circuit search; nonfinding is not proof",
        "n": args.n,
        "A_mask": args.A,
        "B_mask": args.B,
        "trials_requested": args.trials,
        "seed": args.seed,
        "result": search(args.n, args.A, args.B, args.trials, args.seed),
    }
    print(json.dumps(payload, indent=2))

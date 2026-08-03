"""Exact orbit enumeration of both-sensitive three-game Farkas circuits.

The discovery MILP in :mod:`minimize_both_sensitive_support` uses a floating
point epsilon.  This script replaces that gap by an exact rational SMT model.
For an integer rank-r matrix, a circuit has at most r+1 columns.  Its primitive
integer kernel vector is made of minors, so for the present {-1,0,1} matrix a
normalized positive circuit has every nonzero entry at least

    1 / ((r + 1) * r ** (r / 2)).

At n=5, r=12 and the exact floor is therefore 1/(13*12**6).  Z3's linear
rational arithmetic sees every positive circuit, while Boolean selectors make
support blocking and symmetry reduction exact.  An UNSAT result at every
support size through r+1 is an exhaustive certificate relative only to Z3's
exact LRA/Boolean decision procedure, not to numerical tolerances.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from fractions import Fraction as F

import numpy as np
import sympy as sp
import z3

from minimize_both_sensitive_support import (
    core_positive_circuit_supports,
    permute_meta,
    preserving_player_permutations,
)
from search_both_sensitive_circuits import eliminated_matrix, exactify_support, full_ray


def exact_integer_matrix(matrix):
    integer = np.asarray(matrix, dtype=int)
    assert np.array_equal(matrix, integer)
    assert set(np.unique(integer)).issubset({-1, 0, 1})
    return integer


def rational(value):
    value = z3.simplify(value)
    return F(value.numerator_as_long(), value.denominator_as_long())


def reduce_positive_support(matrix, support, weights):
    """Reduce an exact positive kernel point to a positive circuit."""
    support = list(support)
    weights = [F(value) for value in weights]
    while True:
        block = sp.Matrix(matrix[:, support].tolist())
        nullspace = block.nullspace()
        if len(nullspace) == 1:
            circuit_weights = exactify_support(matrix, support)
            assert circuit_weights is not None
            return tuple(support), tuple(circuit_weights)

        direction = None
        for vector in nullspace:
            candidate = [F(value) for value in vector]
            ratios = [candidate[i] / weights[i] for i in range(len(weights))]
            if len(set(ratios)) > 1:
                direction = candidate
                break
        assert direction is not None
        scale = min(direction[i] / weights[i] for i in range(len(weights)))
        smaller = [direction[i] - scale * weights[i] for i in range(len(weights))]
        assert all(value >= 0 for value in smaller)
        keep = [i for i, value in enumerate(smaller) if value > 0]
        assert 0 < len(keep) < len(support)
        support = [support[i] for i in keep]
        weights = [smaller[i] for i in keep]


def orbit_supports(support, rowmeta, n, A, B):
    metadata_index = {meta: index for index, meta in enumerate(rowmeta)}
    return {
        tuple(
            sorted(
                metadata_index[permute_meta(rowmeta[index], permutation)]
                for index in support
            )
        )
        for permutation in preserving_player_permutations(n, A, B)
    }


def core_subcircuit_cuts(matrix, rowmeta, n):
    base_indices = [
        index
        for index, meta in enumerate(rowmeta)
        if meta[0] == "core" and meta[1] == 0
    ]
    base_circuits = core_positive_circuit_supports(matrix, rowmeta, n)
    metadata_index = {meta: index for index, meta in enumerate(rowmeta)}
    cuts = []
    for game in range(3):
        for circuit in base_circuits:
            coalitions = [rowmeta[index][2] for index in circuit]
            cuts.append(
                tuple(metadata_index[("core", game, coalition)] for coalition in coalitions)
            )
    return cuts, len(base_circuits)


def build_solver(matrix, rowmeta, mandatory, epsilon, support_bound, blocked, cuts,
                 timeout_ms, require_both_mono, A, B):
    columns = matrix.shape[1]
    lambdas = [z3.Real(f"lambda_{index}") for index in range(columns)]
    selected = [z3.Bool(f"selected_{index}") for index in range(columns)]
    solver = z3.Solver()
    if timeout_ms:
        solver.set(timeout=timeout_ms)

    eps = z3.Q(epsilon.numerator, epsilon.denominator)
    for weight, active in zip(lambdas, selected):
        indicator = z3.If(active, z3.RealVal(1), z3.RealVal(0))
        solver.add(weight >= eps * indicator)
        solver.add(weight <= indicator)
    solver.add(z3.Sum(lambdas) == 1)
    for row in matrix:
        solver.add(z3.Sum([int(value) * weight for value, weight in zip(row, lambdas)]) == 0)
    for index in mandatory:
        solver.add(selected[index])
    solver.add(z3.Sum([z3.If(active, 1, 0) for active in selected]) <= support_bound)

    if require_both_mono:
        for label in (A, B):
            arm = [
                selected[index]
                for index, meta in enumerate(rowmeta)
                if meta[0] == "mono" and meta[-1] == label
            ]
            solver.add(z3.Or(arm))

    add_support_blocks(solver, selected, itertools.chain(cuts, blocked))
    return solver, lambdas, selected


def add_support_blocks(solver, selected, supports):
    """Exclude every supplied support and all of its supersets."""
    for support in supports:
        solver.add(z3.Or([z3.Not(selected[index]) for index in support]))


def enumerate_exact(n, A, B, start_support, max_support, timeout_ms,
                    max_orbits, require_both_mono, use_core_cuts,
                    seed_payload=None):
    matrix_float, inequalities, equalities, rowmeta = eliminated_matrix(n, A, B)
    matrix = exact_integer_matrix(matrix_float)
    rank = int(sp.Matrix(matrix.tolist()).rank())
    circuit_support_bound = rank + 1
    max_support = min(max_support, circuit_support_bound)
    # r**ceil(r/2) is a simple integer upper bound for r**(r/2); it is exact
    # at the even rank r=12 used in the five-player classification.
    determinant_bound = rank ** ((rank + 1) // 2)
    epsilon = F(1, (rank + 1) * determinant_bound)
    bump_A = rowmeta.index(("core", 1, A))
    bump_B = rowmeta.index(("core", 2, B))

    if use_core_cuts:
        cuts, base_cut_count = core_subcircuit_cuts(matrix, rowmeta, n)
    else:
        cuts, base_cut_count = [], 0
    blocked = []
    recorded_signatures = set()
    circuits = []
    support_results = []
    seeded_orbits = 0
    if seed_payload is not None:
        assert seed_payload["n"] == n
        assert seed_payload["A_mask"] == A
        assert seed_payload["B_mask"] == B
        metadata_index = {meta: index for index, meta in enumerate(rowmeta)}
        for detail in seed_payload["circuits"]:
            support = tuple(
                metadata_index[tuple(meta)] for meta in detail["active_rows"]
            )
            weights = exactify_support(matrix, support)
            assert weights == detail["circuit_weights"]
            orbit = orbit_supports(support, rowmeta, n, A, B)
            signature = min(orbit)
            if signature in recorded_signatures:
                continue
            recorded_signatures.add(signature)
            blocked.extend(sorted(orbit))
            seeded_orbits += 1

    for bound in range(start_support, max_support + 1):
        found_at_bound = 0
        solver, lambdas, selected = build_solver(
            matrix, rowmeta, (bump_A, bump_B), epsilon, bound, blocked, cuts,
            timeout_ms, require_both_mono, A, B,
        )
        while True:
            status = solver.check()
            if status == z3.unknown:
                support_results.append({
                    "support_bound": bound,
                    "status": "unknown",
                    "reason": solver.reason_unknown(),
                    "new_both_sensitive_orbits": found_at_bound,
                })
                return {
                    "status": "incomplete: exact solver returned unknown",
                    "n": n,
                    "A_mask": A,
                    "B_mask": B,
                    "rank": rank,
                    "circuit_support_bound": circuit_support_bound,
                    "exact_epsilon": str(epsilon),
                    "single_game_core_cuts_per_block": base_cut_count,
                    "require_both_mono": require_both_mono,
                    "seeded_both_sensitive_orbits": seeded_orbits,
                    "support_results": support_results,
                    "circuits": circuits,
                }
            if status == z3.unsat:
                support_results.append({
                    "support_bound": bound,
                    "status": "unsat after orbit blocking",
                    "new_both_sensitive_orbits": found_at_bound,
                    "blocked_support_orbits": len(recorded_signatures),
                })
                break

            model = solver.model()
            model_support = [
                index for index, active in enumerate(selected)
                if z3.is_true(model.eval(active, model_completion=True))
            ]
            model_weights = [rational(model.eval(lambdas[index])) for index in model_support]
            support, weights = reduce_positive_support(matrix, model_support, model_weights)
            orbit = orbit_supports(support, rowmeta, n, A, B)
            signature = min(orbit)
            if signature not in recorded_signatures:
                recorded_signatures.add(signature)
                new_blocks = sorted(orbit)
            else:
                # Defensive fallback: the exact same support must never recur.
                new_blocks = [tuple(support)]
            blocked.extend(new_blocks)
            add_support_blocks(solver, selected, new_blocks)

            if bump_A not in support or bump_B not in support:
                continue
            ray = full_ray(weights, support, inequalities, equalities, n)
            efficiencies = ray[len(rowmeta):]
            circuits.append({
                "support_size": len(support),
                "orbit_size": len(orbit),
                "circuit_weights": list(weights),
                "efficiency_weights": efficiencies,
                "active_rows": [rowmeta[index] for index in support],
            })
            found_at_bound += 1
            if max_orbits and len(circuits) >= max_orbits:
                return {
                    "status": "stopped at requested orbit limit",
                    "n": n,
                    "A_mask": A,
                    "B_mask": B,
                    "rank": rank,
                    "columns": matrix.shape[1],
                    "circuit_support_bound": circuit_support_bound,
                    "determinant_bound": determinant_bound,
                    "exact_epsilon": str(epsilon),
                    "single_game_core_cuts_per_block": base_cut_count,
                    "require_both_mono": require_both_mono,
                    "seeded_both_sensitive_orbits": seeded_orbits,
                    "support_results": support_results,
                    "circuits": circuits,
                }

    return {
        "status": "exact exhaustive enumeration completed",
        "n": n,
        "A_mask": A,
        "B_mask": B,
        "rank": rank,
        "columns": matrix.shape[1],
        "circuit_support_bound": circuit_support_bound,
        "determinant_bound": determinant_bound,
        "exact_epsilon": str(epsilon),
        "single_game_core_cuts_per_block": base_cut_count,
        "require_both_mono": require_both_mono,
        "seeded_both_sensitive_orbits": seeded_orbits,
        "support_results": support_results,
        "both_sensitive_orbits": len(circuits),
        "circuits": circuits,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5)
    parser.add_argument("--A", type=lambda value: int(value, 0), default=0b00111)
    parser.add_argument("--B", type=lambda value: int(value, 0), default=0b11000)
    parser.add_argument("--start-support", type=int, default=2)
    parser.add_argument("--max-support", type=int, default=13)
    parser.add_argument("--timeout-ms", type=int, default=0)
    parser.add_argument("--max-orbits", type=int, default=0)
    parser.add_argument("--require-both-mono", action="store_true")
    parser.add_argument("--no-core-cuts", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--seed-enumeration", type=Path, action="append", default=[])
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    seed_payload = None
    if args.seed_enumeration:
        seeds = [json.loads(path.read_text()) for path in args.seed_enumeration]
        seed_payload = {
            "n": seeds[0]["n"],
            "A_mask": seeds[0]["A_mask"],
            "B_mask": seeds[0]["B_mask"],
            "circuits": [
                circuit for seed in seeds for circuit in seed["circuits"]
            ],
        }
    payload = enumerate_exact(
        args.n, args.A, args.B, args.start_support, args.max_support,
        args.timeout_ms, args.max_orbits, args.require_both_mono,
        not args.no_core_cuts, seed_payload,
    )
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")

"""MILP search for the sparsest Farkas dependency using both bump rows.

This complements ``search_both_sensitive_circuits.py``.  A positive circuit
containing both distinguished columns is itself a feasible dependency here.
If the minimum-support solution has a one-dimensional exact nullspace and is
strictly positive, it is such a circuit.  A higher-dimensional support is only
diagnostic evidence: the epsilon floor makes a nonfinding non-rigorous.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import sympy as sp
from scipy.optimize import Bounds, LinearConstraint, milp

from exactlp import exact_linprog
from search_both_sensitive_circuits import (
    eliminated_matrix,
    exactify_support,
    full_ray,
)


def balanced_endpoint_margin(n, A, B, support, weights, rowmeta, efficiencies):
    """Optimize a circuit inequality over arbitrary balanced star endpoints.

    Grand worth is normalized to one.  Balancedness is witnessed directly by
    one core allocation for each of the three games, so this is an exact LP.
    A negative margin produces a balanced-family counterexample.
    """
    grand = (1 << n) - 1
    worth_offset = 3 * n
    d_A_index = worth_offset + grand - 1
    d_B_index = d_A_index + 1
    variable_count = d_B_index + 1
    objective = [0] * variable_count
    for index, weight in zip(support, weights):
        meta = rowmeta[index]
        if meta[0] != "core":
            continue
        _kind, game, coalition = meta
        objective[worth_offset + coalition - 1] -= weight
        if game == 1 and coalition == A:
            objective[d_A_index] -= weight
        if game == 2 and coalition == B:
            objective[d_B_index] -= weight

    A_ub, b_ub = [], []
    for game in range(3):
        for coalition in range(1, grand):
            row = [0] * variable_count
            row[worth_offset + coalition - 1] = 1
            if game == 1 and coalition == A:
                row[d_A_index] = 1
            if game == 2 and coalition == B:
                row[d_B_index] = 1
            for player in range(n):
                if coalition >> player & 1:
                    row[game * n + player] = -1
            A_ub.append(row)
            b_ub.append(0)
    for index in (d_A_index, d_B_index):
        row = [0] * variable_count
        row[index] = -1
        A_ub.append(row)
        b_ub.append(0)

    A_eq, b_eq = [], []
    for game in range(3):
        row = [0] * variable_count
        for player in range(n):
            row[game * n + player] = 1
        A_eq.append(row)
        b_eq.append(1)

    def solve(allocation_bound=None):
        bounded_A = list(A_ub)
        bounded_b = list(b_ub)
        if allocation_bound is not None:
            for index in range(3 * n):
                upper = [0] * variable_count
                upper[index] = 1
                bounded_A.append(upper)
                bounded_b.append(allocation_bound)
                lower = [0] * variable_count
                lower[index] = -1
                bounded_A.append(lower)
                bounded_b.append(allocation_bound)
        return exact_linprog(objective, bounded_A, bounded_b, A_eq, b_eq)

    status, optimum, solution = solve()
    allocation_bound = None
    if status == "unbounded":
        allocation_bound = 2
        status, optimum, solution = solve(allocation_bound)
    if status != "optimal":
        return {"status": status}
    maximum_supported_worth = -optimum
    margin = sum(efficiencies) - maximum_supported_worth
    return {
        "status": status,
        "unbounded_without_allocation_box": allocation_bound is not None,
        "allocation_box": allocation_bound,
        "farkas_margin": str(margin),
        "balanced_counterexample": margin < 0,
        "maximum_supported_worth": str(maximum_supported_worth),
        "efficiency_total": str(sum(efficiencies)),
        "bumps": {
            "A": str(solution[d_A_index]),
            "B": str(solution[d_B_index]),
        },
        "core_allocations": [
            [str(solution[game * n + player]) for player in range(n)]
            for game in range(3)
        ],
        "base_worths": {
            str(coalition): str(solution[worth_offset + coalition - 1])
            for coalition in range(1, grand)
        },
    }


def core_positive_circuit_supports(matrix, rowmeta, n):
    """Enumerate exact positive circuits contained in one game's core rows."""
    indices = [i for i, meta in enumerate(rowmeta) if meta[0] == "core" and meta[1] == 0]
    circuits = []
    for size in range(2, n + 1):
        for support in itertools.combinations(indices, size):
            block = matrix[:, support]
            if np.linalg.matrix_rank(block) != size - 1:
                continue
            numerical = np.linalg.svd(block, full_matrices=True)[2][-1]
            if not (np.all(numerical > 1e-8) or np.all(numerical < -1e-8)):
                continue
            if exactify_support(matrix, support) is not None:
                circuits.append(support)
    return circuits


def smallest_positive_subcircuit(matrix, support):
    """Extract a smallest exact positive circuit from a dependent support."""
    support = tuple(sorted(support))
    for size in range(2, len(support) + 1):
        for candidate in itertools.combinations(support, size):
            weights = exactify_support(matrix, candidate)
            if weights is not None:
                return candidate, weights
    return None, None


def preserving_player_permutations(n, A, B):
    blocks = [
        [i for i in range(n) if A >> i & 1],
        [i for i in range(n) if B >> i & 1],
        [i for i in range(n) if not ((A | B) >> i & 1)],
    ]
    choices = [list(itertools.permutations(block)) for block in blocks]
    for images in itertools.product(*choices):
        permutation = list(range(n))
        for block, image in zip(blocks, images):
            for source, target in zip(block, image):
                permutation[source] = target
        yield tuple(permutation)


def permute_mask(mask, permutation):
    result = 0
    for player, target in enumerate(permutation):
        if mask >> player & 1:
            result |= 1 << target
    return result


def permute_meta(meta, permutation):
    if meta[0] == "core":
        kind, game, coalition = meta
        return kind, game, permute_mask(coalition, permutation)
    kind, source, target, player, label = meta
    return (
        kind,
        source,
        target,
        permutation[player],
        permute_mask(label, permutation),
    )


def minimize_support(
    n: int,
    A: int,
    B: int,
    epsilon: float,
    time_limit: float,
    require_both_mono: bool,
    circuit_cuts: bool,
    max_supports: int,
    support_slack: int,
    all_core_circuit_cuts: bool,
    max_circuits: int,
    block_symmetry_orbits: bool,
    skip_balanced_endpoint_test: bool,
    checkpoint_path: Path | None = None,
    seed_payloads=(),
):
    matrix, inequalities, equalities, rowmeta = eliminated_matrix(n, A, B)
    p = matrix.shape[1]
    bump_A = rowmeta.index(("core", 1, A))
    bump_B = rowmeta.index(("core", 2, B))

    # Variables are (lambda_0,...,lambda_{p-1}, z_0,...,z_{p-1}), with
    # lambda_i <= z_i and binary z_i.  Sum(lambda)=1 fixes scale.
    objective = np.r_[np.zeros(p), np.ones(p)]
    integrality = np.r_[np.zeros(p), np.ones(p)]
    lower = np.zeros(2 * p)
    upper = np.ones(2 * p)
    lower[bump_A] = epsilon
    lower[bump_B] = epsilon

    kernel_rows = np.c_[matrix, np.zeros((matrix.shape[0], p))]
    normalization = np.r_[np.ones(p), np.zeros(p)][None, :]
    linking = np.c_[np.eye(p), -np.eye(p)]
    constraints = [
        LinearConstraint(kernel_rows, 0.0, 0.0),
        LinearConstraint(normalization, 1.0, 1.0),
        LinearConstraint(linking, -np.inf, 0.0),
    ]
    metadata_index = {meta: i for i, meta in enumerate(rowmeta)}

    def add_orbit_block(block_support):
        orbit_supports = {tuple(block_support)}
        if block_symmetry_orbits:
            orbit_supports = {
                tuple(sorted(
                    metadata_index[permute_meta(rowmeta[index], permutation)]
                    for index in block_support
                ))
                for permutation in preserving_player_permutations(n, A, B)
            }
        for orbit_support in orbit_supports:
            selector = np.zeros(2 * p)
            selector[[p + i for i in orbit_support]] = 1.0
            constraints.append(
                LinearConstraint(selector, -np.inf, len(orbit_support) - 1.0)
            )
        return len(orbit_supports)
    if require_both_mono:
        for label in (A, B):
            mono_selector = np.zeros(2 * p)
            for i, meta in enumerate(rowmeta):
                if meta[0] == "mono" and meta[-1] == label:
                    mono_selector[i] = 1.0
            constraints.append(LinearConstraint(mono_selector, epsilon, np.inf))
    if circuit_cuts:
        grand = (1 << n) - 1
        for game in range(3):
            for coalition in range(1, grand):
                complement = grand ^ coalition
                if coalition >= complement:
                    continue
                selector = np.zeros(2 * p)
                selector[p + metadata_index[("core", game, coalition)]] = 1.0
                selector[p + metadata_index[("core", game, complement)]] = 1.0
                constraints.append(LinearConstraint(selector, -np.inf, 1.0))
    core_circuit_count = 0
    if all_core_circuit_cuts:
        base_core_indices = [
            i for i, meta in enumerate(rowmeta) if meta[0] == "core" and meta[1] == 0
        ]
        base_position = {index: position for position, index in enumerate(base_core_indices)}
        base_circuits = core_positive_circuit_supports(matrix, rowmeta, n)
        core_circuit_count = len(base_circuits)
        for game in range(3):
            for base_support in base_circuits:
                selector = np.zeros(2 * p)
                for base_index in base_support:
                    coalition = rowmeta[base_core_indices[base_position[base_index]]][2]
                    index = metadata_index[("core", game, coalition)]
                    selector[p + index] = 1.0
                constraints.append(
                    LinearConstraint(selector, -np.inf, len(base_support) - 1.0)
                )
    seeded_circuits = 0
    seeded_supports = 0
    for seed_payload in seed_payloads:
        assert seed_payload.get("n", n) == n
        assert seed_payload.get("A_mask", A) == A
        assert seed_payload.get("B_mask", B) == B
        for detail in seed_payload.get("circuits", []):
            support = [metadata_index[tuple(meta)] for meta in detail["active_rows"]]
            seeded_supports += add_orbit_block(support)
            seeded_circuits += 1
    payload = {
        "n": n,
        "A_mask": A,
        "B_mask": B,
        "epsilon": epsilon,
        "require_both_mono": require_both_mono,
        "circuit_cuts": circuit_cuts,
        "all_core_circuit_cuts": all_core_circuit_cuts,
        "single_game_core_circuits_excluded_per_block": core_circuit_count,
        "seeded_circuit_representatives": seeded_circuits,
        "seeded_labeled_supports": seeded_supports,
        "rigor": "diagnostic only: positive epsilon can exclude a circuit",
    }

    def checkpoint():
        if checkpoint_path is not None:
            checkpoint_path.write_text(json.dumps(payload, indent=2) + "\n")

    minimum = None
    nullity_histogram = {}
    extracted_subcircuit_histogram = {}
    circuits = []
    for iteration in range(max_supports):
        result = milp(
            objective,
            integrality=integrality,
            bounds=Bounds(lower, upper),
            constraints=constraints,
            options={"time_limit": time_limit},
        )
        payload.update({"status": int(result.status), "message": result.message})
        if result.x is None:
            checkpoint()
            break
        if minimum is None:
            minimum = round(float(result.fun))
            payload["minimum_support_bound"] = minimum
        if float(result.fun) > minimum + support_slack + 1e-6:
            payload["next_support_size"] = float(result.fun)
            break

        lambdas = result.x[:p]
        support = [i for i, value in enumerate(lambdas) if value > 1e-8]
        exact = sp.Matrix(np.asarray(matrix[:, support], dtype=int).tolist())
        nullity = len(support) - int(exact.rank())
        nullity_histogram[str(nullity)] = nullity_histogram.get(str(nullity), 0) + 1
        payload["supports_examined"] = iteration + 1
        payload["nullity_histogram"] = nullity_histogram
        weights = exactify_support(matrix, support)
        circuit_support = tuple(support)
        if weights is None:
            circuit_support, weights = smallest_positive_subcircuit(matrix, support)
        if weights is not None:
            extracted_size = len(circuit_support)
            extracted_subcircuit_histogram[str(extracted_size)] = (
                extracted_subcircuit_histogram.get(str(extracted_size), 0) + 1
            )
            payload["extracted_positive_subcircuit_histogram"] = (
                extracted_subcircuit_histogram
            )
        both_sensitive = (
            weights is not None
            and bump_A in circuit_support
            and bump_B in circuit_support
        )
        if both_sensitive:
            ray = full_ray(weights, circuit_support, inequalities, equalities, n)
            efficiencies = ray[len(rowmeta):]
            detail = {
                "model_support_size": len(support),
                "circuit_weights": weights,
                "efficiency_weights": efficiencies,
                "active_rows": [rowmeta[i] for i in circuit_support],
                "balanced_endpoint_test": (
                    {"status": "skipped for circuit discovery"}
                    if skip_balanced_endpoint_test
                    else balanced_endpoint_margin(
                        n, A, B, circuit_support, weights, rowmeta, efficiencies
                    )
                ),
            }
            circuits.append(detail)
            payload["positive_circuit_found"] = True
            payload["circuits_found"] = len(circuits)
            payload["circuits"] = circuits
            if len(circuits) >= max_circuits:
                payload.update(detail)
                checkpoint()
                break

        # Exclude this binary support and, optionally, its entire orbit under
        # permutations that preserve the labeled player blocks A, B, and R.
        binary_support = [i for i, value in enumerate(result.x[p:]) if value > 0.5]
        block_support = (
            list(circuit_support)
            if weights is not None and not both_sensitive
            else binary_support
        )
        add_orbit_block(block_support)
        checkpoint()
    else:
        payload["enumeration_limit_reached"] = True
    payload.setdefault("positive_circuit_found", False)
    return payload


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5)
    parser.add_argument("--A", type=lambda value: int(value, 0), default=0b00011)
    parser.add_argument("--B", type=lambda value: int(value, 0), default=0b01100)
    parser.add_argument("--epsilon", type=float, default=1e-4)
    parser.add_argument("--time-limit", type=float, default=120.0)
    parser.add_argument("--require-both-mono", action="store_true")
    parser.add_argument(
        "--circuit-cuts",
        action="store_true",
        help="exclude complementary core-row pairs, which are positive subcircuits",
    )
    parser.add_argument("--max-circuits", type=int, default=1)
    parser.add_argument(
        "--block-symmetry-orbits",
        action="store_true",
        help="exclude the full A/B/R-preserving orbit of each examined support",
    )
    parser.add_argument(
        "--all-core-circuit-cuts",
        action="store_true",
        help="exclude every positive circuit supported within one game's core rows",
    )
    parser.add_argument("--max-supports", type=int, default=1)
    parser.add_argument(
        "--skip-balanced-endpoint-test",
        action="store_true",
        help="defer the expensive exact endpoint LP until after circuit discovery",
    )
    parser.add_argument(
        "--support-slack",
        type=int,
        default=0,
        help="enumerate supports this many rows above the minimum",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="write the JSON payload to this path instead of standard output",
    )
    parser.add_argument(
        "--seed-payload",
        type=Path,
        action="append",
        default=[],
        help="block all circuit orbits stored in a previous payload",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rendered = json.dumps(
        minimize_support(
            args.n,
            args.A,
            args.B,
            args.epsilon,
            args.time_limit,
            args.require_both_mono,
            args.circuit_cuts,
            args.max_supports,
            args.support_slack,
            args.all_core_circuit_cuts,
            args.max_circuits,
            args.block_symmetry_orbits,
            args.skip_balanced_endpoint_test,
            args.output,
            [json.loads(path.read_text()) for path in args.seed_payload],
        ),
        indent=2,
    )
    if args.output:
        args.output.write_text(rendered + "\n")
    else:
        print(rendered)

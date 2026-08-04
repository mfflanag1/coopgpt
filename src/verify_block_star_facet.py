"""Exact audit of the dimension-free block-star facet theorem.

The manuscript proof is symbolic.  This script is only a bug detector: it
checks the incidence identity, circuit rank, and all prospective exceptional
sets for canonical block stars, then checks the claimed saturated stars in
the two-column and universal three-poorer Lmin families.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import z3

from verify_n5_exact_leximin_monotonicity_counterexample import (
    BASE_GENERATORS,
    PHI_BASE,
    lower_envelope,
)
from verify_three_poorer_boundary_family import generators, lower_envelope as family_envelope


def members(n, coalition):
    return [i + 1 for i in range(n) if coalition >> i & 1]


def payoff(point, coalition):
    return sum(point[i] for i in range(len(point)) if coalition >> i & 1)


def rank(matrix):
    rows = [[F(value) for value in row] for row in matrix]
    result = 0
    column = 0
    while result < len(rows) and column < len(rows[0]):
        pivot = next((i for i in range(result, len(rows)) if rows[i][column]), None)
        if pivot is None:
            column += 1
            continue
        rows[result], rows[pivot] = rows[pivot], rows[result]
        scale = rows[result][column]
        rows[result] = [value / scale for value in rows[result]]
        for i in range(len(rows)):
            if i != result and rows[i][column]:
                scale = rows[i][column]
                rows[i] = [a - scale * b for a, b in zip(rows[i], rows[result])]
        result += 1
        column += 1
    return result


def decompositions(n, support):
    """Return new exceptional sets admitted by the supported coalitions."""
    full = (1 << n) - 1
    answers = []
    for exceptional in range(1, full):
        if exceptional in support:
            continue
        solver = z3.Solver()
        weights = [z3.Real(f"w_{n}_{exceptional}_{j}") for j in range(len(support))]
        common = z3.Real(f"r_{n}_{exceptional}")
        solver.add(*(weight >= 0 for weight in weights))
        for player in range(n):
            load = sum(
                weight
                for coalition, weight in zip(support, weights)
                if coalition >> player & 1
            )
            solver.add(load - int(exceptional >> player & 1) == common)
        if solver.check() == z3.sat:
            answers.append(members(n, exceptional))
    return answers


def canonical_star(k):
    """One H player and k singleton peripheral blocks."""
    n = k + 1
    full = (1 << n) - 1
    root = 1
    spokes = [root | (1 << j) for j in range(1, n)]
    loads = [
        sum(int(spoke >> i & 1) for spoke in spokes)
        - (k - 1) * int(root >> i & 1)
        for i in range(n)
    ]
    if loads != [1] * n:
        raise AssertionError(f"k={k}: block-star identity failed")

    # Project incidence modulo 1_N by subtracting the last coordinate.
    projected = [
        [int(coalition >> i & 1) - int(coalition >> (n - 1) & 1)
         for i in range(n - 1)]
        for coalition in spokes + [root]
    ]
    full_rank = rank(projected)
    deletion_ranks = [rank(projected[:j] + projected[j + 1:]) for j in range(k + 1)]
    if full_rank != k or any(value != k for value in deletion_ranks):
        raise AssertionError(f"k={k}: support is not a circuit")
    witnesses = decompositions(n, spokes + [root])
    if witnesses:
        raise AssertionError(f"k={k}: unexpected decompositions {witnesses}")
    return {
        "peripheral_block_count": k,
        "canonical_player_count": n,
        "circuit_rank": full_rank,
        "all_single_deletion_ranks": deletion_ranks,
        "new_exceptional_sets": witnesses,
        "indecomposable": True,
    }


def sharp_five_player_star():
    values = lower_envelope(BASE_GENERATORS)
    phi = PHI_BASE
    n = 5
    full = (1 << n) - 1
    left = sum(1 << i for i in (0, 2, 4))
    right = sum(1 << i for i in (2, 3, 4))
    root = left & right
    exterior = full & ~(left | right)
    spokes = [left, right, root | exterior]
    slacks = [payoff(phi, coalition) - values[coalition] for coalition in spokes]
    root_slack = payoff(phi, root) - values[root]
    if sum(slacks) != 2 * root_slack:
        raise AssertionError("five-player rooted block star is not saturated")
    return {
        "root": members(n, root),
        "spokes": [members(n, coalition) for coalition in spokes],
        "spoke_slacks": [str(value) for value in slacks],
        "root_slack": str(root_slack),
        "facet_slack_equality": f"{sum(slacks)} = 2*{root_slack}",
    }


def three_poorer_stars(max_m, max_h):
    cases = []
    for m in range(3, max_m + 1):
        for h in range(2, max_h + 1):
            points = generators(m, h)
            values = family_envelope(points)
            phi = tuple([1, 1, 2] + [1] * (m - 3) + [3] * h)
            n = m + h
            root = sum(1 << i for i in range(m, n))
            spokes = [root | (1 << i) for i in range(m)]
            slacks = [payoff(phi, coalition) - values[coalition] for coalition in spokes]
            root_slack = payoff(phi, root) - values[root]
            expected = [0, 2, 0] + [1] * (m - 3)
            if slacks != expected or sum(slacks) != (m - 1) * root_slack:
                raise AssertionError(f"(m,h)=({m},{h}): star saturation failed")
            cases.append({
                "poorer_side_size": m,
                "richer_suffix_size": h,
                "spoke_slacks": [str(value) for value in slacks],
                "root_slack": str(root_slack),
                "facet_slack_equality": f"{sum(slacks)} = {m - 1}*{root_slack}",
            })
    return cases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-blocks", type=int, default=7)
    parser.add_argument("--max-poorer-side", type=int, default=7)
    parser.add_argument("--max-richer-suffix", type=int, default=6)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = {
        "status": "block-star facet theorem audited",
        "arithmetic": "exact rational and exact SMT",
        "finite_audit_is_not_proof": True,
        "canonical_stars": [canonical_star(k) for k in range(2, args.max_blocks + 1)],
        "five_player_rooted_star": sharp_five_player_star(),
        "universal_three_poorer_stars": three_poorer_stars(
            args.max_poorer_side, args.max_richer_suffix
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

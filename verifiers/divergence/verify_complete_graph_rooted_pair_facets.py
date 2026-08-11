#!/usr/bin/env python3
"""Exact audit of the complete-graph rooted pair-lift facet family."""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "verifiers" / "lib"))

from catalogue import load as load_catalogue  # noqa: E402


def edges(m: int) -> tuple[tuple[int, int], ...]:
    return tuple(itertools.combinations(range(m), 2))


def matrix_rank(columns: tuple[int, ...], n: int) -> int:
    matrix = [[F((column >> row) & 1) for column in columns] for row in range(n)]
    rank = 0
    for column in range(len(columns)):
        pivot = next((row for row in range(rank, n) if matrix[row][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scale = matrix[rank][column]
        matrix[rank] = [value / scale for value in matrix[rank]]
        for row in range(n):
            if row == rank or matrix[row][column] == 0:
                continue
            scale = matrix[row][column]
            matrix[row] = [
                value - scale * pivot_value
                for value, pivot_value in zip(matrix[row], matrix[rank])
            ]
        rank += 1
    return rank


def support_system(m: int, p: int) -> tuple[int, tuple[int, ...], tuple[int, ...]]:
    edge_list = edges(m)
    n = 1 + len(edge_list) + p
    stars = []
    for vertex in range(m):
        mask = 1
        for index, edge in enumerate(edge_list, start=1):
            if vertex in edge:
                mask |= 1 << index
        stars.append(mask)
    pairs = [1 | (1 << (1 + len(edge_list) + index)) for index in range(p)]
    positive = tuple((*stars, *pairs))
    support = (1, *positive)
    coefficients = (-(m - 2 + 2 * p), *((1,) * m), *((2,) * p))
    loads = tuple(
        sum(coefficient for coalition, coefficient in zip(support, coefficients) if coalition >> player & 1)
        for player in range(n)
    )
    if loads != (2,) * n:
        raise AssertionError((m, p, "incidence identity", loads))
    if matrix_rank(support, n) != len(support):
        raise AssertionError((m, p, "support rank"))
    return n, positive, support


def additive_solution(m: int, bits: tuple[int, ...]) -> tuple[tuple[F, ...], F] | None:
    """Solve a_i+a_j-g=b_ij modulo the gauge (a,g)->(a+t,g+2t)."""
    edge_list = edges(m)
    b = {edge: F(value) for edge, value in zip(edge_list, bits)}
    # Gauge a_0=0.  Then a_j=g+b_0j and any edge among 1,...,m-1 fixes g.
    g = b[1, 2] - b[0, 1] - b[0, 2]
    a = (F(0), *(g + b[0, j] for j in range(1, m)))
    if any(a[i] + a[j] - g != b[i, j] for i, j in edge_list):
        return None
    return tuple(a), g


def feasible_exceptional(
    m: int,
    p: int,
    bits: tuple[int, ...],
    outside: tuple[int, ...],
    beta: int,
) -> bool:
    solved = additive_solution(m, bits)
    if solved is None:
        return False
    a, g = solved
    lower = max(-value for value in a)
    if p:
        lower = max(lower, *(F(-g - value, 2) for value in outside))
    denominator = m + 2 * p - 2
    upper = F(beta - sum(outside), denominator) + F((1 - p) * g - sum(a), denominator)
    return lower <= upper


def supported(m: int, p: int, bits: tuple[int, ...], outside: tuple[int, ...], beta: int) -> bool:
    edge_list = edges(m)
    selected_edges = {edge for edge, value in zip(edge_list, bits) if value}
    if beta == 1 and not selected_edges and sum(outside) == 0:
        return True  # exceptional root
    for vertex in range(m):
        star = {edge for edge in edge_list if vertex in edge}
        if beta == 1 and selected_edges == star and sum(outside) == 0:
            return True
    if beta == 1 and not selected_edges and sum(outside) == 1:
        return True  # one rooted pair spoke
    return False


def audit(m: int, p: int) -> dict:
    edge_list = edges(m)
    n, positive, support = support_system(m, p)
    feasible = 0
    unsupported_proper = []
    additive_patterns = 0
    for bits in itertools.product((0, 1), repeat=len(edge_list)):
        if additive_solution(m, bits) is not None:
            additive_patterns += 1
        for outside in itertools.product((0, 1), repeat=p):
            for beta in (0, 1):
                if not feasible_exceptional(m, p, bits, outside, beta):
                    continue
                feasible += 1
                empty = beta == 0 and not any(bits) and not any(outside)
                full = beta == 1 and all(bits) and all(outside)
                if not empty and not full and not supported(m, p, bits, outside, beta):
                    unsupported_proper.append(
                        {"beta": beta, "edges": list(bits), "outside": list(outside)}
                    )
    if unsupported_proper:
        raise AssertionError((m, p, unsupported_proper[0]))
    row_signatures = {
        tuple((coalition >> player) & 1 for coalition in positive)
        for player in range(1, n)
    }
    clone_saturated = len(row_signatures) == len(positive)
    return {
        "m": m,
        "outside_pair_spokes": p,
        "players": n,
        "positive_coalitions": m + p,
        "support_size": m + p + 1,
        "incidence_rank": matrix_rank(support, n),
        "additive_binary_edge_patterns": additive_patterns,
        "expected_patterns": 2 * m + 2,
        "feasible_exceptional_candidates_including_empty_and_full": feasible,
        "unsupported_proper_exceptional_candidates": 0,
        "distinct_nonroot_incidence_rows": len(row_signatures),
        "clone_expanded_saturated": clone_saturated,
    }


def audit_published_catalogue() -> dict:
    counts = {}
    total = 0
    for n in range(3, 7):
        _letters, rows = load_catalogue(n)
        selected = []
        for row in rows:
            exceptional = row["exceptional"]
            if exceptional is None or exceptional & (exceptional - 1):
                continue
            root = exceptional.bit_length() - 1
            positive = tuple(mask for mask, coefficient in row["lam"].items() if coefficient > 0)
            if not all(mask >> root & 1 for mask in positive):
                raise AssertionError((n, "catalogued singleton facet is not rooted"))
            signatures = {
                tuple((mask >> player) & 1 for mask in positive)
                for player in range(n)
                if player != root
            }
            if len(signatures) != len(positive):
                raise AssertionError((n, "catalogued singleton facet is not clone-saturated"))
            selected.append(row)
        counts[str(n)] = len(selected)
        total += len(selected)
    return {
        "dimensions": "3..6",
        "singleton_exceptional_types_by_n": counts,
        "singleton_exceptional_types": total,
        "all_rooted_and_clone_saturated": True,
        "source": "published Studeny-Kratochvil electronic catalogue bundled in verifiers/lib/cat",
    }
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = [audit(m, p) for m in range(4, 7) for p in range(0, 4)]
    if any(row["additive_binary_edge_patterns"] != row["expected_patterns"] for row in rows):
        raise AssertionError("binary additive edge-pattern classification failed")
    report = {
        "status": "exact complete-graph rooted pair-lift facet audit passed",
        "human_family": (
            "sum_v 1_{S_v}+2 sum_o 1_{r,o}-(m-2+2p)e_r=2 1_N, "
            "where nonroot edge players are E(K_m) and S_v is the rooted vertex star"
        ),
        "parameter_rows": len(rows),
        "parameter_grid": {"m": "4..6", "outside_pair_spokes": "0..3"},
        "additive_binary_edge_patterns_by_m": {
            str(m): 2 * m + 2 for m in range(4, 7)
        },
        "all_support_ranks_exact": all(
            row["incidence_rank"] == row["support_size"] for row in rows
        ),
        "all_unsupported_proper_exceptional_counts_zero": all(
            row["unsupported_proper_exceptional_candidates"] == 0 for row in rows
        ),
        "all_feasible_candidates_are_empty_full_or_support": all(
            row["feasible_exceptional_candidates_including_empty_and_full"]
            == row["m"] + row["outside_pair_spokes"] + 3
            for row in rows
        ),
        "all_members_outside_clone_expanded_saturated_class": all(
            not row["clone_expanded_saturated"] for row in rows
        ),
        "published_catalogue_control": audit_published_catalogue(),
        "first_non_clone_member": {"m": 4, "p": 0, "players": 7},
        "scope": (
            "the displayed exceptional-set case analysis is the dimension-free proof; "
            "this exhaustive grid is a regression and falsification audit"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

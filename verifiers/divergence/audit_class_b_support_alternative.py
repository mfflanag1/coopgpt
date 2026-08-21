#!/usr/bin/env python3
"""Exact reduced audit for the s=2 class-B support alternative.

This is not a verifier of the universal conjecture.  It performs two sharply
scoped tasks fixed in the campaign note:

1. exhibit the exotic heavy--outsider matching top dual (CB6), showing that
   Lmax top optimality and the selector-comparison signs alone do not imply
   the PXC78/PXC84 support dichotomy;
2. test the maximally constrained exact-core lift of that obstruction.  The
   lift includes every z-tight inequality compatible with x-z except the
   forbidden PXC78/PXC84 rows, as well as the three PXC86 Lmin pinning rows.
   Failure of this one lift is not a universal infeasibility theorem.

All arithmetic and linear programs are exact rational computations.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from exactlp import exact_linprog

from audit_costar_saturation_dichotomy import coalition_sum
from audit_menu_relaxed_root_exchange import ordered_saturated_roots
from audit_spectral_or_reserve import margins, selectors


N = 7
TOTAL = F(20)
FULL = (1 << N) - 1
R, H, A, B = 0, 1, 2, 3
OUTSIDERS = (4, 5, 6)
X = (F(6), F(4), F(2), F(2), F(2), F(2), F(2))
Z = (
    F(31, 7), F(31, 7), F(30, 7), F(30, 7),
    F(6, 7), F(6, 7), F(6, 7),
)
Z_MATCHING = (
    F(31, 7), F(31, 7), F(22, 7), F(22, 7),
    F(2), F(2), F(6, 7),
)
Z_COUNTEREXAMPLE = (
    F(31, 7), F(31, 7), F(23, 7), F(23, 7),
    F(13, 7), F(13, 7), F(6, 7),
)
DIFFERENCE = tuple(x - z for x, z in zip(X, Z))


def mask(*players: int) -> int:
    return sum(1 << player for player in players)


PAIR = mask(R, H)
HEAVY_BLOCK = mask(H, *OUTSIDERS)
DOUBLE_COSTARS = {
    mask(R, H, other, outsider)
    for other in (A, B)
    for outsider in OUTSIDERS
}
MATCHING_ROWS = (mask(R, H, B, 4), mask(R, H, A, 5), mask(H, 6))


def solve_top_cover(allowed: tuple[int, ...], objective_player: int | None = None):
    """Solve the normalized two-top over-cover on a prescribed row menu."""
    count = len(allowed)
    eta = count
    alpha_r = count + 1
    alpha_h = count + 2
    width = count + 3

    equalities = []
    equality_rhs = []
    for player in range(N):
        row = [F(0)] * width
        for index, coalition in enumerate(allowed):
            row[index] = F((coalition >> player) & 1)
        row[eta] = F(-1)
        if player == R:
            row[alpha_r] = F(-1)
        if player == H:
            row[alpha_h] = F(-1)
        equalities.append(row)
        equality_rhs.append(F(0))
    row = [F(0)] * width
    row[alpha_r] = row[alpha_h] = F(1)
    equalities.append(row)
    equality_rhs.append(F(1))

    inequalities = []
    inequality_rhs = []
    for variable in range(width):
        row = [F(0)] * width
        row[variable] = F(-1)
        inequalities.append(row)
        inequality_rhs.append(F(0))

    objective = [F(0)] * width
    if objective_player == R:
        objective[alpha_r] = F(-1)
    elif objective_player == H:
        objective[alpha_h] = F(-1)
    status, _, solution = exact_linprog(
        objective, inequalities, inequality_rhs, equalities, equality_rhs
    )
    return status, solution, (eta, alpha_r, alpha_h)


def audit_matching_ray() -> dict:
    status, solution, (eta, alpha_r, alpha_h) = solve_top_cover(MATCHING_ROWS)
    if status != "optimal":
        raise AssertionError("CB6 matching support became infeasible")
    expected = (F(1, 3), F(1, 3), F(2, 3))
    actual = (solution[eta], solution[alpha_r], solution[alpha_h])
    if actual != expected or any(solution[index] != F(1, 3) for index in range(3)):
        raise AssertionError(("CB6 coefficients changed", actual, solution[:3]))
    comparison_slacks = tuple(coalition_sum(DIFFERENCE, row) for row in MATCHING_ROWS)
    if comparison_slacks != (F(0), F(0), F(5, 7)):
        raise AssertionError(("CB6 comparison slacks changed", comparison_slacks))
    return {
        "rows": [list(i for i in range(N) if row >> i & 1) for row in MATCHING_ROWS],
        "weights": ["1/3", "1/3", "1/3"],
        "eta": "1/3",
        "alpha": ["1/3", "2/3"],
        "comparison_slacks": [str(value) for value in comparison_slacks],
    }


def coalition_minimizer(constraints: dict[int, F]):
    inequalities = []
    inequality_rhs = []
    for coalition, bound in constraints.items():
        inequalities.append([
            F(-int(bool(coalition >> player & 1))) for player in range(N)
        ])
        inequality_rhs.append(-bound)
    for player in range(N):
        row = [F(0)] * N
        row[player] = F(-1)
        inequalities.append(row)
        inequality_rhs.append(F(0))
    equality = [[F(1)] * N]
    equality_rhs = [TOTAL]

    def minimize(coalition: int) -> F:
        objective = [F(int(bool(coalition >> player & 1))) for player in range(N)]
        status, value, _ = exact_linprog(
            objective, inequalities, inequality_rhs, equality, equality_rhs
        )
        if status != "optimal":
            raise AssertionError(("coalition-minimum LP failed", coalition, status))
        return value

    return minimize


def audit_maximal_lift() -> dict:
    """Test one maximal reduced-menu lift; this is not an exhaustive test."""
    excluded = {PAIR, HEAVY_BLOCK, *DOUBLE_COSTARS}
    constraints = {}
    for coalition in range(1, FULL):
        if coalition.bit_count() < 2 or coalition in excluded:
            continue
        if coalition_sum(DIFFERENCE, coalition) >= 0:
            constraints[coalition] = coalition_sum(Z, coalition)

    # The three fixed PXC86 rows are sufficient for its human Lmin proof.
    constraints.update({mask(R, H, A): F(12), mask(R, H, B): F(12), mask(R, A, B): F(10)})
    minimize = coalition_minimizer(constraints)
    singleton_values = tuple(minimize(1 << player) for player in range(N))
    result = {
        "constraint_count": len(constraints),
        "singleton_values": [str(value) for value in singleton_values],
        "singleton_normalized": all(value == 0 for value in singleton_values),
    }
    if result["singleton_normalized"]:
        values = tuple(minimize(coalition) for coalition in range(1 << N))
        x, z = selectors(values, N)
        result.update({
            "lmin": [str(value) for value in x],
            "lmax": [str(value) for value in z],
            "prescribed_lmin": x == X,
            "prescribed_lmax": z == Z,
        })
        root_rows = ordered_saturated_roots(values, x, z)
        result["root_count"] = len(root_rows)
        result["packet_margin"] = str(margins(values, x, z)["packet_margin"])
    return result


def audit_matching_lift() -> dict:
    """Lift CB6 using only its rows and the three PXC86 Lmin rows."""
    constraints = {
        coalition: coalition_sum(Z, coalition) for coalition in MATCHING_ROWS
    }
    constraints.update({
        mask(R, H, A): F(12),
        mask(R, H, B): F(12),
        mask(R, A, B): F(10),
    })
    minimize = coalition_minimizer(constraints)
    values = tuple(minimize(coalition) for coalition in range(1 << N))
    singleton_values = tuple(values[1 << player] for player in range(N))
    if any(singleton_values):
        raise AssertionError(("matching lift lost singleton normalization", singleton_values))
    x, z = selectors(values, N)
    if x != X or z != Z_MATCHING:
        raise AssertionError(("matching lift selectors changed", x, z))
    root_rows = ordered_saturated_roots(values, x, z)
    if len(root_rows) != 1 or root_rows[0][:3] != (R, (H, A, B), OUTSIDERS):
        raise AssertionError(("matching lift root changed", root_rows))
    margin = margins(values, x, z)["packet_margin"]
    if margin != 0:
        raise AssertionError(("matching lift left the packet boundary", margin))
    special_gaps = {
        "top_pair": coalition_sum(z, PAIR) - values[PAIR],
        "heavy_block": coalition_sum(z, HEAVY_BLOCK) - values[HEAVY_BLOCK],
        "double_costars": tuple(
            coalition_sum(z, coalition) - values[coalition]
            for coalition in sorted(DOUBLE_COSTARS)
        ),
    }
    if special_gaps["top_pair"] <= 0 or special_gaps["heavy_block"] <= 0:
        raise AssertionError(("matching lift entered a known support", special_gaps))
    if not any(gap > 0 for gap in special_gaps["double_costars"]):
        raise AssertionError("matching lift unexpectedly has the full PXC78 menu")
    return {
        "constraint_count": len(constraints),
        "singleton_values": [str(value) for value in singleton_values],
        "lmin": [str(value) for value in x],
        "lmax": [str(value) for value in z],
        "packet_margin": "0",
        "ordered_saturated_root": True,
        "special_gaps": {
            "top_pair": str(special_gaps["top_pair"]),
            "heavy_block": str(special_gaps["heavy_block"]),
            "double_costars": [str(value) for value in special_gaps["double_costars"]],
        },
    }


def counterexample_constraints() -> dict[int, F]:
    constraints = {
        coalition: coalition_sum(Z_COUNTEREXAMPLE, coalition)
        for coalition in MATCHING_ROWS
    }
    constraints.update({
        mask(R, H, A): F(12),
        mask(R, H, B): F(12),
        mask(R, A, B): F(10),
        mask(R, H, A, 6): F(13),
        mask(R, H, B, 6): F(13),
    })
    return constraints


def audit_counterexample_lift() -> dict:
    """Exact counterexample to the original PXC78-or-PXC84 dichotomy."""
    constraints = counterexample_constraints()
    minimize = coalition_minimizer(constraints)
    values = tuple(minimize(coalition) for coalition in range(1 << N))
    singleton_values = tuple(values[1 << player] for player in range(N))
    if any(singleton_values):
        raise AssertionError(("counterexample lost singleton normalization", singleton_values))
    x, z = selectors(values, N)
    if x != X or z != Z_COUNTEREXAMPLE:
        raise AssertionError(("counterexample selectors changed", x, z))
    root_rows = ordered_saturated_roots(values, x, z)
    if len(root_rows) != 1 or root_rows[0][:3] != (R, (H, A, B), OUTSIDERS):
        raise AssertionError(("counterexample root changed", root_rows))
    packet_margin = margins(values, x, z)["packet_margin"]
    if packet_margin != F(-1, 7):
        raise AssertionError(("counterexample packet margin changed", packet_margin))
    pair_gap = coalition_sum(z, PAIR) - values[PAIR]
    heavy_gap = coalition_sum(z, HEAVY_BLOCK) - values[HEAVY_BLOCK]
    double_gaps = tuple(
        coalition_sum(z, coalition) - values[coalition]
        for coalition in sorted(DOUBLE_COSTARS)
    )
    if pair_gap <= 0 or heavy_gap <= 0 or not any(gap > 0 for gap in double_gaps):
        raise AssertionError(("counterexample entered PXC78 or PXC84", pair_gap, heavy_gap, double_gaps))
    from audit_chosen_family_costar_closure import best_family_margin
    from audit_direct_ceiling_common_hinge_trichotomy import has_direct_packet
    direct = has_direct_packet(x, z, F(N, (N * N) // 4))
    family_margin = best_family_margin(values, x, z, R, (H, A, B), OUTSIDERS)
    if not direct or family_margin is not None:
        raise AssertionError(("counterexample closure classification changed", direct, family_margin))
    return {
        "defining_core_constraints": [
            {
                "coalition": [i for i in range(N) if coalition >> i & 1],
                "lower_bound": str(bound),
            }
            for coalition, bound in constraints.items()
        ],
        "singleton_values": [str(value) for value in singleton_values],
        "lmin": [str(value) for value in x],
        "lmax": [str(value) for value in z],
        "packet_margin": str(packet_margin),
        "ordered_saturated_root": True,
        "top_pair_gap": str(pair_gap),
        "heavy_block_gap": str(heavy_gap),
        "double_costar_gaps": [str(value) for value in double_gaps],
        "refutes_original_class_b_dichotomy": True,
        "new_support": "two matched double co-stars plus one heavy-outsider pair",
        "existing_closure": "direct packet",
        "chosen_family_margin": None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = {
        "claim": "reduced s=2 class-B support alternative audit",
        "matching_ray": audit_matching_ray(),
        "matching_exact_game_lift": audit_matching_lift(),
        "counterexample_exact_game_lift": audit_counterexample_lift(),
        "maximal_lift": audit_maximal_lift(),
        "scope": (
            "the exact lift refutes the original class-A-or-top-pair closure "
            "conjecture but does not refute the hybrid-overlap inequality; "
            "failure of the single maximal lift is not a universal theorem"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

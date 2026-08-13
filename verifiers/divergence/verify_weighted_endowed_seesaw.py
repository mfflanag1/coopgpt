#!/usr/bin/env python3
"""Exact audit of the endowed two-flat four-role seesaw theorem.

The human theorem identifies weighted Lmin/Lmax with two max-min values of a
2x2 crossing-time matrix, excludes diagonal middle gaps, and gives the exact
minimum total cost of every adjacent unit gap.  This script audits the closed
formula, independently replays staged LPs, and exactifies the unique n=6
target-equality role pattern by canonical block expansion.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from itertools import product
from pathlib import Path

COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))
from exactlp import exact_linprog  # noqa: E402


def atomic_target(n):
    return F(4 * n, n * n - (n % 2))


def clamp(value, width):
    return min(max(value, F(0)), F(width))


def crossing_matrix(weights, endowments, width):
    return {
        (rising, falling): F(
            weights[rising] * (endowments[falling] + width)
            - weights[falling] * endowments[rising],
            weights[rising] + weights[falling],
        )
        for rising in (0, 2)
        for falling in (1, 3)
    }


def selector_positions(weights, endowments, width):
    matrix = crossing_matrix(weights, endowments, width)
    lmin = max(min(matrix[r, f] for f in (1, 3)) for r in (0, 2))
    lmax = max(min(matrix[r, f] for r in (0, 2)) for f in (1, 3))
    ordered = sorted(clamp(value, width) for value in matrix.values())
    lmin, lmax = clamp(lmin, width), clamp(lmax, width)
    if sorted((lmin, lmax)) != ordered[1:3]:
        raise AssertionError((weights, endowments, width, matrix, lmin, lmax))
    return lmin, lmax, matrix


def adjacent_unit_gap_cost(low_weight, high_weight, side_a, side_b):
    """Exact minimum T for a unit adjacent middle gap.

    `low_weight` and `high_weight` are the two roles on the common direction;
    the other two weights are unordered.  A return value of None means that
    two unit-weight common-direction roles have identical crossing rows and
    cannot support a positive adjacent gap.
    """

    p, r = low_weight, high_weight
    q, b = sorted((side_a, side_b))
    if p > 1:
        return F(2) + F(p, q) + F(p + q + b, r)
    if r == 1:
        return None
    if q == 1:
        return F(2 * (2 * r + b + 1), r - 1)
    return F((q + 1) * (2 * r + q + b), q * (r - 1))


def oriented_adjacent_costs(weights):
    """Costs for both low rows and both low columns.

    Reversing the seesaw parameter turns a low column into a low row whose
    common low-direction role is the *other* (formerly high) column.
    """

    h0, h1, h2, h3 = weights
    return (
        adjacent_unit_gap_cost(h0, h2, h1, h3),
        adjacent_unit_gap_cost(h2, h0, h1, h3),
        adjacent_unit_gap_cost(h3, h1, h0, h2),
        adjacent_unit_gap_cost(h1, h3, h0, h2),
    )


def exact_gap_ratio_bound(weights):
    costs = [cost for cost in oriented_adjacent_costs(weights) if cost is not None]
    return max((F(1) / cost for cost in costs), default=F(0))


def independent_adjacent_gap_lp(low_weight, high_weight, side_a, side_b):
    """Minimize total for a unit low-row gap in the original variables."""

    p, r = low_weight, high_weight
    q, b = sorted((side_a, side_b))
    weights = (p, r, q, b)
    # Variables are e_p,e_r,e_q,e_b,s,l.  The two low crossings are <=l,
    # the two high crossings are >=l+1, and clipping requires s>=l+1.
    aub, bub = [], []
    for variable in range(6):
        row = [F(0)] * 6
        row[variable] = F(-1)
        aub.append(row)
        bub.append(F(0))
    row = [F(0)] * 6
    row[5], row[4] = F(1), F(-1)
    aub.append(row)
    bub.append(F(-1))
    for index, falling_weight in enumerate((q, b), start=2):
        low = [F(0)] * 6
        low[index] = p
        low[4] = p
        low[0] = -falling_weight
        low[5] = -(p + falling_weight)
        aub.append(low)
        bub.append(F(0))
        high = [F(0)] * 6
        high[index] = -r
        high[4] = -r
        high[1] = falling_weight
        high[5] = r + falling_weight
        aub.append(high)
        bub.append(-(r + falling_weight))
    aeq, beq = [], []
    for role, weight in enumerate(weights):
        if weight == 1:
            row = [F(0)] * 6
            row[role] = F(1)
            aeq.append(row)
            beq.append(F(0))
    return exact_linprog(
        [F(1), F(1), F(1), F(1), F(2), F(0)],
        aub,
        bub,
        aeq,
        beq,
    )


def independent_formula_lp_census(maximum_n=20):
    checked = 0
    infeasible = 0
    for n in range(5, maximum_n + 1):
        for p in range(1, n - 2):
            for r in range(1, n - p - 1):
                for side_a in range(1, n - p - r):
                    side_b = n - p - r - side_a
                    expected = adjacent_unit_gap_cost(p, r, side_a, side_b)
                    status, optimum, _ = independent_adjacent_gap_lp(
                        p, r, side_a, side_b
                    )
                    checked += 1
                    if expected is None:
                        if status != "infeasible":
                            raise AssertionError(
                                ("expected impossible gap", p, r, side_a, side_b, status)
                            )
                        infeasible += 1
                    elif status != "optimal" or optimum != expected:
                        raise AssertionError(
                            (
                                "independent unit-gap optimum",
                                p,
                                r,
                                side_a,
                                side_b,
                                status,
                                optimum,
                                expected,
                            )
                        )
    return checked, infeasible


def affine(role, endowments, width):
    if role in (0, 2):
        return F(1), F(endowments[role])
    return F(-1), F(endowments[role] + width)


def exact_staged_selector(weights, endowments, width, mode):
    pinned, free, trace = {}, set(range(4)), []
    while free:
        aub = [[F(-1), F(0)], [F(1), F(0)]]
        bub = [F(0), F(width)]
        aeq, beq = [], []
        for role, payoff in pinned.items():
            slope, intercept = affine(role, endowments, width)
            aeq.append([slope, F(0)])
            beq.append(payoff - intercept)
        for role in free:
            slope, intercept = affine(role, endowments, width)
            if mode == "min":
                aub.append([-slope, F(weights[role])])
                bub.append(intercept)
            else:
                aub.append([slope, F(-weights[role])])
                bub.append(-intercept)
        objective = [F(0), F(-1 if mode == "min" else 1)]
        status, optimum, _ = exact_linprog(objective, aub, bub, aeq, beq)
        if status != "optimal":
            raise AssertionError((mode, status))
        level = -optimum if mode == "min" else optimum
        aeq.append([F(0), F(1)])
        beq.append(level)
        newly = []
        for role in sorted(free):
            slope, intercept = affine(role, endowments, width)
            objective = [F(-slope if mode == "min" else slope), F(0)]
            status, optimum, _ = exact_linprog(objective, aub, bub, aeq, beq)
            if status != "optimal":
                raise AssertionError((mode, role, status))
            extreme = (-optimum if mode == "min" else optimum) + intercept
            if extreme == weights[role] * level:
                newly.append(role)
        if not newly:
            raise AssertionError((mode, "stage pinned nobody", level))
        for role in newly:
            pinned[role] = weights[role] * level
            free.remove(role)
        trace.append({"level": str(level), "newly_pinned_roles": newly})
    return tuple(pinned[i] for i in range(4)), trace


def controls():
    inputs = (
        ((1, 1, 1, 2), (0, 0, 0, 2), 1),
        ((1, 2, 1, 2), (0, 0, 0, 2), 1),
        ((1, 2, 1, 3), (0, 2, 0, 0), 1),
        ((5, 1, 1, 1), (0, 0, 0, 0), 6),
        ((1, 6, 14, 12), (9, 6, 7, 3), 15),
        ((8, 3, 2, 5), (2, 4, 1, 7), 11),
        ((2, 7, 9, 4), (5, 0, 3, 6), 13),
        ((6, 41, 263, 23), (31, 9, 2, 6), 59),
    )
    rows = []
    for weights, endowments, width in inputs:
        expected_lmin, expected_lmax, matrix = selector_positions(
            weights, endowments, width
        )
        lmin, lmin_trace = exact_staged_selector(weights, endowments, width, "min")
        lmax, lmax_trace = exact_staged_selector(weights, endowments, width, "max")
        if lmin[0] - endowments[0] != expected_lmin:
            raise AssertionError((weights, "Lmin", lmin, expected_lmin))
        if lmax[0] - endowments[0] != expected_lmax:
            raise AssertionError((weights, "Lmax", lmax, expected_lmax))
        total = F(sum(endowments) + 2 * width)
        overlap = total - 2 * abs(expected_lmin - expected_lmax)
        rows.append(
            {
                "weights": list(weights),
                "endowments": list(endowments),
                "width": width,
                "crossing_matrix": {
                    f"{r}{f}": str(value) for (r, f), value in matrix.items()
                },
                "lmin": [str(value) for value in lmin],
                "lmax": [str(value) for value in lmax],
                "overlap_ratio": str(overlap / total),
                "atomic_target": str(atomic_target(sum(weights))),
                "lmin_trace": lmin_trace,
                "lmax_trace": lmax_trace,
            }
        )
    return rows


def exact_game_selector(values, mode):
    """Independent complete staged selector on an atomic zero-singleton game."""

    n = (len(values) - 1).bit_length()
    grand = (1 << n) - 1
    pinned, free, trace = {}, set(range(n)), []
    while free:
        variable_count = n + 1
        level_index = n
        aub, bub = [], []
        for coalition in range(1, grand):
            row = [F(0)] * variable_count
            for player in range(n):
                if coalition >> player & 1:
                    row[player] = F(-1)
            aub.append(row)
            bub.append(-values[coalition])
        for player in free:
            row = [F(0)] * variable_count
            if mode == "min":
                row[player], row[level_index] = F(-1), F(1)
            else:
                row[player], row[level_index] = F(1), F(-1)
            aub.append(row)
            bub.append(F(0))
        aeq = [[F(1)] * n + [F(0)]]
        beq = [values[grand]]
        for player, payoff in pinned.items():
            row = [F(0)] * variable_count
            row[player] = F(1)
            aeq.append(row)
            beq.append(payoff)
        objective = [F(0)] * variable_count
        objective[level_index] = F(-1 if mode == "min" else 1)
        status, optimum, _ = exact_linprog(objective, aub, bub, aeq, beq)
        if status != "optimal":
            raise AssertionError(("atomic stage", mode, status))
        level = -optimum if mode == "min" else optimum
        level_row = [F(0)] * variable_count
        level_row[level_index] = F(1)
        aeq.append(level_row)
        beq.append(level)
        newly = []
        for player in sorted(free):
            objective = [F(0)] * variable_count
            objective[player] = F(-1 if mode == "min" else 1)
            status, optimum, _ = exact_linprog(objective, aub, bub, aeq, beq)
            if status != "optimal":
                raise AssertionError(("atomic pin", mode, player, status))
            extreme = -optimum if mode == "min" else optimum
            if extreme == level:
                newly.append(player)
        if not newly:
            raise AssertionError(("atomic stage pinned nobody", mode, level))
        for player in newly:
            pinned[player] = level
            free.remove(player)
        trace.append({"level": str(level), "newly_pinned_players": newly})
    return tuple(pinned[player] for player in range(n)), trace


def canonical_equality_expansion():
    """Exactify the unique n=6 equality pattern of the gap-cost theorem."""

    weights = (2, 1, 2, 1)
    role_endpoints = (
        (F(3), F(3, 2), F(0), F(3, 2)),
        (F(9, 2), F(0), F(3, 2), F(0)),
    )
    role_values = []
    for coalition in range(16):
        role_values.append(
            min(
                sum(point[role] for role in range(4) if coalition >> role & 1)
                for point in role_endpoints
            )
        )
    blocks = ((0, 1), (2,), (3, 4), (5,))
    values = []
    for coalition in range(64):
        full_roles = 0
        for role, block in enumerate(blocks):
            if all(coalition >> player & 1 for player in block):
                full_roles |= 1 << role
        values.append(role_values[full_roles])
    if any(values[1 << player] != 0 for player in range(6)):
        raise AssertionError("canonical expansion is not singleton-normalized")

    grand = 63
    for coalition in range(64):
        objective = [
            F(1) if coalition >> player & 1 else F(0) for player in range(6)
        ]
        aub, bub = [], []
        for proper in range(1, grand):
            aub.append(
                [F(-1) if proper >> player & 1 else F(0) for player in range(6)]
            )
            bub.append(-values[proper])
        status, optimum, _ = exact_linprog(
            objective,
            aub,
            bub,
            [[F(1)] * 6],
            [values[grand]],
        )
        if status != "optimal" or optimum != values[coalition]:
            raise AssertionError(("canonical exactness", coalition, status, optimum))

    lmin, lmin_trace = exact_game_selector(values, "min")
    lmax, lmax_trace = exact_game_selector(values, "max")
    expected_lmin = (F(2), F(2), F(1, 2), F(1, 2), F(1, 2), F(1, 2))
    expected_lmax = (F(3, 2), F(3, 2), F(3, 2), F(0), F(0), F(3, 2))
    if lmin != expected_lmin or lmax != expected_lmax:
        raise AssertionError(("canonical selectors", lmin, lmax))
    overlap = sum(min(left, right) for left, right in zip(lmin, lmax))
    total = values[grand]
    if overlap / total != F(2, 3):
        raise AssertionError(("canonical overlap", overlap, total))
    return {
        "role_weights": list(weights),
        "role_endpoints": [[str(value) for value in point] for point in role_endpoints],
        "atomic_players_by_role": [list(block) for block in blocks],
        "singleton_normalized": True,
        "coalition_exactness_minima_checked": 64,
        "lmin": [str(value) for value in lmin],
        "lmax": [str(value) for value in lmax],
        "sorted_lmin_profile": [str(value) for value in sorted(lmin)],
        "sorted_lmax_profile": [str(value) for value in sorted(lmax)],
        "overlap_ratio": str(overlap / total),
        "lmin_trace": lmin_trace,
        "lmax_trace": lmax_trace,
        "identified_six_player_profile": "S6 equality survivor 1408: (4,2) versus (2,4)",
    }


def formula_census(maximum_n=60):
    checked = 0
    rows = []
    equalities = []
    for n in range(5, maximum_n + 1):
        target = atomic_target(n)
        minimum = None
        minimizer = None
        for h0 in range(1, n - 2):
            for h1 in range(1, n - h0 - 1):
                for h2 in range(1, n - h0 - h1):
                    weights = (h0, h1, h2, n - h0 - h1 - h2)
                    for orientation, cost in enumerate(oriented_adjacent_costs(weights)):
                        checked += 1
                        ratio = F(1) if cost is None else F(1) - F(2) / cost
                        if minimum is None or ratio < minimum:
                            minimum = ratio
                            minimizer = (weights, orientation, cost)
                        if n >= 6 and ratio < target:
                            raise AssertionError(
                                ("gap-cost target", n, weights, orientation, ratio, target)
                            )
                        if n >= 6 and ratio == target:
                            equalities.append((n, weights, orientation, cost))
        rows.append(
            {
                "n": n,
                "target": str(target),
                "minimum_adjacent_bound": str(minimum),
                "margin": str(minimum - target),
                "first_minimizer": {
                    "weights": list(minimizer[0]),
                    "orientation": minimizer[1],
                    "unit_gap_cost": None if minimizer[2] is None else str(minimizer[2]),
                },
            }
        )
    return checked, rows, equalities


def bounded_grid():
    checked = 0
    rows = []
    for n in range(5, 21):
        target = atomic_target(n)
        minimum = None
        minimizer = None
        for h0 in range(1, n - 2):
            for h1 in range(1, n - h0 - 1):
                for h2 in range(1, n - h0 - h1):
                    weights = (h0, h1, h2, n - h0 - h1 - h2)
                    for endowments in product(range(4), repeat=4):
                        if any(
                            weights[i] == 1 and endowments[i] != 0
                            for i in range(4)
                        ):
                            continue
                        for width in range(1, 5):
                            lmin, lmax, _ = selector_positions(
                                weights, endowments, width
                            )
                            total = F(sum(endowments) + 2 * width)
                            gap_ratio = abs(lmin - lmax) / total
                            ratio = F(1) - 2 * gap_ratio
                            checked += 1
                            if minimum is None or ratio < minimum:
                                minimum = ratio
                                minimizer = (weights, endowments, width)
                            if n >= 6 and ratio < target:
                                raise AssertionError(
                                    (n, weights, endowments, width, ratio, target)
                                )
                            formula_bound = exact_gap_ratio_bound(weights)
                            if gap_ratio > formula_bound:
                                raise AssertionError(
                                    (
                                        "adjacent gap-cost formula",
                                        weights,
                                        endowments,
                                        width,
                                        gap_ratio,
                                        formula_bound,
                                    )
                                )
        rows.append(
            {
                "n": n,
                "target": str(target),
                "minimum_ratio": str(minimum),
                "margin": str(minimum - target),
                "first_minimizer": {
                    "weights": list(minimizer[0]),
                    "endowments": list(minimizer[1]),
                    "width": minimizer[2],
                },
            }
        )
    return checked, rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    independent_lp_checked, impossible_lp_rows = independent_formula_lp_census()
    formula_checked, formula_rows, equalities = formula_census()
    checked, grid_rows = bounded_grid()
    if not equalities:
        raise AssertionError("the six-player equality pattern was not recovered")
    if any(n != 6 for n, _, _, _ in equalities):
        raise AssertionError(("unexpected target equality", equalities))
    report = {
        "status": "weighted endowed seesaw target theorem audited exactly",
        "selector_theorem": (
            "Lmin=max over rising rows of their minimum crossing time; "
            "Lmax=max over falling columns of their minimum crossing time; "
            "the crossing-line cycle excludes a diagonal split, after which "
            "clipping makes these the two middle crossing times"
        ),
        "gap_cost_theorem": {
            "diagonal_gap": "impossible by the strict four-term crossing-order cycle",
            "adjacent_unit_gap_cost": {
                "p_gt_1": "2+p/q+(p+q+b)/r",
                "p_eq_1_r_eq_1": "no positive gap",
                "p_eq_1_q_eq_1": "2(2r+b+1)/(r-1)",
                "p_eq_1_q_gt_1": "(q+1)(2r+q+b)/(q(r-1))",
                "convention": "q=min(side weights)<=b; p is the common low-direction role and r its opposite",
            },
            "atomic_target": "O/T >= 4n/[n^2-(n mod 2)] for every n>=6",
            "formula_weight_range": "all positive four-role vectors through n=60",
            "oriented_formula_rows_checked": formula_checked,
            "independently_formulated_exact_unit_gap_lps_through_n20": independent_lp_checked,
            "independent_lp_infeasible_equal_unit_row_cases": impossible_lp_rows,
            "rows": formula_rows,
            "target_equalities": [
                {
                    "n": n,
                    "weights": list(weights),
                    "orientation": orientation,
                    "unit_gap_cost": str(cost),
                }
                for n, weights, orientation, cost in equalities
            ],
        },
        "canonical_six_player_equality_expansion": canonical_equality_expansion(),
        "independent_exact_staged_lp_controls": controls(),
        "bounded_grid": {
            "atomic_weight_range": "5..20",
            "endowment_coordinates": "0..3",
            "widths": "1..4",
            "cases_checked": checked,
            "rows": grid_rows,
        },
        "scope": (
            "the selector, diagonal exclusion, adjacent gap-cost formulas, and atomic "
            "inequality are human theorems; the formula census and bounded endowment "
            "grid are regression/falsification evidence rather than the proof"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

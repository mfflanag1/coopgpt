#!/usr/bin/env python3
"""Classify the two forced blocker packets in the localized ``(4,2,0)`` case.

After fixing the Lmin-bottom anchor ``a=0`` and the Lmax-top anchor ``b=1``,
the two C1 directions ``-e_1+e_5`` and ``-e_1+e_4`` are automatically
lex-improving at Lmin.  Their opposite-selection blockers must have the form

    {1,4} union A,    {1,5} union B,       A,B subset {0,2,3}.

This script enumerates all 64 labelled pairs, quotients the feasible pairs by
the residual swaps ``2<->3`` and ``4<->5``, and finds a subset-minimal menu of
the other seventeen localized implications closing each representative.

The output is an explanatory finite classification.  It is not independent
proof evidence for the parent anchor-localized formula.
"""
from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path

import z3

from audit_strict_exchange_p4_anchor_core import selected_implications, source_row


REMAINDER = (0, 2, 3)
FORCED_C1_INDICES = (0, 1)


def subsets(items):
    return [
        tuple(choice)
        for size in range(len(items) + 1)
        for choice in combinations(items, size)
    ]


def point_sum(point, players):
    if not players:
        return z3.RealVal(0)
    return z3.Sum(*(point[index] for index in players))


def packet_constraints(x, z, q1, first, second):
    """Return the opposite and q1 comparisons for one concrete blocker pair."""
    coalitions = ((1, 4, *first), (1, 5, *second))
    rows = []
    for coalition in coalitions:
        rows.extend(
            (
                point_sum(z, coalition) >= point_sum(x, coalition),
                point_sum(q1, coalition) >= point_sum(x, coalition),
            )
        )
    return rows


def verdict(assertions, timeout_ms):
    solver = z3.Solver()
    solver.set(timeout=timeout_ms)
    solver.add(*assertions)
    return solver.check()


def swap_remainder(coalition):
    return tuple(
        sorted(3 if player == 2 else 2 if player == 3 else player for player in coalition)
    )


def pair_images(pair):
    """Residual S2 x S2 images; the M-swap exchanges the two blocker roles."""
    first, second = pair
    p_swapped = (swap_remainder(first), swap_remainder(second))
    return (pair, p_swapped, (second, first), (p_swapped[1], p_swapped[0]))


def canonical_pair(pair):
    return min(pair_images(pair))


def subset_minimal_core(common, implications, timeout_ms):
    active = list(range(len(implications)))
    if verdict([*common, *implications], timeout_ms) != z3.unsat:
        return None
    changed = True
    while changed:
        changed = False
        for index in tuple(active):
            trial = [item for item in active if item != index]
            status = verdict(
                [*common, *(implications[item] for item in trial)], timeout_ms
            )
            if status == z3.unsat:
                active = trial
                changed = True
            elif status != z3.sat:
                raise RuntimeError(f"core minimization returned {status}")
    return active


def class8_hand_checks(timeout_ms):
    """Check the reduced inequalities used in the all-human class-8 lemma."""
    x = [z3.Real(f"packet_hand_x_{index}") for index in range(6)]
    z = [z3.Real(f"packet_hand_z_{index}") for index in range(6)]
    distance = point_sum(x, (0, 1, 2, 3)) - point_sum(z, (0, 1, 2, 3))
    first = (0, 1, 2, 4)
    second = (0, 1, 2, 5)
    activation_premises = [
        point_sum(z, range(6)) == 1,
        z[0] >= 0,
        z[2] >= 0,
        z[3] >= 0,
        z[1] >= z[4],
        point_sum(z, first) >= point_sum(x, first),
        point_sum(z, second) >= point_sum(x, second),
        x[3] <= x[4],
        x[3] <= x[5],
        distance > z3.RealVal(1) / 3,
    ]
    activation_status = verdict(activation_premises, timeout_ms)
    if activation_status != z3.unsat:
        raise AssertionError(f"class-8 activation hand lemma is {activation_status}")

    d = [z3.Real(f"packet_hand_d_{index}") for index in range(6)]
    blocker_premises = [
        z3.Sum(*d) == 0,
        *(d[index] > 0 for index in (0, 1, 2, 3)),
        *(d[index] < 0 for index in (4, 5)),
        point_sum(d, first) <= 0,
        point_sum(d, second) <= 0,
    ]
    direction = (0, -1, 0, -1, 1, 1)
    eligible = []
    for mask in range(1, (1 << 6) - 1):
        coalition = tuple(index for index in range(6) if mask & (1 << index))
        if sum(direction[index] for index in coalition) >= 0:
            continue
        status = verdict(
            [*blocker_premises, point_sum(d, coalition) <= 0], timeout_ms
        )
        if status != z3.unsat:
            raise AssertionError(f"class-8 blocker {coalition} is {status}")
        eligible.append({"coalition": list(coalition), "opposite_comparison": "unsat"})
    if len(eligible) != 20:
        raise AssertionError(f"expected 20 class-8 blocker coalitions, got {len(eligible)}")
    return {
        "packet_class": 8,
        "packet": {"first_optional_players": [0, 2], "second_optional_players": [0, 2]},
        "direction": list(direction),
        "side": "min",
        "negated_lex_activation_verdict": "unsat",
        "activation_uses_q1": False,
        "eligible_negative_cut_count": len(eligible),
        "eligible_negative_cuts": eligible,
        "every_opposite_blocker_comparison_verdict": "unsat",
        "blocker_exclusion_uses_q1": False,
    }


def class3_hand_checks(timeout_ms):
    """Check the two-exchange relay used in the all-human class-3 lemma."""
    x = [z3.Real(f"packet_class3_x_{index}") for index in range(6)]
    z = [z3.Real(f"packet_class3_z_{index}") for index in range(6)]
    q1 = [z3.Real(f"packet_class3_q_{index}") for index in range(6)]
    d = [x[index] - z[index] for index in range(6)]
    common = [
        point_sum(x, range(6)) == 1,
        point_sum(z, range(6)) == 1,
        point_sum(q1, range(6)) == 1,
        q1[1] == 0,
        *(value >= 0 for value in (*x, *z, *q1)),
        *(d[index] > 0 for index in (0, 1, 2, 3)),
        *(d[index] < 0 for index in (4, 5)),
        *(x[0] <= x[index] for index in range(1, 6)),
        *(z[1] >= z[index] for index in (0, 2, 3, 4, 5)),
        point_sum(d, (0, 1, 2, 3)) > z3.RealVal(1) / 3,
        *packet_constraints(x, z, q1, (), (0, 2)),
    ]

    first_direction = (0, -1, 0, -1, 1, 1)
    second_direction = (0, 0, -1, -1, 1, 1)
    first_activation_failure = z3.Or(
        x[1] <= x[4], x[1] <= x[5], x[3] <= x[4], x[3] <= x[5]
    )
    if verdict([*common, first_activation_failure], timeout_ms) != z3.unsat:
        raise AssertionError("class-3 first exchange activation did not close")

    def eligible(direction):
        rows = []
        for mask in range(1, (1 << 6) - 1):
            coalition = tuple(index for index in range(6) if mask & (1 << index))
            if sum(direction[index] for index in coalition) < 0:
                rows.append(coalition)
        return rows

    def comparisons(coalition):
        return [
            point_sum(z, coalition) >= point_sum(x, coalition),
            point_sum(q1, coalition) >= point_sum(x, coalition),
        ]

    first_feasible = []
    for coalition in eligible(first_direction):
        status = verdict([*common, *comparisons(coalition)], timeout_ms)
        if status == z3.sat:
            first_feasible.append(coalition)
        elif status != z3.unsat:
            raise RuntimeError(f"class-3 first blocker {coalition} returned {status}")
    expected_first = [(1, 3, 5), (0, 1, 3, 5)]
    if first_feasible != expected_first:
        raise AssertionError(f"unexpected class-3 first blockers: {first_feasible}")

    second_activation_failure = z3.Or(
        x[2] <= x[4], x[2] <= x[5], x[3] <= x[4], x[3] <= x[5]
    )
    relay_rows = []
    for coalition in first_feasible:
        status = verdict(
            [*common, *comparisons(coalition), second_activation_failure], timeout_ms
        )
        if status != z3.unsat:
            raise AssertionError(f"class-3 relay after {coalition} is {status}")
        relay_rows.append(
            {"first_blocker": list(coalition), "negated_second_activation": "unsat"}
        )

    second_feasible = []
    for coalition in eligible(second_direction):
        status = verdict([*common, *comparisons(coalition)], timeout_ms)
        if status == z3.sat:
            second_feasible.append(coalition)
        elif status != z3.unsat:
            raise RuntimeError(f"class-3 second blocker {coalition} returned {status}")
    expected_second = [(2, 3, 5), (0, 2, 3, 5)]
    if second_feasible != expected_second:
        raise AssertionError(f"unexpected class-3 second blockers: {second_feasible}")

    pair_rows = []
    for first in first_feasible:
        for second in second_feasible:
            status = verdict(
                [*common, *comparisons(first), *comparisons(second)], timeout_ms
            )
            if status != z3.unsat:
                raise AssertionError(f"class-3 blocker pair {(first, second)} is {status}")
            pair_rows.append(
                {
                    "first_blocker": list(first),
                    "second_blocker": list(second),
                    "joint_verdict": "unsat",
                }
            )
    return {
        "packet_class": 3,
        "packet": {"first_optional_players": [], "second_optional_players": [0, 2]},
        "first_direction": list(first_direction),
        "negated_first_activation_verdict": "unsat",
        "first_eligible_negative_cut_count": len(eligible(first_direction)),
        "first_feasible_blockers": [list(coalition) for coalition in first_feasible],
        "relay_checks": relay_rows,
        "second_direction": list(second_direction),
        "second_eligible_negative_cut_count": len(eligible(second_direction)),
        "second_feasible_blockers": [list(coalition) for coalition in second_feasible],
        "joint_blocker_pairs": pair_rows,
        "all_four_joint_blocker_pairs_verdict": "unsat",
    }


def class11_relay_reduction_checks(timeout_ms):
    """Restate the class-11 relay and check its two displayed hand identities.

    This is deliberately not labelled a complete hand proof: the exact blocker
    lists are still finite SMT classifications.  The two algebraic identities
    checked below isolate the human part that no longer depends on those lists.
    """
    x = [z3.Real(f"packet_class11_x_{index}") for index in range(6)]
    z = [z3.Real(f"packet_class11_z_{index}") for index in range(6)]
    q1 = [z3.Real(f"packet_class11_q_{index}") for index in range(6)]
    d = [x[index] - z[index] for index in range(6)]
    distance = point_sum(d, (0, 1, 2, 3))
    p4 = (1, 2, 4)
    p5 = (1, 2, 3, 5)
    common = [
        point_sum(x, range(6)) == 1,
        point_sum(z, range(6)) == 1,
        point_sum(q1, range(6)) == 1,
        q1[1] == 0,
        *(value >= 0 for value in (*x, *z, *q1)),
        *(d[index] > 0 for index in (0, 1, 2, 3)),
        *(d[index] < 0 for index in (4, 5)),
        *(x[0] <= x[index] for index in range(1, 6)),
        *(z[1] >= z[index] for index in (0, 2, 3, 4, 5)),
        distance > z3.RealVal(1) / 3,
        *packet_constraints(x, z, q1, (2,), (2, 3)),
    ]

    # The first Lmax exchange is activated by z_1>z_2,z_3.  The final
    # Lmin exchange is activated by x_1>x_2.  Both negations contradict the
    # displayed packet inequalities and D>1/3.
    first_activation_premises = [
        point_sum(x, range(6)) == 1,
        point_sum(z, range(6)) == 1,
        *(z[index] >= 0 for index in range(6)),
        *(z[1] >= z[index] for index in (0, 2, 3, 4, 5)),
        x[0] <= x[5],
        distance > z3.RealVal(1) / 3,
        point_sum(z, p4) >= point_sum(x, p4),
        point_sum(z, p5) >= point_sum(x, p5),
    ]
    if verdict(
        [*first_activation_premises, z3.Or(z[1] <= z[2], z[1] <= z[3])],
        timeout_ms,
    ) != z3.unsat:
        raise AssertionError("class-11 first Lmax activation did not close")
    if verdict([*common, x[1] <= x[2]], timeout_ms) != z3.unsat:
        raise AssertionError("class-11 final Lmin activation did not close")

    # Check the exact weighted identity printed in the paper note for the
    # implication x_1<=x_2 => D<=1/3.  Every parenthesized term is <=0 under
    # that assumption; the final term is the efficiency equality for z.
    activation_identity = (
        z3.RealVal(1) / 3 * (-x[4])
        + z3.RealVal(4) / 3 * (-z[0])
        + z3.RealVal(1) / 3 * (-z[3])
        + z3.RealVal(2) / 3 * (z[1] - x[1])
        + (x[0] - x[5])
        + z3.RealVal(2) / 3 * (z[5] - z[1])
        + z3.RealVal(1) / 3 * (point_sum(x, p4) - point_sum(z, p4))
        + (point_sum(x, p5) - point_sum(z, p5))
        + z3.RealVal(1) / 3 * (x[1] - x[2])
        + z3.RealVal(1) / 3 * (point_sum(z, range(6)) - 1)
    )
    activation_residual = z3.simplify(
        activation_identity - (distance - z3.RealVal(1) / 3)
    )
    if not z3.eq(activation_residual, z3.RealVal(0)):
        raise AssertionError(
            f"class-11 x-order weighted identity changed: {activation_residual}"
        )

    def eligible(direction):
        return [
            tuple(index for index in range(6) if mask & (1 << index))
            for mask in range(1, (1 << 6) - 1)
            if sum(direction[index] for index in range(6) if mask & (1 << index)) < 0
        ]

    def comparisons(coalition, side):
        if side == "max":
            return [
                point_sum(x, coalition) >= point_sum(z, coalition),
                point_sum(q1, coalition) >= point_sum(z, coalition),
            ]
        return [
            point_sum(z, coalition) >= point_sum(x, coalition),
            point_sum(q1, coalition) >= point_sum(x, coalition),
        ]

    def feasible_blockers(direction, side, premises):
        rows = []
        for coalition in eligible(direction):
            status = verdict([*common, *premises, *comparisons(coalition, side)], timeout_ms)
            if status == z3.sat:
                rows.append(coalition)
            elif status != z3.unsat:
                raise RuntimeError(
                    f"class-11 {side} blocker {coalition} returned {status}"
                )
        return rows

    first_direction = (0, -1, 1, 1, 0, -1)
    second_direction = (0, -1, 1, 0, 0, 0)
    first_feasible = feasible_blockers(first_direction, "max", [])
    expected_first = [(0, 1, 2, 5)]
    if first_feasible != expected_first:
        raise AssertionError(f"unexpected class-11 first blockers: {first_feasible}")

    first_rows = comparisons(expected_first[0], "max")
    second_feasible = feasible_blockers(second_direction, "max", first_rows)
    expected_second = [(0, 1, 3)]
    if second_feasible != expected_second:
        raise AssertionError(f"unexpected class-11 second blockers: {second_feasible}")

    second_rows = comparisons(expected_second[0], "max")
    terminal_feasible = feasible_blockers(
        second_direction, "min", [*first_rows, *second_rows]
    )
    if terminal_feasible:
        raise AssertionError(f"unexpected class-11 terminal blockers: {terminal_feasible}")

    # One otherwise awkward first-stage exclusion, C={0,1}, has a compact
    # checkable weighted identity.  This records the exact algebra rather than
    # treating an UNSAT core as proof evidence.
    c01 = (0, 1)
    c01_identity = (
        z3.RealVal(4) / 3 * (-z[0])
        + z3.RealVal(1) / 3 * (-z[2])
        + z3.RealVal(1) / 3 * (-z[3])
        + z3.RealVal(1) / 3 * (-q1[4])
        + (x[0] - x[5])
        + z3.RealVal(2) / 3 * (z[5] - z[1])
        + z3.RealVal(2) / 3 * (point_sum(x, p5) - point_sum(z, p5))
        + z3.RealVal(1) / 3 * (point_sum(x, p5) - point_sum(q1, p5))
        + z3.RealVal(1) / 3 * (point_sum(z, c01) - point_sum(q1, c01))
        + z3.RealVal(1) / 3 * (point_sum(q1, range(6)) - 1)
        + z3.RealVal(1) / 3 * q1[1]
    )
    c01_residual = z3.simplify(c01_identity - (distance - z3.RealVal(1) / 3))
    if not z3.eq(c01_residual, z3.RealVal(0)):
        raise AssertionError(
            f"class-11 C={{0,1}} weighted identity changed: {c01_residual}"
        )

    return {
        "packet_class": 11,
        "packet": {
            "first_optional_players": [2],
            "second_optional_players": [2, 3],
        },
        "human_activated_directions": [list(first_direction), list(second_direction)],
        "negated_first_lmax_activation_verdict": "unsat",
        "negated_final_lmin_activation_verdict": "unsat",
        "x_order_weighted_identity": "checked",
        "first_eligible_negative_cut_count": len(eligible(first_direction)),
        "first_feasible_blockers": [list(item) for item in first_feasible],
        "c01_blocker_weighted_identity": "checked",
        "second_eligible_negative_cut_count": len(eligible(second_direction)),
        "second_feasible_blockers": [list(item) for item in second_feasible],
        "terminal_feasible_blockers": [],
        "complete_forced_relay": True,
        "complete_hand_proof": False,
        "remaining_human_task": "replace the other finite blocker exclusions by structural inequalities",
    }


def class4_star_reduction_checks(timeout_ms):
    """Independently restate the partially humanized class-4 relay star."""
    x = [z3.Real(f"packet_class4_x_{index}") for index in range(6)]
    z = [z3.Real(f"packet_class4_z_{index}") for index in range(6)]
    q1 = [z3.Real(f"packet_class4_q_{index}") for index in range(6)]
    d = [x[index] - z[index] for index in range(6)]
    distance = point_sum(d, (0, 1, 2, 3))
    common = [
        point_sum(x, range(6)) == 1,
        point_sum(z, range(6)) == 1,
        point_sum(q1, range(6)) == 1,
        q1[1] == 0,
        *(value >= 0 for value in (*x, *z, *q1)),
        *(d[index] > 0 for index in (0, 1, 2, 3)),
        *(d[index] < 0 for index in (4, 5)),
        *(x[0] <= x[index] for index in range(1, 6)),
        *(z[1] >= z[index] for index in (0, 2, 3, 4, 5)),
        distance > z3.RealVal(1) / 3,
        *packet_constraints(x, z, q1, (), (2,)),
    ]

    def eligible(direction):
        return [
            tuple(index for index in range(6) if mask & (1 << index))
            for mask in range(1, (1 << 6) - 1)
            if sum(direction[index] for index in range(6) if mask & (1 << index)) < 0
        ]

    def comparisons(coalition, side, sources=("opposite", "q1")):
        rows = []
        if side == "max":
            if "opposite" in sources:
                rows.append(point_sum(x, coalition) >= point_sum(z, coalition))
            if "q1" in sources:
                rows.append(point_sum(q1, coalition) >= point_sum(z, coalition))
        else:
            if "opposite" in sources:
                rows.append(point_sum(z, coalition) >= point_sum(x, coalition))
            if "q1" in sources:
                rows.append(point_sum(q1, coalition) >= point_sum(x, coalition))
        return rows

    def feasible(direction, side, premises=(), sources=("opposite", "q1")):
        rows = []
        for coalition in eligible(direction):
            status = verdict(
                [*common, *premises, *comparisons(coalition, side, sources)],
                timeout_ms,
            )
            if status == z3.sat:
                rows.append(coalition)
            elif status != z3.unsat:
                raise RuntimeError(
                    f"class-4 {side} blocker {coalition} returned {status}"
                )
        return rows

    root_direction = (0, -1, 0, -1, 1, 1)
    root_activation_failure = z3.Or(
        *(x[p] <= x[m] for p in (1, 3) for m in (4, 5))
    )
    if verdict([*common, root_activation_failure], timeout_ms) != z3.unsat:
        raise AssertionError("class-4 root Lmin activation did not close")

    opposite_candidates = feasible(
        root_direction, "min", sources=("opposite",)
    )
    expected_opposite = [
        (1, 3, 4),
        (1, 2, 3, 4),
        (1, 3, 5),
        (0, 1, 3, 5),
        (1, 2, 3, 5),
    ]
    if opposite_candidates != expected_opposite:
        raise AssertionError(
            f"unexpected class-4 opposite candidates: {opposite_candidates}"
        )
    root_blockers = feasible(root_direction, "min")
    expected_root = [(1, 2, 3, 4), (1, 3, 5), (0, 1, 3, 5)]
    if root_blockers != expected_root:
        raise AssertionError(f"unexpected class-4 root blockers: {root_blockers}")

    max_direction = (0, -1, 1, 0, 0, 0)
    min_direction = (0, 0, -1, -1, 1, 1)
    branch_rows = []
    for blocker in root_blockers:
        blocker_rows = comparisons(blocker, "min")
        if blocker == expected_root[0]:
            activation_failure = z[1] <= z[2]
            direction = max_direction
            side = "max"
            terminal_sources = ("q1",)
        else:
            activation_failure = z3.Or(
                *(x[p] <= x[m] for p in (2, 3) for m in (4, 5))
            )
            direction = min_direction
            side = "min"
            terminal_sources = ("opposite",)
        if verdict([*common, *blocker_rows, activation_failure], timeout_ms) != z3.unsat:
            raise AssertionError(f"class-4 activation after {blocker} did not close")
        source_feasible = feasible(
            direction, side, blocker_rows, sources=terminal_sources
        )
        if source_feasible:
            raise AssertionError(
                f"class-4 terminal source blockers after {blocker}: {source_feasible}"
            )
        terminal_feasible = feasible(direction, side, blocker_rows)
        if terminal_feasible:
            raise AssertionError(
                f"class-4 terminal full blockers after {blocker}: {terminal_feasible}"
            )
        branch_rows.append(
            {
                "root_blocker": list(blocker),
                "forced_direction": list(direction),
                "side": side,
                "negated_activation_verdict": "unsat",
                "terminal_exclusion_source": terminal_sources[0],
                "terminal_source_feasible_blockers": [],
                "terminal_full_feasible_blockers": [],
            }
        )

    return {
        "packet_class": 4,
        "packet": {
            "first_optional_players": [],
            "second_optional_players": [2],
        },
        "root_direction": list(root_direction),
        "negated_root_activation_verdict": "unsat",
        "root_eligible_negative_cut_count": len(eligible(root_direction)),
        "root_opposite_candidates": [list(item) for item in opposite_candidates],
        "root_feasible_blockers": [list(item) for item in root_blockers],
        "branches": branch_rows,
        "complete_forced_relay": True,
        "complete_hand_proof": True,
        "terminal_hand_certificate_count": 20,
        "terminal_hand_certificate_scope": (
            "sixteen q1-complement identities and four opposite-base-cut identities"
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout-ms", type=int, default=300_000)
    args = parser.parse_args()

    base, canonical, implications, metadata = selected_implications(source_row())
    common_base = [*base, *canonical]
    x = [z3.Real(f"equality_exchange_x_{index}") for index in range(6)]
    z = [z3.Real(f"equality_exchange_z_{index}") for index in range(6)]
    q1 = [z3.Real(f"equality_exchange_q_1_{index}") for index in range(6)]

    forced_rows = []
    for index in FORCED_C1_INDICES:
        antecedent = implications[index].children()[0]
        status = verdict([*common_base, z3.Not(antecedent)], args.timeout_ms)
        if status != z3.unsat:
            raise AssertionError(f"C1 antecedent {index} was not forced: {status}")
        forced_rows.append(
            {
                "direction_index": index,
                "direction": metadata[index]["direction"],
                "negated_antecedent_verdict": "unsat",
            }
        )

    feasible_pairs = []
    infeasible_pairs = []
    for first in subsets(REMAINDER):
        for second in subsets(REMAINDER):
            pair = (first, second)
            packet = packet_constraints(x, z, q1, first, second)
            status = verdict([*common_base, *packet], args.timeout_ms)
            if status == z3.sat:
                feasible_pairs.append(pair)
            elif status == z3.unsat:
                infeasible_pairs.append(pair)
            else:
                raise RuntimeError(f"packet {pair} returned {status}")

    feasible_set = set(feasible_pairs)
    representatives = sorted({canonical_pair(pair) for pair in feasible_pairs})
    remaining_implications = implications[2:]
    rows = []
    covered = set()
    for class_index, pair in enumerate(representatives, start=1):
        images = sorted(set(pair_images(pair)))
        if not all(image in feasible_set for image in images):
            raise AssertionError("feasibility was not invariant under residual symmetry")
        covered.update(images)
        first, second = pair
        packet = packet_constraints(x, z, q1, first, second)
        common = [*common_base, *packet]
        full_status = verdict([*common, *remaining_implications], args.timeout_ms)
        if full_status != z3.unsat:
            raise AssertionError(f"packet class {class_index} remained {full_status}")
        core = subset_minimal_core(common, remaining_implications, args.timeout_ms)
        if core is None:
            raise AssertionError(f"packet class {class_index} has no closing core")

        ablations = []
        for local_index in core:
            trial = [item for item in core if item != local_index]
            status = verdict(
                [*common, *(remaining_implications[item] for item in trial)],
                args.timeout_ms,
            )
            if status != z3.sat:
                raise AssertionError(
                    f"packet class {class_index} core ablation {local_index} is {status}"
                )
            ablations.append({"direction_index": local_index + 2, "verdict": "sat"})

        selected = []
        for local_index in core:
            global_index = local_index + 2
            item = metadata[global_index]
            selected.append(
                {
                    "direction_index": global_index,
                    "side": item["side"],
                    "direction": item["direction"],
                    "parent_schema": item["parent_schema"],
                    "residual_orbit": item["residual_orbit"],
                }
            )
        rows.append(
            {
                "class": class_index,
                "first_optional_players": list(first),
                "second_optional_players": list(second),
                "raw_orbit_size": len(images),
                "base_with_packet_verdict": "sat",
                "all_remaining_implications_verdict": "unsat",
                "subset_minimal_core_size": len(core),
                "subset_minimal_core": selected,
                "single_core_direction_ablations": ablations,
            }
        )

    if covered != feasible_set:
        raise AssertionError("the symmetry representatives do not cover every feasible pair")
    if len(feasible_pairs) + len(infeasible_pairs) != 64:
        raise AssertionError("the packet enumeration is not exhaustive")
    class8 = rows[7]
    if (
        class8["class"] != 8
        or class8["first_optional_players"] != [0, 2]
        or class8["second_optional_players"] != [0, 2]
        or [item["direction_index"] for item in class8["subset_minimal_core"]] != [17]
    ):
        raise AssertionError("the class-8 hand lemma is detached from its packet row")
    class3 = rows[2]
    if (
        class3["class"] != 3
        or class3["first_optional_players"] != []
        or class3["second_optional_players"] != [0, 2]
        or [item["direction_index"] for item in class3["subset_minimal_core"]] != [17, 18]
    ):
        raise AssertionError("the class-3 hand lemma is detached from its packet row")

    payload = {
        "schema": "strict-exchange-p4-packet-classes-v1",
        "status": "PASS",
        "scope": (
            "finite explanation of the anchor-localized p4 proof; packet cases "
            "strengthen the parent relaxation and are not independent proof evidence"
        ),
        "case": "p4_n2_t0",
        "fixed_anchors": {"x_bottom": 0, "z_top": 1},
        "forced_c1_antecedents": forced_rows,
        "optional_player_set": list(REMAINDER),
        "raw_blocker_pair_count": 64,
        "base_feasible_pair_count": len(feasible_pairs),
        "base_infeasible_pair_count": len(infeasible_pairs),
        "residual_symmetry": ["swap 2 and 3", "swap 4 and 5 (exchanges blocker roles)"],
        "feasible_symmetry_class_count": len(rows),
        "feasible_orbit_size_sum": sum(row["raw_orbit_size"] for row in rows),
        "classes": rows,
        "class3_hand_lemma": class3_hand_checks(args.timeout_ms),
        "class4_star_reduction": class4_star_reduction_checks(args.timeout_ms),
        "class8_hand_lemma": class8_hand_checks(args.timeout_ms),
        "class11_relay_reduction": class11_relay_reduction_checks(args.timeout_ms),
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

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
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Audit every class-5 cut layer and find sparse witness over-covers.

The pure difference-cone layer uses exact Fourier--Motzkin elimination.  The
context and target-witness layers import the localized encoder and frozen
relay, so their use maps are integration evidence rather than an independent
human-to-machine proof.  Each rejected cut receives an exact incidence
over-cover suitable for separate rational exactification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

import z3

from audit_strict_exchange_p4_anchor_core import selected_implications, source_row
from audit_strict_exchange_p4_class6_activation_overcovers import sparse_weights
from audit_strict_exchange_p4_packet_classes import packet_constraints
from audit_strict_exchange_p4_relay_trees import alternatives, coalition, verdict
from verify_strict_exchange_p4_class9_hand_certificates import (
    d_form,
    eligible,
    fourier_motzkin_feasible,
)

HERE = Path(__file__).resolve().parent


def difference_rows(path, metadata):
    rows = []
    for index in range(5):
        coefficients = [Fraction() for _ in range(5)]
        coefficients[index] = -1
        rows.append((tuple(coefficients), Fraction(-1)))
    rows.append(((-1, -1, -1, -1, 1), Fraction(-1)))
    # Symmetric class-5 sandwich: d0+d1 <= delta4,delta5 <= d2+d3.
    rows.extend([
        ((1, 1, 0, 0, -1), Fraction()),
        ((0, 0, -1, -1, 1), Fraction()),
    ])
    for direction, cut in path:
        form = d_form(cut)
        rows.append((form if metadata[direction]["side"] == "min"
                     else tuple(-value for value in form), Fraction()))
    return rows


def certificate(stage, direction, cut, q_rows, weights, loads, bound):
    return {
        "stage": stage,
        "direction_index": direction,
        "candidate": list(cut),
        "used_q_comparisons": [
            {
                "source": row["source"],
                "coalition": list(row["coalition"]),
                "reference": row["reference"],
                "weight": weight,
            }
            for row, weight in zip(q_rows, weights, strict=True) if weight
        ],
        "incidence_loads": list(loads),
        "nonanchor_support_bound": bound,
        "allocation_lower_sum_exceeds_bound": True,
    }


def layer_summary(rows):
    return {
        "count": len(rows),
        "support_sizes": dict(sorted(Counter(
            len(row["used_q_comparisons"]) for row in rows).items())),
        "maximum_coefficients": dict(sorted(Counter(
            max(item["weight"] for item in row["used_q_comparisons"])
            for row in rows).items())),
        "bounds": dict(sorted(Counter(
            row["nonanchor_support_bound"] for row in rows).items())),
    }


def digest(rows):
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--details", action="store_true")
    args = parser.parse_args()

    base, canonical, implications, metadata = selected_implications(source_row())
    x = [z3.Real(f"equality_exchange_x_{index}") for index in range(6)]
    z = [z3.Real(f"equality_exchange_z_{index}") for index in range(6)]
    q = [z3.Real(f"equality_exchange_q_1_{index}") for index in range(6)]
    packet = packet_constraints(x, z, q, (0,), (0,))
    alternative_map = {
        direction: {tuple(coalition(item)): item for item in alternatives(implications[direction])}
        for direction in range(len(implications))
    }
    universal = json.loads((HERE / "strict_exchange_p4_universal_order_relays.json").read_text())
    class_row = next(row for row in universal["rows"] if row["class"] == 5)

    stage_count = eligible_count = pure_candidate_count = branch_count = 0
    candidate_sets = Counter()
    context_certificates = []
    target_certificates = []

    def walk(node, order, path):
        nonlocal stage_count, eligible_count, pure_candidate_count, branch_count
        direction = node["direction_index"]
        order_constraint = x[3] <= x[4] if order == "W" else x[3] > x[4]
        allocation_state = [*base[:21], *canonical, packet[0], packet[2], order_constraint]
        full_context_state = [*base, *canonical, packet[0], packet[2], order_constraint]
        q_constraints = [packet[1], packet[3]]
        q_rows = [
            {"source": "P4", "coalition": (0, 1, 4), "reference": "x", "point": x},
            {"source": "P5", "coalition": (0, 1, 5), "reference": "x", "point": x},
        ]
        for depth, (parent, cut) in enumerate(path):
            item = alternative_map[parent][cut]
            comparisons = item.children() if z3.is_and(item) else (item,)
            allocation_state.append(comparisons[0])
            full_context_state.append(comparisons[0])
            q_constraints.append(comparisons[1])
            reference = "z" if metadata[parent]["side"] == "max" else "x"
            q_rows.append({
                "source": f"A{depth}:h{parent}",
                "coalition": cut,
                "reference": reference,
                "point": z if reference == "z" else x,
            })
        stage = order + "".join(
            f"-h{parent}C{''.join(map(str, cut))}" for parent, cut in path
        ) + f"-h{direction}"
        cuts = eligible(tuple(metadata[direction]["direction"]))
        stage_count += 1
        eligible_count += len(cuts)
        pure_candidates = []
        for cut in cuts:
            form = d_form(cut)
            blocker = form if metadata[direction]["side"] == "min" else tuple(-v for v in form)
            if not fourier_motzkin_feasible(
                    [*difference_rows(path, metadata), (blocker, Fraction())], 5):
                continue
            pure_candidates.append(cut)
            pure_candidate_count += 1
            item = alternative_map[direction][cut]
            comparisons = item.children() if z3.is_and(item) else (item,)
            status = verdict([*full_context_state, *q_constraints, comparisons[0]], 300_000)
            if status == z3.unsat:
                weights, loads, bound = sparse_weights(
                    q_rows, [*allocation_state, comparisons[0]])
                context_certificates.append(certificate(
                    stage, direction, cut, q_rows, weights, loads, bound))
                continue
            if status != z3.sat:
                raise RuntimeError(f"context check returned {status} at {stage}:{cut}")
            status = verdict(
                [*full_context_state, *q_constraints, item], 300_000)
            if status == z3.sat:
                branch_count += 1
                continue
            if status != z3.unsat:
                raise RuntimeError(f"target check returned {status} at {stage}:{cut}")
            reference = "z" if metadata[direction]["side"] == "max" else "x"
            target_rows = [*q_rows, {
                "source": f"T:h{direction}",
                "coalition": cut,
                "reference": reference,
                "point": z if reference == "z" else x,
            }]
            weights, loads, bound = sparse_weights(
                target_rows, [*allocation_state, comparisons[0]])
            target_certificates.append(certificate(
                stage, direction, cut, target_rows, weights, loads, bound))
        candidate_sets[tuple(pure_candidates)] += 1
        for branch in node.get("branches", []):
            walk(branch["child"], order,
                 [*path, (direction, tuple(branch["coalition"]))])

    walk(class_row["weak_branch"]["tree"], "W", [])
    walk(class_row["strict_branch"]["tree"], "S", [])
    context_summary = layer_summary(context_certificates)
    target_summary = layer_summary(target_certificates)
    actual = {
        "stage_count": stage_count,
        "eligible_cut_use_count": eligible_count,
        "pure_difference_exclusion_count": eligible_count - pure_candidate_count,
        "pure_difference_candidate_count": pure_candidate_count,
        "distinct_candidate_set_count": len(candidate_sets),
        "context": context_summary,
        "target": target_summary,
        "relay_branch_count": branch_count,
    }
    expected = {
        "stage_count": 90,
        "eligible_cut_use_count": 1736,
        "pure_difference_exclusion_count": 1464,
        "pure_difference_candidate_count": 272,
        "distinct_candidate_set_count": 24,
        "context": {
            "count": 34,
            "support_sizes": {2: 8, 3: 4, 4: 16, 5: 6},
            "maximum_coefficients": {1: 18, 2: 16},
            "bounds": {1: 10, 2: 22, 3: 2},
        },
        "target": {
            "count": 150,
            "support_sizes": {1: 6, 2: 59, 3: 51, 4: 34},
            "maximum_coefficients": {1: 147, 2: 3},
            "bounds": {0: 6, 1: 110, 2: 34},
        },
        "relay_branch_count": 88,
    }
    if actual != expected:
        raise AssertionError(f"class-5 layered census changed: {actual}")
    payload = {
        "schema": "strict-exchange-p4-class5-overcovers-v1",
        "status": "PASS",
        "scope": "encoding-shared class-5 context/target use maps with exact difference-cone and incidence arithmetic; not independent human-to-machine evidence",
        "class": 5,
        "packet": {"first_optional_players": [0], "second_optional_players": [0]},
        **actual,
        "context_certificate_sha256": digest(context_certificates),
        "target_certificate_sha256": digest(target_certificates),
        **({
            "context_certificates": context_certificates,
            "target_certificates": target_certificates,
        } if args.details else {}),
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

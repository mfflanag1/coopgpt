#!/usr/bin/env python3
"""Audit the allocation-context layer in the class-6 cut census.

Exact Fourier--Motzkin elimination first retains the cuts compatible with the
pure payoff-difference cone.  The localized encoder then tests the opposite
comparison together with the already active packet/ancestor q^1 comparisons.
For every cut rejected only at this second layer, the script finds a sparse
incidence over-cover.  This is an encoding-shared integration audit, not
independent evidence for the human-to-machine interface.
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


def difference_rows(path):
    rows = []
    for index in range(5):
        coefficients = [Fraction() for _ in range(5)]
        coefficients[index] = -1
        rows.append((tuple(coefficients), Fraction(-1)))
    rows.append(((-1, -1, -1, -1, 1), Fraction(-1)))
    # Class 6 packet sandwich: d0+d1 <= delta4 <= d3.
    rows.extend([
        ((1, 1, 0, 0, -1), Fraction()),
        ((0, 0, 0, -1, 1), Fraction()),
    ])
    for side, cut in path:
        form = d_form(cut)
        rows.append((form if side == "min" else tuple(-value for value in form),
                     Fraction()))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--details", action="store_true")
    args = parser.parse_args()

    base, canonical, implications, metadata = selected_implications(source_row())
    x = [z3.Real(f"equality_exchange_x_{index}") for index in range(6)]
    z = [z3.Real(f"equality_exchange_z_{index}") for index in range(6)]
    q = [z3.Real(f"equality_exchange_q_1_{index}") for index in range(6)]
    packet = packet_constraints(x, z, q, (0,), (0, 2))
    alternative_map = {
        direction: {tuple(coalition(item)): item for item in alternatives(implications[direction])}
        for direction in range(len(implications))
    }
    universal = json.loads((HERE / "strict_exchange_p4_universal_order_relays.json").read_text())
    class_row = next(row for row in universal["rows"] if row["class"] == 6)

    pure_candidate_count = 0
    context_survivor_count = 0
    certificates = []

    def walk(node, order, path):
        nonlocal pure_candidate_count, context_survivor_count
        direction = node["direction_index"]
        order_constraint = x[3] <= x[4] if order == "W" else x[3] > x[4]
        # Keep the allocation-side lower-bound search independent of the q^1
        # simplex.  The full context test below adds those eight base rows.
        allocation_state = [*base[:21], *canonical, packet[0], packet[2], order_constraint]
        full_context_state = [*base, *canonical, packet[0], packet[2], order_constraint]
        q_constraints = [packet[1], packet[3]]
        q_rows = [
            {"source": "P4", "coalition": (0, 1, 4), "reference": "x", "point": x},
            {"source": "P5", "coalition": (0, 1, 2, 5), "reference": "x", "point": x},
        ]
        difference_path = []
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
            difference_path.append((metadata[parent]["side"], cut))

        stage = order + "".join(
            f"-h{parent}C{''.join(map(str, cut))}" for parent, cut in path
        ) + f"-h{direction}"
        for cut in eligible(tuple(metadata[direction]["direction"])):
            form = d_form(cut)
            blocker = form if metadata[direction]["side"] == "min" else tuple(-v for v in form)
            if not fourier_motzkin_feasible(
                    [*difference_rows(difference_path), (blocker, Fraction())], 5):
                continue
            pure_candidate_count += 1
            item = alternative_map[direction][cut]
            comparisons = item.children() if z3.is_and(item) else (item,)
            state = [*full_context_state, *q_constraints, comparisons[0]]
            status = verdict(state, 300_000)
            if status == z3.sat:
                context_survivor_count += 1
                continue
            if status != z3.unsat:
                raise RuntimeError(f"context check returned {status} at {stage}:{cut}")
            weights, loads, bound = sparse_weights(q_rows, [*allocation_state, comparisons[0]])
            certificates.append({
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
            })
        for branch in node.get("branches", []):
            walk(branch["child"], order,
                 [*path, (direction, tuple(branch["coalition"]))])

    walk(class_row["weak_branch"]["tree"], "W", [])
    walk(class_row["strict_branch"]["tree"], "S", [])
    support_sizes = Counter(len(row["used_q_comparisons"]) for row in certificates)
    maximum_coefficients = Counter(
        max(item["weight"] for item in row["used_q_comparisons"]) for row in certificates
    )
    bounds = Counter(row["nonanchor_support_bound"] for row in certificates)
    actual = {
        "pure_difference_candidate_count": pure_candidate_count,
        "context_exclusion_count": len(certificates),
        "context_survivor_count": context_survivor_count,
        "support_sizes": dict(sorted(support_sizes.items())),
        "maximum_coefficients": dict(sorted(maximum_coefficients.items())),
        "bounds": dict(sorted(bounds.items())),
    }
    expected = {
        "pure_difference_candidate_count": 213,
        "context_exclusion_count": 11,
        "context_survivor_count": 202,
        "support_sizes": {2: 3, 3: 4, 4: 3, 5: 1},
        "maximum_coefficients": {1: 8, 2: 3},
        "bounds": {1: 4, 2: 5, 3: 2},
    }
    if actual != expected:
        raise AssertionError(f"class-6 context census changed: {actual}")
    canonical_bytes = json.dumps(certificates, sort_keys=True, separators=(",", ":")).encode()
    payload = {
        "schema": "strict-exchange-p4-class6-context-overcovers-v1",
        "status": "PASS",
        "scope": "encoding-shared allocation-context audit after an exact difference-cone census; incidence supports are exact but the use map is not independent human-to-machine evidence",
        "class": 6,
        "packet": {"first_optional_players": [0], "second_optional_players": [0, 2]},
        **actual,
        "certificate_sha256": hashlib.sha256(canonical_bytes).hexdigest(),
        **({"certificates": certificates} if args.details else {}),
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

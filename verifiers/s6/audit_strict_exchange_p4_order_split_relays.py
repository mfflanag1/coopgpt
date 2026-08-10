#!/usr/bin/env python3
"""Expose the minimal payoff-order splits closing packet classes 9 and 10.

The unsplit forced-relay audit stalls at the root in both classes.  Class 9
closes after the exhaustive split x3<=x4 / x3>x4.  Class 10 closes on the
second branch of that split directly; the first branch closes after the nested
split x1<=x2 / x1>x2.  These are machine-checked decompositions of the parent
packet relaxations, not hand proofs or independent theorem evidence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import z3

from audit_strict_exchange_p4_anchor_core import selected_implications, source_row
from audit_strict_exchange_p4_packet_classes import packet_constraints
from audit_strict_exchange_p4_relay_trees import relay_tree, tree_summary, verdict


def branch(common, split, core, implications, metadata, timeout_ms):
    status = verdict([*common, split], timeout_ms)
    if status != z3.sat:
        raise AssertionError(f"order branch is not a genuine SAT relaxation: {status}")
    tree = relay_tree([*common, split], core, implications, metadata, timeout_ms)
    summary = tree_summary(tree)
    if summary["open_leaves"]:
        raise AssertionError(f"order branch remained open: {summary}")
    return {"base_with_order_verdict": "sat", "summary": summary, "tree": tree}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout-ms", type=int, default=300_000)
    args = parser.parse_args()

    base, canonical, implications, metadata = selected_implications(source_row())
    x = [z3.Real(f"equality_exchange_x_{index}") for index in range(6)]
    z = [z3.Real(f"equality_exchange_z_{index}") for index in range(6)]
    q1 = [z3.Real(f"equality_exchange_q_1_{index}") for index in range(6)]

    class9_common = [
        *base,
        *canonical,
        *packet_constraints(x, z, q1, (0, 2), (2,)),
    ]
    class9_core = [6, 9, 14, 17]
    class9_branches = {
        "x3<=x4": branch(
            class9_common, x[3] <= x[4], class9_core,
            implications, metadata, args.timeout_ms,
        ),
        "x3>x4": branch(
            class9_common, x[3] > x[4], class9_core,
            implications, metadata, args.timeout_ms,
        ),
    }
    class9_counts = [item["summary"]["closed_leaves"] for item in class9_branches.values()]
    if class9_counts != [2, 3]:
        raise AssertionError(f"class-9 split anatomy changed: {class9_counts}")

    class10_common = [
        *base,
        *canonical,
        *packet_constraints(x, z, q1, (2,), (2,)),
    ]
    class10_core = [9, 12, 14, 17]
    class10_right = branch(
        class10_common, x[3] > x[4], class10_core,
        implications, metadata, args.timeout_ms,
    )
    class10_left_common = [*class10_common, x[3] <= x[4]]
    class10_left = {
        "x1<=x2": branch(
            class10_left_common, x[1] <= x[2], class10_core,
            implications, metadata, args.timeout_ms,
        ),
        "x1>x2": branch(
            class10_left_common, x[1] > x[2], class10_core,
            implications, metadata, args.timeout_ms,
        ),
    }
    class10_counts = [
        class10_right["summary"]["closed_leaves"],
        *(item["summary"]["closed_leaves"] for item in class10_left.values()),
    ]
    if class10_counts != [4, 1, 4]:
        raise AssertionError(f"class-10 split anatomy changed: {class10_counts}")

    payload = {
        "schema": "strict-exchange-p4-order-split-relays-v1",
        "status": "PASS",
        "scope": (
            "machine-checked order-split relay decomposition of packet classes 9 and 10; "
            "not a hand proof and not independent evidence for the parent theorem"
        ),
        "class9": {
            "packet": {"first_optional_players": [0, 2], "second_optional_players": [2]},
            "raw_orbit_size": 4,
            "core_direction_indices": class9_core,
            "order_tree": "split x3<=x4 versus x3>x4",
            "closed_leaf_count": sum(class9_counts),
            "branches": class9_branches,
        },
        "class10": {
            "packet": {"first_optional_players": [2], "second_optional_players": [2]},
            "raw_orbit_size": 2,
            "core_direction_indices": class10_core,
            "order_tree": "split x3<=x4 versus x3>x4; on x3<=x4 split x1<=x2 versus x1>x2",
            "closed_leaf_count": sum(class10_counts),
            "x3>x4": class10_right,
            "x3<=x4": {"nested_branches": class10_left},
        },
        "complete_order_split_classes": [9, 10],
        "complete_order_split_labelled_packet_count": 6,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

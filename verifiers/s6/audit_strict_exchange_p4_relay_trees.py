#!/usr/bin/env python3
"""Expose forced-exchange relay trees inside the localized p4 packet table.

For each exact blocker-packet class, start with its frozen subset-minimal core.
Whenever a remaining direction is forced lex-improving, retain only blocker
alternatives that are SAT with the current branch and recurse after choosing
one.  A leaf closes when a forced direction has no feasible blocker.  A leaf
is left open when no unused core direction is forced.

This is an explanatory decomposition of the parent relaxation, not an
independent proof object and not an assertion that SAT branches are games.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import z3
from z3.z3util import get_vars

from audit_strict_exchange_p4_anchor_core import selected_implications, source_row
from audit_strict_exchange_p4_packet_classes import packet_constraints


HERE = Path(__file__).resolve().parent
HAND_CLASSES = {3, 8}


def verdict(assertions, timeout_ms):
    solver = z3.Solver()
    solver.set(timeout=timeout_ms)
    solver.add(*assertions)
    return solver.check()


def alternatives(implication):
    consequent = implication.children()[1]
    return consequent.children() if z3.is_or(consequent) else (consequent,)


def coalition(alternative):
    comparisons = alternative.children() if z3.is_and(alternative) else (alternative,)
    names = {str(variable) for variable in get_vars(comparisons[0])}
    prefix = "equality_exchange_x_"
    players = sorted(int(name.removeprefix(prefix)) for name in names if name.startswith(prefix))
    if not players:
        raise AssertionError("failed to recover a blocker coalition")
    return players


def feasible_alternatives(common, implication, timeout_ms):
    rows = []
    for index, alternative in enumerate(alternatives(implication)):
        status = verdict([*common, alternative], timeout_ms)
        if status == z3.sat:
            rows.append((index, alternative))
        elif status != z3.unsat:
            raise RuntimeError(f"blocker alternative {index} returned {status}")
    return rows


def relay_tree(common, direction_indices, implications, metadata, timeout_ms, depth=0):
    state_status = verdict(common, timeout_ms)
    if state_status == z3.unsat:
        return {"depth": depth, "status": "closed", "reason": "linear branch"}
    if state_status != z3.sat:
        raise RuntimeError(f"relay state returned {state_status}")

    candidates = []
    for index in direction_indices:
        antecedent = implications[index].children()[0]
        forced_status = verdict([*common, z3.Not(antecedent)], timeout_ms)
        if forced_status == z3.unsat:
            feasible = feasible_alternatives(common, implications[index], timeout_ms)
            candidates.append((len(feasible), index, feasible))
        elif forced_status != z3.sat:
            raise RuntimeError(f"direction {index} activation returned {forced_status}")
    if not candidates:
        return {
            "depth": depth,
            "status": "open",
            "reason": "no unused core direction is forced",
        }

    _, index, feasible = min(candidates, key=lambda item: (item[0], item[1]))
    item = metadata[index]
    node = {
        "depth": depth,
        "status": "branch" if feasible else "closed",
        "direction_index": index,
        "side": item["side"],
        "direction": item["direction"],
        "parent_schema": item["parent_schema"],
        "residual_orbit": item["residual_orbit"],
        "eligible_negative_cut_count": len(alternatives(implications[index])),
        "feasible_blocker_count": len(feasible),
    }
    if not feasible:
        node["reason"] = "forced improving direction has no feasible blocker"
        return node

    remaining = [candidate for candidate in direction_indices if candidate != index]
    node["branches"] = []
    for alternative_index, alternative in feasible:
        node["branches"].append(
            {
                "alternative_index": alternative_index,
                "coalition": coalition(alternative),
                "child": relay_tree(
                    [*common, alternative],
                    remaining,
                    implications,
                    metadata,
                    timeout_ms,
                    depth + 1,
                ),
            }
        )
    return node


def tree_summary(tree):
    if "branches" not in tree:
        return {
            "open_leaves": int(tree["status"] == "open"),
            "closed_leaves": int(tree["status"] == "closed"),
            "maximum_depth": tree["depth"],
        }
    children = [tree_summary(branch["child"]) for branch in tree["branches"]]
    return {
        "open_leaves": sum(child["open_leaves"] for child in children),
        "closed_leaves": sum(child["closed_leaves"] for child in children),
        "maximum_depth": max(child["maximum_depth"] for child in children),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout-ms", type=int, default=300_000)
    args = parser.parse_args()

    base, canonical, implications, metadata = selected_implications(source_row())
    packet_audit = json.loads((HERE / "strict_exchange_p4_packet_classes.json").read_text())
    x = [z3.Real(f"equality_exchange_x_{index}") for index in range(6)]
    z = [z3.Real(f"equality_exchange_z_{index}") for index in range(6)]
    q1 = [z3.Real(f"equality_exchange_q_1_{index}") for index in range(6)]

    rows = []
    for packet in packet_audit["classes"]:
        first = tuple(packet["first_optional_players"])
        second = tuple(packet["second_optional_players"])
        common = [*base, *canonical, *packet_constraints(x, z, q1, first, second)]
        core = [item["direction_index"] for item in packet["subset_minimal_core"]]
        tree = relay_tree(common, core, implications, metadata, args.timeout_ms)
        summary = tree_summary(tree)
        rows.append(
            {
                "class": packet["class"],
                "raw_orbit_size": packet["raw_orbit_size"],
                "packet": {
                    "first_optional_players": list(first),
                    "second_optional_players": list(second),
                },
                "core_direction_indices": core,
                "complete_forced_relay": summary["open_leaves"] == 0,
                "separate_hand_proof": packet["class"] in HAND_CLASSES,
                "summary": summary,
                "tree": tree,
            }
        )

    complete = [row for row in rows if row["complete_forced_relay"]]
    expected_complete = [3, 4, 7, 8, 11]
    if [row["class"] for row in complete] != expected_complete:
        raise AssertionError("the complete forced-relay class list changed")
    if sum(row["raw_orbit_size"] for row in complete) != 18:
        raise AssertionError("the complete relay trees no longer cover 18 labelled packets")

    payload = {
        "schema": "strict-exchange-p4-relay-trees-v1",
        "status": "PASS",
        "scope": (
            "forced-exchange decomposition of the packet cores; closed trees are "
            "machine-checked explanations, SAT/open leaves are not games"
        ),
        "packet_class_count": len(rows),
        "complete_forced_relay_classes": expected_complete,
        "complete_forced_relay_class_count": len(complete),
        "complete_forced_relay_labelled_packet_count": sum(
            row["raw_orbit_size"] for row in complete
        ),
        "separately_humanized_classes": sorted(HAND_CLASSES),
        "rows": rows,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

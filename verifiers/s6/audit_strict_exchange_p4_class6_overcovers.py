#!/usr/bin/env python3
"""Find sparse zero-anchor over-covers for every class-6 witness filter.

This audit imports the localized encoder and frozen universal relay.  It is a
machine-checked decomposition and humanization roadmap, not independent proof
evidence for the theorem or its human-to-machine interface.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

import z3

from audit_strict_exchange_p4_anchor_core import selected_implications, source_row
from audit_strict_exchange_p4_packet_classes import packet_constraints
from audit_strict_exchange_p4_relay_trees import alternatives, coalition, verdict

HERE = Path(__file__).resolve().parent


def point_sum(point, coalition):
    return z3.Sum(*(point[i] for i in coalition))


def incidence_loads(rows, weights):
    return tuple(
        sum(
            weight
            for row, weight in zip(rows, weights, strict=True)
            if player in row["coalition"]
        )
        for player in range(6)
    )


def sparse_weights(rows, allocation_state):
    solver = z3.Solver()
    solver.set(timeout=300_000)
    solver.add(*allocation_state)

    def closes(weights):
        loads = incidence_loads(rows, weights)
        bound = max(loads[player] for player in range(6) if player != 1)
        rhs = z3.Sum(
            *(
                weight * point_sum(row["point"], row["coalition"])
                for row, weight in zip(rows, weights, strict=True)
                if weight
            )
        )
        solver.push()
        solver.add(rhs <= bound)
        status = solver.check()
        solver.pop()
        if status == z3.unknown:
            raise RuntimeError("allocation-side over-cover check returned unknown")
        return status == z3.unsat, loads, bound

    # Prefer unit-weight covers, then allow multiplicity two.  Within each
    # lane minimize support and total weight deterministically.
    for support in range(1, len(rows) + 1):
        for indices in itertools.combinations(range(len(rows)), support):
            weights = tuple(int(index in indices) for index in range(len(rows)))
            closed, loads, bound = closes(weights)
            if closed:
                return weights, loads, bound
    weighted = []
    for weights in itertools.product((0, 1, 2), repeat=len(rows)):
        if not any(weights) or max(weights) < 2:
            continue
        weighted.append((sum(bool(weight) for weight in weights), sum(weights), weights))
    for _, __, weights in sorted(weighted):
        closed, loads, bound = closes(weights)
        if closed:
            return weights, loads, bound
    raise AssertionError("no coefficient-at-most-two over-cover found")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--details", action="store_true")
    args = parser.parse_args()

    base, canonical, implications, metadata = selected_implications(source_row())
    x = [z3.Real(f"equality_exchange_x_{i}") for i in range(6)]
    z = [z3.Real(f"equality_exchange_z_{i}") for i in range(6)]
    q = [z3.Real(f"equality_exchange_q_1_{i}") for i in range(6)]
    packet = packet_constraints(x, z, q, (0,), (0, 2))
    packet_opposite = [packet[0], packet[2]]
    common_allocation = [*base[:21], *canonical, *packet_opposite]
    alternative_map = {
        direction: {tuple(coalition(item)): item for item in alternatives(implications[direction])}
        for direction in range(len(implications))
    }

    universal = json.loads((HERE / "strict_exchange_p4_universal_order_relays.json").read_text())
    class_row = next(row for row in universal["rows"] if row["class"] == 6)
    stages = []

    def walk(node, order, path):
        if "direction_index" in node:
            stages.append((order, node["direction_index"], tuple(path)))
        for branch in node.get("branches", []):
            walk(
                branch["child"],
                order,
                [*path, (node["direction_index"], tuple(branch["coalition"]))],
            )

    walk(class_row["weak_branch"]["tree"], "W", [])
    walk(class_row["strict_branch"]["tree"], "S", [])
    if len(stages) != 49:
        raise AssertionError(f"class-6 stage count changed: {len(stages)}")

    certificates = []
    opposite_candidate_count = 0
    full_survivor_count = 0
    for order, direction, path in stages:
        order_constraint = x[3] <= x[4] if order == "W" else x[3] > x[4]
        ancestors = [alternative_map[parent][cut] for parent, cut in path]
        allocation_state = [*common_allocation, order_constraint]
        for ancestor in ancestors:
            allocation_state.append(ancestor.children()[0])

        for item in alternatives(implications[direction]):
            comparisons = item.children() if z3.is_and(item) else (item,)
            full_state = [*base, *canonical, *packet, order_constraint, *ancestors]
            if verdict([*full_state, comparisons[0]], 300_000) != z3.sat:
                continue
            opposite_candidate_count += 1
            if verdict([*full_state, item], 300_000) == z3.sat:
                full_survivor_count += 1
                continue

            candidate = tuple(coalition(item))
            q_rows = [
                {"source": "P4", "coalition": (0, 1, 4), "reference": "x", "point": x},
                {"source": "P5", "coalition": (0, 1, 2, 5), "reference": "x", "point": x},
            ]
            for depth, (parent, cut) in enumerate(path):
                reference = "z" if metadata[parent]["side"] == "max" else "x"
                q_rows.append(
                    {
                        "source": f"A{depth}:h{parent}",
                        "coalition": cut,
                        "reference": reference,
                        "point": z if reference == "z" else x,
                    }
                )
            reference = "z" if metadata[direction]["side"] == "max" else "x"
            q_rows.append(
                {
                    "source": f"target:h{direction}",
                    "coalition": candidate,
                    "reference": reference,
                    "point": z if reference == "z" else x,
                }
            )
            weights, loads, bound = sparse_weights(q_rows, [*allocation_state, comparisons[0]])
            used = []
            for row, weight in zip(q_rows, weights, strict=True):
                if weight:
                    used.append(
                        {
                            "source": row["source"],
                            "coalition": list(row["coalition"]),
                            "reference": row["reference"],
                            "weight": weight,
                        }
                    )
            stage_name = order + "".join(
                f"-h{parent}C{''.join(map(str, cut))}" for parent, cut in path
            ) + f"-h{direction}"
            certificates.append(
                {
                    "stage": stage_name,
                    "direction_index": direction,
                    "candidate": list(candidate),
                    "used_q_comparisons": used,
                    "incidence_loads": list(loads),
                    "nonanchor_support_bound": bound,
                    "allocation_lower_sum_exceeds_bound": True,
                }
            )

    support_sizes = Counter(len(row["used_q_comparisons"]) for row in certificates)
    maximum_coefficients = Counter(
        max(item["weight"] for item in row["used_q_comparisons"]) for row in certificates
    )
    bounds = Counter(row["nonanchor_support_bound"] for row in certificates)
    expected = {
        "certificate_count": 155,
        "opposite_candidate_count": 202,
        "full_survivor_count": 47,
        "support_sizes": {1: 12, 2: 82, 3: 27, 4: 30, 5: 4},
        "maximum_coefficients": {1: 150, 2: 5},
        "bounds": {0: 12, 1: 98, 2: 42, 3: 3},
    }
    actual = {
        "certificate_count": len(certificates),
        "opposite_candidate_count": opposite_candidate_count,
        "full_survivor_count": full_survivor_count,
        "support_sizes": dict(sorted(support_sizes.items())),
        "maximum_coefficients": dict(sorted(maximum_coefficients.items())),
        "bounds": dict(sorted(bounds.items())),
    }
    if actual != expected:
        raise AssertionError(f"class-6 over-cover census changed: {actual}")

    certificate_bytes = json.dumps(certificates, sort_keys=True, separators=(",", ":")).encode()
    payload = {
        "schema": "strict-exchange-p4-class6-overcovers-v1",
        "status": "PASS",
        "scope": "encoding-shared exact-LRA audit of all class-6 q1 filters; incidence support is exact but allocation-side UNSAT checks are not independent proof objects",
        "class": 6,
        "packet": {"first_optional_players": [0], "second_optional_players": [0, 2]},
        "stage_count": len(stages),
        **actual,
        "certificate_sha256": hashlib.sha256(certificate_bytes).hexdigest(),
        **({"certificates": certificates} if args.details else {}),
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

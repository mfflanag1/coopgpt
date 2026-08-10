#!/usr/bin/env python3
"""Explore every class-5 relay activation as allocation-infeasible or sparse q.

This audit shares the localized encoder and frozen universal relay.  It
verifies the elementary activation-failure expansions, removes the failures
already contradicted by anchors/order, and finds a zero-anchor incidence
over-cover for every remaining witness-dependent failure.  It is a discovery
and integration audit, not an independent hand proof.
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
from audit_strict_exchange_p4_class6_overcovers import incidence_loads, point_sum
from audit_strict_exchange_p4_packet_classes import packet_constraints
from audit_strict_exchange_p4_relay_trees import alternatives, coalition, verdict

HERE = Path(__file__).resolve().parent


def failure_cases(direction, x, z):
    if direction == 7:
        return ((z[0] >= z[1],), (z[2] >= z[1],))
    if direction == 10:
        return ((z[0] >= z[1],),)
    if direction == 11:
        return ((z[3] >= z[4], z[3] >= z[5]),)
    if direction == 12:
        return ((z[2] >= z[4], z[2] >= z[5]),)
    if direction == 15:
        return ((x[0] >= x[1],),)
    if direction == 16:
        return tuple(
            (left, right)
            for left in (x[1] <= x[4], x[2] <= x[4])
            for right in (x[1] <= x[5], x[2] <= x[5])
        )
    if direction == 17:
        return tuple(
            (left, right)
            for left in (x[3] <= x[4], x[1] <= x[4])
            for right in (x[3] <= x[5], x[1] <= x[5])
        )
    if direction == 18:
        return tuple(
            (left, right)
            for left in (x[2] <= x[4], x[3] <= x[4])
            for right in (x[2] <= x[5], x[3] <= x[5])
        )
    raise AssertionError(f"unexpected class-5 direction {direction}")


def sparse_weights(rows, allocation_state):
    solver = z3.Solver()
    solver.set(timeout=300_000)
    solver.add(*allocation_state)

    def closes(weights):
        loads = incidence_loads(rows, weights)
        bound = max(loads[player] for player in range(6) if player != 1)
        lower_sum = z3.Sum(
            *(
                weight * point_sum(row["point"], row["coalition"])
                for row, weight in zip(rows, weights, strict=True)
                if weight
            )
        )
        solver.push()
        solver.add(lower_sum <= bound)
        status = solver.check()
        solver.pop()
        if status == z3.unknown:
            raise RuntimeError("class-5 activation over-cover returned unknown")
        return status == z3.unsat, loads, bound

    for support in range(1, len(rows) + 1):
        for indices in itertools.combinations(range(len(rows)), support):
            weights = tuple(int(index in indices) for index in range(len(rows)))
            closed, loads, bound = closes(weights)
            if closed:
                return weights, loads, bound
    weighted = []
    for weights in itertools.product((0, 1, 2), repeat=len(rows)):
        if not any(weights) or max(weights) != 2:
            continue
        weighted.append((sum(bool(weight) for weight in weights), sum(weights), weights))
    for _, __, weights in sorted(weighted):
        closed, loads, bound = closes(weights)
        if closed:
            return weights, loads, bound
    raise AssertionError("no coefficient-at-most-two activation over-cover found")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--details", action="store_true")
    args = parser.parse_args()

    base, canonical, implications, metadata = selected_implications(source_row())
    x = [z3.Real(f"equality_exchange_x_{i}") for i in range(6)]
    z = [z3.Real(f"equality_exchange_z_{i}") for i in range(6)]
    q = [z3.Real(f"equality_exchange_q_1_{i}") for i in range(6)]
    packet = packet_constraints(x, z, q, (0,), (0,))
    common_allocation = [*base[:21], *canonical, packet[0], packet[2]]
    alternative_map = {
        direction: {tuple(coalition(item)): item for item in alternatives(implications[direction])}
        for direction in range(len(implications))
    }
    universal = json.loads((HERE / "strict_exchange_p4_universal_order_relays.json").read_text())
    class_row = next(row for row in universal["rows"] if row["class"] == 5)

    stage_count = 0
    total_failure_cases = 0
    structural_failure_cases = 0
    direct_cases = []
    certificates = []

    def walk(node, order, path):
        nonlocal stage_count, total_failure_cases, structural_failure_cases
        stage_count += 1
        direction = node["direction_index"]
        stage = order + "".join(
            f"-h{parent}C{''.join(map(str, cut))}" for parent, cut in path
        ) + f"-h{direction}"
        order_constraint = x[3] <= x[4] if order == "W" else x[3] > x[4]
        allocation_state = [*common_allocation, order_constraint]
        q_rows = [
            {"source": "P4", "coalition": (0, 1, 4), "reference": "x", "point": x},
            {"source": "P5", "coalition": (0, 1, 5), "reference": "x", "point": x},
        ]
        for depth, (parent, cut) in enumerate(path):
            item = alternative_map[parent][cut]
            allocation_state.append(item.children()[0])
            reference = "z" if metadata[parent]["side"] == "max" else "x"
            q_rows.append(
                {
                    "source": f"A{depth}:h{parent}",
                    "coalition": cut,
                    "reference": reference,
                    "point": z if reference == "z" else x,
                }
            )

        cases = failure_cases(direction, x, z)
        total_failure_cases += len(cases)
        failure_dnf = z3.Or(*(z3.And(*case) for case in cases))
        mismatch = failure_dnf != z3.Not(implications[direction].arg(0))
        if verdict([*allocation_state, mismatch], 300_000) != z3.unsat:
            raise AssertionError(f"activation failure expansion changed at {stage}")

        for case_index, failure in enumerate(cases):
            status = verdict([*allocation_state, *failure], 300_000)
            if status == z3.unsat:
                direct_cases.append(
                    {"stage": stage, "direction_index": direction,
                     "failure_case": case_index}
                )
                structural_failure_cases += 1
                continue
            if status != z3.sat:
                raise RuntimeError(f"activation residual returned {status}")
            weights, loads, bound = sparse_weights(q_rows, [*allocation_state, *failure])
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
            certificates.append(
                {
                    "stage": stage,
                    "direction_index": direction,
                    "failure_case": case_index,
                    "used_q_comparisons": used,
                    "incidence_loads": list(loads),
                    "nonanchor_support_bound": bound,
                }
            )
        for branch in node.get("branches", []):
            walk(
                branch["child"],
                order,
                [*path, (direction, tuple(branch["coalition"]))],
            )

    walk(class_row["weak_branch"]["tree"], "W", [])
    walk(class_row["strict_branch"]["tree"], "S", [])

    supports = Counter(len(row["used_q_comparisons"]) for row in certificates)
    coefficients = Counter(
        max(item["weight"] for item in row["used_q_comparisons"]) for row in certificates
    )
    bounds = Counter(row["nonanchor_support_bound"] for row in certificates)
    signatures = Counter(
        (
            tuple(
                (item["source"], item["weight"])
                for item in row["used_q_comparisons"]
            ),
            tuple(row["incidence_loads"]),
            row["nonanchor_support_bound"],
            row["direction_index"],
            row["failure_case"],
        )
        for row in certificates
    )
    actual = {
        "stage_count": stage_count,
        "activation_failure_case_count": total_failure_cases,
        "allocation_infeasible_case_count": structural_failure_cases,
        "witness_overcover_count": len(certificates),
        "overcover_signature_count": len(signatures),
        "support_sizes": dict(sorted(supports.items())),
        "maximum_coefficients": dict(sorted(coefficients.items())),
        "bounds": dict(sorted(bounds.items())),
    }
    expected = {
        "stage_count": 90,
        "activation_failure_case_count": 285,
        "allocation_infeasible_case_count": 195,
        "witness_overcover_count": 90,
        "overcover_signature_count": 63,
        "support_sizes": {2: 61, 3: 11, 4: 18},
        "maximum_coefficients": {1: 90},
        "bounds": {1: 63, 2: 27},
    }
    if actual != expected:
        raise AssertionError(f"class-5 activation census changed: {actual}")
    canonical_bytes = json.dumps(certificates, sort_keys=True, separators=(",", ":")).encode()
    payload = {
        "schema": "strict-exchange-p4-class5-activation-overcovers-v1",
        "status": "PASS",
        "scope": "encoding-shared decomposition of all class-5 activation failures; incidence supports instantiate the solver-free zero-anchor theorem but allocation-side strictness and coverage remain integration audits",
        "class": 5,
        **actual,
        "allocation_infeasible_cases": direct_cases,
        "certificate_sha256": hashlib.sha256(canonical_bytes).hexdigest(),
        **({"certificates": certificates} if args.details else {}),
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

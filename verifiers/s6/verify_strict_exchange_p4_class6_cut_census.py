#!/usr/bin/env python3
"""Verify the complete class-6 cut partition with exact arithmetic.

This checker imports no solver, optimizer, computer-algebra system, or
production encoder.  It hard-codes the seven class-6 directions and packet
sandwich, recomputes all pure difference-cone candidates by exact Fourier--
Motzkin elimination, and checks the disjoint exhaustive partition into 11
allocation-context exclusions, 155 witness exclusions, and 47 relay branches.
The frozen relay and use maps remain integration inputs, not independent proof
of the human-to-machine mapping.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
RELAY = HERE / "strict_exchange_p4_universal_order_relays.json"
CONTEXT_ROWS = HERE / "strict_exchange_p4_class6_context_identity_rows.json"
WITNESS_ROWS = HERE / "strict_exchange_p4_class6_allocation_identity_rows.json"

DIRECTIONS = {
    7: ("max", (1, -1, 1, 0, 0, -1)),
    10: ("max", (1, -1, 0, 0, 0, 0)),
    11: ("max", (1, 0, 0, 1, -1, -1)),
    12: ("max", (1, 0, 1, 0, -1, -1)),
    15: ("min", (1, -1, 0, 0, 0, 0)),
    17: ("min", (0, -1, 0, -1, 1, 1)),
    18: ("min", (0, 0, -1, -1, 1, 1)),
}
EXPECTED_STAGE_TYPES = {
    (7, 20, 5): 3,
    (7, 20, 6): 6,
    (10, 16, 8): 2,
    (10, 16, 9): 1,
    (11, 20, 2): 3,
    (12, 20, 2): 1,
    (15, 16, 8): 7,
    (15, 16, 9): 4,
    (17, 20, 2): 15,
    (18, 20, 1): 7,
}
EXPECTED_CANDIDATE_SHA256 = "8c0128a11215ca09b23213e91a9893e18edf280f94d90a4f203af31bffc5717b"
BASE_MENUS = {
    7: {(1,), (1, 3), (1, 3, 4), (0, 1, 3, 5), (1, 2, 3, 5)},
    10: {(1,), (1, 2), (1, 3), (1, 2, 3), (1, 2, 4), (1, 3, 4),
         (1, 2, 3, 4), (1, 2, 3, 5)},
    11: {(2, 4), (1, 2, 4)},
    12: {(3, 4), (1, 3, 4)},
    15: {(1, 4), (1, 5), (1, 2, 5), (1, 3, 5), (1, 4, 5),
         (1, 2, 4, 5), (1, 3, 4, 5), (1, 2, 3, 4, 5)},
    17: {(1, 3, 5), (0, 1, 3, 5)},
    18: {(2, 3, 5)},
}
# The sole menu refinement: after the weak h11 blocker C=124, these three
# direction types each acquire one additional difference-cone candidate.
RICH_BRANCH_EXTRAS = {7: {(1, 3, 5)}, 10: {(1, 3, 5)}, 15: {(1, 2, 4)}}


def eligible(direction):
    return [coalition for size in range(1, 6)
            for coalition in combinations(range(6), size)
            if sum(direction[player] for player in coalition) < 0]


def d_form(coalition):
    # Coordinates d0,d1,d2,d3,delta4; efficiency gives
    # delta5=d0+d1+d2+d3-delta4.
    result = [Fraction() for _ in range(5)]
    for player in coalition:
        if player < 4:
            result[player] += 1
        elif player == 4:
            result[4] -= 1
        else:
            for index in range(4):
                result[index] -= 1
            result[4] += 1
    return tuple(result)


def normalize(rows):
    best = {}
    for coefficients, rhs in rows:
        key = tuple(coefficients)
        if key not in best or rhs < best[key]:
            best[key] = rhs
    return [(key, rhs) for key, rhs in best.items()]


def fourier_motzkin_feasible(rows, variable_count=5):
    rows = normalize(rows)
    for index in reversed(range(variable_count)):
        positive, negative, zero = [], [], []
        for coefficients, rhs in rows:
            value = coefficients[index]
            if value > 0:
                positive.append((coefficients, rhs))
            elif value < 0:
                negative.append((coefficients, rhs))
            else:
                zero.append((coefficients[:index] + coefficients[index + 1:], rhs))
        combined = list(zero)
        if positive and negative:
            for p, prhs in positive:
                for n, nrhs in negative:
                    coefficients = tuple(
                        (-n[index]) * p[j] + p[index] * n[j]
                        for j in range(len(p)) if j != index
                    )
                    combined.append((coefficients,
                                     (-n[index]) * prhs + p[index] * nrhs))
        rows = normalize(combined)
        if any(not coefficients and rhs < 0 for coefficients, rhs in rows):
            return False
    return not any(rhs < 0 for _, rhs in rows)


def cone_rows(path):
    rows = []
    # Homogeneity permits normalization of all six strict sign magnitudes.
    for index in range(5):
        coefficients = [Fraction() for _ in range(5)]
        coefficients[index] = -1
        rows.append((tuple(coefficients), Fraction(-1)))
    rows.append(((-1, -1, -1, -1, 1), Fraction(-1)))
    # Class-6 packet sandwich: d0+d1 <= delta4 <= d3.
    rows.extend([
        ((1, 1, 0, 0, -1), Fraction()),
        ((0, 0, 0, -1, 1), Fraction()),
    ])
    for direction, coalition in path:
        side, _ = DIRECTIONS[direction]
        form = d_form(coalition)
        rows.append((form if side == "min" else tuple(-value for value in form),
                     Fraction()))
    return rows


def use_keys(path):
    payload = json.loads(path.read_text())
    return {(row["stage"], tuple(row["candidate"])) for row in payload["uses"]}


def census(relay_payload, context_keys, witness_keys,
           expected_digest=EXPECTED_CANDIDATE_SHA256):
    class_row = next(row for row in relay_payload["rows"] if row["class"] == 6)
    stage_types = Counter()
    menu_variants = Counter()
    candidate_keys = set()
    branch_keys = set()
    stage_count = eligible_count = 0

    def walk(node, order, path):
        nonlocal stage_count, eligible_count
        direction = node["direction_index"]
        if direction not in DIRECTIONS:
            raise AssertionError(f"unknown class-6 direction h{direction}")
        side, vector = DIRECTIONS[direction]
        if tuple(node["direction"]) != vector or node["side"] != side:
            raise AssertionError(f"relay direction metadata changed at h{direction}")
        stage = order + "".join(
            f"-h{parent}C{''.join(map(str, cut))}" for parent, cut in path
        ) + f"-h{direction}"
        cuts = eligible(vector)
        if node["eligible_negative_cut_count"] != len(cuts):
            raise AssertionError(f"eligible-cut metadata changed at {stage}")
        candidates = []
        for cut in cuts:
            form = d_form(cut)
            blocker = form if side == "min" else tuple(-value for value in form)
            if fourier_motzkin_feasible([*cone_rows(path), (blocker, Fraction())]):
                candidates.append(cut)
                candidate_keys.add((stage, cut))
        rich_branch = any(parent == 11 and cut == (1, 2, 4) for parent, cut in path)
        expected_menu = BASE_MENUS[direction] | (
            RICH_BRANCH_EXTRAS.get(direction, set()) if rich_branch else set()
        )
        if set(candidates) != expected_menu:
            raise AssertionError(
                f"orbit-menu atlas changed at {stage}: {set(candidates)}"
            )
        menu_variants[(direction, "rich-124" if rich_branch and direction in RICH_BRANCH_EXTRAS
                       else "base")] += 1
        stage_count += 1
        eligible_count += len(cuts)
        stage_types[(direction, len(cuts), len(candidates))] += 1
        if node["feasible_blocker_count"] != len(node.get("branches", [])):
            raise AssertionError(f"relay branch metadata changed at {stage}")
        for branch in node.get("branches", []):
            cut = tuple(branch["coalition"])
            key = stage, cut
            if key in branch_keys:
                raise AssertionError(f"duplicate branch key {key}")
            branch_keys.add(key)
            walk(branch["child"], order, [*path, (direction, cut)])

    walk(class_row["weak_branch"]["tree"], "W", [])
    walk(class_row["strict_branch"]["tree"], "S", [])
    canonical = json.dumps(
        [[stage, list(cut)] for stage, cut in sorted(candidate_keys)],
        sort_keys=True, separators=(",", ":"),
    ).encode()
    digest = hashlib.sha256(canonical).hexdigest()
    if expected_digest != "TO_BE_FROZEN" and digest != expected_digest:
        raise AssertionError(f"pure candidate digest changed: {digest}")
    if dict(stage_types) != EXPECTED_STAGE_TYPES:
        raise AssertionError(f"stage-type census changed: {stage_types}")
    expected_variants = {
        (7, "base"): 3, (7, "rich-124"): 6,
        (10, "base"): 2, (10, "rich-124"): 1,
        (11, "base"): 3, (12, "base"): 1,
        (15, "base"): 7, (15, "rich-124"): 4,
        (17, "base"): 15, (18, "base"): 7,
    }
    if dict(menu_variants) != expected_variants:
        raise AssertionError(f"menu-variant census changed: {menu_variants}")
    layers = [context_keys, witness_keys, branch_keys]
    if any(layers[i] & layers[j] for i in range(3) for j in range(i + 1, 3)):
        raise AssertionError("class-6 cut layers overlap")
    partition = context_keys | witness_keys | branch_keys
    if partition != candidate_keys:
        missing = candidate_keys - partition
        extra = partition - candidate_keys
        raise AssertionError(f"cut partition mismatch: missing={missing}, extra={extra}")
    actual = {
        "stage_count": stage_count,
        "eligible_cut_use_count": eligible_count,
        "pure_difference_exclusion_count": eligible_count - len(candidate_keys),
        "pure_difference_candidate_count": len(candidate_keys),
        "context_exclusion_count": len(context_keys),
        "witness_exclusion_count": len(witness_keys),
        "relay_branch_count": len(branch_keys),
        "distinct_candidate_set_count": len({
            # Recover candidate sets by stage from the exact key set.
            tuple(sorted(cut for candidate_stage, cut in candidate_keys if candidate_stage == stage))
            for stage, _ in candidate_keys
        }),
    }
    expected = {
        "stage_count": 49,
        "eligible_cut_use_count": 924,
        "pure_difference_exclusion_count": 711,
        "pure_difference_candidate_count": 213,
        "context_exclusion_count": 11,
        "witness_exclusion_count": 155,
        "relay_branch_count": 47,
        "distinct_candidate_set_count": 10,
    }
    if actual != expected:
        raise AssertionError(f"complete cut census changed: {actual}")
    return actual, digest, stage_types, menu_variants


def expect_rejection(action, message):
    try:
        action()
    except AssertionError:
        return message
    raise AssertionError(f"mutation unexpectedly passed: {message}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--relay", type=Path, default=RELAY)
    parser.add_argument("--context-rows", type=Path, default=CONTEXT_ROWS)
    parser.add_argument("--witness-rows", type=Path, default=WITNESS_ROWS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    relay_payload = json.loads(args.relay.read_text())
    context_keys = use_keys(args.context_rows)
    witness_keys = use_keys(args.witness_rows)
    counts, digest, stage_types, menu_variants = census(
        relay_payload, context_keys, witness_keys
    )

    missing_context = set(context_keys)
    missing_context.pop()
    partition_mutation = expect_rejection(
        lambda: census(relay_payload, missing_context, witness_keys, digest),
        "rejected context-use deletion",
    )
    relay_mutation = copy.deepcopy(relay_payload)
    row = next(item for item in relay_mutation["rows"] if item["class"] == 6)
    row["weak_branch"]["tree"]["direction"][0] += 1
    direction_mutation = expect_rejection(
        lambda: census(relay_mutation, context_keys, witness_keys, digest),
        "rejected direction mutation",
    )
    digest_mutation = expect_rejection(
        lambda: census(relay_payload, context_keys, witness_keys, "0" * 64),
        "rejected candidate-digest mutation",
    )
    report = {
        "schema": "strict-exchange-p4-class6-cut-census-audit-v1",
        "status": "PASS",
        "scope": "solver-free exact Fourier--Motzkin census and exhaustive cut-layer partition; frozen relay/use maps are integration records, not independent human-to-machine evidence",
        **counts,
        "pure_candidate_sha256": digest,
        "stage_type_counts": {
            f"h{direction}:eligible{eligible_count}:candidates{candidate_count}": count
            for (direction, eligible_count, candidate_count), count in sorted(stage_types.items())
        },
        "orbit_menu_atlas": {
            f"h{direction}": {
                "base": [list(cut) for cut in sorted(BASE_MENUS[direction])],
                **({"after_h11_C124_extra": [list(cut) for cut in sorted(RICH_BRANCH_EXTRAS[direction])]}
                   if direction in RICH_BRANCH_EXTRAS else {}),
            }
            for direction in sorted(BASE_MENUS)
        },
        "menu_variant_counts": {
            f"h{direction}:{variant}": count
            for (direction, variant), count in sorted(menu_variants.items())
        },
        "mutation_controls": {
            "partition": partition_mutation,
            "direction": direction_mutation,
            "candidate_digest": digest_mutation,
        },
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

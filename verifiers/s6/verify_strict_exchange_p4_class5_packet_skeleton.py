#!/usr/bin/env python3
"""Verify the reusable hand skeleton for packet class 5.

This checker uses only exact rational coefficient arithmetic and finite order
enumeration.  It imports neither a solver nor the production encoder.  The
frozen universal relay JSON is read only to audit where the lemma is used;
that integration count is not proof evidence for the lemma or the theorem.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
RELAY = HERE / "strict_exchange_p4_universal_order_relays.json"


def linear(*terms):
    out = {}
    for multiplier, form in terms:
        multiplier = Fraction(multiplier)
        for name, value in form.items():
            result = out.get(name, Fraction()) + multiplier * value
            if result:
                out[name] = result
            else:
                out.pop(name, None)
    return out


def variable(name):
    return {name: Fraction(1)}


D = [variable(f"d{i}") for i in range(4)]
DELTA = {4: variable("delta4"), 5: variable("delta5")}
S = linear((1, D[0]), (1, D[1]))
T = linear((1, D[2]), (1, D[3]))
EFFICIENCY = linear((1, DELTA[4]), (1, DELTA[5]), (-1, S), (-1, T))
LOWER = {m: linear((1, S), (-1, DELTA[m])) for m in (4, 5)}
UPPER = {m: linear((1, DELTA[m]), (-1, T)) for m in (4, 5)}


def assert_identity(left, right, label):
    residual = linear((1, left), (-1, right))
    if residual:
        raise AssertionError(f"{label} identity failed: {residual}")


def cut_difference(coalition):
    """Return x(C)-z(C) in d/delta coordinates."""
    return linear(
        *((1, D[i]) for i in coalition if i < 4),
        *((-1, DELTA[i]) for i in coalition if i >= 4),
    )


def eligible_h15_cuts():
    # h15=e0-e1, so h15(C)<0 exactly when 1 is in C and 0 is not.
    return {
        coalition
        for size in range(1, 6)
        for coalition in combinations(range(6), size)
        if 1 in coalition and 0 not in coalition
    }


def audit_packet_sandwich():
    # EFFICIENCY + (s-delta_other) = delta_m-t.
    assert_identity(UPPER[4], linear((1, EFFICIENCY), (1, LOWER[5])), "delta4 upper")
    assert_identity(UPPER[5], linear((1, EFFICIENCY), (1, LOWER[4])), "delta5 upper")
    return {
        "efficiency": "delta4+delta5=(d0+d1)+(d2+d3)",
        "packet_lower_bounds": ["d0+d1<=delta4", "d0+d1<=delta5"],
        "derived_upper_bounds": ["delta4<=d2+d3", "delta5<=d2+d3"],
    }


def audit_h15_cut_classification(expected=None):
    eligible = eligible_h15_cuts()
    candidates = set()
    exclusions = {}
    for coalition in sorted(eligible):
        rich = set(coalition) & {4, 5}
        poor = set(coalition) & {2, 3}
        difference = cut_difference(coalition)
        if not rich:
            # d(C) is a nonempty sum containing strictly positive d1.
            rhs = linear(*((1, D[i]) for i in coalition))
            assert_identity(difference, rhs, f"no-rich cut {coalition}")
            exclusions[coalition] = "strictly positive P-sum"
        elif len(rich) == 1 and poor == {2, 3}:
            m = next(iter(rich))
            rhs = linear((1, D[1]), (-1, UPPER[m]))
            assert_identity(difference, rhs, f"full-poor one-rich cut {coalition}")
            exclusions[coalition] = "d1+(d2+d3-delta_m)>0"
        else:
            candidates.add(coalition)

        if len(rich) == 2:
            missing = {2, 3} - poor
            rhs = linear((-1, D[0]), *((-1, D[i]) for i in sorted(missing)), (-1, EFFICIENCY))
            assert_identity(difference, rhs, f"two-rich cut {coalition}")

    canonical = {
        (1, 4), (1, 2, 4), (1, 3, 4),
        (1, 5), (1, 2, 5), (1, 3, 5),
        (1, 4, 5), (1, 2, 4, 5), (1, 3, 4, 5), (1, 2, 3, 4, 5),
    }
    target = canonical if expected is None else expected
    if candidates != target:
        raise AssertionError(f"h15 candidate census changed: {sorted(candidates)}")
    if len(exclusions) != 6 or candidates & set(exclusions) or candidates | set(exclusions) != eligible:
        raise AssertionError("h15 classification is not an exhaustive partition")
    return {
        "eligible_negative_cut_count": len(eligible),
        "opposite_comparison_candidate_count": len(candidates),
        "excluded_cut_count": len(exclusions),
        "candidates": [list(c) for c in sorted(candidates)],
        "exclusions": [
            {"coalition": list(c), "reason": exclusions[c]} for c in sorted(exclusions)
        ],
    }


def chain_holds(values, links):
    for left, relation, right in links:
        if relation == "<" and not values[left] < values[right]:
            return False
        if relation == "<=" and not values[left] <= values[right]:
            return False
    return True


def audit_anchor_chains(mutated=None):
    chains = {
        "h10": [("z0", "<", "x0"), ("x0", "<=", "x4"), ("x4", "<", "z4"), ("z4", "<=", "z1")],
        "h15": [("x0", "<=", "x4"), ("x4", "<", "z4"), ("z4", "<=", "z1"), ("z1", "<", "x1")],
    }
    if mutated:
        name, indices = mutated
        for index in indices:
            left, _, right = chains[name][index]
            chains[name][index] = (left, "<=", right)
    targets = {"h10": ("z0", "z1"), "h15": ("x0", "x1")}
    counts = {}
    for name, links in chains.items():
        variables = sorted({v for link in links for v in (link[0], link[2])})
        satisfying = 0
        for levels in product(range(5), repeat=len(variables)):
            values = dict(zip(variables, levels, strict=True))
            if not chain_holds(values, links):
                continue
            satisfying += 1
            left, right = targets[name]
            if not values[left] < values[right]:
                raise AssertionError(f"{name} chain no longer forces {left}<{right}: {values}")
        if satisfying == 0:
            raise AssertionError(f"{name} chain has no finite-order representative")
        counts[name] = satisfying
    return {
        "h10_chain": "z0<x0<=x4<z4<=z1, hence z0<z1",
        "h15_chain": "x0<=x4<z4<=z1<x1, hence x0<x1",
        "tested_level_assignments_per_chain": 5**5,
        "satisfying_level_assignments": counts,
    }


def walk_h15(node, rows):
    if node.get("direction_index") == 15:
        rows.append(
            {
                "depth": node["depth"],
                "feasible_blocker_count": node["feasible_blocker_count"],
                "coalitions": [branch["coalition"] for branch in node.get("branches", [])],
            }
        )
    for branch in node.get("branches", []):
        walk_h15(branch["child"], rows)


def audit_relay_integration(candidates):
    data = json.loads(RELAY.read_text())
    row = next(item for item in data["rows"] if item["class"] == 5)
    uses = []
    walk_h15(row["weak_branch"]["tree"], uses)
    walk_h15(row["strict_branch"]["tree"], uses)
    candidate_set = {tuple(c) for c in candidates}
    for use in uses:
        if not {tuple(c) for c in use["coalitions"]} <= candidate_set:
            raise AssertionError("relay h15 child lies outside the hand classification")
    if len(uses) != 10:
        raise AssertionError(f"expected ten h15 uses, found {len(uses)}")
    return {
        "scope": "encoding-shared integration audit, not proof evidence",
        "h15_relay_node_count": len(uses),
        "weak_branch_node_count": 4,
        "strict_branch_node_count": 6,
        "all_relay_children_in_hand_candidate_set": True,
    }


def reject(function, label):
    try:
        function()
    except AssertionError:
        return label
    raise AssertionError(f"mutation passed: {label}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    sandwich = audit_packet_sandwich()
    classification = audit_h15_cut_classification()
    chains = audit_anchor_chains()
    mutations = [
        reject(lambda: audit_anchor_chains(("h10", (0, 2))), "weaken both h10 sign links"),
        reject(lambda: audit_anchor_chains(("h15", (1, 3))), "weaken both h15 sign links"),
        reject(
            lambda: audit_h15_cut_classification(
                {tuple(c) for c in classification["candidates"]} - {(1, 4)}
            ),
            "delete h15 candidate",
        ),
        reject(
            lambda: audit_h15_cut_classification(
                {tuple(c) for c in classification["candidates"]} | {(1, 2, 3, 4)}
            ),
            "add excluded h15 cut",
        ),
    ]
    integration = audit_relay_integration(classification["candidates"])
    payload = {
        "schema": "strict-exchange-p4-class5-packet-skeleton-v1",
        "status": "PASS",
        "scope": "solver-free hand lemma for class-5 packet; partial humanization, not a complete class-5 proof and not independent theorem evidence",
        "packet_sandwich": sandwich,
        "automatic_anchor_exchanges": chains,
        "h15_cut_classification": classification,
        "relay_integration": integration,
        "rejected_mutations": mutations,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

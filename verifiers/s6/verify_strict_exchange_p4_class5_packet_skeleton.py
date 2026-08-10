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


def constant(value):
    return {"constant": Fraction(value)} if value else {}


def point_sum(point, coalition):
    return linear(*((1, point[i]) for i in coalition))


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


def crossing_system(B, C):
    x = [variable(f"x{i}") for i in range(6)]
    z = [variable(f"z{i}") for i in range(6)]
    q = [variable(f"q{i}") for i in range(6)]
    inequalities = {}
    for i in (4, 5):
        inequalities[f"x{i}>=0"] = linear((-1, x[i]))
        inequalities[f"z{i}<=z1"] = linear((1, z[i]), (-1, z[1]))
    for i in (1, 2, 3):
        inequalities[f"d{i}>=0"] = linear((1, z[i]), (-1, x[i]))
    for m in (4, 5):
        packet = (0, 1, m)
        inequalities[f"P{m}q"] = linear((1, point_sum(x, packet)), (-1, point_sum(q, packet)))
    inequalities["Bq"] = linear((1, point_sum(z, B)), (-1, point_sum(q, B)))
    inequalities["Cq"] = linear((1, point_sum(x, C)), (-1, point_sum(q, C)))
    equalities = {
        "sumx": linear((1, point_sum(x, range(6))), (-1, constant(1))),
        "sumz": linear((1, point_sum(z, range(6))), (-1, constant(1))),
        "sumq": linear((1, point_sum(q, range(6))), (-1, constant(1))),
        "q1": q[1],
    }
    target = linear((1, x[0]), (-1, z[0]))
    return inequalities, equalities, target


def verify_crossing_identity(B, C, inequality_multipliers, equality_multipliers):
    inequalities, equalities, target = crossing_system(B, C)
    terms = []
    for name, multiplier in inequality_multipliers.items():
        if name not in inequalities or Fraction(multiplier) < 0:
            raise AssertionError(f"bad crossing inequality {name}")
        terms.append((Fraction(multiplier), inequalities[name]))
    for name, multiplier in equality_multipliers.items():
        if name not in equalities:
            raise AssertionError(f"bad crossing equality {name}")
        terms.append((Fraction(multiplier), equalities[name]))
    assert_identity(linear(*terms), target, f"crossing B={B}, C={C}")


def audit_crossing_lemma(mutate=False):
    exclusions = []
    for k, ell in ((2, 3), (3, 2)):
        for m in (4, 5):
            B = (1, k)
            C = tuple(sorted((1, ell, m)))
            multipliers = {
                "x4>=0": 1, "x5>=0": 1, "d1>=0": 2, f"d{ell}>=0": 1,
                "z4<=z1": 1, "z5<=z1": 1, f"P{9-m}q": 1, "Bq": 1, "Cq": 1,
            }
            if mutate and not exclusions:
                multipliers["d1>=0"] = 1
            verify_crossing_identity(B, C, multipliers, {"sumz": -1, "sumq": 1, "q1": 2})
            exclusions.append((B, C, "split-poor crossing"))
    for m in (4, 5):
        B = (1, 2, 3)
        C = (1, m)
        verify_crossing_identity(
            B, C,
            {"x4>=0": 1, "x5>=0": 1, "d1>=0": 2,
             "z4<=z1": 1, "z5<=z1": 1, f"P{9-m}q": 1, "Bq": 1, "Cq": 1},
            {"sumz": -1, "sumq": 1, "q1": 2},
        )
        exclusions.append((B, C, "empty-poor crossing"))
    B = (1, 2, 3)
    C = (1, 2, 3, 4, 5)
    verify_crossing_identity(
        B, C,
        {"x4>=0": 1, "x5>=0": 1, "d1>=0": 2, "z4<=z1": 1,
         "z5<=z1": 1, "P4q": 1, "P5q": 1, "Bq": 1, "Cq": 1},
        {"sumx": -1, "sumz": -1, "sumq": 2, "q1": 2},
    )
    exclusions.append((B, C, "full-complement crossing"))

    h10 = {(1, 2), (1, 3), (1, 2, 3)}
    h15 = {
        (1, 4), (1, 2, 4), (1, 3, 4), (1, 5), (1, 2, 5), (1, 3, 5),
        (1, 4, 5), (1, 2, 4, 5), (1, 3, 4, 5), (1, 2, 3, 4, 5),
    }
    excluded_pairs = {(B, C) for B, C, _ in exclusions}
    allowed = {(B, C) for B in h10 for C in h15} - excluded_pairs
    if len(exclusions) != 7 or len(allowed) != 23:
        raise AssertionError("crossing pair census changed")
    return {
        "h10_predecessor_types": [list(B) for B in sorted(h10)],
        "h15_packet_candidates": len(h15),
        "raw_pair_count": len(h10) * len(h15),
        "excluded_pair_count": len(exclusions),
        "allowed_pair_count": len(allowed),
        "excluded_pairs": [
            {"h10_blocker": list(B), "h15_blocker": list(C), "orbit_reason": reason}
            for B, C, reason in exclusions
        ],
        "identity_target": "d0=x0-z0>0; every excluded pair would imply d0<=0",
        "identity_orbit_count": 3,
        "allowed_pairs": allowed,
    }


def walk_h15(node, rows, last_h10=None):
    if node.get("direction_index") == 10:
        # The selected blocker is recorded on each outgoing branch below.
        pass
    if node.get("direction_index") == 15:
        rows.append(
            {
                "depth": node["depth"],
                "h10_predecessor": list(last_h10) if last_h10 else None,
                "feasible_blocker_count": node["feasible_blocker_count"],
                "coalitions": [branch["coalition"] for branch in node.get("branches", [])],
            }
        )
    for branch in node.get("branches", []):
        predecessor = tuple(branch["coalition"]) if node.get("direction_index") == 10 else last_h10
        walk_h15(branch["child"], rows, predecessor)


def audit_relay_integration(candidates, allowed_pairs):
    data = json.loads(RELAY.read_text())
    row = next(item for item in data["rows"] if item["class"] == 5)
    uses = []
    walk_h15(row["weak_branch"]["tree"], uses)
    walk_h15(row["strict_branch"]["tree"], uses)
    candidate_set = {tuple(c) for c in candidates}
    for use in uses:
        if not {tuple(c) for c in use["coalitions"]} <= candidate_set:
            raise AssertionError("relay h15 child lies outside the hand classification")
        if use["h10_predecessor"] is None:
            raise AssertionError("relay h15 node has no h10 predecessor")
        if any((tuple(use["h10_predecessor"]), tuple(C)) not in allowed_pairs for C in use["coalitions"]):
            raise AssertionError("relay h10/h15 pair violates the crossing lemma")
    if len(uses) != 10:
        raise AssertionError(f"expected ten h15 uses, found {len(uses)}")
    return {
        "scope": "encoding-shared integration audit, not proof evidence",
        "h15_relay_node_count": len(uses),
        "weak_branch_node_count": 4,
        "strict_branch_node_count": 6,
        "all_relay_children_in_hand_candidate_set": True,
        "all_relay_h10_h15_pairs_pass_crossing_lemma": True,
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
    crossing = audit_crossing_lemma()
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
        reject(lambda: audit_crossing_lemma(mutate=True), "crossing identity coefficient"),
    ]
    integration = audit_relay_integration(classification["candidates"], crossing.pop("allowed_pairs"))
    payload = {
        "schema": "strict-exchange-p4-class5-packet-skeleton-v2",
        "status": "PASS",
        "scope": "solver-free hand lemma for class-5 packet; partial humanization, not a complete class-5 proof and not independent theorem evidence",
        "packet_sandwich": sandwich,
        "automatic_anchor_exchanges": chains,
        "h15_cut_classification": classification,
        "h10_h15_crossing_lemma": crossing,
        "relay_integration": integration,
        "rejected_mutations": mutations,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

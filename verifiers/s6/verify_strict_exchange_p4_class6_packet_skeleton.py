#!/usr/bin/env python3
"""Verify the solver-free packet and root skeleton for packet class 6."""
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


def assert_identity(left, right, label):
    residual = linear((1, left), (-1, right))
    if residual:
        raise AssertionError(f"{label} identity failed: {residual}")


D = [variable(f"d{i}") for i in range(4)]
DELTA = {4: variable("delta4"), 5: variable("delta5")}
S = linear((1, D[0]), (1, D[1]))
EFFICIENCY = linear(
    (1, DELTA[4]), (1, DELTA[5]),
    (-1, D[0]), (-1, D[1]), (-1, D[2]), (-1, D[3]),
)
LOWER4 = linear((1, S), (-1, DELTA[4]))
LOWER5 = linear((1, S), (1, D[2]), (-1, DELTA[5]))
UPPER4 = linear((1, DELTA[4]), (-1, D[3]))
UPPER5 = linear((1, DELTA[5]), (-1, D[2]), (-1, D[3]))


def cut_difference(coalition):
    return linear(
        *((1, D[i]) for i in coalition if i < 4),
        *((-1, DELTA[i]) for i in coalition if i >= 4),
    )


def eligible(direction):
    return {
        C for size in range(1, 6) for C in combinations(range(6), size)
        if sum(direction[i] for i in C) < 0
    }


def audit_sandwich():
    assert_identity(UPPER4, linear((1, EFFICIENCY), (1, LOWER5)), "delta4 upper")
    assert_identity(UPPER5, linear((1, EFFICIENCY), (1, LOWER4)), "delta5 upper")
    return {
        "efficiency": "delta4+delta5=d0+d1+d2+d3",
        "packet_lower_bounds": ["d0+d1<=delta4", "d0+d1+d2<=delta5"],
        "derived_upper_bounds": ["delta4<=d3", "delta5<=d2+d3"],
        "strict_consequence": "d0+d1<=d3",
    }


def audit_root_activations(mutate=False):
    weak_count = 0
    for levels in product(range(5), repeat=6):
        values = dict(zip(("z0", "x0", "z3", "x3", "x4", "z4"), levels, strict=True))
        strict_link = values["x4"] < values["z4"] if not mutate else values["x4"] <= values["z4"]
        if not (values["z0"] < values["x0"] <= values["x4"] and strict_link
                and values["z3"] < values["x3"] <= values["x4"]):
            continue
        weak_count += 1
        if not max(values["z0"], values["z3"]) < values["z4"]:
            raise AssertionError("weak h11 root activation failed")
    strict_count = 0
    variables = ("x1", "z1", "z4", "x4", "z5", "x5", "x3")
    for levels in product(range(5), repeat=len(variables)):
        values = dict(zip(variables, levels, strict=True))
        order_link = values["x3"] > values["x4"] if not mutate else values["x3"] >= values["x4"]
        if not (values["x1"] > values["z1"] >= values["z4"] > values["x4"]
                and values["z1"] >= values["z5"] > values["x5"] and order_link):
            continue
        strict_count += 1
        if not min(values["x1"], values["x3"]) > min(values["x4"], values["x5"]):
            raise AssertionError("strict h17 root activation failed")
    if not weak_count or not strict_count:
        raise AssertionError("root chain has no finite-order representative")
    return {
        "weak_h11_chain": "z0,z3<z4 on x3<=x4, hence max(z0,z3)<max(z4,z5)",
        "strict_h17_chain": "x1>x4,x5 and x3>x4 on x3>x4, hence min(x1,x3)>min(x4,x5)",
        "weak_satisfying_level_assignments": weak_count,
        "strict_satisfying_level_assignments": strict_count,
    }


def audit_root_cuts(expected_h11=None, expected_h17=None):
    h11_candidates = set()
    h11_eligible = eligible((1, 0, 0, 1, -1, -1))
    for C in h11_eligible:
        rich = set(C) & {4, 5}
        if len(rich) == 2:
            missing = set(range(4)) - set(C)
            assert_identity(
                cut_difference(C),
                linear(*((-1, D[i]) for i in sorted(missing)), (-1, EFFICIENCY)),
                f"h11 two-rich {C}",
            )
            continue
        if len(rich) != 1:
            raise AssertionError(f"unexpected h11 cut {C}")
        m = next(iter(rich))
        poor = set(C) & {1, 2}
        if m == 4 and poor in ({2}, {1, 2}):
            h11_candidates.add(C)
        elif m == 4 and not poor:
            assert_identity(cut_difference(C), linear((-1, DELTA[4])), f"h11 4-empty {C}")
        elif m == 4 and poor == {1}:
            assert_identity(cut_difference(C), linear((-1, D[0]), (1, LOWER4)), f"h11 4-one {C}")
        elif m == 5:
            missing = {0, 1, 2} - poor
            assert_identity(
                cut_difference(C),
                linear(*((-1, D[i]) for i in sorted(missing)), (1, LOWER5)),
                f"h11 rich-5 {C}",
            )
        else:
            raise AssertionError(f"unclassified h11 cut {C}")
    canonical_h11 = {(2, 4), (1, 2, 4)}
    if h11_candidates != (canonical_h11 if expected_h11 is None else expected_h11):
        raise AssertionError(f"h11 candidates changed: {h11_candidates}")

    h17_candidates = set()
    h17_eligible = eligible((0, -1, 0, -1, 1, 1))
    for C in h17_eligible:
        rich = set(C) & {4, 5}
        if not rich:
            assert_identity(cut_difference(C), linear(*((1, D[i]) for i in C)), f"h17 no-rich {C}")
            continue
        if len(rich) != 1 or not {1, 3} <= set(C):
            raise AssertionError(f"unexpected h17 cut {C}")
        m = next(iter(rich))
        if m == 5 and 2 not in C:
            h17_candidates.add(C)
        elif m == 4:
            rhs = linear((1, D[1]), (-1, UPPER4), *((1, D[i]) for i in (0, 2) if i in C))
            assert_identity(cut_difference(C), rhs, f"h17 rich-4 {C}")
        elif m == 5 and 2 in C:
            rhs = linear((1, D[1]), (-1, UPPER5), *((1, D[i]) for i in (0,) if i in C))
            assert_identity(cut_difference(C), rhs, f"h17 rich-5 with 2 {C}")
        else:
            raise AssertionError(f"unclassified h17 cut {C}")
    canonical_h17 = {(1, 3, 5), (0, 1, 3, 5)}
    if h17_candidates != (canonical_h17 if expected_h17 is None else expected_h17):
        raise AssertionError(f"h17 candidates changed: {h17_candidates}")
    return {
        "weak_h11": {"eligible_negative_cut_count": len(h11_eligible), "blockers": [list(C) for C in sorted(h11_candidates)]},
        "strict_h17": {"eligible_negative_cut_count": len(h17_eligible), "blockers": [list(C) for C in sorted(h17_candidates)]},
    }


def audit_integration(root_cuts):
    data = json.loads(RELAY.read_text())
    row = next(item for item in data["rows"] if item["class"] == 6)
    weak = row["weak_branch"]["tree"]
    strict = row["strict_branch"]["tree"]
    if weak.get("direction_index") != 11 or strict.get("direction_index") != 17:
        raise AssertionError("class-6 roots changed")
    if {tuple(b["coalition"]) for b in weak["branches"]} != {tuple(C) for C in root_cuts["weak_h11"]["blockers"]}:
        raise AssertionError("weak blocker integration changed")
    if {tuple(b["coalition"]) for b in strict["branches"]} != {tuple(C) for C in root_cuts["strict_h17"]["blockers"]}:
        raise AssertionError("strict blocker integration changed")
    return {
        "scope": "encoding-shared integration audit, not proof evidence",
        "effective_closed_leaf_count": row["effective_closed_leaf_count"],
        "weak_root_matches_hand_list": True,
        "strict_root_matches_hand_list": True,
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
    sandwich = audit_sandwich()
    activations = audit_root_activations()
    cuts = audit_root_cuts()
    mutations = [
        reject(lambda: audit_root_activations(mutate=True), "weaken root strict links"),
        reject(lambda: audit_root_cuts({(2, 4)}, {(1, 3, 5), (0, 1, 3, 5)}), "delete weak root blocker"),
        reject(lambda: audit_root_cuts({(2, 4), (1, 2, 4)}, {(1, 3, 5)}), "delete strict root blocker"),
    ]
    payload = {
        "schema": "strict-exchange-p4-class6-packet-skeleton-v1",
        "status": "PASS",
        "scope": "solver-free class-6 packet and root lemma; partial humanization, not a complete class-6 proof or independent theorem evidence",
        "packet_sandwich": sandwich,
        "root_activations": activations,
        "root_cut_classification": cuts,
        "relay_integration": audit_integration(cuts),
        "rejected_mutations": mutations,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

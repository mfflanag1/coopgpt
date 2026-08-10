#!/usr/bin/env python3
"""Verify the class-9 order-split relay with exact, solver-free arithmetic.

The checked proof object separates 52 distinct weighted identities from their
71 uses.  This checker reconstructs every affine form at every use site,
requires nonnegative inequality multipliers, recomputes the difference-cone
candidate census by exact Fourier--Motzkin elimination, and audits that the
use map exhausts every discarded candidate and every relay activation.

No production encoder, numerical optimizer, SMT solver, or computer-algebra
package is imported here.
"""
from __future__ import annotations

import argparse
import copy
import json
from fractions import Fraction
from itertools import combinations
from math import lcm
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "strict_exchange_p4_class9_hand_certificate_rows.json"

H6 = (1, -1, 1, 0, -1, 0)
H17 = (0, -1, 0, -1, 1, 1)
H9 = H14 = (0, -1, 1, 0, 0, 0)
C0 = (3, 4)
C1 = (1, 2, 3, 4)
C2 = (0, 1, 3)
C3 = (1, 3)


def config(order, branches=(), blocker_side=None):
    return {"order": order, "branches": tuple(branches),
            "blocker_side": blocker_side}


STAGE_CONFIGS = {
    "W-root6": config("W", blocker_side="max"),
    "W-root6-z0": config("W"),
    "W-root6-z2": config("W"),
    "W-C0-h17": config("W", (("C0", C0, "max"),)),
    "W-C1-h9": config("W", (("C1", C1, "max"),), "max"),
    "W-C2-h14": config("W", (("C1", C1, "max"), ("C2", C2, "max"))),
    "W-term": config("W", (("C1", C1, "max"), ("C2", C2, "max")), "min"),
    "W-terminal-anchor": config("W", (("C1", C1, "max"), ("C2", C2, "max"))),
    "S-root17": config("S", blocker_side="min"),
    "S-C1-h6-z0": config("S", (("C1m", C1, "min"),)),
    "S-C1-h6-z2": config("S", (("C1m", C1, "min"),)),
    "S-C1-afterC1-h6": config("S", (("C1m", C1, "min"),), "max"),
    "S-direct-C3-h14": config("S", (("C1m", C1, "min"), ("C3", C3, "max"))),
    "S-direct-C3-term": config("S", (("C1m", C1, "min"), ("C3", C3, "max")), "min"),
    "S-direct-anchor": config("S", (("C1m", C1, "min"), ("C3", C3, "max"))),
    "S-C1-h9": config("S", (("C1m", C1, "min"), ("C1M", C1, "max")), "max"),
    "S-long-C3-h14": config("S", (("C1m", C1, "min"), ("C1M", C1, "max"), ("C3", C3, "max"))),
    "S-long-C2-h14": config("S", (("C1m", C1, "min"), ("C1M", C1, "max"), ("C2", C2, "max"))),
    "S-long-C3-term": config("S", (("C1m", C1, "min"), ("C1M", C1, "max"), ("C3", C3, "max")), "min"),
    "S-long-C2-term": config("S", (("C1m", C1, "min"), ("C1M", C1, "max"), ("C2", C2, "max")), "min"),
    "S-long-C3-anchor": config("S", (("C1m", C1, "min"), ("C1M", C1, "max"), ("C3", C3, "max"))),
    "S-long-C2-anchor": config("S", (("C1m", C1, "min"), ("C1M", C1, "max"), ("C2", C2, "max"))),
}


def linear(*terms):
    result = {}
    for multiplier, form in terms:
        multiplier = Fraction(multiplier)
        for name, coefficient in form.items():
            value = result.get(name, Fraction()) + multiplier * coefficient
            if value:
                result[name] = value
            else:
                result.pop(name, None)
    return result


def variable(name):
    return {name: Fraction(1)}


def constant(value):
    value = Fraction(value)
    return {"constant": value} if value else {}


def point_sum(point, players):
    return linear(*((1, point[player]) for player in players))


def comparison(table, name, coalition, left, right):
    table[name] = linear((1, point_sum(left, coalition)),
                         (-1, point_sum(right, coalition)))


def named_system(stage, identity):
    if stage not in STAGE_CONFIGS:
        raise AssertionError(f"unknown stage {stage}")
    cfg = STAGE_CONFIGS[stage]
    x = [variable(f"x{i}") for i in range(6)]
    z = [variable(f"z{i}") for i in range(6)]
    q = [variable(f"q{i}") for i in range(6)]
    inequalities = {}
    for prefix, point in (("x", x), ("z", z), ("q", q)):
        for i in range(6):
            inequalities[f"{prefix}{i}>=0"] = linear((-1, point[i]))
    for i in range(4):
        inequalities[f"d{i}>=0"] = linear((1, z[i]), (-1, x[i]))
    for i in (4, 5):
        inequalities[f"delta{i}>=0"] = linear((1, x[i]), (-1, z[i]))
    for i in range(1, 6):
        inequalities[f"x0<=x{i}"] = linear((1, x[0]), (-1, x[i]))
    for i in (0, 2, 3, 4, 5):
        inequalities[f"z{i}<=z1"] = linear((1, z[i]), (-1, z[1]))
    for name, coalition in (("P4", (0, 1, 2, 4)), ("P5", (1, 2, 5))):
        comparison(inequalities, name + "o", coalition, x, z)
        comparison(inequalities, name + "q", coalition, x, q)
    inequalities[cfg["order"]] = (
        linear((1, x[3]), (-1, x[4])) if cfg["order"] == "W"
        else linear((1, x[4]), (-1, x[3]))
    )
    for name, coalition, side in cfg["branches"]:
        reference, opposite = (x, z) if side == "min" else (z, x)
        comparison(inequalities, name + "o", coalition, reference, opposite)
        comparison(inequalities, name + "q", coalition, reference, q)
    if identity["kind"] == "blocker":
        if cfg["blocker_side"] is None:
            raise AssertionError(f"blocker identity used at non-blocker stage {stage}")
        reference = z if cfg["blocker_side"] == "max" else x
        comparison(inequalities, "Cq", tuple(identity["coalition"]), reference, q)
    hypotheses = {
        "z1<=z0": linear((1, z[1]), (-1, z[0])),
        "z1<=z2": linear((1, z[1]), (-1, z[2])),
        "x3<=x5": linear((1, x[3]), (-1, x[5])),
        "x1<=x2": linear((1, x[1]), (-1, x[2])),
        "x1<=1/3": linear((1, x[1]), (-1, constant(Fraction(1, 3)))),
    }
    for name in identity["inequality_multipliers"]:
        if name in hypotheses:
            inequalities[name] = hypotheses[name]
    equalities = {
        "sumx": linear((1, point_sum(x, range(6))), (-1, constant(1))),
        "sumz": linear((1, point_sum(z, range(6))), (-1, constant(1))),
        "sumq": linear((1, point_sum(q, range(6))), (-1, constant(1))),
        "q1": q[1],
    }
    distance = linear((1, point_sum(x, (0, 1, 2, 3))),
                      (-1, point_sum(z, (0, 1, 2, 3))))
    targets = {
        "D-1/3": linear((1, distance), (-1, constant(Fraction(1, 3)))),
        "d0": linear((1, x[0]), (-1, z[0])),
        "x1-1/3": linear((1, x[1]), (-1, constant(Fraction(1, 3)))),
    }
    if identity["target"] not in targets:
        raise AssertionError(f"unknown target {identity['target']}")
    return inequalities, equalities, targets[identity["target"]]


def verify_use(use, identities):
    if use["identity"] not in identities:
        raise AssertionError(f"unknown identity {use['identity']}")
    identity = identities[use["identity"]]
    if use["kind"] != identity["kind"]:
        raise AssertionError(f"kind mismatch at {use}")
    if identity["kind"] == "blocker":
        if tuple(use["coalition"]) != tuple(identity["coalition"]):
            raise AssertionError(f"coalition mismatch at {use}")
        if use.get("source") != identity.get("source") or use["source"] != "q":
            raise AssertionError(f"source mismatch at {use}")
    inequalities, equalities, target = named_system(use["stage"], identity)
    terms = []
    for name, multiplier in identity["inequality_multipliers"].items():
        multiplier = Fraction(multiplier)
        if name not in inequalities:
            raise AssertionError(f"premise {name} unavailable at {use['stage']}")
        if multiplier < 0:
            raise AssertionError(f"negative inequality multiplier {name}={multiplier}")
        terms.append((multiplier, inequalities[name]))
    for name, multiplier in identity["equality_multipliers"].items():
        if name not in equalities:
            raise AssertionError(f"equality {name} unavailable at {use['stage']}")
        terms.append((Fraction(multiplier), equalities[name]))
    residual = linear((1, linear(*terms)), (-1, target))
    if residual:
        raise AssertionError(f"identity {identity['id']} fails at {use['stage']}: {residual}")
    scale = 1
    values = [Fraction(value) for value in (
        list(identity["inequality_multipliers"].values())
        + list(identity["equality_multipliers"].values())
    )]
    for value in values:
        scale = lcm(scale, value.denominator)
    return {"stage": use["stage"], "identity": identity["id"],
            "kind": identity["kind"], "target": identity["target"],
            **({"coalition": identity["coalition"], "source": "q"}
               if identity["kind"] == "blocker" else {}),
            "integer_scale": scale}


def eligible(direction):
    return [coalition for size in range(1, 6)
            for coalition in combinations(range(6), size)
            if sum(direction[i] for i in coalition) < 0]


def normalize(rows):
    best = {}
    for coefficients, rhs in rows:
        key = tuple(coefficients)
        if key not in best or rhs < best[key]:
            best[key] = rhs
    return [(key, rhs) for key, rhs in best.items()]


def fourier_motzkin_feasible(rows, variable_count):
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


def d_form(coalition):
    # Coordinates: d0,d1,d2,d3,delta4 with
    # delta5=d0+d1+d2+d3-delta4 by efficiency.
    result = [Fraction() for _ in range(5)]
    for player in coalition:
        if player < 4:
            result[player] += 1
        elif player == 4:
            result[4] -= 1
        else:
            for i in range(4):
                result[i] -= 1
            result[4] += 1
    return tuple(result)


def dcone_rows(branches):
    rows = []
    # Strict P-sign magnitudes are homogeneous; normalize each to at least 1.
    for i in range(5):
        coefficients = [Fraction() for _ in range(5)]
        coefficients[i] = -1
        rows.append((tuple(coefficients), Fraction(-1)))
    rows.append(((-1, -1, -1, -1, 1), Fraction(-1)))  # delta5 >= 1
    # Packet sandwich: d0+d1+d2 <= delta4 <= d0+d3.
    rows.extend([
        ((1, 1, 1, 0, -1), Fraction()),
        ((-1, 0, 0, -1, 1), Fraction()),
    ])
    for coalition, side in branches:
        form = d_form(coalition)
        rows.append((form if side == "min" else tuple(-v for v in form),
                     Fraction()))
    return rows


TERMINAL_CANDIDATES = {
    (1, 4), (1, 5), (0, 1, 4), (1, 3, 4), (1, 4, 5),
    (0, 1, 4, 5), (1, 3, 4, 5), (0, 1, 3, 4, 5),
}
STRUCTURAL_STAGES = {
    "W-root6": (H6, "max", (), {(1,), (1, 3), C0, (1, 3, 4),
                                   (1, 3, 5), (0, 1, 3, 4), C1}),
    "W-C0-terminal": (H17, "min", ((C0, "max"),), set()),
    "W-C1-h9": (H9, "max", ((C1, "max"),),
                  {(1,), (0, 1), (1, 3), C2, (0, 1, 5), (1, 3, 4),
                   (1, 3, 5), (0, 1, 3, 4), (0, 1, 3, 5)}),
    "W-term": (H14, "min", ((C1, "max"), (C2, "max")),
               TERMINAL_CANDIDATES | {(0, 1, 5)}),
    "S-root17": (H17, "min", (), {(1, 3, 4), C1}),
    "S-C1-afterC1-h6": (H6, "max", ((C1, "min"),),
                         {(1,), C3, (1, 3, 5), (0, 1, 3, 4), C1}),
    "S-direct-C3-term": (H14, "min", ((C1, "min"), (C3, "max")),
                          TERMINAL_CANDIDATES),
    "S-C1-h9": (H9, "max", ((C1, "min"), (C1, "max")),
                  {(1,), (0, 1), C3, C2, (0, 1, 5), (1, 3, 5),
                   (0, 1, 3, 4), (0, 1, 3, 5)}),
    "S-long-C3-term": (H14, "min", ((C1, "min"), (C1, "max"), (C3, "max")),
                        TERMINAL_CANDIDATES),
    "S-long-C2-term": (H14, "min", ((C1, "min"), (C1, "max"), (C2, "max")),
                        TERMINAL_CANDIDATES),
}


def structural_census(expected_override=None):
    result = {}
    for name, (direction, side, branches, expected) in STRUCTURAL_STAGES.items():
        if expected_override and name in expected_override:
            expected = expected_override[name]
        actual = set()
        for coalition in eligible(direction):
            form = d_form(coalition)
            blocker = form if side == "min" else tuple(-value for value in form)
            if fourier_motzkin_feasible(
                    [*dcone_rows(branches), (blocker, Fraction())], 5):
                actual.add(coalition)
        if actual != expected:
            raise AssertionError(f"structural census changed at {name}: {actual}")
        result[name] = {
            "eligible_cut_count": len(eligible(direction)),
            "opposite_candidate_count": len(actual),
            "opposite_candidates": [list(c) for c in sorted(actual)],
        }
    return result


FILTER_SURVIVORS = {
    "W-root6": {C0, C1},
    "W-C1-h9": {C2},
    "W-term": set(),
    "S-root17": {C1},
    "S-C1-afterC1-h6": {C3, C1},
    "S-direct-C3-term": set(),
    "S-C1-h9": {C3, C2},
    "S-long-C3-term": set(),
    "S-long-C2-term": set(),
}
EXPECTED_ACTIVATION_STAGES = {
    "W-root6-z0", "W-root6-z2", "W-C0-h17", "W-C1-h9", "W-C2-h14",
    "S-C1-h6-z0", "S-C1-h6-z2", "S-direct-C3-h14", "S-C1-h9",
    "S-long-C3-h14", "S-long-C2-h14",
}
EXPECTED_ANCHOR_STAGES = {
    "W-terminal-anchor", "S-direct-anchor", "S-long-C3-anchor", "S-long-C2-anchor",
}


def audit_use_map(uses, identities):
    if len({(u["kind"], u["stage"], tuple(u.get("coalition", ()))) for u in uses}) != len(uses):
        raise AssertionError("duplicate use-map entry")
    blocker_uses = [use for use in uses if use["kind"] == "blocker"]
    actual = {}
    for stage in FILTER_SURVIVORS:
        actual[stage] = {tuple(use["coalition"]) for use in blocker_uses
                         if use["stage"] == stage}
    expected = {stage: STRUCTURAL_STAGES[stage][3] - survivors
                for stage, survivors in FILTER_SURVIVORS.items()}
    if actual != expected:
        raise AssertionError(f"blocker use map is not exhaustive: {actual}")
    activation_stages = [use["stage"] for use in uses if use["kind"] == "activation"]
    if set(activation_stages) != EXPECTED_ACTIVATION_STAGES or len(activation_stages) != 11:
        raise AssertionError(f"activation use map changed: {activation_stages}")
    anchor_stages = [use["stage"] for use in uses if use["kind"] == "anchor"]
    if set(anchor_stages) != EXPECTED_ANCHOR_STAGES or len(anchor_stages) != 4:
        raise AssertionError(f"anchor use map changed: {anchor_stages}")
    used_ids = {use["identity"] for use in uses}
    if used_ids != set(identities):
        raise AssertionError(f"orphan or unused identities: {set(identities) ^ used_ids}")
    return {
        "blocker_uses_by_stage": {stage: len(rows) for stage, rows in expected.items()},
        "activation_stages": sorted(activation_stages),
        "anchor_stages": sorted(anchor_stages),
    }


def audit_target_semantics(uses, identities, strict_targets=frozenset({"d0"})):
    counts = {"D-1/3": 0, "d0": 0, "x1-1/3": 0}
    for use in uses:
        identity = identities[use["identity"]]
        target = identity["target"]
        if target not in counts:
            raise AssertionError(f"unsupported target semantics {target}")
        counts[target] += 1
        if target == "d0" and target not in strict_targets:
            raise AssertionError("d0 use lacks declared strict P-sign semantics")
        if target == "x1-1/3" and not use["stage"].endswith("term"):
            raise AssertionError("threshold blocker used outside a terminal leaf")
        if use["kind"] == "anchor":
            if target != "D-1/3" or "x1<=1/3" not in identity["inequality_multipliers"]:
                raise AssertionError("anchor does not certify the threshold negation")
    if counts != {"D-1/3": 35, "d0": 3, "x1-1/3": 33}:
        raise AssertionError(f"target-use counts changed: {counts}")
    return counts


def expect_rejection(action, message):
    try:
        action()
    except AssertionError:
        return message
    raise AssertionError(f"mutation unexpectedly passed: {message}")


def identity_signature(identity):
    return (
        identity["kind"], identity["target"],
        tuple(identity.get("coalition", ())),
        tuple(sorted(identity["inequality_multipliers"].items())),
        tuple(sorted(identity["equality_multipliers"].items())),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    source = json.loads(args.source.read_text())
    if source.get("schema") != "strict-exchange-p4-class9-hand-certificate-rows-v1":
        raise AssertionError("unexpected proof-object schema")
    if source.get("status") != "FROZEN_PROOF_OBJECT":
        raise AssertionError("proof object is not frozen")
    identities = {row["id"]: row for row in source["identities"]}
    if len(identities) != len(source["identities"]):
        raise AssertionError("duplicate identity id")
    if len({identity_signature(row) for row in identities.values()}) != len(identities):
        raise AssertionError("proof object contains duplicate identities")
    if {kind: sum(row["kind"] == kind for row in identities.values())
            for kind in ("blocker", "activation", "anchor")} != {
                "blocker": 43, "activation": 7, "anchor": 2}:
        raise AssertionError("deduplicated identity counts changed")

    census = structural_census()
    use_map = audit_use_map(source["uses"], identities)
    target_counts = audit_target_semantics(source["uses"], identities)
    checked_uses = [verify_use(use, identities) for use in source["uses"]]

    mutated_identities = copy.deepcopy(identities)
    first = mutated_identities[source["uses"][0]["identity"]]
    premise = next(iter(first["inequality_multipliers"]))
    first["inequality_multipliers"][premise] = str(
        Fraction(first["inequality_multipliers"][premise]) + 1)
    coefficient_mutation = expect_rejection(
        lambda: verify_use(source["uses"][0], mutated_identities),
        "rejected coefficient perturbation")

    incompatible_use = next(copy.deepcopy(use) for use in source["uses"]
                            if use["kind"] == "anchor" and use["identity"] == "T02")
    incompatible_use["stage"] = "W-terminal-anchor"
    use_site_mutation = expect_rejection(
        lambda: verify_use(incompatible_use, identities),
        "rejected identity at a stage lacking its premises")

    removed = set(STRUCTURAL_STAGES["W-root6"][3])
    removed.remove(next(iter(removed)))
    census_mutation = expect_rejection(
        lambda: structural_census({"W-root6": removed}),
        "rejected candidate-set deletion")
    use_map_mutation = expect_rejection(
        lambda: audit_use_map(source["uses"][1:], identities),
        "rejected use-map deletion")
    strict_target_mutation = expect_rejection(
        lambda: audit_target_semantics(source["uses"], identities, frozenset()),
        "rejected removal of strict-target semantics")

    payload = {
        "schema": "strict-exchange-p4-class9-hand-certificate-audit-v1",
        "status": "PASS",
        "scope": "exact difference-cone census, deduplicated weighted identities, and exhaustive use map; pure Fraction arithmetic with no solver or production encoder",
        "packet": {"first_optional_players": [0, 2], "second_optional_players": [2]},
        "order_split": ["x3<=x4", "x3>x4"],
        "identity_counts": {kind: sum(row["kind"] == kind for row in identities.values())
                            for kind in ("blocker", "activation", "anchor")},
        "use_counts": {kind: sum(use["kind"] == kind for use in source["uses"])
                       for kind in ("blocker", "activation", "anchor")},
        "target_use_counts": target_counts,
        "strict_target_semantics": {"d0": "strictly positive by the original P-sign premise"},
        "terminal_anchor": "each terminal branch refutes x1<=1/3; each terminal blocker implies x1<=1/3",
        "structural_census": census,
        "use_map_audit": use_map,
        "coefficient_mutation_control": coefficient_mutation,
        "use_site_mutation_control": use_site_mutation,
        "census_mutation_control": census_mutation,
        "use_map_mutation_control": use_map_mutation,
        "strict_target_mutation_control": strict_target_mutation,
        "checked_uses": checked_uses,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

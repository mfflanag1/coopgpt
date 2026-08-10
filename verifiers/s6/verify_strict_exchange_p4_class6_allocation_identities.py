#!/usr/bin/env python3
"""Verify the exact allocation identities behind all class-6 over-covers.

The stored identities were solver-discovered, but this checker imports no
solver or production encoder.  It reconstructs every named human premise as
an exact affine form and verifies the weighted identities over Q.  With a
``--overcover-details`` file it also checks the complete 155-use link to the
separately regenerated witness supports.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = HERE / "strict_exchange_p4_class6_allocation_identity_rows.json"
COMPACT_OVERCOVERS = HERE / "strict_exchange_p4_class6_overcovers.json"
DIMENSION = 13  # constant, x0,...,x5,z0,...,z5
SIDES = (
    "min", "min", "max", "max", "max", "max", "max", "max", "max",
    "max", "max", "max", "max", "min", "min", "min", "min", "min", "min",
)


def zero():
    return [Fraction() for _ in range(DIMENSION)]


def unit(index, coefficient=1):
    form = zero()
    form[index] = Fraction(coefficient)
    return form


def combine(*terms):
    out = zero()
    for multiplier, form in terms:
        for index, value in enumerate(form):
            out[index] += Fraction(multiplier) * value
    return out


def point_sum(point, coalition):
    offset = 1 if point == "x" else 7
    out = zero()
    for player in coalition:
        out[offset + player] += 1
    return out


def comparison_form(side, coalition):
    x_sum = point_sum("x", coalition)
    z_sum = point_sum("z", coalition)
    # An Lmax blocker has x(C)>=z(C); an Lmin blocker has z(C)>=x(C).
    return combine((1, x_sum), (-1, z_sum)) if side == "max" else combine(
        (1, z_sum), (-1, x_sum)
    )


def premise(source):
    if source == "B0":
        form = point_sum("x", range(6)); form[0] = -1
        return "eq", form
    if source == "B1":
        form = point_sum("z", range(6)); form[0] = -1
        return "eq", form
    match = re.fullmatch(r"B(\d+)", source)
    if match:
        index = int(match.group(1))
        if 2 <= index <= 7:
            return "ge", unit(1 + index - 2)
        if 8 <= index <= 13:
            return "ge", unit(7 + index - 8)
        if 14 <= index <= 17:
            player = index - 14
            return "gt", combine((1, unit(1 + player)), (-1, unit(7 + player)))
        if index in (18, 19):
            player = index - 14
            return "gt", combine((1, unit(7 + player)), (-1, unit(1 + player)))
        if index == 20:
            form = zero(); form[0] = Fraction(-2, 3)
            for player in range(4):
                form[1 + player] += 2
                form[7 + player] -= 2
            return "gt", form
    match = re.fullmatch(r"C(\d+)", source)
    if match:
        index = int(match.group(1))
        if 0 <= index <= 4:
            return "ge", combine((1, unit(2 + index)), (-1, unit(1)))
        if 5 <= index <= 9:
            other = (0, 2, 3, 4, 5)[index - 5]
            return "ge", combine((1, unit(8)), (-1, unit(7 + other)))
    if source in ("P4", "P5"):
        coalition = (0, 1, 4) if source == "P4" else (0, 1, 2, 5)
        return "ge", combine((1, point_sum("z", coalition)), (-1, point_sum("x", coalition)))
    if source == "order-W":
        return "ge", combine((1, unit(5)), (-1, unit(4)))
    if source == "order-S":
        return "gt", combine((1, unit(4)), (-1, unit(5)))
    match = re.fullmatch(r"(?:A\d+|T):h(\d+):C\(([^)]*)\)", source)
    if match:
        direction = int(match.group(1))
        coalition = tuple(int(item) for item in re.findall(r"\d+", match.group(2)))
        return "ge", comparison_form(SIDES[direction], coalition)
    raise AssertionError(f"unknown premise source {source}")


def parsed_form(items):
    return [Fraction(item) for item in items]


def verify_rows(payload):
    identities = payload["identities"]
    uses = payload["uses"]
    if len(identities) != 53 or len(uses) != 155:
        raise AssertionError("class-6 identity census changed")
    identity_map = {row["id"]: row for row in identities}
    if len(identity_map) != len(identities):
        raise AssertionError("duplicate identity id")
    support_sizes = Counter()
    for identity in identities:
        target = parsed_form(identity["target_form"])
        if len(target) != DIMENSION:
            raise AssertionError("wrong target dimension")
        total = zero()
        strict = False
        for row in identity["rows"]:
            kind, form = premise(row["source"])
            if row["kind"] != kind:
                raise AssertionError(f"kind mismatch at {identity['id']}:{row['source']}")
            multiplier = Fraction(row["multiplier"])
            if kind != "eq" and multiplier < 0:
                raise AssertionError("negative inequality multiplier")
            strict |= kind == "gt" and multiplier > 0
            total = combine((1, total), (multiplier, form))
        if total != target:
            raise AssertionError(f"identity mismatch at {identity['id']}")
        if not strict or not identity["strict"]:
            raise AssertionError(f"missing strict premise at {identity['id']}")
        support_sizes[len(identity["rows"])] += 1
    expected_supports = {3: 1, 4: 1, 5: 14, 6: 16, 7: 10, 8: 3, 9: 2, 10: 3, 11: 3}
    if dict(sorted(support_sizes.items())) != expected_supports:
        raise AssertionError(f"identity support census changed: {support_sizes}")
    counts = Counter(use["identity"] for use in uses)
    if set(counts) != set(identity_map):
        raise AssertionError("identity use coverage changed")
    for identity, count in counts.items():
        if identity_map[identity]["use_count"] != count:
            raise AssertionError(f"use count mismatch for {identity}")
    if len({(use["stage"], tuple(use["candidate"])) for use in uses}) != 155:
        raise AssertionError("duplicate class-6 use key")
    categories = Counter()
    identity_categories = Counter()
    path_sources = Counter()
    for identity in identities:
        sources = {row["source"] for row in identity["rows"]}
        if any(source.startswith(("A", "T")) for source in sources):
            category = "path-dependent"
        elif any(source.startswith("P") for source in sources):
            category = "packet-dependent"
        elif any(source.startswith("order") for source in sources):
            category = "order-dependent"
        else:
            category = "anchor/sign only"
        identity_categories[category] += 1
    for use in uses:
        sources = {row["source"] for row in identity_map[use["identity"]]["rows"]}
        if any(source.startswith(("A", "T")) for source in sources):
            category = "path-dependent"
        elif any(source.startswith("P") for source in sources):
            category = "packet-dependent"
        elif any(source.startswith("order") for source in sources):
            category = "order-dependent"
        else:
            category = "anchor/sign only"
        categories[category] += 1
        path_key = ("A" if any(source.startswith("A") for source in sources) else "") + (
            "T" if any(source.startswith("T") for source in sources) else ""
        )
        path_sources[path_key or "none"] += 1
    expected_categories = {
        "anchor/sign only": 57,
        "order-dependent": 37,
        "packet-dependent": 24,
        "path-dependent": 37,
    }
    if dict(categories) != expected_categories:
        raise AssertionError(f"category census changed: {categories}")
    expected_identity_categories = {
        "anchor/sign only": 17,
        "order-dependent": 6,
        "packet-dependent": 8,
        "path-dependent": 22,
    }
    if dict(identity_categories) != expected_identity_categories:
        raise AssertionError(f"identity category census changed: {identity_categories}")
    expected_path_sources = {"none": 118, "A": 33, "AT": 4}
    if dict(path_sources) != expected_path_sources:
        raise AssertionError(f"path-source census changed: {path_sources}")
    return (
        identity_map,
        dict(sorted(support_sizes.items())),
        expected_categories,
        expected_identity_categories,
        expected_path_sources,
    )


def witness_target(certificate):
    target = zero()
    target[0] = -Fraction(certificate["nonanchor_support_bound"])
    loads = [0] * 6
    for row in certificate["used_q_comparisons"]:
        weight = int(row["weight"])
        target = combine((1, target), (weight, point_sum(row["reference"], row["coalition"])))
        for player in row["coalition"]:
            loads[player] += weight
    bound = max(loads[player] for player in range(6) if player != 1)
    if loads != certificate["incidence_loads"] or bound != certificate["nonanchor_support_bound"]:
        raise AssertionError("witness incidence record mismatch")
    return target


def verify_details(payload, identity_map, path):
    details = json.loads(path.read_text())
    certificates = details["certificates"]
    canonical = json.dumps(certificates, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(canonical).hexdigest()
    compact = json.loads(COMPACT_OVERCOVERS.read_text())
    if digest != compact["certificate_sha256"] or digest != details["certificate_sha256"]:
        raise AssertionError("detailed over-cover digest mismatch")
    detail_map = {(row["stage"], tuple(row["candidate"])): row for row in certificates}
    if len(detail_map) != 155:
        raise AssertionError("detailed over-cover census changed")
    for use in payload["uses"]:
        key = use["stage"], tuple(use["candidate"])
        if key not in detail_map:
            raise AssertionError(f"missing detailed use {key}")
        target = witness_target(detail_map[key])
        if target != parsed_form(identity_map[use["identity"]]["target_form"]):
            raise AssertionError(f"witness/allocation target mismatch at {key}")
    return digest


def expect_rejection(payload, mutate):
    trial = copy.deepcopy(payload)
    mutate(trial)
    try:
        verify_rows(trial)
    except AssertionError:
        return "rejected"
    raise AssertionError("mutation unexpectedly passed")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=Path, default=ROWS)
    parser.add_argument("--overcover-details", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.rows.read_text())
    identity_map, supports, categories, identity_categories, path_sources = verify_rows(payload)
    digest = verify_details(payload, identity_map, args.overcover_details) if args.overcover_details else None
    multiplier_mutation = expect_rejection(
        payload,
        lambda trial: trial["identities"][0]["rows"][0].update(multiplier="0"),
    )
    strict_mutation = expect_rejection(
        payload,
        lambda trial: [row.update(kind="ge") for row in trial["identities"][0]["rows"] if row["kind"] == "gt"],
    )
    report = {
        "schema": "strict-exchange-p4-class6-allocation-identity-audit-v1",
        "status": "PASS",
        "scope": "solver-free exact-rational audit of 53 allocation identities at 155 witness-filter uses; use map is an integration record, not independent human-to-machine evidence",
        "identity_count": len(payload["identities"]),
        "use_count": len(payload["uses"]),
        "identity_support_sizes": supports,
        "identity_categories": identity_categories,
        "use_categories": categories,
        "path_source_uses": path_sources,
        "detailed_overcover_sha256": digest,
        "mutation_controls": {
            "coefficient": multiplier_mutation,
            "strict_semantics": strict_mutation,
        },
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

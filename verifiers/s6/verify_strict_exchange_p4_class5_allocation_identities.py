#!/usr/bin/env python3
"""Verify exact allocation identities for all 184 class-5 cut exclusions.

The stored rows were solver-discovered.  This checker imports no solver or
production encoder.  It checks all affine identities over Q, strictness,
premise availability on every relay path, and optional digest linkage to a
freshly regenerated context/target incidence audit.
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

from verify_strict_exchange_p4_class6_allocation_identities import (
    DIMENSION,
    combine,
    premise,
    witness_target,
    zero,
)

HERE = Path(__file__).resolve().parent
ROWS = HERE / "strict_exchange_p4_class5_allocation_identity_rows.json"
COMPACT = HERE / "strict_exchange_p4_class5_overcovers.json"


def parsed_form(items):
    return [Fraction(item) for item in items]


def stage_sources(use):
    stage = use["stage"]
    order = stage[0]
    tokens = re.findall(r"h(\d+)(?:C(\d+))?", stage)
    if order not in ("W", "S") or not tokens or tokens[-1][1]:
        raise AssertionError(f"bad stage syntax {stage}")
    direction = int(tokens[-1][0])
    if direction != use["direction_index"]:
        raise AssertionError(f"direction mismatch at {stage}")
    available = {f"B{index}" for index in range(21)}
    available |= {f"C{index}" for index in range(10)}
    available |= {"P4", "P5", f"order-{order}"}
    for depth, (parent, digits) in enumerate(tokens[:-1]):
        cut = tuple(int(digit) for digit in digits)
        available.add(f"A{depth}:h{int(parent)}:C{cut}")
    available.add(f"T:h{direction}:C{tuple(use['candidate'])}")
    return available


def path_key(identity):
    sources = {row["source"] for row in identity["rows"]}
    return (("A" if any(source.startswith("A") for source in sources) else "")
            + ("T" if any(source.startswith("T") for source in sources) else "")) or "none"


def verify_rows(payload):
    if payload.get("schema") != "strict-exchange-p4-class5-allocation-identities-v1":
        raise AssertionError("unexpected class-5 identity schema")
    identities = payload["identities"]
    uses = payload["uses"]
    if len(identities) != 107 or len(uses) != 184:
        raise AssertionError("class-5 identity census changed")
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
            kind, form = premise(row["source"], packet5=(0, 1, 5))
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
    expected_supports = {3: 2, 5: 19, 6: 40, 7: 26, 8: 14, 9: 1, 10: 3, 11: 2}
    if dict(sorted(support_sizes.items())) != expected_supports:
        raise AssertionError(f"identity support census changed: {support_sizes}")
    counts = Counter(use["identity"] for use in uses)
    if set(counts) != set(identity_map):
        raise AssertionError("identity use coverage changed")
    keys = {(use["layer"], use["stage"], tuple(use["candidate"])) for use in uses}
    if len(keys) != 184:
        raise AssertionError("duplicate class-5 use key")
    if Counter(use["layer"] for use in uses) != {"context": 34, "target": 150}:
        raise AssertionError("class-5 layer census changed")
    for use in uses:
        identity = identity_map[use["identity"]]
        if identity["direction_index"] != use["direction_index"]:
            raise AssertionError(f"identity direction mismatch at {use['stage']}")
        if identity["use_count"] != counts[use["identity"]]:
            raise AssertionError(f"use count mismatch for {use['identity']}")
        unavailable = {row["source"] for row in identity["rows"]} - stage_sources(use)
        if unavailable:
            raise AssertionError(f"unavailable premises at {use['stage']}: {unavailable}")
    path_sources = Counter(path_key(identity_map[use["identity"]]) for use in uses)
    expected_paths = {"none": 94, "A": 50, "T": 38, "AT": 2}
    if dict(path_sources) != expected_paths:
        raise AssertionError(f"path-source census changed: {path_sources}")
    return identity_map, dict(sorted(support_sizes.items())), expected_paths


def verify_details(payload, identity_map, path):
    details = json.loads(path.read_text())
    compact = json.loads(COMPACT.read_text())
    detail_map = {}
    digests = {}
    for layer in ("context", "target"):
        certificates = details[f"{layer}_certificates"]
        canonical = json.dumps(certificates, sort_keys=True, separators=(",", ":")).encode()
        digest = hashlib.sha256(canonical).hexdigest()
        if digest != details[f"{layer}_certificate_sha256"] or digest != compact[f"{layer}_certificate_sha256"]:
            raise AssertionError(f"{layer} over-cover digest mismatch")
        digests[layer] = digest
        for row in certificates:
            key = layer, row["stage"], tuple(row["candidate"])
            if key in detail_map:
                raise AssertionError(f"duplicate detailed use {key}")
            detail_map[key] = row
    if len(detail_map) != 184:
        raise AssertionError("detailed class-5 census changed")
    for use in payload["uses"]:
        key = use["layer"], use["stage"], tuple(use["candidate"])
        if key not in detail_map:
            raise AssertionError(f"missing detailed class-5 use {key}")
        target = witness_target(detail_map[key])
        if target != parsed_form(identity_map[use["identity"]]["target_form"]):
            raise AssertionError(f"incidence/allocation target mismatch at {key}")
    return digests


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
    identity_map, supports, path_sources = verify_rows(payload)
    digests = verify_details(payload, identity_map, args.overcover_details) if args.overcover_details else None
    coefficient_mutation = expect_rejection(
        payload, lambda trial: trial["identities"][0]["rows"][0].update(multiplier="0"))
    premise_site_mutation = expect_rejection(
        payload, lambda trial: trial["uses"][0].update(stage="W-h16"))
    strict_mutation = expect_rejection(
        payload,
        lambda trial: [row.update(kind="ge") for row in trial["identities"][0]["rows"]
                       if row["kind"] == "gt"],
    )
    report = {
        "schema": "strict-exchange-p4-class5-allocation-identity-audit-v1",
        "status": "PASS",
        "scope": "solver-free exact-rational audit of 107 identities at all 184 context/target exclusions; use maps remain integration records",
        "identity_count": len(payload["identities"]),
        "use_count": len(payload["uses"]),
        "layer_use_counts": dict(sorted(Counter(use["layer"] for use in payload["uses"]).items())),
        "identity_support_sizes": supports,
        "path_source_uses": path_sources,
        "detailed_overcover_sha256": digests,
        "mutation_controls": {
            "coefficient": coefficient_mutation,
            "premise_site": premise_site_mutation,
            "strict_semantics": strict_mutation,
        },
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

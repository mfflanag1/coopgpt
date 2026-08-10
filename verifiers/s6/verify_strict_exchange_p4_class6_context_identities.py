#!/usr/bin/env python3
"""Verify the exact allocation identities for 11 class-6 context exclusions.

The stored rows were solver-discovered.  This checker imports no solver or
production encoder: it reconstructs named affine premises over Q, checks every
identity coefficient exactly, checks that each premise is available at each
declared relay site, and links the targets to a regenerated detailed incidence
audit when ``--context-details`` is supplied.
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
ROWS = HERE / "strict_exchange_p4_class6_context_identity_rows.json"
COMPACT = HERE / "strict_exchange_p4_class6_context_overcovers.json"


def parsed_form(items):
    return [Fraction(item) for item in items]


def stage_sources(use):
    stage = use["stage"]
    order = stage[0]
    if order not in ("W", "S"):
        raise AssertionError(f"bad stage order {stage}")
    tokens = re.findall(r"h(\d+)(?:C(\d+))?", stage)
    if not tokens or tokens[-1][1]:
        raise AssertionError(f"bad stage syntax {stage}")
    branches = tokens[:-1]
    direction = int(tokens[-1][0])
    if direction != use["direction_index"]:
        raise AssertionError(f"direction mismatch at {stage}")
    available = {f"B{index}" for index in range(21)}
    available |= {f"C{index}" for index in range(10)}
    available |= {"P4", "P5", f"order-{order}"}
    for depth, (parent, digits) in enumerate(branches):
        cut = tuple(int(digit) for digit in digits)
        available.add(f"A{depth}:h{int(parent)}:C{cut}")
    available.add(f"T:h{direction}:C{tuple(use['candidate'])}")
    return available


def verify_rows(payload):
    if payload.get("schema") != "strict-exchange-p4-class6-context-allocation-identities-v1":
        raise AssertionError("unexpected context identity schema")
    identities = payload["identities"]
    uses = payload["uses"]
    if len(identities) != 9 or len(uses) != 11:
        raise AssertionError("context identity census changed")
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
    expected_supports = {6: 2, 7: 1, 8: 1, 10: 4, 11: 1}
    if dict(sorted(support_sizes.items())) != expected_supports:
        raise AssertionError(f"identity support census changed: {support_sizes}")
    counts = Counter(use["identity"] for use in uses)
    if set(counts) != set(identity_map):
        raise AssertionError("identity use coverage changed")
    keys = {(use["stage"], tuple(use["candidate"])) for use in uses}
    if len(keys) != 11:
        raise AssertionError("duplicate context use key")
    for use in uses:
        identity = identity_map[use["identity"]]
        if identity["direction_index"] != use["direction_index"]:
            raise AssertionError(f"identity direction mismatch at {use['stage']}")
        if identity["use_count"] != counts[use["identity"]]:
            raise AssertionError(f"use count mismatch for {use['identity']}")
        unavailable = {row["source"] for row in identity["rows"]} - stage_sources(use)
        if unavailable:
            raise AssertionError(f"unavailable premises at {use['stage']}: {unavailable}")
    return identity_map, dict(sorted(support_sizes.items()))


def verify_details(payload, identity_map, path):
    details = json.loads(path.read_text())
    certificates = details["certificates"]
    canonical = json.dumps(certificates, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(canonical).hexdigest()
    compact = json.loads(COMPACT.read_text())
    if digest != details["certificate_sha256"] or digest != compact["certificate_sha256"]:
        raise AssertionError("context over-cover digest mismatch")
    detail_map = {(row["stage"], tuple(row["candidate"])): row for row in certificates}
    if len(detail_map) != 11:
        raise AssertionError("detailed context census changed")
    for use in payload["uses"]:
        key = use["stage"], tuple(use["candidate"])
        if key not in detail_map:
            raise AssertionError(f"missing detailed context use {key}")
        target = witness_target(detail_map[key])
        if target != parsed_form(identity_map[use["identity"]]["target_form"]):
            raise AssertionError(f"context/allocation target mismatch at {key}")
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
    parser.add_argument("--context-details", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.rows.read_text())
    identity_map, supports = verify_rows(payload)
    digest = verify_details(payload, identity_map, args.context_details) if args.context_details else None
    coefficient_mutation = expect_rejection(
        payload, lambda trial: trial["identities"][0]["rows"][0].update(multiplier="0")
    )
    premise_site_mutation = expect_rejection(
        payload, lambda trial: trial["uses"][0].update(stage="W-h7")
    )
    strict_mutation = expect_rejection(
        payload,
        lambda trial: [row.update(kind="ge") for row in trial["identities"][0]["rows"]
                       if row["kind"] == "gt"],
    )
    report = {
        "schema": "strict-exchange-p4-class6-context-identity-audit-v1",
        "status": "PASS",
        "scope": "solver-free exact-rational audit of nine identities at all 11 pre-witness context exclusions; use map is an integration record, not independent human-to-machine evidence",
        "identity_count": len(payload["identities"]),
        "use_count": len(payload["uses"]),
        "identity_support_sizes": supports,
        "detailed_context_sha256": digest,
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

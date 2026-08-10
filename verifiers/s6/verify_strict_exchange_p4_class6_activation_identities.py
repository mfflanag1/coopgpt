#!/usr/bin/env python3
"""Verify exact class-6 activation over-cover allocation identities.

The identities were solver-discovered.  This checker imports no solver or
production encoder: it reconstructs every affine premise and checks the 36
lower-bound identities plus the one direct contradiction over Q.  An optional
detailed activation census links the identities to all sparse incidence rows.
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
    combine,
    parsed_form,
    point_sum,
    premise as common_premise,
    witness_target,
    zero,
)

HERE = Path(__file__).resolve().parent
ROWS = HERE / "strict_exchange_p4_class6_activation_identity_rows.json"
COMPACT = HERE / "strict_exchange_p4_class6_activation_overcovers.json"


def coordinate(point, player):
    form = zero()
    form[(1 if point == "x" else 7) + player] = 1
    return form


def difference(high_point, high_player, low_point, low_player):
    return combine(
        (1, coordinate(high_point, high_player)),
        (-1, coordinate(low_point, low_player)),
    )


def failure_premise(source, direction, failure_case):
    match = re.fullmatch(r"F(\d+)\.(\d+)", source)
    if not match:
        return common_premise(source)
    case, atom = map(int, match.groups())
    if case != failure_case:
        raise AssertionError(f"failure source {source} used in case {failure_case}")
    forms = {
        (7, 1): (difference("z", 2, "z", 1),),
        (11, 0): (difference("z", 3, "z", 4), difference("z", 3, "z", 5)),
        (12, 0): (difference("z", 2, "z", 4), difference("z", 2, "z", 5)),
        (17, 0): (difference("x", 4, "x", 3), difference("x", 5, "x", 3)),
        (18, 0): (difference("x", 4, "x", 2), difference("x", 5, "x", 2)),
        (18, 1): (difference("x", 4, "x", 2), difference("x", 5, "x", 3)),
    }
    if (direction, failure_case) not in forms or atom >= len(forms[(direction, failure_case)]):
        raise AssertionError(f"unknown failure premise {direction}:{source}")
    return "ge", forms[(direction, failure_case)][atom]


def verify_identity(identity, contradiction=False):
    total = zero()
    strict = False
    for row in identity["rows"]:
        kind, form = failure_premise(
            row["source"], identity["direction_index"], identity["failure_case"]
        )
        if row["kind"] != kind:
            raise AssertionError(f"kind mismatch at {identity['id']}:{row['source']}")
        multiplier = Fraction(row["multiplier"])
        if kind != "eq" and multiplier < 0:
            raise AssertionError("negative inequality multiplier")
        strict |= kind == "gt" and multiplier > 0
        total = combine((1, total), (multiplier, form))
    target = zero() if contradiction else parsed_form(identity["target_form"])
    if total != target:
        raise AssertionError(f"identity mismatch at {identity['id']}")
    if not strict or (not contradiction and not identity["strict"]):
        raise AssertionError(f"missing strict premise at {identity['id']}")


def category(identity):
    sources = {row["source"] for row in identity["rows"]}
    if any(source.startswith("A") for source in sources):
        return "path-dependent"
    if any(source.startswith("P") for source in sources):
        return "packet-dependent"
    if any(source.startswith("order") for source in sources):
        return "order-dependent"
    return "anchor/sign only"


def verify_rows(payload):
    identities, uses = payload["identities"], payload["uses"]
    if len(identities) != 26 or len(uses) != 36:
        raise AssertionError("activation identity census changed")
    identity_map = {row["id"]: row for row in identities}
    if len(identity_map) != 26:
        raise AssertionError("duplicate activation identity id")
    supports = Counter()
    identity_categories = Counter()
    for identity in identities:
        verify_identity(identity)
        supports[len(identity["rows"])] += 1
        identity_categories[category(identity)] += 1
    expected_supports = {5: 3, 7: 7, 8: 7, 9: 1, 10: 2, 11: 5, 12: 1}
    if dict(sorted(supports.items())) != expected_supports:
        raise AssertionError(f"activation support census changed: {supports}")
    expected_identity_categories = {
        "anchor/sign only": 7,
        "order-dependent": 2,
        "packet-dependent": 6,
        "path-dependent": 11,
    }
    if dict(identity_categories) != expected_identity_categories:
        raise AssertionError(f"activation identity categories changed: {identity_categories}")
    counts = Counter(use["identity"] for use in uses)
    if set(counts) != set(identity_map):
        raise AssertionError("activation identity coverage changed")
    use_categories = Counter()
    for use in uses:
        identity = identity_map[use["identity"]]
        if (
            use["direction_index"] != identity["direction_index"]
            or use["failure_case"] != identity["failure_case"]
        ):
            raise AssertionError("activation use type mismatch")
        if counts[use["identity"]] != identity["use_count"]:
            raise AssertionError("activation identity use count mismatch")
        use_categories[category(identity)] += 1
    expected_use_categories = {
        "anchor/sign only": 8,
        "order-dependent": 2,
        "packet-dependent": 9,
        "path-dependent": 17,
    }
    if dict(use_categories) != expected_use_categories:
        raise AssertionError(f"activation use categories changed: {use_categories}")
    direct = payload["direct_identity"]
    verify_identity(direct, contradiction=True)
    if len(payload["direct_uses"]) != direct["use_count"] or direct["use_count"] != 4:
        raise AssertionError("direct activation use count changed")
    if any(
        use["direction_index"] != 7 or use["failure_case"] != 1
        for use in payload["direct_uses"]
    ):
        raise AssertionError("direct activation type changed")
    return identity_map, expected_supports, expected_identity_categories, expected_use_categories


def verify_details(payload, identity_map, path):
    details = json.loads(path.read_text())
    certificates = details["certificates"]
    canonical = json.dumps(certificates, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(canonical).hexdigest()
    compact = json.loads(COMPACT.read_text())
    if digest != compact["certificate_sha256"] or digest != details["certificate_sha256"]:
        raise AssertionError("activation over-cover digest mismatch")
    detail_map = {
        (row["stage"], row["direction_index"], row["failure_case"]): row
        for row in certificates
    }
    if len(detail_map) != 36:
        raise AssertionError("activation detail census changed")
    for use in payload["uses"]:
        key = use["stage"], use["direction_index"], use["failure_case"]
        if key not in detail_map:
            raise AssertionError(f"missing activation detail {key}")
        target = witness_target(detail_map[key])
        if target != parsed_form(identity_map[use["identity"]]["target_form"]):
            raise AssertionError(f"activation target mismatch at {key}")
    compact_direct = {
        (row["stage"], row["direction_index"], row["failure_case"])
        for row in compact["direct_allocation_cases"]
    }
    stored_direct = {
        (row["stage"], row["direction_index"], row["failure_case"])
        for row in payload["direct_uses"]
    }
    if compact_direct != stored_direct:
        raise AssertionError("direct activation map mismatch")
    return digest


def expect_rejection(payload, mutate):
    trial = copy.deepcopy(payload)
    mutate(trial)
    try:
        verify_rows(trial)
    except AssertionError:
        return "rejected"
    raise AssertionError("activation mutation unexpectedly passed")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=Path, default=ROWS)
    parser.add_argument("--overcover-details", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.rows.read_text())
    identity_map, supports, identity_categories, use_categories = verify_rows(payload)
    digest = verify_details(payload, identity_map, args.overcover_details) if args.overcover_details else None
    coefficient_mutation = expect_rejection(
        payload, lambda trial: trial["identities"][0]["rows"][0].update(multiplier="0")
    )
    failure_mutation = expect_rejection(
        payload, lambda trial: trial["identities"][0].update(failure_case=9)
    )
    report = {
        "schema": "strict-exchange-p4-class6-activation-identity-audit-v1",
        "status": "PASS",
        "scope": "solver-free exact-rational audit of 26 activation lower-bound identities at 36 witness uses and one direct identity at four uses; coverage remains relay-derived",
        "identity_count": len(payload["identities"]),
        "witness_use_count": len(payload["uses"]),
        "direct_identity_count": 1,
        "direct_use_count": len(payload["direct_uses"]),
        "identity_support_sizes": supports,
        "identity_categories": identity_categories,
        "use_categories": use_categories,
        "detailed_overcover_sha256": digest,
        "mutation_controls": {
            "coefficient": coefficient_mutation,
            "failure_semantics": failure_mutation,
        },
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

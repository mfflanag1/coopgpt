#!/usr/bin/env python3
"""Verify every exact class-5 activation identity without a solver.

The stored identities were solver-discovered.  This checker independently
reconstructs their named affine premises over Q, checks path availability and
strictness, and links all 195 zero-target contradictions plus all 90 witness
lower bounds to a freshly regenerated activation census when requested.
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
    parsed_form,
    point_sum,
    premise as common_premise,
    witness_target,
    zero,
)

HERE = Path(__file__).resolve().parent
ROWS = HERE / "strict_exchange_p4_class5_activation_identity_rows.json"
COMPACT = HERE / "strict_exchange_p4_class5_activation_overcovers.json"


def coordinate(point, player):
    form = zero()
    form[(1 if point == "x" else 7) + player] = 1
    return form


def difference(high_point, high_player, low_point, low_player):
    return combine(
        (1, coordinate(high_point, high_player)),
        (-1, coordinate(low_point, low_player)),
    )


def failure_forms(direction, failure_case):
    forms = {
        (7, 0): (difference("z", 0, "z", 1),),
        (7, 1): (difference("z", 2, "z", 1),),
        (10, 0): (difference("z", 0, "z", 1),),
        (11, 0): (difference("z", 3, "z", 4), difference("z", 3, "z", 5)),
        (12, 0): (difference("z", 2, "z", 4), difference("z", 2, "z", 5)),
        (15, 0): (difference("x", 0, "x", 1),),
        (16, 0): (difference("x", 4, "x", 1), difference("x", 5, "x", 1)),
        (16, 1): (difference("x", 4, "x", 1), difference("x", 5, "x", 2)),
        (16, 2): (difference("x", 4, "x", 2), difference("x", 5, "x", 1)),
        (16, 3): (difference("x", 4, "x", 2), difference("x", 5, "x", 2)),
        (17, 0): (difference("x", 4, "x", 3), difference("x", 5, "x", 3)),
        (17, 1): (difference("x", 4, "x", 3), difference("x", 5, "x", 1)),
        (17, 2): (difference("x", 4, "x", 1), difference("x", 5, "x", 3)),
        (17, 3): (difference("x", 4, "x", 1), difference("x", 5, "x", 1)),
        (18, 0): (difference("x", 4, "x", 2), difference("x", 5, "x", 2)),
        (18, 1): (difference("x", 4, "x", 2), difference("x", 5, "x", 3)),
        (18, 2): (difference("x", 4, "x", 3), difference("x", 5, "x", 2)),
        (18, 3): (difference("x", 4, "x", 3), difference("x", 5, "x", 3)),
    }
    try:
        return forms[(direction, failure_case)]
    except KeyError as error:
        raise AssertionError(f"unknown activation failure {direction}:{failure_case}") from error


def activation_premise(source, direction, failure_case):
    match = re.fullmatch(r"F(\d+)\.(\d+)", source)
    if not match:
        return common_premise(source, packet5=(0, 1, 5))
    case, atom = map(int, match.groups())
    if case != failure_case:
        raise AssertionError(f"failure source {source} used in case {failure_case}")
    forms = failure_forms(direction, failure_case)
    if atom >= len(forms):
        raise AssertionError(f"unknown failure atom {direction}:{source}")
    return "ge", forms[atom]


def stage_sources(use):
    stage = use["stage"]
    order = stage[0]
    tokens = re.findall(r"h(\d+)(?:C(\d+))?", stage)
    if order not in ("W", "S") or not tokens or tokens[-1][1]:
        raise AssertionError(f"bad stage syntax {stage}")
    direction = int(tokens[-1][0])
    if direction != use["direction_index"]:
        raise AssertionError(f"direction mismatch at {stage}")
    failure = failure_forms(direction, use["failure_case"])
    available = {f"B{index}" for index in range(21)}
    available |= {f"C{index}" for index in range(10)}
    available |= {"P4", "P5", f"order-{order}"}
    for depth, (parent, digits) in enumerate(tokens[:-1]):
        cut = tuple(int(digit) for digit in digits)
        available.add(f"A{depth}:h{int(parent)}:C{cut}")
    available |= {f"F{use['failure_case']}.{atom}" for atom in range(len(failure))}
    return available


def category(identity):
    sources = {row["source"] for row in identity["rows"]}
    if any(source.startswith("A") for source in sources):
        return "path-dependent"
    if any(source.startswith("P") for source in sources):
        return "packet-dependent"
    if any(source.startswith("order") for source in sources):
        return "order-dependent"
    return "anchor/sign only"


def rich_swap(form):
    swapped = list(form)
    swapped[5], swapped[6] = swapped[6], swapped[5]
    swapped[11], swapped[12] = swapped[12], swapped[11]
    return swapped


def affine_signature(identity, swap=False):
    """Forget source aliases and canonicalize the exact identity under 4<->5."""
    rows = []
    for row in identity["rows"]:
        kind, form = activation_premise(
            row["source"], identity["direction_index"], identity["failure_case"]
        )
        if swap:
            form = rich_swap(form)
        rows.append((kind, Fraction(row["multiplier"]), tuple(form)))
    target = parsed_form(identity["target_form"])
    if swap:
        target = rich_swap(target)
    return identity["direction_index"], tuple(sorted(rows, key=repr)), tuple(target)


def motif_key(identity):
    direct = repr(affine_signature(identity))
    swapped = repr(affine_signature(identity, swap=True))
    return min(direct, swapped)


def verify_rows(payload):
    if payload.get("schema") != "strict-exchange-p4-class5-activation-allocation-identities-v1":
        raise AssertionError("unexpected class-5 activation identity schema")
    identities, uses = payload["identities"], payload["uses"]
    if len(identities) != 72 or len(uses) != 285:
        raise AssertionError("class-5 activation identity census changed")
    identity_map = {identity["id"]: identity for identity in identities}
    if len(identity_map) != len(identities):
        raise AssertionError("duplicate activation identity id")
    support_sizes = Counter()
    identity_categories = Counter()
    for identity in identities:
        target = parsed_form(identity["target_form"])
        if len(target) != DIMENSION:
            raise AssertionError("wrong target dimension")
        total = zero()
        strict = False
        for row in identity["rows"]:
            kind, form = activation_premise(
                row["source"], identity["direction_index"], identity["failure_case"]
            )
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
        identity_categories[category(identity)] += 1
    expected_supports = {2: 4, 4: 11, 5: 9, 6: 5, 7: 9, 8: 18, 9: 4, 10: 10, 11: 2}
    if dict(sorted(support_sizes.items())) != expected_supports:
        raise AssertionError(f"activation support census changed: {support_sizes}")
    expected_identity_categories = {
        "anchor/sign only": 29,
        "order-dependent": 12,
        "path-dependent": 31,
    }
    if dict(identity_categories) != expected_identity_categories:
        raise AssertionError(f"activation identity categories changed: {identity_categories}")
    counts = Counter(use["identity"] for use in uses)
    if set(counts) != set(identity_map):
        raise AssertionError("activation identity coverage changed")
    keys = {
        (use["stage"], use["direction_index"], use["failure_case"])
        for use in uses
    }
    if len(keys) != 285:
        raise AssertionError("duplicate activation use key")
    layers = Counter(use["layer"] for use in uses)
    if layers != {"allocation-infeasible": 195, "witness": 90}:
        raise AssertionError(f"activation layer census changed: {layers}")
    use_categories = Counter()
    for use in uses:
        identity = identity_map[use["identity"]]
        if (use["direction_index"], use["failure_case"]) != (
            identity["direction_index"], identity["failure_case"]
        ):
            raise AssertionError(f"activation identity type mismatch at {use['stage']}")
        if identity["use_count"] != counts[use["identity"]]:
            raise AssertionError(f"activation use count mismatch for {use['identity']}")
        unavailable = {row["source"] for row in identity["rows"]} - stage_sources(use)
        if unavailable:
            raise AssertionError(f"unavailable activation premises at {use['stage']}: {unavailable}")
        target_is_zero = not any(parsed_form(identity["target_form"]))
        if target_is_zero != (use["layer"] == "allocation-infeasible"):
            raise AssertionError(f"activation layer/target mismatch at {use['stage']}")
        use_categories[category(identity)] += 1
    expected_use_categories = {
        "anchor/sign only": 202,
        "order-dependent": 51,
        "path-dependent": 32,
    }
    if dict(use_categories) != expected_use_categories:
        raise AssertionError(f"activation use categories changed: {use_categories}")
    motifs = {}
    for identity in identities:
        motifs.setdefault(motif_key(identity), []).append(identity["id"])
    motif_sizes = Counter(len(group) for group in motifs.values())
    if motif_sizes != {1: 29, 2: 12, 3: 5, 4: 1}:
        raise AssertionError(f"activation affine-motif census changed: {motif_sizes}")
    path_motifs = {
        key: group for key, group in motifs.items()
        if category(identity_map[group[0]]) == "path-dependent"
    }
    if len(motifs) != 47 or len(path_motifs) != 20:
        raise AssertionError("activation affine-motif counts changed")
    if any(
        len({category(identity_map[identity]) for identity in group}) != 1
        for group in motifs.values()
    ):
        raise AssertionError("activation motif mixes path and path-free identities")
    path_residuals = Counter(
        (use["direction_index"], use["failure_case"])
        for use in uses if category(identity_map[use["identity"]]) == "path-dependent"
    )
    expected_path_residuals = {
        (11, 0): 4, (12, 0): 4,
        (16, 0): 2, (16, 1): 1, (16, 2): 1, (16, 3): 9,
        (17, 0): 2, (18, 0): 6, (18, 1): 3,
    }
    if dict(path_residuals) != expected_path_residuals:
        raise AssertionError(f"activation path residuals changed: {path_residuals}")
    compression = {
        "path_free_identity_count": 41,
        "path_free_use_count": 253,
        "path_dependent_identity_count": 31,
        "path_dependent_use_count": 32,
        "affine_motif_count": len(motifs),
        "path_free_affine_motif_count": len(motifs) - len(path_motifs),
        "path_dependent_affine_motif_count": len(path_motifs),
        "path_residual_groups": {
            f"h{direction}:failure{failure}": count
            for (direction, failure), count in sorted(path_residuals.items())
        },
    }
    return (
        identity_map,
        dict(sorted(support_sizes.items())),
        expected_identity_categories,
        expected_use_categories,
        compression,
    )


def verify_details(payload, identity_map, path):
    details = json.loads(path.read_text())
    compact = json.loads(COMPACT.read_text())
    certificates = details["certificates"]
    canonical = json.dumps(certificates, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(canonical).hexdigest()
    if digest != details["certificate_sha256"] or digest != compact["certificate_sha256"]:
        raise AssertionError("class-5 activation over-cover digest mismatch")
    witness_map = {
        (row["stage"], row["direction_index"], row["failure_case"]): row
        for row in certificates
    }
    direct_keys = {
        (row["stage"], row["direction_index"], row["failure_case"])
        for row in compact["allocation_infeasible_cases"]
    }
    if len(witness_map) != 90 or len(direct_keys) != 195 or witness_map.keys() & direct_keys:
        raise AssertionError("class-5 activation detail partition changed")
    stored_witness = {
        (use["stage"], use["direction_index"], use["failure_case"])
        for use in payload["uses"] if use["layer"] == "witness"
    }
    stored_direct = {
        (use["stage"], use["direction_index"], use["failure_case"])
        for use in payload["uses"] if use["layer"] == "allocation-infeasible"
    }
    if stored_witness != set(witness_map) or stored_direct != direct_keys:
        raise AssertionError("class-5 activation use/detail map mismatch")
    for use in payload["uses"]:
        if use["layer"] != "witness":
            continue
        key = use["stage"], use["direction_index"], use["failure_case"]
        target = witness_target(witness_map[key])
        if target != parsed_form(identity_map[use["identity"]]["target_form"]):
            raise AssertionError(f"activation incidence/identity mismatch at {key}")
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
    identity_map, supports, identity_categories, use_categories, compression = verify_rows(payload)
    digest = (
        verify_details(payload, identity_map, args.overcover_details)
        if args.overcover_details else None
    )
    coefficient_mutation = expect_rejection(
        payload, lambda trial: trial["identities"][0]["rows"][0].update(multiplier="0")
    )
    failure_mutation = expect_rejection(
        payload, lambda trial: trial["uses"][0].update(failure_case=9)
    )
    layer_mutation = expect_rejection(
        payload, lambda trial: trial["uses"][0].update(layer="witness")
    )
    path_use_index = next(
        index for index, use in enumerate(payload["uses"])
        if category(identity_map[use["identity"]]) == "path-dependent"
    )
    path_site_mutation = expect_rejection(
        payload, lambda trial: trial["uses"][path_use_index].update(stage="S-h11")
    )
    report = {
        "schema": "strict-exchange-p4-class5-activation-identity-audit-v1",
        "status": "PASS",
        "scope": "solver-free exact-rational audit of 72 identities at all 285 class-5 activation failures, with 47 affine motifs and a 32-use path residual; relay semantics remain an external-review obligation",
        "identity_count": len(payload["identities"]),
        "use_count": len(payload["uses"]),
        "layer_use_counts": dict(sorted(Counter(use["layer"] for use in payload["uses"]).items())),
        "identity_support_sizes": supports,
        "identity_categories": identity_categories,
        "use_categories": use_categories,
        "map_compression": compression,
        "detailed_overcover_sha256": digest,
        "mutation_controls": {
            "coefficient": coefficient_mutation,
            "failure_semantics": failure_mutation,
            "layer_partition": layer_mutation,
            "path_site": path_site_mutation,
        },
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
r"""Exact controls for the dimension-free one-aligned-spoke star (PXC54).

The proof is human algebra.  This driver scans finite n=6 controls, the
seven fixed hostile/equality branches, and the neutral control for the exact
hypotheses.  Enumeration audits scope and arithmetic only.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_carrier_separator_payment import full_tight_support  # noqa: E402
from audit_direct_ceiling_common_hinge_trichotomy import has_direct_packet  # noqa: E402
from audit_labelled_facet_cover_duality import maximum_overlap_roots  # noqa: E402
from audit_lmax_overcover import records  # noqa: E402
from audit_pxc52_coloured_charge import fractions, lower_envelope  # noqa: E402
from verify_labelled_branch_duals import CASES  # noqa: E402
from verify_mixed_witness_projection import NEUTRAL_CASE  # noqa: E402


def coalition_sum(point, coalition):
    return sum(
        (point[player] for player in range(len(point)) if coalition >> player & 1),
        F(0),
    )


def overlap(x, z):
    return sum((min(a, b) for a, b in zip(x, z)), F(0))


def certificates(values, x, z):
    n = len(x)
    total = sum(x, F(0))
    gainers = tuple(player for player in range(n) if z[player] > x[player])
    if n < 6 or len(gainers) < 2 or total <= 0 or total != sum(z, F(0)):
        return ()
    g = len(gainers)
    gainer_set = set(gainers)
    x_tight = set(full_tight_support(values, x))
    z_tight = set(full_tight_support(values, z))
    answer = []
    for root in maximum_overlap_roots(x, z):
        if root in gainer_set:
            continue
        spokes = tuple(sorted((1 << root) | (1 << player) for player in gainers))
        outside = set(range(n)) - gainer_set - {root}
        minimum_gainer = min(x[player] for player in gainers)
        if not all(spoke in x_tight for spoke in spokes):
            continue
        if not (
            all(x[root] >= x[player] for player in gainers)
            and all(minimum_gainer >= x[player] for player in outside)
            and all(z[root] >= z[player] for player in gainers)
        ):
            continue

        gainer_x_total = sum((x[player] for player in gainers), F(0))
        gainer_z_total = sum((z[player] for player in gainers), F(0))
        packet_left = g * x[root] + gainer_x_total
        if packet_left > total:
            raise AssertionError("aligned-spoke-star witness packet failed")
        total_gain = gainer_z_total - gainer_x_total
        imbalance = g * x[root] - gainer_x_total
        imbalance_ceiling = F(n - 2 * g, n - 2) * total
        if imbalance > imbalance_ceiling:
            raise AssertionError("aligned-spoke-star imbalance bound failed")
        highest_z = max(z[player] for player in gainers)
        for aligned in gainers:
            aligned_spoke = (1 << root) | (1 << aligned)
            if z[aligned] != highest_z or aligned_spoke not in z_tight:
                continue
            if 2 * z[aligned] > x[root] + x[aligned]:
                raise AssertionError("one-spoke alignment inequality failed")
            if g == 2:
                other = next(player for player in gainers if player != aligned)
                gain_ceiling = x[root] - min(x[player] for player in gainers)
                if total_gain > x[root] - x[other] or total_gain > gain_ceiling:
                    raise AssertionError("two-gainer aligned-spoke transfer failed")
                sharp_gain_ceiling = F(n - 4, 2 * (n - 2)) * total
                if gain_ceiling > sharp_gain_ceiling:
                    raise AssertionError("two-gainer extremal gap bound failed")
                floor = F(n, 2 * (n - 2)) * total
            else:
                if total_gain > imbalance:
                    raise AssertionError("multi-gainer aligned-spoke transfer failed")
                sharp_gain_ceiling = imbalance_ceiling
                floor = F(2 * (g - 1), n - 2) * total
            target = F(n, (n * n) // 4) * total
            actual = overlap(x, z)
            if actual < floor or floor < target:
                raise AssertionError("aligned-spoke-star target bound failed")
            answer.append(
                {
                    "root": root,
                    "gainers": list(gainers),
                    "gainer_count": g,
                    "lmin_tight_spokes": list(spokes),
                    "aligned_gainer": aligned,
                    "common_aligned_spoke": aligned_spoke,
                    "packet_left": str(packet_left),
                    "total_gain": str(total_gain),
                    "root_gainer_imbalance": str(imbalance),
                    "gain_ceiling": str(sharp_gain_ceiling),
                    "proved_floor": str(floor),
                    "hybrid_target": str(target),
                    "actual_overlap": str(actual),
                }
            )
    return tuple(answer)


def lower_envelope_case(case):
    generators = (tuple(map(F, case["g"])), tuple(map(F, case["h"])))
    return (
        lower_envelope(generators),
        tuple(map(F, case["x"])),
        tuple(map(F, case["z"])),
    )


def neutral_from_file(path):
    payload = json.loads(path.read_text())
    generators = tuple(fractions(row) for row in payload["game"]["generators"])
    return (
        lower_envelope(generators),
        fractions(payload["selections"]["lmin"]),
        fractions(payload["selections"]["lmax"]),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--neutral-control", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    archive_rows = []
    seen_records = 0
    positive_residual_rows = 0
    positive_residual_rows_matching = 0
    for path in args.paths:
        payload = json.loads(path.read_text())
        for source, trail, values, x, z in records(payload, path):
            seen_records += 1
            found = certificates(values, x, z)
            total = sum(x, F(0))
            floor = min(x)
            ceiling = max(z)
            positive_residual = (
                not has_direct_packet(x, z, F(2, 3))
                and ceiling - floor + total * floor / ceiling < F(2, 3) * total
                and floor > 0
            )
            positive_residual_rows += positive_residual
            positive_residual_rows_matching += positive_residual and bool(found)
            if found:
                archive_rows.append(
                    {"source": source.name, "trail": trail, "certificates": found}
                )

    fixed_rows = []
    for case in CASES:
        values, x, z = lower_envelope_case(case)
        found = certificates(values, x, z)
        fixed_rows.append({"name": case["name"], "certificates": found})

    neutral_values, neutral_x, neutral_z = neutral_from_file(args.neutral_control)
    neutral = certificates(neutral_values, neutral_x, neutral_z)
    if len(neutral) != 1:
        raise AssertionError("neutral aligned-spoke-star certificate changed")
    neutral_row = neutral[0]
    expected = {
        "root": 3,
        "gainers": [0, 1],
        "gainer_count": 2,
        "lmin_tight_spokes": [9, 10],
        "aligned_gainer": 0,
        "common_aligned_spoke": 9,
        "proved_floor": "7/10",
        "hybrid_target": "7/12",
    }
    if {key: neutral_row[key] for key in expected} != expected:
        raise AssertionError("neutral aligned-spoke-star theorem data changed")
    expected_counts = (374, 46, 90, 16, 8)
    actual_counts = (
        seen_records,
        len(archive_rows),
        sum(len(row["certificates"]) for row in archive_rows),
        positive_residual_rows,
        positive_residual_rows_matching,
    )
    if actual_counts != expected_counts:
        raise AssertionError(("aligned-spoke-star archive partition changed", actual_counts))
    if any(row["certificates"] for row in fixed_rows):
        raise AssertionError("a fixed hostile/equality branch unexpectedly entered the star class")

    distribution = Counter(
        certificate["gainer_count"]
        for row in archive_rows
        for certificate in row["certificates"]
    )
    report = {
        "status": "exact multi-gainer aligned-spoke-star controls verified",
        "human_theorem": (
            "an ordered Lmin-tight star to every gainer plus one common spoke "
            "to a highest-Lmax gainer implies O/T >= n/[2(n-2)] for g=2 "
            "and O/T >= 2(g-1)/(n-2) for g>=3"
        ),
        "archive_records_scanned": seen_records,
        "archive_rows_matching_theorem": len(archive_rows),
        "archive_certificates": sum(len(row["certificates"]) for row in archive_rows),
        "positive_residual_rows": positive_residual_rows,
        "positive_residual_rows_matching_theorem": positive_residual_rows_matching,
        "archive_gainer_count_distribution": {
            str(key): value for key, value in sorted(distribution.items())
        },
        "archive_rows": archive_rows,
        "fixed_hostile_and_equality_controls": fixed_rows,
        "neutral_control": neutral_row,
        "scope": (
            "dimension-free human theorem; finite scans audit exact hypotheses "
            "and arithmetic, not universal aligned-spoke-star selection"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

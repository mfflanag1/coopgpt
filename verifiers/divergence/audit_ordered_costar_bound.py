#!/usr/bin/env python3
r"""Exact controls for the ordered rooted co-star theorem (PXC55).

The proof is dimension-free human algebra.  This driver scans the n=6
archives and fixed hostile/equality controls for its exact hypotheses and
checks every displayed rational inequality.  Counts are scope audits, not an
enumerative proof of universal co-star selection.
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
    outsiders_count = n - g - 1
    x_tight = set(full_tight_support(values, x))
    z_tight = set(full_tight_support(values, z))
    answer = []
    for root in maximum_overlap_roots(x, z):
        if root in gainer_set:
            continue
        outsiders = set(range(n)) - gainer_set - {root}
        minimum_gainer = min(x[player] for player in gainers)
        if not (
            all(x[root] >= x[player] for player in gainers)
            and all(minimum_gainer >= x[player] for player in outsiders)
        ):
            continue
        costars = {
            omitted: (1 << root)
            | sum(1 << player for player in gainers if player != omitted)
            for omitted in gainers
        }
        if not all(coalition in x_tight for coalition in costars.values()):
            continue
        highest_gainer_z = max(z[player] for player in gainers)
        for omitted, common_costar in costars.items():
            if (
                z[omitted] != highest_gainer_z
                or z[root] < z[omitted]
                or common_costar not in z_tight
            ):
                continue
            gainer_x_total = sum((x[player] for player in gainers), F(0))
            gainer_z_total = sum((z[player] for player in gainers), F(0))
            packet_left = F(g, g - 1) * x[root] + gainer_x_total
            if packet_left > total:
                raise AssertionError("ordered co-star witness packet failed")
            if gainer_z_total > x[root] + gainer_x_total - x[omitted]:
                raise AssertionError("ordered co-star comparison transfer failed")
            total_gain = gainer_z_total - gainer_x_total
            root_gap = x[root] - x[omitted]
            if total_gain > root_gap:
                raise AssertionError("ordered co-star gain bound failed")
            gap_ceiling = F(g * (n - g) - n, g * (n - g)) * total
            if root_gap > gap_ceiling:
                raise AssertionError("ordered co-star extremal gap failed")
            floor = F(n, g * (n - g)) * total
            target = F(n, (n * n) // 4) * total
            actual = overlap(x, z)
            if actual < floor or floor < target:
                raise AssertionError("ordered co-star target bound failed")
            equality_cardinality = g * (n - g) == (n * n) // 4
            answer.append(
                {
                    "root": root,
                    "gainers": list(gainers),
                    "gainer_count": g,
                    "outside_count": outsiders_count,
                    "omitted_highest_gainer": omitted,
                    "lmin_tight_costars": [costars[player] for player in gainers],
                    "common_costar": common_costar,
                    "packet_left": str(packet_left),
                    "total_gain": str(total_gain),
                    "root_omitted_gap": str(root_gap),
                    "gap_ceiling": str(gap_ceiling),
                    "proved_floor": str(floor),
                    "hybrid_target": str(target),
                    "actual_overlap": str(actual),
                    "balanced_cardinality_for_possible_target_equality": (
                        equality_cardinality
                    ),
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
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
        fixed_rows.append(
            {"name": case["name"], "certificates": certificates(values, x, z)}
        )

    certificate_count = sum(len(row["certificates"]) for row in archive_rows)
    expected_counts = (374, 84, 186, 16, 16)
    actual_counts = (
        seen_records,
        len(archive_rows),
        certificate_count,
        positive_residual_rows,
        positive_residual_rows_matching,
    )
    if actual_counts != expected_counts:
        raise AssertionError(("ordered co-star archive partition changed", actual_counts))
    sharp = {
        row["name"]: len(row["certificates"])
        for row in fixed_rows
        if row["name"].startswith("sharp_family")
    }
    if sharp != {"sharp_family_p2_k4": 4, "sharp_family_p3_k3": 3}:
        raise AssertionError(("sharp-family co-star controls changed", sharp))

    distribution = Counter(
        certificate["gainer_count"]
        for row in archive_rows
        for certificate in row["certificates"]
    )
    report = {
        "status": "exact ordered rooted co-star controls verified",
        "human_theorem": (
            "an ordered complete Lmin rooted co-star on g gainers and one "
            "common co-star omitting a highest-Lmax gainer imply "
            "O/T >= n/[g(n-g)] >= n/floor(n^2/4)"
        ),
        "archive_records_scanned": seen_records,
        "archive_rows_matching_theorem": len(archive_rows),
        "archive_certificates": certificate_count,
        "archive_gainer_count_distribution": {
            str(key): value for key, value in sorted(distribution.items())
        },
        "positive_residual_rows": positive_residual_rows,
        "positive_residual_rows_matching_theorem": positive_residual_rows_matching,
        "archive_rows": archive_rows,
        "fixed_hostile_and_equality_controls": fixed_rows,
        "scope": (
            "dimension-free human theorem; finite scans audit exact hypotheses, "
            "arithmetic, and equality compatibility, not universal co-star selection"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

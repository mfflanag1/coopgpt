#!/usr/bin/env python3
r"""Exact controls for the dimension-free two-spoke alignment bound.

The proof is human algebra.  This driver detects the theorem's hypotheses in
the n=6 archives and reconstructs the seven-player neutral control.  It is a
scope/falsification audit, not a proof by enumeration.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_carrier_separator_payment import full_tight_support  # noqa: E402
from audit_labelled_facet_cover_duality import maximum_overlap_roots  # noqa: E402
from audit_lmax_overcover import records  # noqa: E402
from audit_pxc52_coloured_charge import fractions, lower_envelope  # noqa: E402


def overlap(x, z):
    return sum((min(a, b) for a, b in zip(x, z)), F(0))


def certificates(values, x, z):
    n = len(x)
    total = sum(x, F(0))
    if n < 6 or total <= 0 or total != sum(z, F(0)):
        return ()
    gainers = tuple(player for player in range(n) if z[player] > x[player])
    if len(gainers) != 2:
        return ()
    x_tight = set(full_tight_support(values, x))
    z_tight = set(full_tight_support(values, z))
    answer = []
    for root in maximum_overlap_roots(x, z):
        if root in gainers:
            continue
        for aligned, other in (gainers, tuple(reversed(gainers))):
            pair_aligned = (1 << root) | (1 << aligned)
            pair_other = (1 << root) | (1 << other)
            outside = set(range(n)) - {root, aligned, other}
            if pair_aligned not in x_tight or pair_other not in x_tight:
                continue
            if pair_aligned not in z_tight:
                continue
            if not (
                x[root] >= x[aligned] >= x[other]
                and all(x[other] >= x[player] for player in outside)
                and z[root] == z[aligned]
                and z[other] <= z[aligned]
            ):
                continue

            packet_left = 2 * x[root] + x[aligned] + x[other]
            if packet_left > total:
                raise AssertionError("two-spoke witness packet inequality failed")
            if 2 * z[aligned] > x[root] + x[aligned]:
                raise AssertionError("aligned z-tight spoke inequality failed")
            if x[root] > (n - 3) * x[other]:
                raise AssertionError("two-spoke order consequence failed")
            if x[root] + x[other] > total / 2:
                raise AssertionError("two-spoke packet consequence failed")
            maximum_gap = F(n - 4, 2 * (n - 2)) * total
            if x[root] - x[other] > maximum_gap:
                raise AssertionError("two-spoke extremal gap bound failed")
            total_gain = sum((z[player] - x[player] for player in gainers), F(0))
            if total_gain > x[root] - x[other]:
                raise AssertionError("aligned-spoke gain transfer failed")
            floor = F(n, 2 * (n - 2)) * total
            target = F(n, (n * n) // 4) * total
            actual = overlap(x, z)
            if actual < floor or floor < target:
                raise AssertionError("two-spoke target bound failed")
            answer.append(
                {
                    "root": root,
                    "aligned_gainer": aligned,
                    "other_gainer": other,
                    "x_tight_spokes": [pair_aligned, pair_other],
                    "common_aligned_spoke": pair_aligned,
                    "packet_left": str(packet_left),
                    "root_to_lower_gainer_gap": str(x[root] - x[other]),
                    "maximum_gap": str(maximum_gap),
                    "total_gain": str(total_gain),
                    "proved_floor": str(floor),
                    "hybrid_target": str(target),
                    "actual_overlap": str(actual),
                }
            )
    return tuple(answer)


def neutral_case(path):
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
    for path in args.paths:
        payload = json.loads(path.read_text())
        for source, trail, values, x, z in records(payload, path):
            seen_records += 1
            found = certificates(values, x, z)
            if found:
                archive_rows.append(
                    {
                        "source": source.name,
                        "trail": trail,
                        "certificates": found,
                    }
                )

    neutral_values, neutral_x, neutral_z = neutral_case(args.neutral_control)
    neutral = certificates(neutral_values, neutral_x, neutral_z)
    if len(neutral) != 1:
        raise AssertionError("neutral two-spoke certificate changed")
    row = neutral[0]
    expected = {
        "root": 3,
        "aligned_gainer": 0,
        "other_gainer": 1,
        "x_tight_spokes": [9, 10],
        "common_aligned_spoke": 9,
        "proved_floor": "7/10",
        "hybrid_target": "7/12",
    }
    if {key: row[key] for key in expected} != expected:
        raise AssertionError("neutral two-spoke theorem data changed")

    report = {
        "status": "exact two-spoke alignment controls verified",
        "human_theorem": (
            "two Lmin-tight root spokes, one Lmax-aligned spoke, two gainers, "
            "and the stated Lmin/Lmax orders imply O/T >= n/[2(n-2)]"
        ),
        "archive_records_scanned": seen_records,
        "archive_rows_matching_theorem": len(archive_rows),
        "archive_certificates": sum(
            len(item["certificates"]) for item in archive_rows
        ),
        "archive_rows": archive_rows,
        "neutral_control": row,
        "scope": (
            "the theorem is dimension-free human algebra; finite rows only "
            "audit its hypotheses and exact arithmetic"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

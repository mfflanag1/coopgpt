#!/usr/bin/env python3
r"""Exact hostile controls for the PXC51 quantitative handover.

The six-player marked-hinge audit lexicographically minimizes the alignment
defect over each maximum-root-load face.  This verifier checks its finite
partition and then reconstructs the seven-player neutral control from its
lower-envelope generators.  The latter refutes an Lmin-only handover from
positive PXC49 root excess while confirming that the full mixed one-witness
projection closes the target.
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
from audit_labelled_facet_cover_duality import (  # noqa: E402
    maximum_overlap_roots,
)
from audit_marked_hinge_deficiency_transfer import (  # noqa: E402
    best_aligned_full_menu_packet,
)
from audit_n6_sparse_lmax_complete_lmin_roots import (  # noqa: E402
    complete_lmin_support,
    specialized_root_minimum,
)


def fractions(values):
    return tuple(F(value) for value in values)


def lower_envelope(generators):
    n = len(generators[0])
    return tuple(
        min(
            sum(
                (
                    generator[player]
                    for player in range(n)
                    if coalition >> player & 1
                ),
                F(0),
            )
            for generator in generators
        )
        for coalition in range(1 << n)
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--marked-audit", required=True, type=Path)
    parser.add_argument("--neutral-control", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    marked = json.loads(args.marked_audit.read_text())
    expected_counts = {
        "positive_deficiency_transfer_rows": 21,
        "positive_transfer_rows_without_eligible_hinge_top_root": 6,
        "eligible_full_menu_rows_with_tied_root_excess": 7,
        "eligible_full_menu_rows_with_positive_root_excess": 8,
        "eligible_positive_packets_with_zero_alignment_defect": 3,
        "eligible_positive_packets_whose_charge_covers_total_gain": 4,
    }
    actual_counts = {
        key: marked["counts"].get(key) for key in expected_counts
    }
    if actual_counts != expected_counts:
        raise AssertionError(("marked PXC51 partition changed", actual_counts))
    positive_rows = marked[
        "eligible_full_menu_positive_packet_alignment_controls"
    ]
    if len(positive_rows) != 8:
        raise AssertionError("PXC51 positive-row list is incomplete")
    if sum(F(row["excess_alignment_defect"]) <= 0 for row in positive_rows) != 4:
        raise AssertionError("PXC51 lexicographic closing count changed")

    neutral = json.loads(args.neutral_control.read_text())
    generators = tuple(
        fractions(generator) for generator in neutral["game"]["generators"]
    )
    values = lower_envelope(generators)
    x = fractions(neutral["selections"]["lmin"])
    z = fractions(neutral["selections"]["lmax"])
    if sum(x, F(0)) != 1 or sum(z, F(0)) != 1:
        raise AssertionError("neutral control is not normalized")
    support_x = complete_lmin_support(values, x)
    full_support_x = tuple(full_tight_support(values, x))
    support_z = tuple(full_tight_support(values, z))
    common = set(full_support_x) & set(support_z)
    top = {player for player, value in enumerate(z) if value == max(z)}
    roots = set(maximum_overlap_roots(x, z))
    target = F(7, 12)
    controls = []
    for hinge in sorted(common):
        members = {
            player for player in range(len(x)) if hinge >> player & 1
        }
        eligible = members & top & roots
        if not eligible or not (top - members):
            continue
        packet = best_aligned_full_menu_packet(
            x,
            z,
            {"support": support_z},
            hinge,
            eligible,
        )
        if packet["root_excess"] <= 0:
            continue
        budget = packet["comparison_budget"]
        root = packet["root"]
        x_only = specialized_root_minimum(x, z, support_x, (), root)
        mixed = specialized_root_minimum(x, z, support_x, support_z, root)
        controls.append(
            {
                "hinge": hinge,
                "root": root,
                "root_excess": str(packet["root_excess"]),
                "comparison_charge": str(budget["comparison_charge"]),
                "total_gain": str(budget["total_gain"]),
                "excess_alignment_defect": str(
                    budget["excess_alignment_defect"]
                ),
                "lmin_only_one_witness_bound": str(x_only),
                "full_mixed_one_witness_bound": str(mixed),
                "target": str(target),
            }
        )
    if [row["hinge"] for row in controls] != [10, 26]:
        raise AssertionError("neutral marked-hinge controls changed")
    for row in controls:
        if row["root_excess"] != "1":
            raise AssertionError("neutral packet lost positive root excess")
        if row["comparison_charge"] != "0":
            raise AssertionError("neutral common packet gained comparison charge")
        if row["excess_alignment_defect"] != "711/19046":
            raise AssertionError("neutral alignment shortfall changed")
        if F(row["lmin_only_one_witness_bound"]) != F(8, 15):
            raise AssertionError("neutral Lmin-only bound changed")
        if F(row["full_mixed_one_witness_bound"]) != F(5, 6):
            raise AssertionError("neutral mixed bound changed")
        if not (
            F(row["lmin_only_one_witness_bound"])
            < target
            < F(row["full_mixed_one_witness_bound"])
        ):
            raise AssertionError("neutral handover no longer separates the routes")

    report = {
        "status": "exact PXC51 handover controls verified",
        "six_player_lexicographic_partition": actual_counts,
        "six_player_positive_rows": len(positive_rows),
        "six_player_rows_closed_by_optimized_comparison_charge": 4,
        "neutral_seven_player_controls": controls,
        "conclusion": (
            "positive full-menu root excess does not force comparison-charge "
            "alignment or a target-reaching Lmin-only root relaxation; the "
            "full coloured mixed-witness projection can be essential"
        ),
        "scope": (
            "finite exact controls only; this refutes two universal shortcut "
            "lemmas but does not prove existence of a target-reaching mixed "
            "packet in every dimension"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Exact discovery audit for the affordable-root/direct-packet handover.

This audit deliberately separates three statements.

1. On the archived n=6 pairs, if every maximum-overlap root has a negative
   or degenerate best labelled-row margin, some direct packet reaches 2/3.
2. The tempting stronger rule ``H = all maximum-overlap roots`` has five
   exact failures in that archive.
3. Each of those five failures is repaired by adjoining one highest-Lmin
   remaining nongainer to H.  The repaired comparison coalition is Lmin
   tight and the direct master identity gives the stronger base 4/5.

The direct master identity is a human theorem.  The three finite assertions
above are only exact-rational discovery/falsification evidence; the archive
is not a census of six-player exact games and this script is not the missing
all-dimensional selection proof.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_labelled_facet_cover_duality import (  # noqa: E402
    maximum_overlap_roots,
    solve_labelled_cover,
)
from audit_lmax_overcover import records  # noqa: E402
from audit_n6_sparse_lmax_complete_lmin_roots import (  # noqa: E402
    complete_lmin_support,
)
from verify_two_stratum_direct_gluing import master_identity  # noqa: E402


def direct_witnesses(x, z, support, target, allowed_h=None):
    """Return exact direct-packet witnesses, optionally restricting H."""
    n = len(x)
    gainers = tuple(i for i in range(n) if z[i] > x[i])
    nongainers = tuple(i for i in range(n) if z[i] <= x[i])
    h_sets = (
        tuple(allowed_h)
        if allowed_h is not None
        else tuple(
            h_set
            for size in range(1, len(nongainers))
            for h_set in itertools.combinations(nongainers, size)
        )
    )
    if allowed_h is not None:
        h_sets = (h_sets,)
    witnesses = []
    for h_set in h_sets:
        if not set(h_set) <= set(nongainers):
            continue
        p_set = tuple(i for i in nongainers if i not in h_set)
        if not p_set:
            continue
        for size in range(len(gainers)):
            for j_set in itertools.combinations(gainers, size):
                row = master_identity(x, z, p_set, gainers, h_set, j_set)
                if F(row["base_bound_ratio"]) < target:
                    continue
                if not row["packet_hits_interval"]:
                    continue
                witnesses.append(
                    {
                        "P": list(p_set),
                        "G": list(gainers),
                        "H": list(h_set),
                        "J": list(j_set),
                        "base_bound_ratio": row["base_bound_ratio"],
                        "comparison_coalition": row["comparison_coalition"],
                        "comparison_is_lmin_tight": (
                            row["comparison_coalition"] in support
                        ),
                        "comparison_slack": row["comparison_slack"],
                        "x_order_residual": row["x_order_residual"],
                        "z_order_residual": row["z_order_residual"],
                        "residual_sum_nonnegative": (
                            F(row["x_order_residual"])
                            + F(row["z_order_residual"])
                            >= 0
                        ),
                    }
                )
    return witnesses


def first_tight(witnesses):
    return next(
        (row for row in witnesses if row["comparison_is_lmin_tight"]),
        None,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    target = F(2, 3)
    all_unaffordable = 0
    root_block_successes = 0
    repaired = []
    repaired_locked_pairs = 0
    repaired_pair_free = 0

    for path in args.paths:
        payload = json.loads(path.read_text())
        for _source, trail, values, x, z in records(payload, path):
            if len(x) != 6:
                continue
            support = complete_lmin_support(values, x)
            roots = maximum_overlap_roots(x, z)
            audits = tuple(solve_labelled_cover(support, root, 6) for root in roots)
            if any(row["affordable"] for row in audits):
                continue
            all_unaffordable += 1

            unrestricted = direct_witnesses(x, z, support, target)
            if not unrestricted:
                raise AssertionError((path.name, trail, "direct-or-affordable failure"))

            root_block = first_tight(
                direct_witnesses(x, z, support, target, allowed_h=roots)
            )
            if root_block is not None:
                root_block_successes += 1
                continue

            nongainers = tuple(i for i in range(6) if z[i] <= x[i])
            remaining = tuple(i for i in nongainers if i not in roots)
            highest_remaining = max(x[i] for i in remaining)
            repairs = []
            for extra in remaining:
                if x[extra] != highest_remaining:
                    continue
                repair = first_tight(
                    direct_witnesses(
                        x,
                        z,
                        support,
                        target,
                        allowed_h=tuple(roots) + (extra,),
                    )
                )
                if repair is not None:
                    repairs.append(repair)
            if not repairs:
                raise AssertionError((path.name, trail, "one-step root-block repair failure"))
            witness = repairs[0]
            if F(witness["base_bound_ratio"]) != F(4, 5):
                raise AssertionError("unexpected one-step repair base")
            root_set = set(roots)
            mutual_locked_pair = all(
                len(audit["tight_rooted_pairs"]) == 1
                and audit["tight_rooted_pairs"][0] in root_set
                and not audit["unique_pair_partner_escaped_by_nonpair"]
                for audit in audits
            )
            pair_free = all(not audit["tight_rooted_pairs"] for audit in audits)
            if mutual_locked_pair:
                repaired_locked_pairs += 1
                classification = "mutual locked maximum-overlap pair"
            elif pair_free:
                repaired_pair_free += 1
                classification = "pair-free maximum-overlap roots"
            else:
                raise AssertionError((path.name, trail, "unexpected repair type"))
            repaired.append(
                {
                    "source": path.name,
                    "trail": trail,
                    "x": [str(value) for value in x],
                    "z": [str(value) for value in z],
                    "maximum_overlap_roots": list(roots),
                    "root_block_classification": classification,
                    "root_audits": audits,
                    "repair": witness,
                }
            )

    if all_unaffordable != 233:
        raise AssertionError(f"expected 233 all-unaffordable rows, found {all_unaffordable}")
    if root_block_successes != 228 or len(repaired) != 5:
        raise AssertionError((root_block_successes, len(repaired)))
    if (repaired_locked_pairs, repaired_pair_free) != (4, 1):
        raise AssertionError((repaired_locked_pairs, repaired_pair_free))

    report = {
        "status": "exact-rational discovery and hostile falsification audit",
        "n6_archived_records_with_all_maximum_overlap_roots_unaffordable": (
            all_unaffordable
        ),
        "n6_rows_with_some_direct_packet": all_unaffordable,
        "n6_rows_closed_by_tight_root_block_packet": root_block_successes,
        "n6_root_block_counterexamples": len(repaired),
        "n6_counterexamples_repaired_by_one_upper_nongainer": len(repaired),
        "n6_repaired_mutual_locked_pair_rows": repaired_locked_pairs,
        "n6_repaired_pair_free_rows": repaired_pair_free,
        "counterexamples": repaired,
        "valid_conditional_statement": (
            "For any chosen H and J, the proved direct master identity reaches "
            "the target when its cardinality base reaches the target and its "
            "comparison and residual-sum terms are nonnegative; Lmin tightness "
            "of H union J makes the comparison automatic."
        ),
        "falsified_statement": (
            "If every maximum-overlap root is unaffordable, taking H to be "
            "exactly the maximum-overlap root block always supplies the direct packet."
        ),
        "surviving_selection_conjecture": (
            "If every maximum-overlap root is unaffordable, some upper block of "
            "nongainers containing those roots and some gainer packet form an "
            "Lmin-tight target-reaching direct comparison."
        ),
        "scope": (
            "374 archived n=6 pairs only; exact finite evidence, not a six-player "
            "domain classification and not an all-dimensional theorem"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

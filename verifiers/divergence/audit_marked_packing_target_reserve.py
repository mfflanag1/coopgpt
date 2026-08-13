#!/usr/bin/env python3
"""Exact audit of the marked-packing/target-reserve interface.

For a root-containing fractional packing ``u`` put

    delta = sum(u) - 1,
    q_i = 1 - sum_{S: i in S} u_S       (i != r).

If ``A`` is any offroot player set and ``P_S=A\S``, coordinate counting gives

    sum_S u_S z(P_S) = delta z(A) + sum_{i in A} q_i z_i,
    sum_S u_S |P_S| = delta |A| + sum_{i in A} q_i.

If every packing column is Lmin-tight, core feasibility of Lmax also gives

    sum_{i != r} q_i (x_i-z_i) >= delta (x_r-z_r).

These are human identities; the script checks them with exact arithmetic on
the labelled price-maximizing marked packings in the n=6 archive.  On rows
where every maximum-overlap root is unaffordable, it additionally asks the
strictly stronger finite question whether a *positive column of that same
marked packing* supplies a carrier-containing proper comparison whose
target reserve closes the sharp 2/3 bound.  This is finite evidence only.
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

from audit_labelled_facet_cover_duality import (  # noqa: E402
    maximum_overlap_roots,
    solve_labelled_cover,
)
from audit_lmax_overcover import coalition_sum, records  # noqa: E402
from audit_n6_sparse_lmax_complete_lmin_roots import (  # noqa: E402
    complete_lmin_support,
)
from verify_excluded_block_deficit_quota import target_reserve_row  # noqa: E402


def marked_packing(support: tuple[int, ...], audit: dict, root: int) -> tuple[tuple[int, F], ...]:
    """Reconstruct the price-preserving marked packing behind the LP row."""
    root_mask = 1 << root
    good = tuple(audit["tight_rooted_pairs"])
    menu = tuple(
        coalition
        for coalition in support
        if coalition & root_mask and coalition.bit_count() >= 3
    )
    nonpair_weights = tuple(map(F, audit["max_root_excess_top_face_packing"]))
    if len(menu) != len(nonpair_weights):
        raise AssertionError("labelled packing/menu mismatch")

    rows = [(coalition, weight) for coalition, weight in zip(menu, nonpair_weights) if weight]
    for player in good:
        load = sum(
            (weight for coalition, weight in rows if coalition >> player & 1),
            F(0),
        )
        residual = F(1) - load
        if residual < 0:
            raise AssertionError("negative tight-pair residual")
        if residual:
            rows.append((root_mask | (1 << player), residual))
    return tuple(rows)


def audit_root(values, x, z, support, root, gate, target):
    n = len(x)
    gainers = tuple(i for i in range(n) if z[i] > x[i])
    nongainers = tuple(i for i in range(n) if z[i] <= x[i])
    offroot_nongainers = tuple(i for i in nongainers if i != root)
    packing = marked_packing(support, gate, root)
    total_mass = sum((weight for _coalition, weight in packing), F(0))
    delta = total_mass - 1
    loads = tuple(
        sum(
            (weight for coalition, weight in packing if coalition >> i & 1),
            F(0),
        )
        for i in range(n)
    )
    if loads[root] != total_mass or any(loads[i] > 1 for i in range(n) if i != root):
        raise AssertionError("not a root-containing fractional packing")
    q = tuple(F(0) if i == root else F(1) - loads[i] for i in range(n))

    weighted_z_complements = F(0)
    weighted_complement_sizes = F(0)
    for coalition, weight in packing:
        p_set = tuple(i for i in offroot_nongainers if not coalition >> i & 1)
        weighted_z_complements += weight * sum((z[i] for i in p_set), F(0))
        weighted_complement_sizes += weight * len(p_set)
    z_identity_rhs = delta * sum((z[i] for i in offroot_nongainers), F(0))
    z_identity_rhs += sum((q[i] * z[i] for i in offroot_nongainers), F(0))
    size_identity_rhs = delta * len(offroot_nongainers)
    size_identity_rhs += sum((q[i] for i in offroot_nongainers), F(0))
    if weighted_z_complements != z_identity_rhs:
        raise AssertionError("weighted complement-sum identity failed")
    if weighted_complement_sizes != size_identity_rhs:
        raise AssertionError("weighted complement-cardinality identity failed")

    tangent_lhs = sum((q[i] * (x[i] - z[i]) for i in range(n) if i != root), F(0))
    tangent_rhs = delta * (x[root] - z[root])
    if tangent_lhs < tangent_rhs:
        raise AssertionError("rooted tangent inequality failed")

    if gate["tight_rooted_pairs"]:
        carriers = set(gate["tight_rooted_pairs"])
    else:
        carriers = set(gate["common_nonpair_carriers"])
    candidates = []
    for coalition, weight in packing:
        comparison_gainers = tuple(i for i in gainers if coalition >> i & 1)
        h_set = tuple(i for i in nongainers if coalition >> i & 1)
        p_set = tuple(i for i in nongainers if not coalition >> i & 1)
        contains_carrier = bool(carriers) and carriers <= set(h_set)
        proper = len(comparison_gainers) < len(gainers)
        if not p_set or not contains_carrier or not proper:
            continue
        row = target_reserve_row(x, z, p_set, gainers, h_set, target)
        candidates.append(
            {
                "coalition": coalition,
                "weight": str(weight),
                "P": list(p_set),
                "H": list(h_set),
                "comparison_gainers": list(comparison_gainers),
                "target_reserve": row["nonlow_target_reserve"],
                "target_reserve_closes": row["target_reserve_closes"],
            }
        )
    all_support_closers = []
    packing_masks = tuple(coalition for coalition, _weight in packing)
    for coalition in support:
        comparison_gainers = tuple(i for i in gainers if coalition >> i & 1)
        h_set = tuple(i for i in nongainers if coalition >> i & 1)
        p_set = tuple(i for i in nongainers if not coalition >> i & 1)
        contains_carrier = bool(carriers) and carriers <= set(h_set)
        proper = len(comparison_gainers) < len(gainers)
        comparison_slack = coalition_sum(z, coalition) - coalition_sum(x, coalition)
        if not p_set or not contains_carrier or not proper or comparison_slack < 0:
            continue
        row = target_reserve_row(x, z, p_set, gainers, h_set, target)
        if not row["target_reserve_closes"]:
            continue
        distances = tuple((coalition ^ mask).bit_count() for mask in packing_masks)
        all_support_closers.append(
            {
                "coalition": coalition,
                "P": list(p_set),
                "H": list(h_set),
                "comparison_gainers": list(comparison_gainers),
                "comparison_slack": str(comparison_slack),
                "target_reserve": row["nonlow_target_reserve"],
                "minimum_packing_column_exchange": min(distances),
            }
        )
    return {
        "root": root,
        "affordable": gate["affordable"],
        "facet_margin": gate["margin"],
        "delta": str(delta),
        "q_total": str(sum(q, F(0))),
        "packing_support_size": len(packing),
        "weighted_z_complements": str(weighted_z_complements),
        "weighted_complement_sizes": str(weighted_complement_sizes),
        "tangent_slack": str(tangent_lhs - tangent_rhs),
        "candidate_rows": candidates,
        "all_support_closers": all_support_closers,
        "minimum_closing_exchange": (
            min(row["minimum_packing_column_exchange"] for row in all_support_closers)
            if all_support_closers
            else None
        ),
        "same_packing_target_reserve_closes": any(
            row["target_reserve_closes"] for row in candidates
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    target = F(2, 3)
    counts = Counter()
    failures = []
    for path in args.paths:
        payload = json.loads(path.read_text())
        for _source, trail, values, x, z in records(payload, path):
            if len(x) != 6:
                continue
            support = complete_lmin_support(values, x)
            roots = maximum_overlap_roots(x, z)
            gates = tuple(solve_labelled_cover(support, root, 6) for root in roots)
            if any(gate["affordable"] for gate in gates):
                continue
            counts["all_roots_unaffordable_records"] += 1
            root_rows = tuple(
                audit_root(values, x, z, support, root, gate, target)
                for root, gate in zip(roots, gates)
            )
            counts["audited_roots"] += len(root_rows)
            closing_roots = sum(row["same_packing_target_reserve_closes"] for row in root_rows)
            counts["roots_with_same_packing_reserve"] += closing_roots
            for row in root_rows:
                if F(row["delta"]) > 0:
                    counts["positive_excess_roots"] += 1
                    if row["same_packing_target_reserve_closes"]:
                        counts["positive_excess_roots_with_same_packing_reserve"] += 1
                else:
                    counts["zero_excess_roots"] += 1
                    if row["same_packing_target_reserve_closes"]:
                        counts["zero_excess_roots_with_same_packing_reserve"] += 1
                if row["all_support_closers"]:
                    counts["roots_with_support_reserve"] += 1
                    counts[
                        f"roots_minimum_closing_exchange_{row['minimum_closing_exchange']}"
                    ] += 1
            if closing_roots:
                counts["records_with_same_packing_reserve"] += 1
            else:
                if all(F(row["delta"]) == 0 for row in root_rows):
                    counts["failed_records_all_roots_zero_excess"] += 1
                else:
                    counts["failed_records_with_positive_excess_root"] += 1
                failures.append(
                    {
                        "source": path.name,
                        "trail": trail,
                        "roots": root_rows,
                    }
                )

    expected = {
        "all_roots_unaffordable_records": 233,
        "audited_roots": 521,
        "zero_excess_roots": 521,
        "roots_with_support_reserve": 521,
        "roots_minimum_closing_exchange_0": 444,
        "roots_minimum_closing_exchange_1": 25,
        "roots_minimum_closing_exchange_2": 52,
        "records_with_same_packing_reserve": 199,
        "failed_records_all_roots_zero_excess": 34,
    }
    for key, value in expected.items():
        if counts[key] != value:
            raise AssertionError((key, counts[key], value))
    if len(failures) != 34:
        raise AssertionError(("records_without_same_packing_reserve", len(failures)))

    report = {
        "status": "exact marked-packing complement and target-reserve audit",
        **dict(counts),
        "records_without_same_packing_reserve": len(failures),
        "first_failures": failures[:10],
        "scope": (
            "All-root-unaffordable records in the archived n=6 exact pairs. "
            "The complement and tangent identities are human; reserve closure "
            "is finite falsification evidence, not a universal selection theorem."
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

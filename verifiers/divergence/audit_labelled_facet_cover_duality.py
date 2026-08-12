#!/usr/bin/env python3
r"""Exact labelled rooted-row packing/cover duality audit.

For a root r, let G contain the nonroot players i for which {r,i} is
Lmin-tight, let B be its complement, and let H be the offroot traces A of
the root-containing Lmin-tight coalitions of size at least three.  Put

  K=floor(n^2/4)-n+1,
  C=K(|G|-1)-|B|,
  w(A)=K(1-|A cap G|)+|A cap B|.

The maximum canonical marked-facet margin is

  C + max { sum_A w(A)a_A : a>=0, incidence(a)<=1 },

whose exact LP dual is

  C + min { sum_i y_i : y>=0, y(A)>=w(A) for every A in H }.

This script checks the identity and strong duality on the finite n=6 archive
and the fixed hostile/sharp n=7 branch controls.  The displayed elimination
and ordinary LP duality are the proof; this is a regression/falsification
audit, not an all-dimensional selection theorem.
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

from audit_lmax_overcover import records  # noqa: E402
from audit_direct_ceiling_common_hinge_trichotomy import has_direct_packet  # noqa: E402
from audit_n6_sparse_lmax_complete_lmin_roots import complete_lmin_support  # noqa: E402
from exactlp import exact_linprog  # noqa: E402
from verify_labelled_branch_duals import CASES  # noqa: E402


def solve_labelled_cover(support: tuple[int, ...], root: int, n: int) -> dict:
    root_mask = 1 << root
    nonroots = tuple(i for i in range(n) if i != root)
    tight = set(support)
    good = tuple(i for i in nonroots if root_mask | (1 << i) in tight)
    good_set = set(good)
    bad = tuple(i for i in nonroots if i not in good_set)
    bad_set = set(bad)
    menu = tuple(
        coalition
        for coalition in support
        if coalition & root_mask and coalition.bit_count() >= 3
    )
    traces = tuple(coalition & ~root_mask for coalition in menu)
    K = n * n // 4 - n + 1
    constant = F(K * (len(good) - 1) - len(bad))
    weights = tuple(
        F(
            K * (1 - sum((trace >> i) & 1 for i in good_set))
            + sum((trace >> i) & 1 for i in bad_set)
        )
        for trace in traces
    )

    # Packing primal: maximize w.a subject to offroot incidence loads <= 1.
    primal_ub = [
        [F((trace >> i) & 1) for trace in traces]
        for i in nonroots
    ]
    primal_rhs = [F(1)] * len(nonroots)
    for j in range(len(traces)):
        primal_ub.append(
            [F(-1 if k == j else 0) for k in range(len(traces))]
        )
        primal_rhs.append(F(0))
    status, primal_objective, primal_solution = exact_linprog(
        [-weight for weight in weights], primal_ub, primal_rhs
    )
    if status != "optimal":
        raise AssertionError((root, "labelled packing", status))
    packing_value = -primal_objective

    # Cover dual: minimize sum y_i subject to y(trace) >= w(trace), y >= 0.
    dual_ub = [
        [F(-((trace >> i) & 1)) for i in nonroots]
        for trace in traces
    ]
    dual_rhs = [-weight for weight in weights]
    for j in range(len(nonroots)):
        dual_ub.append(
            [F(-1 if k == j else 0) for k in range(len(nonroots))]
        )
        dual_rhs.append(F(0))
    status, cover_value, cover_solution = exact_linprog(
        [F(1)] * len(nonroots), dual_ub, dual_rhs
    )
    if status != "optimal" or cover_value != packing_value:
        raise AssertionError((root, "labelled cover duality", status, packing_value, cover_value))

    margin = constant + packing_value
    loads = tuple(
        sum(
            (
                primal_solution[j]
                for j, trace in enumerate(traces)
                if trace >> i & 1
            ),
            F(0),
        )
        for i in nonroots
    )
    residual_pairs = tuple(F(1) - load for load in loads)
    delta = F(len(good) - 1) + sum(
        (
            primal_solution[j]
            * F(1 - sum((trace >> i) & 1 for i in good_set))
            for j, trace in enumerate(traces)
        ),
        F(0),
    )
    q_bad = sum(
        (residual_pairs[j] for j, i in enumerate(nonroots) if i in bad_set),
        F(0),
    )
    if margin != K * delta - q_bad:
        raise AssertionError("labelled-row elimination identity failed")

    # On a zero-margin face, affordability also requires positive root excess.
    max_delta_on_top = delta
    if margin == 0 and traces:
        delta_coefficients = tuple(
            F(1 - sum((trace >> i) & 1 for i in good_set))
            for trace in traces
        )
        status, delta_objective, _ = exact_linprog(
            [-coefficient for coefficient in delta_coefficients],
            primal_ub,
            primal_rhs,
            [[weight for weight in weights]],
            [packing_value],
        )
        if status != "optimal":
            raise AssertionError((root, "top-face root excess", status))
        max_delta_on_top = F(len(good) - 1) - delta_objective

    affordable = margin > 0 or (margin == 0 and max_delta_on_top > 0)
    unique_pair_partner_escaped = None
    if len(good) == 1:
        partner = good[0]
        unique_pair_partner_escaped = any(
            not (trace >> partner & 1) for trace in traces
        )
        if n >= 6 and affordable != unique_pair_partner_escaped:
            raise AssertionError((root, "locked-pair alternative"))

    return {
        "root": root,
        "tight_rooted_pairs": list(good),
        "bad_spoke_players": list(bad),
        "nonpair_menu_size": len(menu),
        "constant": str(constant),
        "positive_weight_count": sum(weight > 0 for weight in weights),
        "packing_value": str(packing_value),
        "cover_value": str(cover_value),
        "margin": str(margin),
        "root_excess": str(delta),
        "max_root_excess_on_top_face": str(max_delta_on_top),
        "q_bad": str(q_bad),
        "affordable": affordable,
        "unique_pair_partner_escaped_by_nonpair": unique_pair_partner_escaped,
        "packing": [str(value) for value in primal_solution],
        "cover": [str(value) for value in cover_solution],
    }


def maximum_overlap_roots(x, z):
    overlap = tuple(min(a, b) for a, b in zip(x, z))
    return tuple(i for i, value in enumerate(overlap) if value == max(overlap))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    n6_rows = []
    n6_positive_residuals = []
    counts = Counter()
    for path in args.paths:
        for _source, trail, values, x, z in records(json.loads(path.read_text()), path):
            if len(x) != 6:
                continue
            support = complete_lmin_support(values, x)
            roots = maximum_overlap_roots(x, z)
            audits = tuple(solve_labelled_cover(support, root, 6) for root in roots)
            counts["n6_records"] += 1
            counts["n6_roots"] += len(roots)
            counts["n6_affordable_roots"] += sum(row["affordable"] for row in audits)
            counts["n6_one_tight_pair_roots"] += sum(
                len(row["tight_rooted_pairs"]) == 1 for row in audits
            )
            counts["n6_one_pair_affordable_roots"] += sum(
                len(row["tight_rooted_pairs"]) == 1 and row["affordable"]
                for row in audits
            )
            counts["n6_one_pair_roots_with_escaping_nonpair"] += sum(
                row["unique_pair_partner_escaped_by_nonpair"] is True
                for row in audits
            )
            counts["n6_records_with_some_affordable_root"] += any(
                row["affordable"] for row in audits
            )
            row = {
                "source": path.name,
                "trail": trail,
                "roots": list(roots),
                "audits": list(audits),
            }
            n6_rows.append(row)
            total, floor, ceiling = sum(x, F(0)), min(x), max(z)
            direct = has_direct_packet(x, z, F(2, 3))
            interpolation = ceiling - floor + total * floor / ceiling >= F(2, 3) * total
            if direct:
                counts["n6_closed_by_direct"] += 1
            elif interpolation:
                counts["n6_closed_next_by_interpolation"] += 1
            elif floor == 0:
                counts["n6_closed_next_by_null_descent"] += 1
            else:
                counts["n6_positive_floor_residuals"] += 1
                counts["n6_positive_residuals_with_affordable_root"] += any(
                    audit["affordable"] for audit in audits
                )
                n6_positive_residuals.append(row)
    if counts["n6_records"] != 374:
        raise AssertionError(f"expected 374 n=6 rows, found {counts['n6_records']}")

    n7_rows = []
    for case in CASES:
        if len(case["x"]) != 7:
            continue
        roots = maximum_overlap_roots(case["x"], case["z"])
        audits = tuple(solve_labelled_cover(case["support_x"], root, 7) for root in roots)
        direct = has_direct_packet(case["x"], case["z"], F(7, 12))
        n7_rows.append(
            {
                "name": case["name"],
                "target": "7/12",
                "actual_overlap": str(
                    sum((min(a, b) for a, b in zip(case["x"], case["z"])), F(0))
                    / sum(case["x"], F(0))
                ),
                "maximum_overlap_roots": list(roots),
                "direct_packet_closes_target": direct,
                "direct_or_affordable_labelled_row": direct
                or any(audit["affordable"] for audit in audits),
                "audits": list(audits),
            }
        )

    report = {
        "status": "exact labelled rooted-row packing/cover duality audit",
        **dict(counts),
        "two_tight_pair_automatic_threshold": (
            "for n>=6, |G|>=2 gives C=K(|G|-1)-|B|>=K-(n-3)>=0; "
            "the zero nonpair packing is affordable with positive root excess"
        ),
        "one_tight_pair_locked_partner_theorem": (
            "for n>=6 and |G|=1, a root is affordable iff some rooted "
            "nonpair trace omits the unique tight-pair partner; otherwise "
            "that partner lies in every packing column and root excess is "
            "identically zero"
        ),
        "n6_four_arm_coverage": (
            "direct, then ceiling interpolation, then zero-floor null descent, "
            "then an affordable canonical labelled rooted row covers all 374 archive records"
        ),
        "n6_first_failures": [
            row
            for row in n6_rows
            if not any(audit["affordable"] for audit in row["audits"])
        ][:10],
        "n6_positive_floor_residuals": n6_positive_residuals,
        "n7_fixed_controls": n7_rows,
        "scope": (
            "374 archived n=6 pairs and six fixed n=7 hostile/sharp branch controls; "
            "exact primal/dual regression only, not a domain theorem"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

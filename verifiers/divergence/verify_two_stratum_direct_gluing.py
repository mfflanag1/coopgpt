#!/usr/bin/env python3
"""Exact audit for the arbitrary-Lmax direct-gluing master theorem.

The theorem itself is the displayed algebraic slack identity.  This driver
checks that identity over an exact parameter grid and verifies a fresh n=7
three-generator control, including its staged selections.  The finite grid is
an arithmetic regression, not the proof of the dimension-free identity.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_lmax_overcover import coalition_sum  # noqa: E402
from verify_labelled_branch_duals import (  # noqa: E402
    CASES,
    branch_system,
    one_witness_minimum,
    verify_complete_selection,
)


N = 7
GENERATORS = (
    (F(3), F(0), F(0), F(6), F(1), F(2), F(0)),
    (F(1), F(0), F(2), F(0), F(0), F(3), F(6)),
    (F(0), F(5), F(0), F(1), F(5), F(0), F(1)),
)
LMIN = (F(3, 2), F(3, 2), F(3, 2), F(9, 4), F(3, 2), F(3, 2), F(9, 4))
LMAX = (F(4, 3), F(2), F(4, 3), F(2), F(2), F(4, 3), F(2))
COMPARISON_COALITION = 74  # {1,3,6}=H union J.


def master_identity(point_x, point_z, p_set, g_set, h_set, j_set):
    p_set, g_set, h_set, j_set = map(tuple, (p_set, g_set, h_set, j_set))
    if set(p_set) | set(g_set) | set(h_set) != set(range(len(point_x))):
        raise AssertionError("P/G/H do not cover the players")
    if set(p_set) & set(g_set) or set(p_set) & set(h_set) or set(g_set) & set(h_set):
        raise AssertionError("P/G/H are not disjoint")
    if not set(j_set) <= set(g_set):
        raise AssertionError("J is not a subset of G")
    p, g, h, s = len(p_set), len(g_set), len(h_set), len(j_set)
    if min(p, g, h) < 1 or s >= g:
        raise AssertionError("invalid block sizes")
    total = sum(point_x, F(0))
    if sum(point_z, F(0)) != total:
        raise AssertionError("selection totals differ")
    if any(point_z[i] > point_x[i] for i in p_set + h_set):
        raise AssertionError("P or H contains a gainer")
    if any(point_x[i] > point_z[i] for i in g_set):
        raise AssertionError("G contains a nongainer")

    def point_sum(point, players):
        return sum((point[i] for i in players), F(0))

    m, q, n = p + g, g + h, p + g + h
    denominator = m - s
    weight = F(g, denominator)
    low_z = point_sum(point_z, p_set) / p
    high_z = point_sum(point_z, g_set + h_set) / q
    comparison_slack = (
        point_sum(point_z, h_set + j_set)
        - point_sum(point_x, h_set + j_set)
    )
    x_order_residual = (
        point_sum(point_x, j_set)
        + (F(1) - weight) * point_sum(point_x, tuple(i for i in g_set if i not in j_set))
        - weight * point_sum(point_x, p_set)
    )
    z_order_residual = (
        (F(1) - weight) * (point_sum(point_z, h_set) - h * high_z)
        - weight * (point_sum(point_z, j_set) - s * high_z)
    )
    gainer_packet = point_sum(point_z, j_set) - point_sum(point_x, j_set)
    h_loss = point_sum(point_x, h_set) - point_sum(point_z, h_set)
    residual_budget = (
        (p - s) * point_sum(point_x, g_set)
        - g * point_sum(point_x, p_set)
        + (p - s) * (point_sum(point_z, h_set) - h * high_z)
        + g * s * high_z
    ) / g
    if comparison_slack != gainer_packet - h_loss:
        raise AssertionError("gain-packet comparison reduction failed")
    if denominator * (x_order_residual + z_order_residual) != g * (
        residual_budget - gainer_packet
    ):
        raise AssertionError("gain-packet budget reduction failed")
    base = F(1) - F(g * p, q * denominator)
    low_weight = F(g * p * n, q * denominator)
    overlap = sum((min(a, b) for a, b in zip(point_x, point_z)), F(0))
    lhs = overlap - base * total
    rhs = (
        low_weight * low_z
        + weight * comparison_slack
        + x_order_residual
        + z_order_residual
    )
    if lhs != rhs:
        raise AssertionError("arbitrary-Lmax master identity failed")
    return {
        "sizes": {"p": p, "g": g, "h": h, "s": s},
        "base_bound_ratio": str(base),
        "comparison_coalition": sum(1 << i for i in h_set + j_set),
        "comparison_slack": str(comparison_slack),
        "x_order_residual": str(x_order_residual),
        "z_order_residual": str(z_order_residual),
        "gainer_packet": str(gainer_packet),
        "h_loss": str(h_loss),
        "residual_budget": str(residual_budget),
        "packet_hits_interval": h_loss <= gainer_packet <= residual_budget,
        "low_z_term": str(low_weight * low_z),
        "actual_overlap_ratio": str(overlap / total),
        "identity_margin": str(lhs),
        "all_payment_terms_nonnegative": all(
            value >= 0
            for value in (
                low_z,
                comparison_slack,
                x_order_residual,
                z_order_residual,
            )
        ),
    }


def audit_archived_direct_branches():
    cases = {case["name"]: case for case in CASES}
    specifications = (
        (
            "actual_top_fixed_failure",
            (5, 6),
            (1, 3, 4),
            (0, 2),
            (4,),
            F(7, 10),
        ),
        (
            "top_and_bottom_fixed_failure",
            (2,),
            (0, 1, 3, 6),
            (4, 5),
            (0, 1, 3),
            F(2, 3),
        ),
    )
    rows = []
    for name, p_set, g_set, h_set, j_set, expected in specifications:
        case = cases[name]
        row = master_identity(case["x"], case["z"], p_set, g_set, h_set, j_set)
        if F(row["base_bound_ratio"]) != expected:
            raise AssertionError("archived direct bound changed")
        if row["comparison_coalition"] not in case["support_x"]:
            raise AssertionError("comparison coalition is not Lmin-tight")
        if not row["all_payment_terms_nonnegative"]:
            raise AssertionError("archived direct branch has a negative payment term")
        rows.append({"name": name, **row})
    return rows


def audit_symbolic_identity():
    checked = 0
    for p in range(1, 6):
        for g in range(1, 6):
            for h in range(1, 6):
                m, q, n = p + g, g + h, p + g + h
                for s in range(g):
                    base = F(1) - F(g * p, q * (m - s))
                    low_weight = F(g * p * n, q * (m - s))
                    comparison_weight = F(g, m - s)
                    for low_z, low_x, high_x in (
                        (F(0), F(1), F(3)),
                        (F(1, 7), F(2, 5), F(4, 3)),
                        (F(1, 11), F(7, 13), F(19, 10)),
                    ):
                        total = m * low_x + h * high_x
                        high_z = (total - p * low_z) / q
                        if not low_z <= low_x <= high_z <= high_x:
                            continue
                        overlap = p * low_z + g * low_x + h * high_z
                        comparison_slack = (
                            (h + s) * high_z - h * high_x - s * low_x
                        )
                        lhs = overlap - base * total
                        rhs = (
                            low_weight * low_z
                            + comparison_weight * comparison_slack
                        )
                        if lhs != rhs:
                            raise AssertionError("two-stratum gluing identity failed")
                        checked += 1
    if not checked:
        raise AssertionError("empty symbolic regression grid")
    return checked


def audit_multistage_identity():
    checked = 0
    for p in range(1, 6):
        for g in range(1, 6):
            for h in range(1, 5):
                m, q, n = p + g, g + h, p + g + h
                for s in range(min(g, p + 1)):
                    if s == g:
                        continue
                    # Strictly ordered, nonuniform P/G payoffs.  Choose the H
                    # level so the comparison slack is exactly zero at l=0.
                    x_p = tuple(F(1) + F(i, 20) for i in range(p))
                    x_g = tuple(F(2) + F(i, 20) for i in range(g))
                    x_j = sum(x_g[:s], F(0))
                    sum_p = sum(x_p, F(0))
                    sum_g = sum(x_g, F(0))
                    tight_high_x = F(
                        (h + s) * (sum_p + sum_g) - q * x_j,
                        h * (g - s),
                    )
                    minimum_high_x = (sum_p + sum_g) / g
                    interior_high_x = (tight_high_x + minimum_high_x) / 2
                    for low_z, high_x in (
                        (F(0), tight_high_x),
                        (F(0), interior_high_x),
                        (min(x_p) / 20, interior_high_x),
                    ):
                        total = sum_p + sum_g + h * high_x
                        high_z = (total - p * low_z) / q
                        if not max(x_p) <= min(x_g) <= max(x_g) <= high_z <= high_x:
                            continue
                        comparison_slack = (
                            (h + s) * high_z - h * high_x - x_j
                        )
                        if comparison_slack < 0:
                            continue
                        denominator = m - s
                        base = F(1) - F(g * p, q * denominator)
                        low_weight = F(g * p * n, q * denominator)
                        comparison_weight = F(g, denominator)
                        order_residual = (
                            x_j
                            + (F(1) - comparison_weight) * (sum_g - x_j)
                            - comparison_weight * sum_p
                        )
                        if order_residual < 0:
                            raise AssertionError("ordered multistage residual is negative")
                        overlap = p * low_z + sum_g + h * high_z
                        if overlap - base * total != (
                            low_weight * low_z
                            + comparison_weight * comparison_slack
                            + order_residual
                        ):
                            raise AssertionError("multistage direct-gluing identity failed")
                        checked += 1
    if not checked:
        raise AssertionError("empty multistage regression grid")
    return checked


def audit_control():
    total = sum(GENERATORS[0], F(0))
    if any(sum(generator, F(0)) != total for generator in GENERATORS):
        raise AssertionError("generator totals differ")
    values = tuple(
        min(coalition_sum(generator, mask) for generator in GENERATORS)
        for mask in range(1 << N)
    )
    if any(values[1 << player] for player in range(N)):
        raise AssertionError("control is not singleton-normalized")
    support_x = tuple(
        mask for mask in range(1, (1 << N) - 1)
        if coalition_sum(LMIN, mask) == values[mask]
    )
    support_z = tuple(
        mask for mask in range(1, (1 << N) - 1)
        if coalition_sum(LMAX, mask) == values[mask]
    )
    if support_x != (48, 74, 88, 122) or support_z != (74, 88):
        raise AssertionError("tight supports changed")
    for point in (LMIN, LMAX):
        if sum(point, F(0)) != total:
            raise AssertionError("selection is inefficient")
        if any(
            coalition_sum(point, mask) < values[mask]
            for mask in range(1, (1 << N) - 1)
        ):
            raise AssertionError("displayed selection left the core")
    verify_complete_selection(values, LMIN, "min", support_x)
    verify_complete_selection(values, LMAX, "max", support_z)

    p, g, h, s = 3, 2, 2, 1
    m, q, n = p + g, g + h, p + g + h
    base = F(1) - F(g * p, q * (m - s))
    low_weight = F(g * p * n, q * (m - s))
    comparison_weight = F(g, m - s)
    overlap = sum((min(a, b) for a, b in zip(LMIN, LMAX)), F(0))
    low_z = LMAX[0]
    comparison_slack = (
        coalition_sum(LMAX, COMPARISON_COALITION)
        - coalition_sum(LMIN, COMPARISON_COALITION)
    )
    if overlap - base * total != (
        low_weight * low_z + comparison_weight * comparison_slack
    ):
        raise AssertionError("control does not instantiate the hand identity")
    if (base, low_weight, comparison_weight) != (F(5, 8), F(21, 8), F(1, 2)):
        raise AssertionError("control coefficients changed")
    if comparison_slack:
        raise AssertionError("comparison should be tight on the control")
    master = master_identity(
        LMIN,
        LMAX,
        (0, 2, 5),
        (1, 4),
        (3, 6),
        (1,),
    )
    if F(master["base_bound_ratio"]) != base:
        raise AssertionError("master identity and specialization disagree")

    case = {
        "x": LMIN,
        "z": LMAX,
        "g": GENERATORS[0],
        "support_x": support_x,
        "support_z": support_z,
    }
    system = branch_system(case)
    rooted_bounds = tuple(one_witness_minimum(system, root) for root in range(N))
    if rooted_bounds != (F(5, 8),) * N:
        raise AssertionError("rooted branch bounds changed")
    return {
        "generators": [[str(q) for q in row] for row in GENERATORS],
        "total": str(total),
        "lmin": [str(q) for q in LMIN],
        "lmax": [str(q) for q in LMAX],
        "lmin_tight_support": list(support_x),
        "lmax_tight_support": list(support_z),
        "comparison_coalition": COMPARISON_COALITION,
        "comparison_slack": str(comparison_slack),
        "overlap": str(overlap),
        "overlap_ratio": str(overlap / total),
        "hand_bound_ratio": str(base),
        "hand_identity": "O-(5/8)T=(21/8)z_0+(1/2)[z(74)-x(74)]",
        "all_rooted_branch_minima": [str(q) for q in rooted_bounds],
        "selection_check": "fourteen exact restricted-support staged LP certificates",
        "master_identity_terms": master,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {
        "status": "exact arbitrary-Lmax direct-gluing master audit",
        "human_theorem": (
            "for any sign partition P/G/H and comparison H+J, the exact "
            "master identity decomposes O-[1-gp/((g+h)(p+g-|J|))]T "
            "into a low-Lmax term, the comparison slack, and explicit "
            "Lmin and Lmax dispersion residuals; a nonnegative residual sum "
            "prove the displayed dimension-free overlap bound, while the "
            "comparison and residual-sum conditions reduce exactly to a "
            "cardinality-constrained interval for the gainer packet"
        ),
        "two_stratum_parameter_rows": audit_symbolic_identity(),
        "multistage_order_parameter_rows": audit_multistage_identity(),
        "arbitrary_lmax_archived_branches": audit_archived_direct_branches(),
        "control": audit_control(),
        "scope": (
            "the master identity and residual criterion are dimension-free; "
            "the finite grids, two archived branches, and n=7 control audit "
            "arithmetic and do not prove that every exact game admits a sign "
            "partition and Lmin-tight comparison whose gainer packet hits the "
            "required exact interval"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

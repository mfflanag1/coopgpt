#!/usr/bin/env python3
"""Exact audit for the arbitrary-Lmax direct-gluing master theorem.

The theorem itself is the displayed algebraic slack identity.  This driver
checks that identity over an exact parameter grid and verifies a fresh n=7
three-generator control, including its staged selections.  The finite grid is
an arithmetic regression, not the proof of the dimension-free identity.
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

from audit_lmax_overcover import coalition_sum, records  # noqa: E402
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
        "each_residual_nonnegative": (
            x_order_residual >= 0 and z_order_residual >= 0
        ),
        "master_bound_conditions_hold": (
            low_z >= 0
            and comparison_slack >= 0
            and x_order_residual + z_order_residual >= 0
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
        if not row["master_bound_conditions_hold"]:
            raise AssertionError("archived direct branch has a negative payment term")
        rows.append({"name": name, **row})
    return rows


def audit_fixed_branch_direct_atlas():
    """Classify all direct packets on the seven fixed hostile branches.

    This is a finite falsification atlas, not a universal selection theorem.
    It checks every sign-compatible P/H partition and every proper gainer
    packet J for the fixed displayed selections.
    """
    expected_direct = {
        "optimized_label_free_spectral_failure",
        "actual_top_fixed_failure",
        "top_and_bottom_fixed_failure",
        "coefficient_two_congestion_failure",
        "primitive_coefficient_seven_failure",
    }
    rows = []
    for case in CASES:
        point_x, point_z = tuple(case["x"]), tuple(case["z"])
        n = len(point_x)
        gainers = tuple(i for i in range(n) if point_z[i] > point_x[i])
        nongainers = tuple(i for i in range(n) if point_z[i] <= point_x[i])
        target = F(n, (n * n) // 4)
        candidates = []
        for h_size in range(1, len(nongainers)):
            for h_set in itertools.combinations(nongainers, h_size):
                p_set = tuple(i for i in nongainers if i not in h_set)
                for s in range(len(gainers)):
                    for j_set in itertools.combinations(gainers, s):
                        certificate = master_identity(
                            point_x, point_z, p_set, gainers, h_set, j_set
                        )
                        base = F(certificate["base_bound_ratio"])
                        if base < target or not certificate["packet_hits_interval"]:
                            continue
                        coalition = certificate["comparison_coalition"]
                        candidates.append({
                            "lmin_tight": coalition in case["support_x"],
                            "p_set": list(p_set),
                            "h_set": list(h_set),
                            "j_set": list(j_set),
                            **certificate,
                        })
        candidates.sort(
            key=lambda row: (
                not row["lmin_tight"],
                -F(row["base_bound_ratio"]),
                len(row["j_set"]),
                row["comparison_coalition"],
            )
        )
        has_direct = bool(candidates)
        if has_direct != (case["name"] in expected_direct):
            raise AssertionError("fixed direct/rooted atlas classification changed")
        total = sum(point_x, F(0))
        overlap = sum((min(a, b) for a, b in zip(point_x, point_z)), F(0))
        positive_lmax_equality = overlap == target * total and min(point_z) > 0
        if not has_direct and not positive_lmax_equality:
            raise AssertionError("rooted-only atlas row lost positive-Lmax equality")
        rows.append({
            "name": case["name"],
            "n": n,
            "target": str(target),
            "direct_candidate_count": len(candidates),
            "lmin_tight_direct_candidate_count": sum(
                row["lmin_tight"] for row in candidates
            ),
            "positive_lmax_equality": positive_lmax_equality,
            "best_prefer_lmin_tight": candidates[0] if candidates else None,
            "classification": (
                "direct packet closes target"
                if has_direct
                else "no direct packet on fixed selection; rooted arm required"
            ),
        })
    return rows


def audit_n6_archive_direct_census():
    """Falsify the tempting direct-only selection conjecture on the archive."""
    paths = (
        COOPGAMES / "verifiers/s6/harvest6_601.json",
        COOPGAMES / "verifiers/s6/harvest6_602.json",
    )
    counts = {
        "records": 0,
        "direct": 0,
        "direct_with_lmin_tight_comparison": 0,
        "no_direct": 0,
        "no_direct_strict_above_target": 0,
        "no_direct_equality": 0,
        "no_direct_positive_lmax": 0,
        "no_direct_lmax_with_zero": 0,
        "no_direct_with_ceiling_root": 0,
        "no_direct_closed_by_ceiling_interpolation": 0,
        "no_direct_not_closed_by_ceiling_interpolation": 0,
        "remaining_zero_floor": 0,
        "remaining_positive_floor_strict": 0,
        "remaining_equality": 0,
    }
    first_strict_failure = None
    for path in paths:
        data = json.loads(path.read_text())
        for _source, trail, values, point_x, point_z in records(data, path):
            if len(point_x) != 6:
                continue
            counts["records"] += 1
            target = F(2, 3)
            gainers = tuple(i for i in range(6) if point_z[i] > point_x[i])
            nongainers = tuple(i for i in range(6) if point_z[i] <= point_x[i])
            found = False
            found_tight = False
            for h_size in range(1, len(nongainers)):
                for h_set in itertools.combinations(nongainers, h_size):
                    p_set = tuple(i for i in nongainers if i not in h_set)
                    for s in range(len(gainers)):
                        for j_set in itertools.combinations(gainers, s):
                            row = master_identity(
                                point_x, point_z, p_set, gainers, h_set, j_set
                            )
                            if (
                                F(row["base_bound_ratio"]) >= target
                                and row["packet_hits_interval"]
                            ):
                                found = True
                                coalition = row["comparison_coalition"]
                                if coalition_sum(point_x, coalition) == values[coalition]:
                                    found_tight = True
            total = sum(point_x, F(0))
            overlap = sum((min(a, b) for a, b in zip(point_x, point_z)), F(0))
            if found:
                counts["direct"] += 1
                counts["direct_with_lmin_tight_comparison"] += found_tight
                continue
            counts["no_direct"] += 1
            floor = min(point_x)
            ceiling = max(point_z)
            ceiling_roots = tuple(
                i for i in range(6)
                if point_z[i] == ceiling and point_x[i] >= ceiling
            )
            if not ceiling_roots:
                raise AssertionError("archived direct failure lost its ceiling root")
            counts["no_direct_with_ceiling_root"] += 1
            interpolation = ceiling - floor + total * floor / ceiling
            interpolation_closes = interpolation >= target * total
            counts[
                "no_direct_closed_by_ceiling_interpolation"
                if interpolation_closes
                else "no_direct_not_closed_by_ceiling_interpolation"
            ] += 1
            if overlap == target * total:
                counts["no_direct_equality"] += 1
                if not interpolation_closes:
                    counts["remaining_equality"] += 1
            else:
                if overlap <= target * total:
                    raise AssertionError("n=6 archive contradicts proved target")
                counts["no_direct_strict_above_target"] += 1
                if not interpolation_closes:
                    counts[
                        "remaining_zero_floor"
                        if floor == 0
                        else "remaining_positive_floor_strict"
                    ] += 1
                if first_strict_failure is None:
                    first_strict_failure = {
                        "source": path.name,
                        "trail": trail,
                        "lmin": [str(q) for q in point_x],
                        "lmax": [str(q) for q in point_z],
                        "overlap_ratio": str(overlap / total),
                        "target": str(target),
                    }
            counts[
                "no_direct_positive_lmax"
                if min(point_z) > 0
                else "no_direct_lmax_with_zero"
            ] += 1
    expected = {
        "records": 374,
        "direct": 296,
        "direct_with_lmin_tight_comparison": 282,
        "no_direct": 78,
        "no_direct_strict_above_target": 76,
        "no_direct_equality": 2,
        "no_direct_positive_lmax": 44,
        "no_direct_lmax_with_zero": 34,
        "no_direct_with_ceiling_root": 78,
        "no_direct_closed_by_ceiling_interpolation": 28,
        "no_direct_not_closed_by_ceiling_interpolation": 50,
        "remaining_zero_floor": 34,
        "remaining_positive_floor_strict": 14,
        "remaining_equality": 2,
    }
    if counts != expected:
        raise AssertionError({"n6 direct census changed": counts})
    return {
        **counts,
        "first_strict_no_direct_control": first_strict_failure,
        "interpretation": (
            "refutes direct-only selection; the separately verified common-hinge "
            "root audit closes all 374 archived pairs at the 2/3 target"
        ),
        "scope": "finite exact archive census, not an all-six-player theorem",
    }


def audit_gpk_canonical_handover():
    """Audit the human direct/rooted handover formulas on G(p,k)."""
    checked = 0
    direct_closes = 0
    samples = []
    sample_parameters = {(3, 2), (2, 4), (3, 3), (1, 5)}
    for p in range(1, 11):
        for k in range(2, 11):
            n = p + k + 1
            low_x = F(p, p + 1)
            root_x = F(p * p * (k - 1), p + 1)
            high_z = F(p * (k - 1), k)
            point_x = (root_x,) + (low_x,) * (p + k)
            point_z = (high_z,) + (F(1, k),) * p + (high_z,) * k
            p_set = tuple(range(1, p + 1))
            g_set = tuple(range(p + 1, n))
            h_set = (0,)
            j_set = g_set[:-1]
            row = master_identity(point_x, point_z, p_set, g_set, h_set, j_set)
            direct_base = F(n, (p + 1) * (k + 1))
            rooted_base = F(n, k * (p + 1))
            target = F(n, (n * n) // 4)
            if F(row["base_bound_ratio"]) != direct_base:
                raise AssertionError("G(p,k) direct handover base changed")
            if F(row["actual_overlap_ratio"]) != rooted_base:
                raise AssertionError("G(p,k) rooted/actual formula changed")
            if any(F(row[key]) for key in (
                "comparison_slack", "x_order_residual", "z_order_residual"
            )):
                raise AssertionError("G(p,k) canonical direct residual changed")
            if rooted_base < target:
                raise AssertionError("G(p,k) rooted block-star bound missed target")
            closes = direct_base >= target
            if closes != ((p + 1) * (k + 1) <= (n * n) // 4):
                raise AssertionError("G(p,k) direct handover criterion changed")
            checked += 1
            direct_closes += closes
            if (p, k) in sample_parameters:
                samples.append({
                    "p": p,
                    "k": k,
                    "n": n,
                    "direct_base": str(direct_base),
                    "rooted_block_star_base": str(rooted_base),
                    "target": str(target),
                    "direct_closes_target": closes,
                })
    return {
        "parameter_rows": checked,
        "direct_closes_target_rows": direct_closes,
        "rooted_closes_target_rows": checked,
        "direct_formula": "n/[(p+1)(k+1)]",
        "rooted_block_star_formula": "n/[k(p+1)]",
        "direct_target_criterion": "(p+1)(k+1)<=floor(n^2/4)",
        "samples": samples,
        "scope": "finite arithmetic grid auditing the displayed human formulas",
    }


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
        "fixed_branch_direct_atlas": audit_fixed_branch_direct_atlas(),
        "n6_archive_direct_census": audit_n6_archive_direct_census(),
        "gpk_canonical_handover": audit_gpk_canonical_handover(),
        "control": audit_control(),
        "scope": (
            "the master identity and residual criterion are dimension-free; "
            "the finite grids, seven-branch direct/rooted atlas, 374-pair n=6 "
            "direct census, two archived branches, and n=7 control audit "
            "arithmetic and do not prove that "
            "every exact game admits a sign "
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

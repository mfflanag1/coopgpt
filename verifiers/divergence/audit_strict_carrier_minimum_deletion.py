#!/usr/bin/env python3
r"""Exact minimum-deletion audit for strict carrier-cycle packets.

For every strict-loss nongainer carrier cycle in the full-menu
all-unaffordable branch, enumerate first one complete staged Lmin support and
then the entire Lmin-tight menu.  Retain rows which contain the cycle, omit at
least one gainer, and exclude at least one nongainer.  For a row ``I`` write
``P`` for its excluded nongainers and ``A`` for its omitted gainers.  This
script checks exactly the two lower certificates (PXC6) and (PXC11).  It
records simultaneous closure in the n=6 archive and exactifies a new n=7
control which refutes simultaneous closure while preserving their maximum.
It also checks the dimension-free tight-co-singleton exchange identities and
shows that every strict n=6 deletion-size handover is one such exchange.

The output is a finite archive theorem and hostile-control replay, not an
all-n selection theorem.  In particular, the script retains every arbitrary
row on which the target reserve is negative as a falsifier for the stronger
"every proper carrier row closes" statement.
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

from audit_carrier_separator_payment import (  # noqa: E402
    carriers,
    directed_cycles,
    full_tight_support,
)
from audit_labelled_facet_cover_duality import (  # noqa: E402
    maximum_overlap_roots,
    solve_labelled_cover,
)
from audit_lmax_overcover import coalition_sum, records  # noqa: E402
from audit_n6_sparse_lmax_complete_lmin_roots import (  # noqa: E402
    complete_lmin_support,
)
from verify_labelled_branch_duals import CASES, verify_complete_selection  # noqa: E402


N7_SIMULTANEOUS_COUNTEREXAMPLE = {
    "name": "minimum_deletion_simultaneous_certificate_counterexample",
    "generators": (
        (1, 5, 0, 7, 0, 0, 0),
        (2, 0, 3, 1, 2, 3, 2),
        (0, 2, 0, 0, 5, 4, 2),
        (0, 1, 5, 6, 0, 1, 0),
    ),
    "x": (F(7, 4), F(7, 4), F(7, 4), F(17, 8), F(7, 4), F(17, 8), F(7, 4)),
    "z": (F(5, 3), F(5, 3), F(5, 3), F(2), F(2), F(2), F(2)),
}


def reserve_row(x, z, support_row, cycle, target):
    n = len(x)
    gainers = tuple(i for i in range(n) if z[i] > x[i])
    nongainers = tuple(i for i in range(n) if z[i] <= x[i])
    omitted_gainers = tuple(i for i in gainers if not support_row >> i & 1)
    excluded = tuple(i for i in nongainers if not support_row >> i & 1)
    if not omitted_gainers or not excluded:
        return None
    if any(not support_row >> i & 1 for i in cycle):
        return None

    p = len(excluded)
    coefficient = F(len(gainers) * n, (n - p) * (p + 1))
    total = sum(x, F(0))
    total_gain = sum((z[i] - x[i] for i in gainers), F(0))
    actual = (
        (F(1) - target) * total
        - total_gain
        - coefficient * sum((z[i] for i in excluded), F(0))
    )
    payment = coalition_sum(z, support_row) - coalition_sum(x, support_row)
    if payment < 0:
        raise AssertionError("an Lmin-tight row has negative comparison payment")
    comparison = (
        (F(1) - target) * total
        - total_gain
        - coefficient * sum((x[i] for i in excluded), F(0))
        + coefficient
        * sum((z[i] - x[i] for i in omitted_gainers), F(0))
    )
    if actual - comparison != coefficient * payment:
        raise AssertionError("PXC10 comparison decomposition failed")

    retained = tuple(i for i in nongainers if support_row >> i & 1)
    block = tuple(cycle)
    extra = tuple(i for i in retained if i not in set(block))
    maximum = z[block[0]]
    if any(z[i] != maximum for i in block):
        raise AssertionError("carrier cycle is not one Lmax root block")
    next_level = max((z[i] for i in excluded), default=F(0))
    ordered = (
        len(block) * maximum
        + sum((z[i] for i in extra), F(0))
        + sum((x[i] for i in gainers), F(0))
        - target * total
        - p * max(coefficient - 1, F(0)) * next_level
    )
    if ordered > actual:
        raise AssertionError("PXC6 ordered-cut lower bound failed")
    excluded_lmax_mass = sum((z[i] for i in excluded), F(0))
    comparison_error = coefficient * payment
    if coefficient <= 1:
        ordered_error_formula = (F(1) - coefficient) * excluded_lmax_mass
    else:
        ordered_error_formula = (coefficient - 1) * (
            p * next_level - excluded_lmax_mass
        )
    ordered_error = actual - ordered
    if ordered_error != ordered_error_formula:
        raise AssertionError("ordered-cut error formula failed")
    minimum_error = min(comparison_error, ordered_error)
    max_certificate = max(comparison, ordered)
    if max_certificate != actual - minimum_error:
        raise AssertionError("PXC12 hybrid minimum-error identity failed")
    overlap_surplus = (F(1) - target) * total - total_gain
    lmax_cut_price = excluded_lmax_mass + p * max(coefficient - 1, F(0)) * next_level
    lmin_omitted_price = coefficient * (excluded_lmax_mass + payment)
    retained_nongainers = tuple(i for i in nongainers if support_row >> i & 1)
    included_gainers = tuple(i for i in gainers if support_row >> i & 1)
    lmax_row_score = sum((z[i] for i in retained_nongainers), F(0)) - (
        p * max(coefficient - 1, F(0)) * next_level
    )
    lmin_row_score = sum((x[i] for i in retained_nongainers), F(0)) - sum(
        (z[i] - x[i] for i in included_gainers), F(0)
    )
    if lmax_cut_price != sum((z[i] for i in nongainers), F(0)) - lmax_row_score:
        raise AssertionError("PXC15 Lmax score identity failed")
    if lmin_omitted_price != coefficient * (
        sum((x[i] for i in nongainers), F(0))
        - total_gain
        - lmin_row_score
    ):
        raise AssertionError("PXC15 Lmin score identity failed")
    if ordered != overlap_surplus - lmax_cut_price:
        raise AssertionError("PXC13 Lmax price identity failed")
    if comparison != overlap_surplus - lmin_omitted_price:
        raise AssertionError("PXC13 Lmin price identity failed")
    return {
        "support_row": support_row,
        "excluded_nongainers": list(excluded),
        "omitted_gainers": list(omitted_gainers),
        "p": p,
        "coefficient": str(coefficient),
        "actual_target_reserve": str(actual),
        "comparison_lower_bound": str(comparison),
        "ordered_cut_lower_bound": str(ordered),
        "comparison_payment": str(payment),
        "comparison_error": str(comparison_error),
        "ordered_cut_error": str(ordered_error),
        "hybrid_minimum_error": str(minimum_error),
        "hybrid_max_certificate": str(max_certificate),
        "overlap_target_surplus": str(overlap_surplus),
        "lmax_cut_price": str(lmax_cut_price),
        "lmin_omitted_price": str(lmin_omitted_price),
        "lmax_row_score": str(lmax_row_score),
        "lmin_row_score": str(lmin_row_score),
    }


def audit_pair(
    source,
    trail,
    values,
    x,
    z,
    selected_support,
    target,
    counters,
    profiles,
    require_both=False,
    residual_exceptions=None,
    handover_details=None,
):
    n = len(x)
    if target != F(n, n * n // 4):
        raise AssertionError("wrong sharp target for player count")
    if any(coalition_sum(x, coalition) != values[coalition] for coalition in selected_support):
        raise AssertionError("selected staged support contains a non-tight row")
    full_support = full_tight_support(values, x)
    complete_menu = set(selected_support) == set(full_support)
    roots = maximum_overlap_roots(x, z)
    gates = tuple(solve_labelled_cover(full_support, root, n) for root in roots)
    if any(gate["affordable"] for gate in gates):
        return []
    graph = {
        gate["root"]: tuple(carrier for carrier in carriers(gate) if carrier in roots)
        for gate in gates
    }
    gainers = tuple(i for i in range(n) if z[i] > x[i])
    nongainers = set(range(n)) - set(gainers)
    total_gain = sum((z[i] - x[i] for i in gainers), F(0))
    negative_rows = []
    for cycle in directed_cycles(graph):
        if not set(cycle) <= nongainers or x[cycle[0]] <= z[cycle[0]]:
            continue
        rows = tuple(
            row
            for coalition in selected_support
            if (row := reserve_row(x, z, coalition, cycle, target)) is not None
        )
        if not rows:
            raise AssertionError((source, trail, cycle, "no admissible carrier row"))
        minimum_p = min(row["p"] for row in rows)
        minimum_rows = tuple(row for row in rows if row["p"] == minimum_p)
        overlap_surpluses = {F(row["overlap_target_surplus"]) for row in minimum_rows}
        if len(overlap_surpluses) != 1:
            raise AssertionError("row-dependent global overlap surplus")
        overlap_surplus = overlap_surpluses.pop()
        z_star = min(F(row["lmax_cut_price"]) for row in minimum_rows)
        x_star = min(F(row["lmin_omitted_price"]) for row in minimum_rows)
        z_all = min(F(row["lmax_cut_price"]) for row in rows)
        x_all = min(F(row["lmin_omitted_price"]) for row in rows)
        if max(F(row["lmax_row_score"]) for row in minimum_rows) + z_star != sum(
            (z[i] for i in nongainers), F(0)
        ):
            raise AssertionError("PXC15 family Lmax score optimum failed")
        coefficient = F(minimum_rows[0]["coefficient"])
        if coefficient * (
            sum((x[i] for i in nongainers), F(0))
            - total_gain
            - max(F(row["lmin_row_score"]) for row in minimum_rows)
        ) != x_star:
            raise AssertionError("PXC15 family Lmin score optimum failed")
        best_max_certificate = max(
            F(row["hybrid_max_certificate"]) for row in minimum_rows
        )
        if best_max_certificate != overlap_surplus - min(z_star, x_star):
            raise AssertionError("PXC13 family price-selection identity failed")
        best_all_max_certificate = max(F(row["hybrid_max_certificate"]) for row in rows)
        if best_all_max_certificate != overlap_surplus - min(z_all, x_all):
            raise AssertionError("PXC16 full-family price-selection identity failed")

        # PXC18: if a retained nongainer j has an x-tight co-singleton,
        # exact uncrossing makes I\{j} tight.  The two prices then obey exact
        # one-player exchange laws.  Audit every such available exchange,
        # not merely the price-improving ones.
        row_by_support = {row["support_row"]: row for row in rows}
        exchange_pairs = []
        for parent in rows:
            parent_support = parent["support_row"]
            for j in sorted(nongainers - set(cycle)):
                if not parent_support >> j & 1:
                    continue
                cosingleton = ((1 << n) - 1) ^ (1 << j)
                if cosingleton not in full_support:
                    continue
                child_support = parent_support & ~(1 << j)
                child = row_by_support.get(child_support)
                if child is None:
                    if complete_menu:
                        raise AssertionError(
                            (
                                source,
                                trail,
                                cycle,
                                parent_support,
                                j,
                                "PXC4 exchange child absent",
                            )
                        )
                    continue
                cp, cq = F(parent["coefficient"]), F(child["coefficient"])
                if cq / cp - 1 != F(
                    2 * parent["p"] + 2 - n,
                    (parent["p"] + 2) * (n - parent["p"] - 1),
                ):
                    raise AssertionError("PXC19 coefficient exchange identity failed")
                xp, xq = F(parent["lmin_omitted_price"]), F(child["lmin_omitted_price"])
                zp, zq = F(parent["lmax_cut_price"]), F(child["lmax_cut_price"])
                comparison_mass = xp / cp
                if xq - xp != (cq - cp) * comparison_mass + cq * x[j]:
                    raise AssertionError("PXC18 Lmin exchange identity failed")
                parent_max = max(z[i] for i in parent["excluded_nongainers"])
                child_max = max(parent_max, z[j])
                ap = parent["p"] * max(cp - 1, F(0))
                aq = child["p"] * max(cq - 1, F(0))
                if zq - zp != z[j] + aq * child_max - ap * parent_max:
                    raise AssertionError("PXC18 Lmax exchange identity failed")
                exchange_pairs.append((parent, child, j))
        counters["tight_cosingleton_exchange_pairs"] += len(exchange_pairs)
        for parent, child, _j in exchange_pairs:
            if F(parent["lmin_omitted_price"]) == x_all:
                if F(child["lmin_omitted_price"]) < x_all:
                    raise AssertionError("PXC20 Lmin minimizer is not exchange-stable")
                counters["global_lmin_price_exchange_stability_checks"] += 1
            if F(parent["lmax_cut_price"]) == z_all:
                if F(child["lmax_cut_price"]) < z_all:
                    raise AssertionError("PXC20 Lmax minimizer is not exchange-stable")
                counters["global_lmax_price_exchange_stability_checks"] += 1
        all_both = not any(
            F(row["comparison_lower_bound"]) < 0
            or F(row["ordered_cut_lower_bound"]) < 0
            for row in minimum_rows
        )
        all_either = all(
            max(
                F(row["comparison_lower_bound"]),
                F(row["ordered_cut_lower_bound"]),
            )
            >= 0
            for row in minimum_rows
        )
        if not all_either:
            raise AssertionError((source, trail, cycle, "minimum-deletion max-certificate failure"))
        if require_both and not all_both:
            raise AssertionError((source, trail, cycle, "minimum-deletion failure"))

        counters["strict_carrier_cycles"] += 1
        counters["admissible_rows"] += len(rows)
        counters["minimum_deletion_rows"] += len(minimum_rows)
        counters["cycles_all_minimum_rows_close_either_certificate"] += all_either
        counters["cycles_all_minimum_rows_close_both_certificates"] += all_both
        counters["cycles_some_minimum_row_closes_both_certificates"] += any(
            F(row["comparison_lower_bound"]) >= 0
            and F(row["ordered_cut_lower_bound"]) >= 0
            for row in minimum_rows
        )
        counters["minimum_family_lmax_price_strictly_cheaper"] += z_star < x_star
        counters["minimum_family_lmin_price_strictly_cheaper"] += x_star < z_star
        counters["minimum_family_colour_price_tie"] += x_star == z_star
        counters["minimum_family_best_max_certificate_closes"] += best_max_certificate >= 0
        counters["full_family_best_max_certificate_closes"] += best_all_max_certificate >= 0
        counters["minimum_deletion_globally_price_optimal"] += min(z_star, x_star) == min(
            z_all, x_all
        )
        counters["larger_deletion_strictly_improves_price"] += min(z_all, x_all) < min(
            z_star, x_star
        )
        counters["full_family_lmax_price_strictly_cheaper"] += z_all < x_all
        counters["full_family_lmin_price_strictly_cheaper"] += x_all < z_all
        counters["full_family_colour_price_tie"] += x_all == z_all
        global_price = min(z_all, x_all)
        optimal_deletion_sizes = sorted(
            {
                row["p"]
                for row in rows
                if min(F(row["lmax_cut_price"]), F(row["lmin_omitted_price"]))
                == global_price
            }
        )
        for optimal_p in optimal_deletion_sizes:
            counters[f"cycles_with_global_optimum_at_p_{optimal_p}"] += 1
        if global_price < min(z_star, x_star):
            counters[
                f"strict_price_handover_p_{minimum_p}_to_p_{min(optimal_deletion_sizes)}"
            ] += 1
            witnesses = [
                (parent, child, j)
                for parent, child, j in exchange_pairs
                if parent["p"] == minimum_p
                and min(
                    F(parent["lmax_cut_price"]),
                    F(parent["lmin_omitted_price"]),
                )
                == min(z_star, x_star)
                and min(
                    F(child["lmax_cut_price"]),
                    F(child["lmin_omitted_price"]),
                )
                == global_price
            ]
            if witnesses:
                counters["strict_handovers_with_tight_cosingleton_exchange"] += 1
                parent, child, j = witnesses[0]
                zero_payoff = x[j] == 0 and z[j] == 0
                counters["strict_handovers_deleting_zero_payoff_player"] += zero_payoff
                if handover_details is not None:
                    handover_details.append(
                        {
                            "source": source,
                            "trail": trail,
                            "cycle": list(cycle),
                            "parent_support_row": parent["support_row"],
                            "child_support_row": child["support_row"],
                            "deleted_player": j,
                            "deleted_lmin_payoff": str(x[j]),
                            "deleted_lmax_payoff": str(z[j]),
                            "parent_price": str(min(z_star, x_star)),
                            "child_price": str(global_price),
                        }
                    )
            else:
                counters["strict_handovers_without_tight_cosingleton_exchange"] += 1
        counters["minimum_rows_zero_comparison_error"] += sum(
            F(row["comparison_error"]) == 0 for row in minimum_rows
        )
        counters["minimum_rows_zero_ordered_cut_error"] += sum(
            F(row["ordered_cut_error"]) == 0 for row in minimum_rows
        )
        counters["minimum_rows_both_errors_zero"] += sum(
            F(row["comparison_error"]) == 0
            and F(row["ordered_cut_error"]) == 0
            for row in minimum_rows
        )
        counters["cycles_all_minimum_rows_zero_comparison_error"] += all(
            F(row["comparison_error"]) == 0 for row in minimum_rows
        )
        counters["cycles_some_minimum_row_zero_comparison_error"] += any(
            F(row["comparison_error"]) == 0 for row in minimum_rows
        )
        if residual_exceptions is not None:
            residual_exceptions.extend(
                {
                    "source": source,
                    "trail": trail,
                    "cycle": list(cycle),
                    **row,
                }
                for row in minimum_rows
                if F(row["comparison_error"]) > 0
            )
        counters["arbitrary_negative_reserve_rows"] += sum(
            F(row["actual_target_reserve"]) < 0 for row in rows
        )
        counters["arbitrary_rows_closing_both_certificates"] += sum(
            F(row["comparison_lower_bound"]) >= 0
            and F(row["ordered_cut_lower_bound"]) >= 0
            for row in rows
        )
        profiles[
            (
                len(gainers),
                len(cycle),
                minimum_p,
                min(len(row["omitted_gainers"]) for row in minimum_rows),
                max(len(row["omitted_gainers"]) for row in minimum_rows),
            )
        ] += 1
        negative_rows.extend(
            {
                "source": source,
                "trail": trail,
                "cycle": list(cycle),
                **row,
            }
            for row in rows
            if F(row["actual_target_reserve"]) < 0
        )
    return negative_rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    extracted_counters, extracted_profiles = Counter(), Counter()
    full_counters, full_profiles = Counter(), Counter()
    extracted_negative_rows, full_negative_rows = [], []
    extracted_residual_exceptions, full_residual_exceptions = [], []
    full_handover_details = []
    for path in args.paths:
        payload = json.loads(path.read_text())
        for _source, trail, values, x, z in records(payload, path):
            if len(x) != 6:
                continue
            extracted_negative_rows.extend(
                audit_pair(
                    path.name,
                    trail,
                    values,
                    x,
                    z,
                    complete_lmin_support(values, x),
                    F(2, 3),
                    extracted_counters,
                    extracted_profiles,
                    require_both=True,
                    residual_exceptions=extracted_residual_exceptions,
                )
            )
            full_negative_rows.extend(
                audit_pair(
                    path.name,
                    trail,
                    values,
                    x,
                    z,
                    full_tight_support(values, x),
                    F(2, 3),
                    full_counters,
                    full_profiles,
                    require_both=True,
                    residual_exceptions=full_residual_exceptions,
                    handover_details=full_handover_details,
                )
            )

    hostile = []
    for case in CASES:
        if len(case["x"]) != 7:
            continue
        x, z = tuple(case["x"]), tuple(case["z"])
        generators = (tuple(map(F, case["g"])), tuple(map(F, case["h"])))
        values = tuple(
            min(coalition_sum(generator, coalition) for generator in generators)
            for coalition in range(1 << 7)
        )
        case_counters, case_profiles = Counter(), Counter()
        found = audit_pair(
            case["name"],
            "fixed hostile control",
            values,
            x,
            z,
            tuple(case["support_x"]),
            F(7, 12),
            case_counters,
            case_profiles,
        )
        hostile.append(
            {
                "name": case["name"],
                **dict(case_counters),
                "negative_arbitrary_rows": found,
            }
        )

    case = N7_SIMULTANEOUS_COUNTEREXAMPLE
    generators = tuple(tuple(map(F, row)) for row in case["generators"])
    values = tuple(
        min(coalition_sum(generator, coalition) for generator in generators)
        for coalition in range(1 << 7)
    )
    if any(values[1 << i] != 0 for i in range(7)):
        raise AssertionError("new control is not singleton-normalized")
    for generator in generators:
        if sum(generator, F(0)) != values[-1] or any(
            coalition_sum(generator, coalition) < values[coalition]
            for coalition in range(1 << 7)
        ):
            raise AssertionError("lower-envelope generator is not a core point")
    x, z = case["x"], case["z"]
    support_x = full_tight_support(values, x)
    support_z = full_tight_support(values, z)
    verify_complete_selection(values, x, "min", support_x)
    verify_complete_selection(values, z, "max", support_z)
    case_counters, case_profiles = Counter(), Counter()
    found = audit_pair(
        case["name"],
        "exact lower-envelope control",
        values,
        x,
        z,
        support_x,
        F(7, 12),
        case_counters,
        case_profiles,
    )
    roots = maximum_overlap_roots(x, z)
    gates = tuple(solve_labelled_cover(support_x, root, 7) for root in roots)
    graph = {
        gate["root"]: tuple(carrier for carrier in carriers(gate) if carrier in roots)
        for gate in gates
    }
    cycles = directed_cycles(graph)
    if roots != (3, 5) or any(gate["affordable"] for gate in gates) or cycles != ((3, 5),):
        raise AssertionError("new n=7 control lost its unaffordable carrier cycle")
    control_rows = tuple(
        row
        for coalition in support_x
        if (row := reserve_row(x, z, coalition, cycles[0], F(7, 12))) is not None
    )
    if len(control_rows) != 2 or any(
        F(row["actual_target_reserve"]) != F(13, 24)
        or F(row["comparison_lower_bound"]) != F(13, 24)
        or F(row["ordered_cut_lower_bound"]) != F(-1, 12)
        or F(row["comparison_error"]) != 0
        or F(row["ordered_cut_error"]) != F(5, 8)
        for row in control_rows
    ):
        raise AssertionError("new n=7 two-colour margins changed")
    hostile.append(
        {
            "name": case["name"],
            "generators": [[str(q) for q in row] for row in generators],
            "lmin": [str(q) for q in x],
            "lmax": [str(q) for q in z],
            "overlap": str(sum((min(x[i], z[i]) for i in range(7)), F(0))),
            "maximum_overlap_roots": list(roots),
            "minimum_deletion_row_details": list(control_rows),
            **dict(case_counters),
            "negative_arbitrary_rows": found,
            "interpretation": (
                "every minimum-deletion row has PXC11=13/24 but PXC6=-1/12; "
                "this refutes simultaneous closure, not the max-certificate"
            ),
        }
    )

    report = {
        "status": "exact finite archive theorem; not an all-n selection proof",
        "inputs": [path.name for path in args.paths],
        "statement_checked": (
            "in the n=6 archive, every minimum-deletion row simultaneously has "
            "nonnegative PXC6 and PXC11 lower certificates; a new exact n=7 "
            "control refutes simultaneous closure but every minimum row retains "
            "a nonnegative max(PXC6,PXC11) certificate; all 29 strict n=6 "
            "full-menu price handovers are exact tight-co-singleton exchanges "
            "deleting a player with zero Lmin and Lmax payoff"
        ),
        "n6_extracted_support_counts": dict(extracted_counters),
        "n6_full_tight_menu_counts": dict(full_counters),
        "extracted_cycle_profiles_g_cycleSize_p_minA_maxA": {
            ",".join(map(str, key)): value
            for key, value in sorted(extracted_profiles.items())
        },
        "full_menu_cycle_profiles_g_cycleSize_p_minA_maxA": {
            ",".join(map(str, key)): value
            for key, value in sorted(full_profiles.items())
        },
        "negative_rows_in_extracted_support": extracted_negative_rows,
        "negative_rows_in_full_tight_menu": full_negative_rows,
        "positive_comparison_error_minimum_rows_in_extracted_support": (
            extracted_residual_exceptions
        ),
        "positive_comparison_error_minimum_rows_in_full_tight_menu": (
            full_residual_exceptions
        ),
        "n6_full_menu_strict_handover_details": full_handover_details,
        "n7_hostile_and_sharp_controls": hostile,
        "limitations": (
            "the n=6 count uses two archived harvest files and one extracted "
            "complete staged support per record; the n=7 replay is a fixed "
            "control family; neither archive is exhaustive in all exact games"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

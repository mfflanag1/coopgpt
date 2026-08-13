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
shows that every strict n=6 deletion-size handover is one such exchange.  The
weaker direct reserve price and its exchange law are checked separately from
the two sufficient certificate prices.

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
from itertools import combinations
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
from audit_lmax_overcover import coalition_sum, records, top_certificate  # noqa: E402
from audit_n6_sparse_lmax_complete_lmin_roots import (  # noqa: E402
    complete_lmin_support,
)
from exactlp import exact_linprog  # noqa: E402
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


def endpoint_face_gap(values, shortage):
    """Compute PXC29's exact common-endpoint Chebyshev gap."""
    # PXC28/exactness supplies an endpoint witness for one co-singleton.
    # Reserve the exact simplex solve for the genuinely aggregate case.
    if len(shortage) == 1:
        return F(0)
    n = (len(values)).bit_length() - 1
    full = (1 << n) - 1
    total = values[full]
    width = n + 1
    t_index = n
    inequalities = []
    inequality_rhs = []
    for coalition in range(1, full):
        row = [F(0)] * width
        for i in range(n):
            if coalition >> i & 1:
                row[i] = F(-1)
        inequalities.append(row)
        inequality_rhs.append(-values[coalition])
    for j in shortage:
        upper_endpoint = total - values[full ^ (1 << j)]
        row = [F(0)] * width
        row[j] = F(-1)
        row[t_index] = F(-1)
        inequalities.append(row)
        inequality_rhs.append(-upper_endpoint)
    equality = [[F(1)] * n + [F(0)]]
    objective = [F(0)] * width
    objective[t_index] = F(1)
    status, optimum, _solution = exact_linprog(
        objective,
        inequalities,
        inequality_rhs,
        equality,
        [total],
    )
    if status != "optimal" or optimum < 0:
        raise AssertionError("PXC29 endpoint-face gap LP failed")
    return optimum


def multi_endpoint_separator_control():
    """Sharp n=7 positive-gap control for PXC29, PXC30, and PXC36."""
    n = 7
    full = (1 << n) - 1
    generators = (
        (F(1), F(0), F(0), F(0), F(0), F(0), F(0)),
        (F(0), F(1), F(0), F(0), F(0), F(0), F(0)),
    )
    values = tuple(
        min(coalition_sum(generator, coalition) for generator in generators)
        for coalition in range(1 << n)
    )
    shortage = (0, 1)
    gap = endpoint_face_gap(values, shortage)
    if gap != F(1, 2):
        raise AssertionError("PXC29 multi-endpoint control gap is not 1/2")
    z = (F(1, 2), F(1, 2), F(0), F(0), F(0), F(0), F(0))
    certificate = top_certificate(values, z)
    alpha = certificate["alpha"]
    expected_alpha = (F(1, 2), F(1, 2), F(0), F(0), F(0), F(0), F(0))
    if alpha != expected_alpha:
        raise AssertionError("unexpected Lmax load in multi-endpoint control")
    beta = (F(1, 2), F(1, 2))
    outside_load = max(alpha[i] for i in range(n) if i not in shortage)
    upper_endpoints = tuple(
        values[full] - values[full ^ (1 << j)] for j in shortage
    )
    price = min(
        (alpha[j] - outside_load) / beta[index]
        for index, j in enumerate(shortage)
    )
    bound = (
        outside_load * values[full]
        + sum(
            ((alpha[j] - outside_load) * upper_endpoints[index]
             for index, j in enumerate(shortage)),
            F(0),
        )
        - price * gap
    )
    if bound != max(z):
        raise AssertionError("PXC36 is not sharp on multi-endpoint control")

    # PXC30: (1/2)1_N plus one half of each dummy singleton equals
    # (1/2)1_(N\{0})+(1/2)1_(N\{1}); its value gap is 1/2.
    gamma = F(1, 2)
    lambdas = {1 << j: F(1, 2) for j in range(2, n)}
    for i in range(n):
        left_load = gamma + sum(
            (weight for coalition, weight in lambdas.items() if coalition >> i & 1),
            F(0),
        )
        right_load = sum(
            (beta[index] for index, j in enumerate(shortage)
             if (full ^ (1 << j)) >> i & 1),
            F(0),
        )
        if left_load != right_load:
            raise AssertionError("PXC30 multi-endpoint incidence identity failed")
    dual_gap = (
        sum((weight * values[coalition] for coalition, weight in lambdas.items()), F(0))
        + gamma * values[full]
        - sum(
            (beta[index] * values[full ^ (1 << j)]
             for index, j in enumerate(shortage)),
            F(0),
        )
    )
    if dual_gap != gap:
        raise AssertionError("PXC30 multi-endpoint value identity failed")
    return {
        "description": "dummy-extended exact two-player simplex; control only",
        "endpoint_gap": str(gap),
        "lmax_load": [str(value) for value in alpha],
        "separator_beta": [str(value) for value in beta],
        "separator_price": str(price),
        "pxc36_bound": str(bound),
        "lmax_ceiling": str(max(z)),
        "pxc30_gamma": str(gamma),
        "pxc30_dummy_singleton_weights": {
            str(coalition.bit_length() - 1): str(weight)
            for coalition, weight in lambdas.items()
        },
        "facet_scope": "decomposable sign-and-price control; not a new facet",
    }


def ceiling_interval_reaches_target(total, minimum, upper, target, n):
    """Minimize m-minimum+total*minimum/m on [total/n, upper] exactly."""
    lower = total / n
    if upper < lower:
        raise AssertionError("invalid ceiling interval")
    stationary_square = total * minimum
    if upper * upper <= stationary_square:
        bound = upper - minimum + total * minimum / upper
        return bound >= target * total
    if lower * lower >= stationary_square:
        bound = lower - minimum + total * minimum / lower
        return bound >= target * total
    # The minimum is 2*sqrt(total*minimum)-minimum.  Both sides of the
    # squared comparison below are nonnegative.
    return 4 * total * minimum >= (target * total + minimum) ** 2


def reachable(graph, source, target):
    frontier = [source]
    seen = set()
    while frontier:
        node = frontier.pop()
        if node == target:
            return True
        if node in seen:
            continue
        seen.add(node)
        frontier.extend(graph.get(node, ()))
    return False


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
    direct_reserve_price = coefficient * excluded_lmax_mass
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
    if actual != overlap_surplus - direct_reserve_price:
        raise AssertionError("PXC22 direct reserve price identity failed")
    if direct_reserve_price > min(lmax_cut_price, lmin_omitted_price):
        raise AssertionError("PXC22 direct price does not dominate both certificates")
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
        "direct_reserve_price": str(direct_reserve_price),
        "lmax_row_score": str(lmax_row_score),
        "lmin_row_score": str(lmin_row_score),
        "retained_nongainer_lmax_mass": str(
            sum((z[i] for i in retained_nongainers), F(0))
        ),
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
    endpoint_gap_cache=None,
    overcover_cache=None,
    pxc40_offtop_details=None,
    pxc40_outside_scc_details=None,
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
        y_all = min(F(row["direct_reserve_price"]) for row in rows)
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
        for p_value in sorted({row["p"] for row in rows}):
            p_rows = tuple(row for row in rows if row["p"] == p_value)
            p_coefficient = F(p_rows[0]["coefficient"])
            p_direct = min(F(row["direct_reserve_price"]) for row in p_rows)
            if p_direct != p_coefficient * (
                sum((z[i] for i in nongainers), F(0))
                - max(F(row["retained_nongainer_lmax_mass"]) for row in p_rows)
            ):
                raise AssertionError("PXC22 fixed-cardinality direct score identity failed")
        best_max_certificate = max(
            F(row["hybrid_max_certificate"]) for row in minimum_rows
        )
        if best_max_certificate != overlap_surplus - min(z_star, x_star):
            raise AssertionError("PXC13 family price-selection identity failed")
        best_all_max_certificate = max(F(row["hybrid_max_certificate"]) for row in rows)
        if best_all_max_certificate != overlap_surplus - min(z_all, x_all):
            raise AssertionError("PXC16 full-family price-selection identity failed")

        # PXC28: tight co-singletons are exactly the coordinates at their
        # individual core upper endpoint T-v(N\{j}).  In an exact game a
        # missing direction therefore comes with an exactness witness at that
        # endpoint, rather than being an unexplained support accident.
        total = sum(x, F(0))
        full_coalition = (1 << n) - 1
        pxc39_checked_cycle = False
        pxc39_closes_cycle = False
        for row in rows:
            shortage = []
            for j in sorted(nongainers - set(cycle)):
                if not row["support_row"] >> j & 1:
                    continue
                upper_endpoint = total - values[full_coalition ^ (1 << j)]
                if x[j] > upper_endpoint:
                    raise AssertionError("PXC28 core upper endpoint violated")
                tight_cosingleton = (full_coalition ^ (1 << j)) in full_support
                if tight_cosingleton != (x[j] == upper_endpoint):
                    raise AssertionError("PXC28 co-singleton/upper-pin equivalence failed")
                counters["retained_noncarrier_nongainer_upper_endpoint_checks"] += 1
                if tight_cosingleton:
                    counters["retained_nongainer_upper_pinned_occurrences"] += 1
                else:
                    shortage.append(j)
                    counters["retained_nongainer_positive_upper_slack_occurrences"] += 1
                    if z[j] == max(z):
                        counters["positive_upper_slack_at_lmax_top_occurrences"] += 1
                    else:
                        counters["positive_upper_slack_off_lmax_top_occurrences"] += 1
            if shortage:
                counters[f"positive_upper_slack_shortage_sets_of_size_{len(shortage)}"] += 1
                key = (values, tuple(shortage))
                if endpoint_gap_cache is None:
                    gap = endpoint_face_gap(values, shortage)
                else:
                    if key not in endpoint_gap_cache:
                        endpoint_gap_cache[key] = endpoint_face_gap(values, shortage)
                    gap = endpoint_gap_cache[key]
                counters["positive_upper_slack_shortage_sets"] += 1
                counters["shortage_sets_with_common_endpoint_witness"] += gap == 0
                counters["shortage_sets_with_positive_sparse_separator_gap"] += gap > 0
                if gap == 0:
                    if overcover_cache is None:
                        certificate = top_certificate(values, z)
                    else:
                        key = (values, z)
                        if key not in overcover_cache:
                            overcover_cache[key] = top_certificate(values, z)
                        certificate = overcover_cache[key]
                    alpha = certificate["alpha"]
                    outside_load = max(alpha[i] for i in range(n) if i not in shortage)
                    upper_mass = sum(
                        (total - values[full_coalition ^ (1 << j)] for j in shortage),
                        F(0),
                    )
                    coupling_bound = sum(
                        (
                            alpha[j]
                            * (total - values[full_coalition ^ (1 << j)])
                            for j in shortage
                        ),
                        F(0),
                    ) + (total - upper_mass) * outside_load
                    if max(z) > coupling_bound:
                        raise AssertionError("PXC34 endpoint/over-cover coupling failed")
                    counters["common_endpoint_overcover_coupling_checks"] += 1
                    counters["pxc34_tight_coupling_bounds"] += max(z) == coupling_bound
                    counters["pxc34_strict_coupling_bounds"] += max(z) < coupling_bound
                    counters["alpha_dominant_common_endpoint_shortage_sets"] += all(
                        alpha[j] >= outside_load for j in shortage
                    )
                    theta = max(alpha)
                    dispersion_bound = theta * total - sum(
                        (
                            (theta - alpha[j])
                            * (total - values[full_coalition ^ (1 << j)])
                            for j in shortage
                        ),
                        F(0),
                    )
                    if max(z) > dispersion_bound:
                        raise AssertionError("PXC35 endpoint dispersion bound failed")
                    counters["pxc35_strict_dispersion_improvements"] += any(
                        alpha[j] < theta
                        and total - values[full_coalition ^ (1 << j)] > 0
                        for j in shortage
                    )
                    counters["pxc35_tight_dispersion_bounds"] += max(z) == dispersion_bound
                    counters["pxc34_strictly_sharper_than_pxc35"] += (
                        coupling_bound < dispersion_bound
                    )
                    actual_cri = max(z) - min(x) + total * min(x) / max(z)
                    counters["actual_ceiling_interpolation_reaches_target"] += (
                        actual_cri >= target * total
                    )
                    counters["pxc35_ceiling_interval_reaches_target"] += (
                        ceiling_interval_reaches_target(
                            total, min(x), dispersion_bound, target, n
                        )
                    )
        if y_all > min(z_all, x_all):
            raise AssertionError("PXC22 direct family price domination failed")
        if max(F(row["actual_target_reserve"]) for row in rows) != overlap_surplus - y_all:
            raise AssertionError("PXC22 direct family selection identity failed")
        counters["full_family_direct_price_closes"] += y_all <= overlap_surplus
        counters["direct_price_strictly_cheaper_than_hybrid_price"] += y_all < min(
            z_all, x_all
        )
        direct_optimal_sizes = sorted(
            {
                row["p"]
                for row in rows
                if F(row["direct_reserve_price"]) == y_all
            }
        )
        for optimal_p in direct_optimal_sizes:
            counters[f"cycles_with_direct_price_optimum_at_p_{optimal_p}"] += 1

        # PXC37: at a globally direct-price-minimizing row before the
        # coefficient midpoint, every player cheaper than the exchange
        # threshold must be an unavailable co-singleton direction.
        for row in rows:
            if F(row["direct_reserve_price"]) != y_all:
                continue
            p = row["p"]
            if 2 * p + 2 > n:
                continue
            excluded = tuple(row["excluded_nongainers"])
            excluded_mass = sum((z[j] for j in excluded), F(0))
            rho = F(n - 2 * p - 2, (n - p) * (p + 1))
            cheap = tuple(
                j
                for j in sorted(nongainers - set(cycle))
                if row["support_row"] >> j & 1 and z[j] < rho * excluded_mass
            )
            counters["direct_optimal_rows_through_midpoint"] += 1
            for j in cheap:
                if (full_coalition ^ (1 << j)) in full_support:
                    raise AssertionError("PXC37 cheap available deletion at direct optimum")
            if not cheap:
                counters["direct_optimal_rows_with_no_cheap_shortage"] += 1
            else:
                counters["direct_optimal_rows_with_cheap_shortage"] += 1
                counters[f"direct_optimal_cheap_shortage_size_{len(cheap)}"] += 1
                counters["direct_optimal_cheap_shortage_at_lmax_top"] += sum(
                    z[j] == max(z) for j in cheap
                )
                counters["direct_optimal_cheap_shortage_off_lmax_top"] += sum(
                    z[j] < max(z) for j in cheap
                )
            retained_noncarrier = tuple(
                j
                for j in sorted(nongainers - set(cycle))
                if row["support_row"] >> j & 1
            )
            expensive = tuple(j for j in retained_noncarrier if j not in cheap)
            coefficient = F(row["coefficient"])
            pxc39_bound = (
                len(cycle) * z[cycle[0]]
                + sum((x[j] for j in gainers), F(0))
                - target * total
                + sum((z[j] for j in cheap), F(0))
                + (F(1) - coefficient + len(expensive) * rho) * excluded_mass
            )
            actual_reserve = F(row["actual_target_reserve"])
            if actual_reserve < pxc39_bound:
                raise AssertionError("PXC39 high-mass reserve bound failed")
            label_currency = sum((z[j] for j in expensive), F(0)) - (
                len(expensive) * rho * excluded_mass
            )
            if actual_reserve != pxc39_bound + label_currency:
                raise AssertionError("PXC40 labelled-currency identity failed")
            counters["pxc39_direct_optimal_reserve_checks"] += 1
            counters["pxc39_high_mass_bound_closes"] += pxc39_bound >= 0
            counters["pxc40_positive_label_currency"] += label_currency > 0
            counters["pxc40_zero_label_currency"] += label_currency == 0
            if pxc39_bound < 0:
                counters[
                    "pxc39_negative_profile_"
                    f"g_{len(gainers)}_h_{len(cycle)}_p_{p}_r_{len(expensive)}"
                ] += 1
                counters["pxc40_label_currency_closes_negative_base"] += (
                    actual_reserve >= 0
                )
                counters["pxc40_negative_base_expensive_players_at_lmax_top"] += sum(
                    z[j] == max(z) for j in expensive
                )
                counters["pxc40_negative_base_expensive_players_off_lmax_top"] += sum(
                    z[j] < max(z) for j in expensive
                )
                counters[
                    "pxc40_offtop_negative_base_rows_with_zero_direct_price"
                ] += any(z[j] < max(z) for j in expensive) and excluded_mass == 0
                counters["pxc40_negative_base_rows_with_zero_ordered_cut_error"] += (
                    F(row["ordered_cut_error"]) == 0
                )
                for j in expensive:
                    if z[j] != max(z):
                        continue
                    if not all(
                        reachable(graph, j, h) and reachable(graph, h, j)
                        for h in cycle
                    ):
                        counters["pxc40_top_currency_outside_carrier_scc"] += 1
                        cycle_set = set(cycle)
                        cycle_split_payments = tuple(
                            coalition_sum(x, coalition) - coalition_sum(z, coalition)
                            for coalition in full_tight_support(values, z)
                            if 0
                            < len(
                                cycle_set
                                & {i for i in range(n) if coalition >> i & 1}
                            )
                            < len(cycle_set)
                        )
                        if any(payment <= 0 for payment in cycle_split_payments):
                            raise AssertionError("one-way cycle separator is not strict")
                        counters[
                            "pxc40_satellite_cycle_has_lmax_separator"
                        ] += bool(cycle_split_payments)
                        counters[
                            "pxc40_satellite_cycle_common_module_contracts"
                        ] += not cycle_split_payments
                        if cycle_split_payments:
                            counters[
                                "pxc40_satellite_separator_bridges_base_within_currency"
                            ] += any(
                                -pxc39_bound <= payment <= label_currency
                                for payment in cycle_split_payments
                            )
                        if pxc40_outside_scc_details is not None:
                            pxc40_outside_scc_details.append(
                                {
                                    "source": source,
                                    "trail": trail,
                                    "cycle": list(cycle),
                                    "currency_player": j,
                                    "carrier_graph": {
                                        str(root): list(targets)
                                        for root, targets in graph.items()
                                    },
                                    "support_row": row["support_row"],
                                    "excluded_nongainers": list(excluded),
                                    "lmin": [str(value) for value in x],
                                    "lmax": [str(value) for value in z],
                                    "pxc39_bound": str(pxc39_bound),
                                    "pxc40_label_currency": str(label_currency),
                                }
                            )
                        continue
                    counters["pxc40_top_currency_in_carrier_scc"] += 1
                    enlarged = set(cycle) | {j}
                    splitting_payments = tuple(
                        coalition_sum(x, coalition) - coalition_sum(z, coalition)
                        for coalition in full_tight_support(values, z)
                        if 0
                        < len(enlarged & {i for i in range(n) if coalition >> i & 1})
                        < len(enlarged)
                    )
                    if any(payment <= 0 for payment in splitting_payments):
                        raise AssertionError("PXC40 enlarged-module separator is not strict")
                    z_splits = bool(splitting_payments)
                    counters["pxc40_enlarged_module_has_lmax_separator"] += z_splits
                    counters["pxc40_enlarged_common_module_contracts"] += not z_splits
                    if splitting_payments:
                        counters[
                            "pxc40_some_separator_payment_fits_label_currency"
                        ] += any(payment <= label_currency for payment in splitting_payments)
                        counters[
                            "pxc40_some_separator_payment_covers_negative_base"
                        ] += max(splitting_payments) >= -pxc39_bound
                        counters[
                            "pxc40_some_separator_payment_bridges_base_within_currency"
                        ] += any(
                            -pxc39_bound <= payment <= label_currency
                            for payment in splitting_payments
                        )
                        counters[
                            "pxc40_sum_separator_payments_covers_negative_base"
                        ] += sum(splitting_payments, F(0)) >= -pxc39_bound
                if pxc40_offtop_details is not None and any(
                    z[j] < max(z) for j in expensive
                ):
                    pxc40_offtop_details.append(
                        {
                            "source": source,
                            "trail": trail,
                            "cycle": list(cycle),
                            "support_row": row["support_row"],
                            "excluded_nongainers": list(excluded),
                            "retained_expensive_nongainers": list(expensive),
                            "lmin": [str(value) for value in x],
                            "lmax": [str(value) for value in z],
                            "pxc39_bound": str(pxc39_bound),
                            "pxc40_label_currency": str(label_currency),
                            "actual_reserve": str(actual_reserve),
                        }
                    )
            pxc39_checked_cycle = True
            pxc39_closes_cycle |= pxc39_bound >= 0
        counters["cycles_with_pxc39_direct_optimal_check"] += pxc39_checked_cycle
        counters["cycles_some_direct_optimal_pxc39_bound_closes"] += pxc39_closes_cycle

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
                yp, yq = F(parent["direct_reserve_price"]), F(child["direct_reserve_price"])
                comparison_mass = xp / cp
                if xq - xp != (cq - cp) * comparison_mass + cq * x[j]:
                    raise AssertionError("PXC18 Lmin exchange identity failed")
                parent_max = max(z[i] for i in parent["excluded_nongainers"])
                child_max = max(parent_max, z[j])
                ap = parent["p"] * max(cp - 1, F(0))
                aq = child["p"] * max(cq - 1, F(0))
                if zq - zp != z[j] + aq * child_max - ap * parent_max:
                    raise AssertionError("PXC18 Lmax exchange identity failed")
                excluded_mass = yp / cp
                if yq - yp != (cq - cp) * excluded_mass + cq * z[j]:
                    raise AssertionError("PXC23 direct-price exchange identity failed")
                exchange_pairs.append((parent, child, j))
        counters["tight_cosingleton_exchange_pairs"] += len(exchange_pairs)

        # PXC26--PXC27: all available tight co-singletons generate a Boolean
        # deletion cube.  At fixed added deletion size, the direct-price
        # optimum deletes the lowest-Lmax members of that cube.
        if complete_menu:
            for parent in rows:
                parent_support = parent["support_row"]
                available = tuple(
                    j
                    for j in sorted(nongainers - set(cycle))
                    if parent_support >> j & 1
                    and (((1 << n) - 1) ^ (1 << j)) in full_support
                )
                if not available:
                    continue
                counters["tight_cosingleton_boolean_cubes"] += 1
                counters["largest_tight_cosingleton_boolean_cube_dimension"] = max(
                    counters["largest_tight_cosingleton_boolean_cube_dimension"],
                    len(available),
                )
                base_mass = sum(
                    (z[i] for i in parent["excluded_nongainers"]), F(0)
                )
                ordered_available_mass = sorted(z[j] for j in available)
                for q in range(len(available) + 1):
                    q_rows = []
                    for deleted in combinations(available, q):
                        child_support = parent_support
                        for j in deleted:
                            child_support &= ~(1 << j)
                        child = row_by_support.get(child_support)
                        if child is None:
                            raise AssertionError(
                                (
                                    source,
                                    trail,
                                    cycle,
                                    parent_support,
                                    deleted,
                                    "PXC26 Boolean deletion vertex absent",
                                )
                            )
                        q_rows.append(child)
                    counters["tight_cosingleton_boolean_cube_vertices_checked"] += len(
                        q_rows
                    )
                    coefficient_q = F(
                        len(gainers) * n,
                        (n - parent["p"] - q) * (parent["p"] + q + 1),
                    )
                    expected = coefficient_q * (
                        base_mass + sum(ordered_available_mass[:q], F(0))
                    )
                    if min(F(row["direct_reserve_price"]) for row in q_rows) != expected:
                        raise AssertionError("PXC27 order-statistic cube optimum failed")
                    counters["boolean_cube_order_statistic_checks"] += 1
        for parent, child, _j in exchange_pairs:
            if F(parent["lmin_omitted_price"]) == x_all:
                if F(child["lmin_omitted_price"]) < x_all:
                    raise AssertionError("PXC20 Lmin minimizer is not exchange-stable")
                counters["global_lmin_price_exchange_stability_checks"] += 1
            if F(parent["lmax_cut_price"]) == z_all:
                if F(child["lmax_cut_price"]) < z_all:
                    raise AssertionError("PXC20 Lmax minimizer is not exchange-stable")
                counters["global_lmax_price_exchange_stability_checks"] += 1
            if F(parent["direct_reserve_price"]) == y_all:
                if F(child["direct_reserve_price"]) < y_all:
                    raise AssertionError("PXC24 direct minimizer is not exchange-stable")
                counters["global_direct_price_exchange_stability_checks"] += 1
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
    full_pxc40_offtop_details = []
    full_pxc40_outside_scc_details = []
    endpoint_gap_cache = {}
    overcover_cache = {}
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
                    endpoint_gap_cache=endpoint_gap_cache,
                    overcover_cache=overcover_cache,
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
                    endpoint_gap_cache=endpoint_gap_cache,
                    overcover_cache=overcover_cache,
                    pxc40_offtop_details=full_pxc40_offtop_details,
                    pxc40_outside_scc_details=full_pxc40_outside_scc_details,
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
            endpoint_gap_cache=endpoint_gap_cache,
            overcover_cache=overcover_cache,
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
        endpoint_gap_cache=endpoint_gap_cache,
        overcover_cache=overcover_cache,
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
            "deleting a player with zero Lmin and Lmax payoff; the exact direct "
            "reserve price is rowwise no larger than either certificate price "
            "and its full-menu optimum closes every archived cycle; tight "
            "co-singletons are exactly the retained nongainer coordinates "
            "pinned at their individual core upper endpoint"
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
        "n6_pxc40_offtop_residual_details": full_pxc40_offtop_details,
        "n6_pxc40_outside_scc_residual_details": full_pxc40_outside_scc_details,
        "n7_hostile_and_sharp_controls": hostile,
        "n7_multi_endpoint_separator_control": multi_endpoint_separator_control(),
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

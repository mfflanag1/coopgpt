#!/usr/bin/env python3
r"""Exact audit of the marked-hinge/common-support deficiency transfer.

For the dual optimum ``(y, epsilon)`` of (CSD-D), every Lmax-top label has
``y_i >= epsilon``.  If ``A`` is tight at both Lmin and Lmax, its Lmax slack
is zero and dual feasibility gives ``y(A) <= 0``.  Hence

  -y(A \ H) >= |A cap H| epsilon,
   y(H \ A) >= |H \ A| epsilon.

This is dimension-free algebra.  The archive replay checks every common row
and records a positive-deficiency equality control; it is not an all-n
target-pricing theorem or a facet classification.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_carrier_separator_payment import (  # noqa: E402
    directed_cycles,
    full_tight_support,
)
from audit_direct_ceiling_common_hinge_trichotomy import (  # noqa: E402
    has_direct_packet,
)
from audit_labelled_facet_cover_duality import (  # noqa: E402
    maximum_overlap_roots,
    solve_labelled_cover,
)
from audit_lmax_overcover import coalition_sum, records  # noqa: E402
from audit_surplus_absorption import minimum_surplus_certificate  # noqa: E402
from exactlp import exact_linprog  # noqa: E402
from verify_mixed_witness_projection import coalition_rank  # noqa: E402
from verify_rooted_hinge_projection import decomposition_witnesses  # noqa: E402


def permute_coalition(coalition, permutation):
    result = 0
    for source, target in enumerate(permutation):
        if coalition >> source & 1:
            result |= 1 << target
    return result


def rooted_support_orbit(root, support, n):
    return min(
        (
            permutation[root],
            tuple(
                sorted(
                    permute_coalition(coalition, permutation)
                    for coalition in support
                )
            ),
        )
        for permutation in itertools.permutations(range(n))
    )


def best_mixed_rooted_pair_packet(certificate, hinge, top, n, roots=None):
    tagged = tuple(certificate["support"]) + (hinge,)
    best = None
    root_covers = []
    candidate_roots = tuple(sorted(top if roots is None else roots))
    if not candidate_roots:
        raise ValueError("mixed rooted packet requires at least one root")
    for root in candidate_roots:
        inequalities, rhs = [], []
        for player in range(n):
            if player == root:
                continue
            inequalities.append(
                [F((coalition >> player) & 1) for coalition in tagged]
            )
            rhs.append(F(1))
        for variable in range(len(tagged)):
            inequalities.append(
                [F(-1 if j == variable else 0) for j in range(len(tagged))]
            )
            rhs.append(F(0))
        objective = [F(-((coalition >> root) & 1)) for coalition in tagged]
        status, negative_load, weights = exact_linprog(
            objective, inequalities, rhs
        )
        if status != "optimal":
            raise AssertionError("aggregate mixed rooted packing did not optimize")
        excess = -negative_load - 1
        offroot = tuple(player for player in range(n) if player != root)
        rooted_columns = tuple(
            coalition for coalition in tagged if coalition >> root & 1
        )
        cover_inequalities = [
            [-F((coalition >> player) & 1) for player in offroot]
            for coalition in rooted_columns
        ]
        cover_rhs = [F(-1)] * len(rooted_columns)
        for variable in range(len(offroot)):
            cover_inequalities.append(
                [F(-1 if j == variable else 0) for j in range(len(offroot))]
            )
            cover_rhs.append(F(0))
        cover_status, cover_value, cover = exact_linprog(
            [F(1)] * len(offroot), cover_inequalities, cover_rhs
        )
        if cover_status != "optimal" or cover_value != -negative_load:
            raise AssertionError("aggregate rooted packing/cover duality failed")
        root_covers.append(
            {
                "root": root,
                "maximum_root_load": -negative_load,
                "cover_value": cover_value,
                "cover": tuple(zip(offroot, cover)),
                "common_carriers": tuple(
                    player
                    for player in offroot
                    if all(
                        coalition >> player & 1
                        for coalition in rooted_columns
                    )
                ),
            }
        )
        if best is None or excess > best["root_excess"]:
            best = {
                "root": root,
                "root_excess": excess,
                "weights": weights,
            }
    if best["root_excess"] <= 0:
        best["root_covers"] = root_covers
        return best

    root = best["root"]
    weights = best["weights"]
    loads = tuple(
        sum(
            (
                weight
                for coalition, weight in zip(tagged, weights)
                if coalition >> player & 1
            ),
            F(0),
        )
        for player in range(n)
    )
    coefficients = {}
    for coalition, weight in zip(tagged, weights):
        if weight:
            coefficients[coalition] = coefficients.get(coalition, F(0)) + weight
    deficit_total = F(0)
    for player in range(n):
        if player == root:
            continue
        deficit = 1 - loads[player]
        if deficit < 0:
            raise AssertionError("aggregate mixed rooted packing overload")
        if deficit:
            pair = (1 << root) | (1 << player)
            coefficients[pair] = coefficients.get(pair, F(0)) + deficit
            deficit_total += deficit
    exceptional = 1 << root
    coefficients[exceptional] = (
        coefficients.get(exceptional, F(0))
        - best["root_excess"]
        - deficit_total
    )
    coefficients = {
        coalition: value for coalition, value in coefficients.items() if value
    }
    identity = tuple(
        sum(
            (
                value
                for coalition, value in coefficients.items()
                if coalition >> player & 1
            ),
            F(0),
        )
        for player in range(n)
    )
    if identity != (F(1),) * n:
        raise AssertionError("aggregate mixed rooted-pair identity failed")
    support = tuple(sorted(coefficients))
    minimal = coalition_rank(support, n) == len(support)
    decompositions = decomposition_witnesses(support, n) if minimal else ()
    best.update(
        {
            "support": support,
            "coefficients": coefficients,
            "support_minimal": minimal,
            "decomposition_count": len(decompositions),
            "exact_cone_facet": minimal and not decompositions,
            "orbit": rooted_support_orbit(root, support, n),
            "deficit_total": deficit_total,
            "marked_margin": (n * n // 4 - n + 1)
            * best["root_excess"]
            - deficit_total,
        }
    )
    return best


def packet_comparison_budget(x, z, certificate, hinge, packet):
    r"""Return the exact mixed-packet comparison budget (PXC50)--(PXC51)."""
    n = len(x)
    root = packet["root"]
    delta = packet["root_excess"]
    if delta <= 0:
        raise ValueError("comparison budget requires positive root excess")
    tagged = tuple(certificate["support"]) + (hinge,)
    weights = packet["weights"]
    loads = tuple(
        sum(
            (
                weight
                for coalition, weight in zip(tagged, weights)
                if coalition >> player & 1
            ),
            F(0),
        )
        for player in range(n)
    )
    if loads[root] != 1 + delta:
        raise AssertionError("positive packet has inconsistent root load")
    deficits = tuple(
        F(0) if player == root else 1 - loads[player]
        for player in range(n)
    )
    if any(deficit < 0 for deficit in deficits):
        raise AssertionError("positive packet has a negative offroot deficit")
    row_payments = tuple(
        coalition_sum(x, coalition) - coalition_sum(z, coalition)
        for coalition in tagged
    )
    if any(
        payment < 0
        for payment, weight in zip(row_payments, weights)
        if weight
    ):
        raise AssertionError("Lmax-tight packet row has negative comparison payment")
    comparison_charge = sum(
        (weight * payment for weight, payment in zip(weights, row_payments)),
        F(0),
    )
    spoke_charge = sum(
        (
            deficits[player] * (x[player] - z[player])
            for player in range(n)
            if player != root
        ),
        F(0),
    )
    root_loss = x[root] - z[root]
    if comparison_charge + spoke_charge != delta * root_loss:
        raise AssertionError("mixed-packet comparison conservation failed")

    gainers = tuple(player for player in range(n) if z[player] > x[player])
    other_nongainers = tuple(
        player
        for player in range(n)
        if player != root and x[player] >= z[player]
    )
    total_gain = sum((z[player] - x[player] for player in gainers), F(0))
    alignment_defect = sum(
        (
            (1 - deficits[player]) * (z[player] - x[player])
            for player in gainers
        ),
        F(0),
    ) + sum(
        (
            deficits[player] * (x[player] - z[player])
            for player in other_nongainers
        ),
        F(0),
    )
    if root_loss < 0:
        raise AssertionError("eligible comparison-budget root is a payoff gainer")
    if comparison_charge != total_gain + delta * root_loss - alignment_defect:
        raise AssertionError("mixed-packet alignment-defect identity failed")

    positive_rows = tuple(
        (coalition, weight, payment)
        for coalition, weight, payment in zip(tagged, weights, row_payments)
        if weight
    )
    if any(not (coalition >> root & 1) for coalition, _, _ in positive_rows):
        raise AssertionError("root-load optimum retains a root-omitting row")
    if sum((weight for _, weight, _ in positive_rows), F(0)) != 1 + delta:
        raise AssertionError("positive rooted packet has wrong normalized mass")
    largest_row_payment = max(payment for _, _, payment in positive_rows)
    if largest_row_payment < comparison_charge / (1 + delta):
        raise AssertionError("normalized packet payment averaging failed")
    return {
        "root": root,
        "root_excess": delta,
        "deficits": deficits,
        "comparison_charge": comparison_charge,
        "spoke_charge": spoke_charge,
        "root_loss": root_loss,
        "total_gain": total_gain,
        "alignment_defect": alignment_defect,
        "normalized_payment_floor": comparison_charge / (1 + delta),
        "largest_row_payment": largest_row_payment,
        "positive_rows": positive_rows,
    }


def best_aligned_full_menu_packet(x, z, certificate, hinge, roots):
    r"""Lexicographically optimize root load, then the PXC51 defect."""
    n = len(x)
    tagged = tuple(certificate["support"]) + (hinge,)
    candidates = []
    maximum_loads = []
    for root in sorted(roots):
        active = tuple(
            variable
            for variable, coalition in enumerate(tagged)
            if coalition >> root & 1
        )
        rooted = tuple(tagged[variable] for variable in active)
        inequalities, rhs = [], []
        for player in range(n):
            if player == root:
                continue
            inequalities.append(
                [F((coalition >> player) & 1) for coalition in rooted]
            )
            rhs.append(F(1))
        for variable in range(len(rooted)):
            inequalities.append(
                [F(-1 if j == variable else 0) for j in range(len(rooted))]
            )
            rhs.append(F(0))
        status, negative_load, _ = exact_linprog(
            [F(-1)] * len(rooted), inequalities, rhs
        )
        if status != "optimal":
            raise AssertionError("eligible full-menu root load did not optimize")
        maximum_load = -negative_load
        maximum_loads.append(maximum_load)
        if maximum_load <= 1:
            continue

        fixed_inequalities = list(inequalities) + [
            [F(1)] * len(rooted),
            [F(-1)] * len(rooted),
        ]
        fixed_rhs = list(rhs) + [maximum_load, -maximum_load]
        alignment_costs = [
            sum(
                (
                    z[player] - x[player]
                    for player in range(n)
                    if player != root and coalition >> player & 1
                ),
                F(0),
            )
            for coalition in rooted
        ]
        status, _, rooted_weights = exact_linprog(
            alignment_costs, fixed_inequalities, fixed_rhs
        )
        if status != "optimal":
            raise AssertionError("alignment defect did not optimize on root face")
        weights = [F(0)] * len(tagged)
        for variable, weight in zip(active, rooted_weights):
            weights[variable] = weight
        packet = {
            "root": root,
            "root_excess": maximum_load - 1,
            "weights": tuple(weights),
        }
        budget = packet_comparison_budget(x, z, certificate, hinge, packet)
        budget["excess_alignment_defect"] = (
            budget["alignment_defect"]
            - packet["root_excess"] * budget["root_loss"]
        )
        candidates.append((packet, budget))
    if not candidates:
        return {
            "root_excess": max(maximum_loads) - 1,
            "maximum_root_loads": tuple(maximum_loads),
        }
    packet, budget = min(
        candidates,
        key=lambda candidate: (
            candidate[1]["excess_alignment_defect"],
            -candidate[0]["root_excess"],
            candidate[0]["root"],
        ),
    )
    packet["comparison_budget"] = budget
    return packet


def full_menu_marked_alternative(values, x, z, hinge):
    n = len(x)
    top = {i for i, value in enumerate(z) if value == max(z)}
    hinge_top = {
        player for player in top if hinge >> player & 1
    }
    z_tight = full_tight_support(values, z)
    packet = best_mixed_rooted_pair_packet(
        {"support": z_tight}, hinge, top, n, roots=hinge_top
    )
    if packet["root_excess"] > 0:
        result = {
            "kind": "positive_full_menu_mixed_packet",
            "root": packet["root"],
            "root_excess": str(packet["root_excess"]),
        }
        if x[packet["root"]] >= z[packet["root"]]:
            budget = packet_comparison_budget(
                x, z, {"support": z_tight}, hinge, packet
            )
            result.update(
                {
                    "comparison_charge": str(budget["comparison_charge"]),
                    "total_gain": str(budget["total_gain"]),
                    "root_loss": str(budget["root_loss"]),
                    "alignment_defect": str(budget["alignment_defect"]),
                    "normalized_payment_floor": str(
                        budget["normalized_payment_floor"]
                    ),
                }
            )
        return result

    covers = {row["root"]: row for row in packet["root_covers"]}
    graph = {}
    for root in sorted(hinge_top):
        carriers = tuple(
            carrier
            for carrier in covers[root]["common_carriers"]
            if carrier in hinge_top
        )
        if not carriers:
            raise AssertionError("tied full-menu root has no top hinge carrier")
        graph[root] = carriers
    cycles = directed_cycles(graph)
    if not cycles:
        raise AssertionError("tied full-menu carrier graph has no cycle")
    cycle = cycles[0]
    cycle_set = set(cycle)
    x_splitters = tuple(
        coalition
        for coalition in full_tight_support(values, x)
        if 0
        < len(
            cycle_set
            & {i for i in range(n) if coalition >> i & 1}
        )
        < len(cycle_set)
    )
    payments = tuple(
        coalition_sum(z, coalition) - coalition_sum(x, coalition)
        for coalition in x_splitters
    )
    if any(payment <= 0 for payment in payments):
        raise AssertionError("full-menu module splitter lacks strict reverse payment")
    if x_splitters:
        return {
            "kind": "lmin_splitter_strict_reverse_payment",
            "carrier_cycle": list(cycle),
            "splitters": list(x_splitters),
            "payments": [str(payment) for payment in payments],
        }
    return {
        "kind": "common_tight_face_module",
        "carrier_cycle": list(cycle),
    }


def audit_record(
    source,
    trail,
    values,
    x,
    z,
    counters,
    controls,
    aggregate_controls,
    packet_rows,
    full_menu_packet_rows,
    tied_rows,
):
    x_tight = set(full_tight_support(values, x))
    z_tight = set(full_tight_support(values, z))
    common = tuple(sorted(x_tight & z_tight))
    if not common:
        return
    certificate = minimum_surplus_certificate(values, x, z)
    epsilon = certificate["epsilon_star"]
    y = certificate["dual_y"]
    top = {i for i, value in enumerate(z) if value == max(z)}
    counters["records_with_common_rows"] += 1
    counters["records_with_positive_common_support_deficiency"] += epsilon > 0
    for coalition in common:
        members = {i for i in range(len(x)) if coalition >> i & 1}
        top_in = members & top
        top_out = top - members
        off_in = members - top
        negative_pool = -sum((y[i] for i in off_in), F(0))
        positive_pool = sum((y[i] for i in top_out), F(0))
        if coalition_sum(y, coalition) > 0:
            raise AssertionError("common row violates zero-slack dual constraint")
        if negative_pool < len(top_in) * epsilon:
            raise AssertionError("marked-hinge negative-price transfer failed")
        if positive_pool < len(top_out) * epsilon:
            raise AssertionError("omitted-top positive-price transfer failed")
        counters["common_rows_checked"] += 1
        counters["common_rows_meeting_and_omitting_top"] += bool(top_in and top_out)
        counters["positive_deficiency_transfer_rows"] += bool(
            epsilon > 0 and top_in and top_out
        )
        if epsilon > 0 and top_in and top_out:
            eligible_roots = top_in & set(maximum_overlap_roots(x, z))
            if not eligible_roots:
                counters[
                    "positive_transfer_rows_without_eligible_hinge_top_root"
                ] += 1
            else:
                full_menu_certificate = {"support": tuple(sorted(z_tight))}
                full_menu_packet = best_aligned_full_menu_packet(
                    x,
                    z,
                    full_menu_certificate,
                    coalition,
                    eligible_roots,
                )
                if full_menu_packet["root_excess"] > 0:
                    budget = full_menu_packet["comparison_budget"]
                    counters[
                        "eligible_full_menu_rows_with_positive_root_excess"
                    ] += 1
                    counters[
                        "eligible_positive_packets_with_zero_alignment_defect"
                    ] += budget["alignment_defect"] == 0
                    counters[
                        "eligible_positive_packets_whose_charge_covers_total_gain"
                    ] += budget["comparison_charge"] >= budget["total_gain"]
                    full_menu_packet_rows.append(
                        {
                            "source": source,
                            "trail": trail,
                            "common_hinge": coalition,
                            "eligible_roots": sorted(eligible_roots),
                            "root": budget["root"],
                            "root_excess": str(budget["root_excess"]),
                            "comparison_charge": str(
                                budget["comparison_charge"]
                            ),
                            "spoke_charge": str(budget["spoke_charge"]),
                            "total_gain": str(budget["total_gain"]),
                            "root_loss": str(budget["root_loss"]),
                            "alignment_defect": str(
                                budget["alignment_defect"]
                            ),
                            "excess_alignment_defect": str(
                                budget["excess_alignment_defect"]
                            ),
                            "normalized_payment_floor": str(
                                budget["normalized_payment_floor"]
                            ),
                            "largest_row_payment": str(
                                budget["largest_row_payment"]
                            ),
                            "offroot_deficits": {
                                str(player): str(deficit)
                                for player, deficit in enumerate(
                                    budget["deficits"]
                                )
                                if deficit
                            },
                            "positive_rows": [
                                {
                                    "coalition": support,
                                    "weight": str(weight),
                                    "comparison_payment": str(payment),
                                }
                                for support, weight, payment in budget[
                                    "positive_rows"
                                ]
                            ],
                        }
                    )
                else:
                    counters[
                        "eligible_full_menu_rows_with_tied_root_excess"
                    ] += 1
            top_trace = members & top
            same_top_trace = tuple(
                support
                for support in certificate["support"]
                if {
                    i for i in range(len(x)) if support >> i & 1
                }
                & top
                == top_trace
            )
            subset_rows = tuple(
                support
                for support in certificate["support"]
                if support & ~coalition == 0
            )
            counters[
                "positive_transfer_rows_with_primal_same_top_trace"
            ] += bool(same_top_trace)
            counters[
                "positive_transfer_rows_with_primal_subset_row"
            ] += bool(subset_rows)
            packet = best_mixed_rooted_pair_packet(
                certificate, coalition, top, len(x)
            )
            counters["positive_transfer_rows_with_positive_root_excess"] += (
                packet["root_excess"] > 0
            )
            counters["positive_transfer_rows_with_tied_root_excess"] += (
                packet["root_excess"] == 0
            )
            if packet["root_excess"] > 0:
                if not packet["exact_cone_facet"]:
                    raise AssertionError(
                        "positive aggregate mixed packet is not an exact-cone facet"
                    )
                counters[
                    "positive_transfer_rows_with_indecomposable_pair_facet"
                ] += 1
                counters[
                    "positive_transfer_facets_with_positive_marked_margin"
                ] += packet["marked_margin"] > 0
                if packet["marked_margin"] <= 0:
                    raise AssertionError(
                        "positive aggregate facet is not affordably marked"
                    )
                packet_rows.append(
                    {
                        "source": source,
                        "trail": trail,
                        "common_hinge": coalition,
                        "root": packet["root"],
                        "root_excess": str(packet["root_excess"]),
                        "deficit_total": str(packet["deficit_total"]),
                        "effective_marked_price": str(
                            packet["deficit_total"] / packet["root_excess"]
                        ),
                        "marked_margin": str(packet["marked_margin"]),
                        "support": list(packet["support"]),
                        "coefficients": [
                            {
                                "coalition": support,
                                "coefficient": str(packet["coefficients"][support]),
                            }
                            for support in packet["support"]
                        ],
                        "support_minimal": packet["support_minimal"],
                        "decomposition_count": packet["decomposition_count"],
                        "exact_cone_facet": packet["exact_cone_facet"],
                        "rooted_support_orbit": [
                            packet["orbit"][0], list(packet["orbit"][1])
                        ],
                    }
                )
            else:
                nonzero_covers = tuple(
                    cover
                    for cover in packet["root_covers"]
                    if cover["maximum_root_load"] > 0
                )
                integral_single_carriers = tuple(
                    cover
                    for cover in nonzero_covers
                    if cover["cover_value"] == 1
                    and sum(value > 0 for _, value in cover["cover"]) == 1
                    and next(
                        value for _, value in cover["cover"] if value > 0
                    )
                    == 1
                )
                counters[
                    "tied_nonzero_root_covers"
                ] += len(nonzero_covers)
                counters[
                    "tied_nonzero_root_covers_integral_single_carrier"
                ] += len(integral_single_carriers)
                if len(integral_single_carriers) != len(nonzero_covers):
                    raise AssertionError(
                        "finite tied aggregate has a genuinely fractional root cover"
                    )
                if any(not cover["common_carriers"] for cover in nonzero_covers):
                    raise AssertionError(
                        "unit tied cover has no common aggregate carrier"
                    )
                counters[
                    "tied_nonzero_roots_with_common_aggregate_carrier"
                ] += len(nonzero_covers)
                roots = maximum_overlap_roots(x, z)
                affordable = any(
                    solve_labelled_cover(tuple(sorted(x_tight)), root, len(x))[
                        "affordable"
                    ]
                    for root in roots
                )
                total = sum(x, F(0))
                floor, ceiling = min(x), max(z)
                direct = has_direct_packet(x, z, F(len(x), len(x) * len(x) // 4))
                interpolation = (
                    ceiling - floor + total * floor / ceiling
                    >= F(len(x), len(x) * len(x) // 4) * total
                )
                if not (direct or interpolation or affordable):
                    raise AssertionError(
                        "tied aggregate transfer escapes all earlier closing arms"
                    )
                counters[
                    "tied_transfer_rows_closed_by_direct"
                ] += direct
                counters[
                    "tied_transfer_rows_closed_by_interpolation"
                ] += interpolation
                counters[
                    "tied_transfer_rows_with_affordable_labelled_root"
                ] += affordable
                counters[
                    "tied_transfer_rows_closed_by_some_earlier_arm"
                ] += 1
                tied_rows.append(
                    {
                        "source": source,
                        "trail": trail,
                        "common_hinge": coalition,
                        "maximum_overlap_roots": list(roots),
                        "direct_target_packet": direct,
                        "ceiling_interpolation": interpolation,
                        "affordable_labelled_root": affordable,
                        "aggregate_root_covers": [
                            {
                                "root": cover["root"],
                                "maximum_root_load": str(
                                    cover["maximum_root_load"]
                                ),
                                "cover_value": str(cover["cover_value"]),
                                "positive_cover": {
                                    str(player): str(value)
                                    for player, value in cover["cover"]
                                    if value > 0
                                },
                                "common_aggregate_carriers": list(
                                    cover["common_carriers"]
                                ),
                            }
                            for cover in packet["root_covers"]
                        ],
                        "full_menu_marked_alternative": (
                            full_menu_marked_alternative(
                                values, x, z, coalition
                            )
                        ),
                    }
                )
                alternative_kind = tied_rows[-1][
                    "full_menu_marked_alternative"
                ]["kind"]
                counters[
                    f"tied_full_menu_alternative_{alternative_kind}"
                ] += 1
            if (
                not same_top_trace
                and len(certificate["support"]) > 1
                and not aggregate_controls
            ):
                aggregate_controls.append(
                    {
                        "source": source,
                        "trail": trail,
                        "common_hinge": coalition,
                        "top": sorted(top),
                        "hinge_top_trace": sorted(top_trace),
                        "epsilon_star": str(epsilon),
                        "optimal_primal_support": list(certificate["support"]),
                        "optimal_primal_weights": [
                            str(value) for value in certificate["weights"]
                        ],
                        "interpretation": (
                            "no optimal over-cover support row has the hinge's "
                            "top trace; a one-row nested shear is unavailable"
                        ),
                    }
                )
        if (
            epsilon > 0
            and top_in
            and top_out
            and negative_pool == len(top_in) * epsilon
            and positive_pool == len(top_out) * epsilon
            and not controls
        ):
            controls.append(
                {
                    "source": source,
                    "trail": trail,
                    "coalition": coalition,
                    "top": sorted(top),
                    "epsilon_star": str(epsilon),
                    "dual_y": [str(value) for value in y],
                    "top_labels_in_hinge": len(top_in),
                    "top_labels_outside_hinge": len(top_out),
                    "negative_offtop_price_in_hinge": str(negative_pool),
                    "positive_top_price_outside_hinge": str(positive_pool),
                    "hinge_dual_value": str(coalition_sum(y, coalition)),
                }
            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    counters = Counter()
    controls = []
    aggregate_controls = []
    packet_rows = []
    full_menu_packet_rows = []
    tied_rows = []
    for path in args.paths:
        payload = json.loads(path.read_text())
        for _source, trail, values, x, z in records(payload, path):
            audit_record(
                path.name,
                trail,
                values,
                x,
                z,
                counters,
                controls,
                aggregate_controls,
                packet_rows,
                full_menu_packet_rows,
                tied_rows,
            )
    orbit_counts = Counter(
        json.dumps(row["rooted_support_orbit"])
        for row in packet_rows
    )
    report = {
        "status": (
            "dimension-free dual and mixed-packet budget identities with "
            "exact finite replay"
        ),
        "statement_checked": (
            "a common hinge containing q Lmax-top labels carries at least "
            "q*epsilon_star of negative dual price on its off-top labels; "
            "every omitted top label separately carries price at least "
            "epsilon_star; an eligible positive full-menu rooted packet "
            "obeys exact comparison-charge conservation and the derived "
            "alignment-defect identity"
        ),
        "inputs": [path.name for path in args.paths],
        "counts": dict(counters),
        "positive_deficiency_equality_control": controls[0] if controls else None,
        "aggregate_support_necessity_control": (
            aggregate_controls[0] if aggregate_controls else None
        ),
        "aggregate_mixed_rooted_pair_facets": packet_rows,
        "aggregate_mixed_rooted_pair_facet_orbits": {
            orbit: count for orbit, count in sorted(orbit_counts.items())
        },
        "eligible_full_menu_positive_packet_alignment_controls": (
            full_menu_packet_rows
        ),
        "tied_aggregate_rows_closed_by_earlier_arms": tied_rows,
        "limitations": (
            "the identity does not prove that the transferred price reaches "
            "the hybrid-overlap target; positive full-menu root excess does "
            "not force zero alignment defect, the finite aggregate packets "
            "are facets, and every finite tied row closes by an earlier arm, "
            "but neither universal closing implication is proved"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

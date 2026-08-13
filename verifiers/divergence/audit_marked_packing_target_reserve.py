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
where every maximum-overlap root is unaffordable, it additionally asks first
whether a positive column of the returned marked packing, and then whether a
positive column of *some packing on the full optimal price face*, supplies a
carrier-containing proper comparison whose target reserve closes the sharp
2/3 bound.  This is finite evidence only.
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
from exactlp import exact_linprog  # noqa: E402
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


def maximum_closer_mass_on_price_face(support, audit, root, n, closers):
    """Maximize total reserve-closing mass over the full optimal price face."""
    root_mask = 1 << root
    good = set(audit["tight_rooted_pairs"])
    bad = set(range(n)) - good - {root}
    menu = tuple(
        coalition
        for coalition in support
        if coalition & root_mask and coalition.bit_count() >= 3
    )
    traces = tuple(coalition & ~root_mask for coalition in menu)
    dimensional_price = n * n // 4 - n + 1
    weights = tuple(
        F(
            dimensional_price
            * (1 - sum((trace >> i) & 1 for i in good))
            + sum((trace >> i) & 1 for i in bad)
        )
        for trace in traces
    )
    inequalities = [
        [F((trace >> player) & 1) for trace in traces]
        for player in range(n)
        if player != root
    ]
    rhs = [F(1)] * (n - 1)
    for j in range(len(menu)):
        inequalities.append([F(-1 if k == j else 0) for k in range(len(menu))])
        rhs.append(F(0))
    closer_set = set(closers)
    objective = [F(-1 if coalition in closer_set else 0) for coalition in menu]
    status, value, solution = exact_linprog(
        objective,
        inequalities,
        rhs,
        [[weight for weight in weights]],
        [F(audit["packing_value"])],
    )
    if status != "optimal":
        raise AssertionError((root, "closer mass on price face", status))
    return -value, tuple(
        (coalition, solution[j])
        for j, coalition in enumerate(menu)
        if solution[j] > 0
    )


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
    good = set(gate["tight_rooted_pairs"])
    bad = set(range(n)) - good - {root}
    dimensional_price = n * n // 4 - n + 1
    cover_values = tuple(map(F, gate["cover"]))
    cover = {
        player: cover_values[j]
        for j, player in enumerate(i for i in range(n) if i != root)
    }

    def price_coefficient(coalition):
        trace = set(i for i in range(n) if i != root and coalition >> i & 1)
        return dimensional_price * (1 - len(trace & good)) + len(trace & bad)

    def cover_slack(coalition):
        trace = tuple(i for i in range(n) if i != root and coalition >> i & 1)
        return sum((cover[i] for i in trace), F()) - price_coefficient(coalition)

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
        minimum_distance = min(distances)
        closest = tuple(
            mask for mask, distance in zip(packing_masks, distances)
            if distance == minimum_distance
        )
        exchange_rows = []
        for mask in closest:
            added = tuple(i for i in range(n) if coalition >> i & 1 and not mask >> i & 1)
            removed = tuple(i for i in range(n) if mask >> i & 1 and not coalition >> i & 1)
            packing_h = tuple(i for i in nongainers if mask >> i & 1)
            packing_p = tuple(i for i in nongainers if not mask >> i & 1)
            packing_reserve = None
            if packing_p:
                packing_reserve = target_reserve_row(
                    x, z, packing_p, gainers, packing_h, target
                )["nonlow_target_reserve"]
            packing_trace = set(i for i in range(n) if i != root and mask >> i & 1)
            closing_trace = set(
                i for i in range(n) if i != root and coalition >> i & 1
            )
            price_loss_formula = dimensional_price * (
                len(closing_trace & good) - len(packing_trace & good)
            ) + len(packing_trace & bad) - len(closing_trace & bad)
            price_loss = price_coefficient(mask) - price_coefficient(coalition)
            if price_loss != price_loss_formula:
                raise AssertionError("labelled-price exchange identity failed")
            reserve_change = None
            reserve_increment_formula = None
            removed_nongainers = tuple(i for i in removed if i in nongainers)
            added_nongainers = tuple(i for i in added if i in nongainers)
            if packing_reserve is not None:
                reserve_change = F(row["nonlow_target_reserve"]) - F(packing_reserve)
                if not added_nongainers and not removed_nongainers:
                    reserve_increment_formula = F(0)
                elif not added_nongainers and len(removed_nongainers) == 1:
                    player = removed_nongainers[0]
                    p = len(packing_p)
                    denominator = (
                        (n - p) * (p + 1) * (n - p - 1) * (p + 2)
                    )
                    reserve_increment_formula = F(
                        len(gainers) * n
                        * (
                            (n - 2 * p - 2)
                            * sum((z[i] for i in packing_p), F(0))
                            - (n - p) * (p + 1) * z[player]
                        ),
                        denominator,
                    )
                if (
                    reserve_increment_formula is not None
                    and reserve_change != reserve_increment_formula
                ):
                    raise AssertionError("target-reserve exchange identity failed")
            exchange_rows.append(
                {
                    "packing_coalition": mask,
                    "added": list(added),
                    "removed": list(removed),
                    "added_gainers": [i for i in added if i in gainers],
                    "added_nongainers": [i for i in added if i in nongainers],
                    "removed_gainers": [i for i in removed if i in gainers],
                    "removed_nongainers": [i for i in removed if i in nongainers],
                    "packing_price_coefficient": price_coefficient(mask),
                    "closing_price_coefficient": price_coefficient(coalition),
                    "price_coefficient_loss": price_loss,
                    "price_coefficient_loss_formula": price_loss_formula,
                    "packing_cover_slack": str(cover_slack(mask)),
                    "closing_cover_slack": str(cover_slack(coalition)),
                    "packing_target_reserve": packing_reserve,
                    "closing_target_reserve": row["nonlow_target_reserve"],
                    "target_reserve_change": (
                        str(reserve_change) if reserve_change is not None else None
                    ),
                    "target_reserve_increment_formula": (
                        str(reserve_increment_formula)
                        if reserve_increment_formula is not None
                        else None
                    ),
                    "same_excluded_cardinality": len(packing_p) == len(p_set),
                }
            )
        all_support_closers.append(
            {
                "coalition": coalition,
                "P": list(p_set),
                "H": list(h_set),
                "comparison_gainers": list(comparison_gainers),
                "comparison_slack": str(comparison_slack),
                "target_reserve": row["nonlow_target_reserve"],
                "minimum_packing_column_exchange": minimum_distance,
                "closest_packing_exchanges": exchange_rows,
            }
        )
    closer_mass, closer_face_packing = maximum_closer_mass_on_price_face(
        support,
        gate,
        root,
        n,
        tuple(row["coalition"] for row in all_support_closers),
    )
    co_singleton_probe = None
    if (
        len(packing) == 1
        and packing[0][1] == 1
        and packing[0][0].bit_count() == n - 1
    ):
        co_singleton = packing[0][0]
        omitted = next(i for i in range(n) if not co_singleton >> i & 1)
        proper_rows = []
        for coalition in support:
            comparison_gainers = tuple(i for i in gainers if coalition >> i & 1)
            h_set = tuple(i for i in nongainers if coalition >> i & 1)
            if not carriers <= set(h_set) or len(comparison_gainers) == len(gainers):
                continue
            intersection = coalition & co_singleton
            p_set = tuple(i for i in nongainers if not intersection >> i & 1)
            intersection_h = tuple(i for i in nongainers if intersection >> i & 1)
            if not p_set:
                continue
            defect = coalition_sum(x, intersection) - values[intersection]
            z_slack = coalition_sum(z, intersection) - values[intersection]
            comparison_payment = coalition_sum(z, intersection) - coalition_sum(
                x, intersection
            )
            if comparison_payment != z_slack - defect:
                raise AssertionError("co-singleton uncrossing payment identity failed")
            if defect != 0:
                raise AssertionError("exact-game tight co-singleton uncrossing failed")
            reserve = target_reserve_row(
                x, z, p_set, gainers, intersection_h, target
            )
            proper_rows.append(
                {
                    "coalition": coalition,
                    "intersection": intersection,
                    "reintroduces_omitted_player": bool(coalition >> omitted & 1),
                    "intersection_defect": str(defect),
                    "intersection_lmax_slack": str(z_slack),
                    "intersection_comparison_payment": str(comparison_payment),
                    "intersection_target_reserve": reserve[
                        "nonlow_target_reserve"
                    ],
                    "intersection_closes": (
                        comparison_payment >= 0 and reserve["target_reserve_closes"]
                    ),
                }
            )
        co_singleton_probe = {
            "coalition": co_singleton,
            "omitted_player": omitted,
            "proper_carrier_row_count": len(proper_rows),
            "crossing_proper_carrier_row_count": sum(
                row["reintroduces_omitted_player"] for row in proper_rows
            ),
            "intersection_closer_count": sum(
                row["intersection_closes"] for row in proper_rows
            ),
            "proper_carrier_rows": proper_rows,
        }
    return {
        "root": root,
        "affordable": gate["affordable"],
        "facet_margin": gate["margin"],
        "delta": str(delta),
        "q_total": str(sum(q, F(0))),
        "packing_support_size": len(packing),
        "tight_rooted_pairs": list(gate["tight_rooted_pairs"]),
        "common_nonpair_carriers": list(gate["common_nonpair_carriers"]),
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
        "maximum_closing_mass_on_price_face": str(closer_mass),
        "price_face_closer_packing": [
            {"coalition": coalition, "weight": str(weight)}
            for coalition, weight in closer_face_packing
        ],
        "some_price_optimal_packing_contains_closer": closer_mass > 0,
        "co_singleton_intersection_probe": co_singleton_probe,
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
    price_face_obstructions = []
    price_face_obstruction_records = set()
    exchange_types = Counter()
    price_loss_distribution = Counter()
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
                    minimum_distance = row["minimum_closing_exchange"]
                    closest_rows = [
                        closer
                        for closer in row["all_support_closers"]
                        if closer["minimum_packing_column_exchange"] == minimum_distance
                    ]
                    exchange = closest_rows[0]["closest_packing_exchanges"][0]
                    exchange_type = (
                        f"addG{len(exchange['added_gainers'])}_"
                        f"addL{len(exchange['added_nongainers'])}_"
                        f"dropG{len(exchange['removed_gainers'])}_"
                        f"dropL{len(exchange['removed_nongainers'])}"
                    )
                    exchange_types[exchange_type] += 1
                    price_loss_distribution[str(exchange["price_coefficient_loss"])] += 1
                if row["some_price_optimal_packing_contains_closer"]:
                    counts["roots_with_price_face_reserve"] += 1
                elif row["all_support_closers"]:
                    minimum_distance = row["minimum_closing_exchange"]
                    closest_rows = [
                        closer
                        for closer in row["all_support_closers"]
                        if closer["minimum_packing_column_exchange"] == minimum_distance
                    ]
                    chosen_closer = closest_rows[0]
                    chosen_exchange = chosen_closer["closest_packing_exchanges"][0]
                    price_face_obstruction_records.add((path.name, trail))
                    price_face_obstructions.append(
                        {
                            "source": path.name,
                            "trail": trail,
                            "root": row["root"],
                            "root_selector_loss": str(
                                x[row["root"]] - z[row["root"]]
                            ),
                            "maximum_overlap_roots": list(roots),
                            "facet_margin": row["facet_margin"],
                            "delta": row["delta"],
                            "packing_support_size": row["packing_support_size"],
                            "tight_rooted_pairs": row["tight_rooted_pairs"],
                            "common_nonpair_carriers": row[
                                "common_nonpair_carriers"
                            ],
                            "co_singleton_intersection_probe": row[
                                "co_singleton_intersection_probe"
                            ],
                            "minimum_exchange": minimum_distance,
                            "closer": chosen_closer,
                            "exchange": chosen_exchange,
                        }
                    )
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
        "roots_with_price_face_reserve": 448,
    }
    for key, value in expected.items():
        if counts[key] != value:
            raise AssertionError((key, counts[key], value))
    if len(failures) != 34:
        raise AssertionError(("records_without_same_packing_reserve", len(failures)))
    if len(price_face_obstructions) != 73:
        raise AssertionError(("price_face_obstruction_count", len(price_face_obstructions)))
    if len(price_face_obstruction_records) != 33:
        raise AssertionError(
            ("price_face_obstruction_record_count", len(price_face_obstruction_records))
        )
    obstruction_root_block_sizes = Counter(
        len(row["maximum_overlap_roots"]) for row in price_face_obstructions
    )
    if obstruction_root_block_sizes != Counter({2: 52, 3: 21}):
        raise AssertionError(
            ("price_face_obstruction_root_blocks", obstruction_root_block_sizes)
        )
    obstruction_loss_types = Counter(
        "strict" if F(row["root_selector_loss"]) > 0 else "tied"
        for row in price_face_obstructions
    )
    if obstruction_loss_types != Counter({"strict": 71, "tied": 2}):
        raise AssertionError(
            ("price_face_obstruction_loss_types", obstruction_loss_types)
        )
    obstruction_crossing_counts = Counter(
        row["co_singleton_intersection_probe"][
            "crossing_proper_carrier_row_count"
        ]
        for row in price_face_obstructions
    )
    if obstruction_crossing_counts != Counter({0: 71, 1: 2}):
        raise AssertionError(
            ("price_face_obstruction_crossings", obstruction_crossing_counts)
        )
    for obstruction in price_face_obstructions:
        exchange = obstruction["exchange"]
        if obstruction["facet_margin"] != "-1":
            raise AssertionError("noncanonical obstruction margin")
        if obstruction["delta"] != "0" or obstruction["packing_support_size"] != 1:
            raise AssertionError("obstruction optimizer is not a unit packing")
        if obstruction["tight_rooted_pairs"]:
            raise AssertionError("obstruction is not in the pair-free root branch")
        expected_carriers = set(obstruction["maximum_overlap_roots"]) - {
            obstruction["root"]
        }
        if set(obstruction["common_nonpair_carriers"]) != expected_carriers:
            raise AssertionError("obstruction carrier is not the other root block")
        if int(exchange["packing_coalition"]).bit_count() != 5:
            raise AssertionError("obstruction packing is not co-singleton")
        probe = obstruction["co_singleton_intersection_probe"]
        if not probe or probe["proper_carrier_row_count"] == 0:
            raise AssertionError("obstruction lacks a proper carrier row")
        if probe["intersection_closer_count"] == 0:
            raise AssertionError("co-singleton intersections do not close")
        if exchange["added"] or len(exchange["removed_gainers"]) != 1:
            raise AssertionError("obstruction is not a gainer deletion")
        if len(exchange["removed_nongainers"]) not in (0, 1):
            raise AssertionError("obstruction changes too many nongainers")
        if exchange["price_coefficient_loss"] != obstruction["minimum_exchange"]:
            raise AssertionError("exchange distance/price loss mismatch")
        if F(exchange["packing_target_reserve"]) < 0:
            raise AssertionError("improper co-singleton row lacks target reserve")

    report = {
        "status": "exact marked-packing complement and target-reserve audit",
        **dict(counts),
        "records_without_same_packing_reserve": len(failures),
        "minimum_exchange_type_distribution": dict(exchange_types),
        "minimum_exchange_price_loss_distribution": dict(price_loss_distribution),
        "price_face_obstruction_count": len(price_face_obstructions),
        "price_face_obstruction_record_count": len(price_face_obstruction_records),
        "price_face_obstruction_root_block_size_distribution": dict(
            obstruction_root_block_sizes
        ),
        "price_face_obstruction_loss_type_distribution": dict(
            obstruction_loss_types
        ),
        "price_face_obstruction_crossing_row_count_distribution": dict(
            obstruction_crossing_counts
        ),
        "price_face_obstruction_classification": (
            "all 73 roots in 33 records are pair-free roots of optimal margin "
            "-1; their common carriers are exactly the other maximum-overlap "
            "roots and their returned optimizer is one unit of a co-singleton row; "
            "25 properize by deleting one payoff gainer at price loss one, "
            "and 48 delete one gainer plus one nongainer at price loss two"
        ),
        "price_face_obstructions": price_face_obstructions,
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

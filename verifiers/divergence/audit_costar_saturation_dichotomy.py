#!/usr/bin/env python3
r"""Exact controls for the rooted co-star saturation dichotomy (PXC60).

In the absence of an Lmin-tight rooted row omitting two gainers, the rooted
packing value is at most g/(g-1).  Equality forces a fractional decorated
complete co-star.  This driver checks the dimension-free counting identities
on the n=6 archives and fixed hostile/equality controls.  Finite counts audit
scope and do not eliminate the intermediate-packing branch universally.
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

from audit_carrier_separator_payment import full_tight_support  # noqa: E402
from audit_ceiling_root_gainer_exclusion import rooted_packing  # noqa: E402
from audit_direct_ceiling_common_hinge_trichotomy import has_direct_packet  # noqa: E402
from audit_lmax_overcover import records  # noqa: E402
from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from exactlp import exact_linprog  # noqa: E402
from verify_labelled_branch_duals import CASES  # noqa: E402


def coalition_sum(point, coalition):
    return sum(
        (point[player] for player in range(len(point)) if coalition >> player & 1),
        F(0),
    )


def strictly_lorenz_improving_tangent(point, direction):
    """Exact small-step Lorenz test, sorting directions inside tied strata."""
    order = tuple(sorted(range(len(point)), key=lambda i: (point[i], direction[i])))
    prefix = F(0)
    prefixes = []
    for player in order[:-1]:
        prefix += direction[player]
        prefixes.append(prefix)
    return all(value >= 0 for value in prefixes) and any(
        value > 0 for value in prefixes
    )


def hall_certificate(rooted, omitted, gainers, outsiders, g):
    """Minimize the weighted Hall slack over normalized decoration prices."""
    if not outsiders:
        return {
            "minimum_slack": None,
            "obstruction_margin": "0",
            "prices": {},
            "type_minima": {},
        }
    beta_index = {player: index for index, player in enumerate(outsiders)}
    t_index = {
        player: len(outsiders) + index for index, player in enumerate(gainers)
    }
    width = len(outsiders) + len(gainers)
    inequalities = []
    rhs = []
    for coalition in rooted:
        if len(omitted[coalition]) != 1:
            continue
        omitted_gainer = omitted[coalition][0]
        row = [F(0)] * width
        row[t_index[omitted_gainer]] = F(1)
        for outsider in outsiders:
            if coalition >> outsider & 1:
                row[beta_index[outsider]] -= F(1)
        inequalities.append(row)
        rhs.append(F(0))
    for outsider in outsiders:
        row = [F(0)] * width
        row[beta_index[outsider]] = F(-1)
        inequalities.append(row)
        rhs.append(F(0))
    equality = [F(0)] * width
    for outsider in outsiders:
        equality[beta_index[outsider]] = F(1)
    objective = [F(0)] * width
    for outsider in outsiders:
        objective[beta_index[outsider]] = F(1)
    for gainer in gainers:
        objective[t_index[gainer]] = -F(1, g - 1)
    status, optimum, solution = exact_linprog(
        objective, inequalities, rhs, [equality], [F(1)]
    )
    if status != "optimal":
        raise AssertionError("weighted Hall dual did not optimize")
    prices = {
        player: solution[beta_index[player]] for player in outsiders
    }
    minima = {
        gainer: min(
            sum(
                (
                    prices[outsider]
                    for outsider in outsiders
                    if coalition >> outsider & 1
                ),
                F(0),
            )
            for coalition in rooted
            if omitted[coalition] == (gainer,)
        )
        for gainer in gainers
    }
    recomputed = F(1) - F(1, g - 1) * sum(minima.values(), F(0))
    if recomputed != optimum:
        raise AssertionError("weighted Hall objective did not recompute")
    return {
        "minimum_slack": str(optimum),
        "obstruction_margin": str(max(F(0), -optimum)),
        "prices": {
            str(player): str(value) for player, value in prices.items() if value
        },
        "type_minima": {
            str(player): str(value) for player, value in minima.items()
        },
    }


def root_rows(values, x, z):
    n = len(x)
    total = sum(x, F(0))
    ceiling = max(z)
    gainers = tuple(player for player in range(n) if z[player] > x[player])
    gainer_set = set(gainers)
    support = tuple(full_tight_support(values, x))
    z_tight = set(full_tight_support(values, z))
    answer = []
    for root in range(n):
        if z[root] != ceiling or x[root] < ceiling or root in gainer_set:
            continue
        rooted, nu, weights, _cover = rooted_packing(support, n, root)
        omitted = {
            coalition: tuple(
                player for player in gainers if not (coalition >> player & 1)
            )
            for coalition in rooted
        }
        has_multiomission = any(len(players) >= 2 for players in omitted.values())
        row = {
            "root": root,
            "gainers": list(gainers),
            "gainer_count": len(gainers),
            "packing_value": str(nu),
            "has_multiomission_row": has_multiomission,
        }
        if has_multiomission or len(gainers) < 2:
            answer.append(row)
            continue

        g = len(gainers)
        cap = F(g, g - 1)
        outsiders = tuple(
            player
            for player in range(n)
            if player not in gainer_set and player != root
        )
        minimum_gainer = min(x[player] for player in gainers)
        ordered = all(x[root] >= x[player] for player in gainers) and all(
            minimum_gainer >= x[player] for player in outsiders
        )
        if not (F(1) <= nu <= cap):
            raise AssertionError("no-multiomission packing escaped its exact interval")
        if nu == 1:
            regime = "unit"
        elif nu == cap:
            regime = "saturated"
        else:
            regime = "intermediate"
        row["regime"] = regime
        row["saturation_cap"] = str(cap)
        row["saturation_deficit"] = str(cap - nu)
        row["ordered"] = ordered
        hall = hall_certificate(rooted, omitted, gainers, outsiders, g)
        hall_obstructed = F(hall["obstruction_margin"]) > 0
        if hall_obstructed != (regime != "saturated"):
            raise AssertionError("packing saturation/Hall alternative disagreed")
        row["weighted_hall"] = hall
        if hall_obstructed:
            prices = {
                player: F(hall["prices"].get(str(player), "0"))
                for player in outsiders
            }
            minima = {
                player: F(hall["type_minima"][str(player)])
                for player in gainers
            }
            direction = [F(0)] * n
            direction[root] = F(g - 1) - sum(minima.values(), F(0))
            for player in gainers:
                direction[player] = minima[player] - 1
            for player in outsiders:
                direction[player] = prices[player]
            if sum(direction, F(0)) != 0 or direction[root] >= 0:
                raise AssertionError("weighted Hall tangent has wrong total or root sign")
            if any(direction[player] > 0 for player in gainers):
                raise AssertionError("weighted Hall tangent has a positive gainer")
            for coalition in rooted:
                if len(omitted[coalition]) == 1 and coalition_sum(direction, coalition) < 0:
                    raise AssertionError("Hall tangent fails on a gainer-omitting rooted row")
            blockers = tuple(
                coalition
                for coalition in support
                if coalition_sum(direction, coalition) < 0
            )
            for coalition in blockers:
                if coalition >> root & 1 and omitted[coalition]:
                    raise AssertionError("Hall blocker has an excluded rooted form")
            negative_donors = tuple(
                player for player in gainers if direction[player] < 0
            ) + (root,)
            positive_recipients = tuple(
                player for player in outsiders if direction[player] > 0
            )
            strict_transfer_order = bool(positive_recipients) and all(
                x[donor] > x[recipient]
                for donor in negative_donors
                for recipient in positive_recipients
            )
            lorenz_improving = strictly_lorenz_improving_tangent(x, direction)
            if lorenz_improving and not blockers:
                raise AssertionError("Lorenz-improving Hall tangent lacks a blocker")
            row["hall_tangent"] = {
                "direction": [str(value) for value in direction],
                "strict_lorenz_transfer_order": strict_transfer_order,
                "strictly_lorenz_improving": lorenz_improving,
                "tight_blockers": list(blockers),
                "root_free_blockers": [
                    coalition for coalition in blockers if not (coalition >> root & 1)
                ],
                "rooted_all_gainer_blockers": [
                    coalition for coalition in blockers if coalition >> root & 1
                ],
            }

        if regime == "saturated":
            omission_weight = {player: F(0) for player in gainers}
            outsider_load = {player: F(0) for player in outsiders}
            average_decoration = F(0)
            positive_rows = []
            for coalition, weight in zip(rooted, weights):
                if not weight:
                    continue
                if len(omitted[coalition]) != 1:
                    raise AssertionError("saturated packing uses a non-costar row")
                omitted_gainer = omitted[coalition][0]
                omission_weight[omitted_gainer] += weight
                decoration = tuple(
                    player
                    for player in outsider_load
                    if coalition >> player & 1
                )
                for player in decoration:
                    outsider_load[player] += weight
                average_decoration += weight * sum(
                    (x[player] for player in decoration), F(0)
                )
                positive_rows.append(
                    {
                        "coalition": coalition,
                        "weight": str(weight),
                        "omitted_gainer": omitted_gainer,
                        "decoration": list(decoration),
                    }
                )
            required = F(1, g - 1)
            if any(value != required for value in omission_weight.values()):
                raise AssertionError("saturated omission weights are not uniform")
            if any(value > 1 for value in outsider_load.values()):
                raise AssertionError("saturated decoration load exceeds one")
            packet_left = F(g, g - 1) * x[root] + sum(
                (x[player] for player in gainers), F(0)
            ) + average_decoration
            if packet_left > total:
                raise AssertionError("fractional decorated packet failed")

            highest_gainer_z = max(z[player] for player in gainers)
            aligned = []
            mu = F((g - 1) * n, g * (n - g))
            total_gain = sum((z[player] - x[player] for player in gainers), F(0))
            actual_overlap = total - total_gain
            target = F(n, (n * n) // 4) * total
            maximum_individual_gain = max(z[player] - x[player] for player in gainers)
            root_loss = x[root] - z[root]
            noncommon_penalty = total_gain - maximum_individual_gain - root_loss
            selection_free_floor = None
            if ordered:
                selection_free_floor = (
                    F(n, g * (n - g)) * total
                    + mu * average_decoration
                    - noncommon_penalty
                )
                if actual_overlap < selection_free_floor:
                    raise AssertionError("selection-free fractional co-star bound failed")
            for positive in positive_rows:
                coalition = positive["coalition"]
                omitted_gainer = positive["omitted_gainer"]
                if (
                    not ordered
                    or coalition not in z_tight
                    or z[omitted_gainer] != highest_gainer_z
                    or z[root] < z[omitted_gainer]
                ):
                    continue
                decoration_loss = sum(
                    (x[player] - z[player] for player in positive["decoration"]),
                    F(0),
                )
                proved_floor = (
                    F(n, g * (n - g)) * total
                    + mu * average_decoration
                    - decoration_loss
                )
                if actual_overlap < proved_floor:
                    raise AssertionError(
                        (
                            "fractional PXC59 overlap bound failed",
                            root,
                            gainers,
                            coalition,
                            average_decoration,
                            decoration_loss,
                            actual_overlap,
                            proved_floor,
                            tuple(zip(rooted, weights)),
                        )
                    )
                aligned.append(
                    {
                        "coalition": coalition,
                        "omitted_gainer": omitted_gainer,
                        "decoration_loss": str(decoration_loss),
                        "proved_floor": str(proved_floor),
                        "target": str(target),
                        "closes_target": proved_floor >= target,
                    }
                )
            row.update(
                {
                    "positive_packing_rows": positive_rows,
                    "omission_weights": {
                        str(player): str(value)
                        for player, value in omission_weight.items()
                    },
                    "outsider_loads": {
                        str(player): str(value)
                        for player, value in outsider_load.items()
                    },
                    "average_decoration_mass": str(average_decoration),
                    "packet_left": str(packet_left),
                    "noncommon_penalty": str(noncommon_penalty),
                    "selection_free_floor": (
                        None if selection_free_floor is None else str(selection_free_floor)
                    ),
                    "selection_free_closes_target": (
                        selection_free_floor is not None and selection_free_floor >= target
                    ),
                    "selection_free_target_margin": (
                        None
                        if selection_free_floor is None
                        else str(selection_free_floor - target)
                    ),
                    "aligned_rows": aligned,
                }
            )
        answer.append(row)
    return tuple(answer)


def lower_envelope_case(case):
    generators = (tuple(map(F, case["g"])), tuple(map(F, case["h"])))
    return (
        lower_envelope(generators),
        tuple(map(F, case["x"])),
        tuple(map(F, case["z"])),
    )


def relaxed_nonselector_control():
    """Ordered saturated packet showing that Lmax optimality is indispensable."""
    x = (F(9),) + (F(1),) * 7
    z = (F(7, 2),) + (F(25, 8),) * 4 + (F(0),) * 3
    n, g = 8, 4
    total = sum(x, F(0))
    gainers = tuple(range(1, 5))
    root = 0
    packet_left = F(g, g - 1) * x[root] + sum(
        (x[player] for player in gainers), F(0)
    )
    total_gain = sum((z[player] - x[player] for player in gainers), F(0))
    maximum_gain = max(z[player] - x[player] for player in gainers)
    root_loss = x[root] - z[root]
    penalty = total_gain - maximum_gain - root_loss
    base = F(n, g * (n - g)) * total
    floor = base - penalty
    target = F(n, (n * n) // 4) * total
    actual = total - total_gain
    costars = tuple(
        (1 << root)
        | sum(1 << player for player in gainers if player != omitted)
        for omitted in gainers
    )
    slacks = tuple(
        coalition_sum(z, coalition) - coalition_sum(x, coalition)
        for coalition in costars
    )
    if total != sum(z, F(0)) or packet_left != total:
        raise AssertionError("relaxed nonselector control lost efficiency or saturation")
    if max(z) != z[root] or any(slack != penalty for slack in slacks):
        raise AssertionError("relaxed nonselector ceiling/co-star comparison changed")
    if not (floor <= actual < target):
        raise AssertionError("relaxed nonselector no-go control no longer separates claims")
    return {
        "status": "exact relaxed allocation-level no-go; not asserted selector-realizable",
        "x": [str(value) for value in x],
        "z": [str(value) for value in z],
        "root": root,
        "gainers": list(gainers),
        "clean_costars": list(costars),
        "costar_slacks": [str(value) for value in slacks],
        "packet_left": str(packet_left),
        "total": str(total),
        "noncommon_penalty": str(penalty),
        "selection_free_floor": str(floor),
        "actual_overlap": str(actual),
        "hybrid_target": str(target),
        "lesson": (
            "ordered saturated packet geometry and core-side co-star comparisons "
            "alone do not imply the target; Lmax optimality must be used"
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    archive = []
    positive_residual = []
    for path in args.paths:
        payload = json.loads(path.read_text())
        for source, trail, values, x, z in records(payload, path):
            rows = root_rows(values, x, z)
            total = sum(x, F(0))
            floor = min(x)
            ceiling = max(z)
            direct = has_direct_packet(x, z, F(2, 3))
            ceiling_closes = (
                ceiling > 0
                and ceiling - floor + total * floor / ceiling >= F(2, 3) * total
            )
            if direct:
                preclosure = "direct"
            elif ceiling_closes:
                preclosure = "ceiling"
            elif floor == 0:
                preclosure = "null"
            else:
                preclosure = "positive_residual"
            record = {
                "source": source.name,
                "trail": trail,
                "preclosure": preclosure,
                "roots": rows,
            }
            archive.append(record)
            if preclosure == "positive_residual":
                positive_residual.append(
                    record
                )

    fixed = []
    for case in CASES:
        values, x, z = lower_envelope_case(case)
        fixed.append({"name": case["name"], "roots": root_rows(values, x, z)})

    archive_roots = tuple(root for record in archive for root in record["roots"])
    residual_roots = tuple(
        root for record in positive_residual for root in record["roots"]
    )
    fixed_roots = tuple(root for record in fixed for root in record["roots"])
    archive_selection_free = tuple(
        F(row["selection_free_target_margin"])
        for row in archive_roots
        if row.get("selection_free_target_margin") is not None
    )
    residual_selection_free = tuple(
        F(row["selection_free_target_margin"])
        for row in residual_roots
        if row.get("selection_free_target_margin") is not None
    )

    def distribution(rows):
        return Counter(
            "multiomission" if row["has_multiomission_row"] else row.get("regime", "small-g")
            for row in rows
        )

    counts = {
        "archive_records": len(archive),
        "archive_roots": len(archive_roots),
        "archive_regimes": dict(sorted(distribution(archive_roots).items())),
        "archive_ordered_regimes": dict(
            sorted(distribution(tuple(row for row in archive_roots if row.get("ordered"))).items())
        ),
        "archive_intermediate_preclosure": dict(
            sorted(
                Counter(
                    record["preclosure"]
                    for record in archive
                    for row in record["roots"]
                    if row.get("regime") == "intermediate"
                ).items()
            )
        ),
        "archive_hall_obstruction_roots": sum(
            F(row.get("weighted_hall", {}).get("obstruction_margin", 0)) > 0
            for row in archive_roots
        ),
        "archive_hall_roots_with_tight_blocker": sum(
            bool(row.get("hall_tangent", {}).get("tight_blockers"))
            for row in archive_roots
        ),
        "archive_hall_roots_with_root_free_blocker": sum(
            bool(row.get("hall_tangent", {}).get("root_free_blockers"))
            for row in archive_roots
        ),
        "archive_hall_roots_with_rooted_all_gainer_blocker": sum(
            bool(row.get("hall_tangent", {}).get("rooted_all_gainer_blockers"))
            for row in archive_roots
        ),
        "archive_strict_order_hall_roots": sum(
            row.get("hall_tangent", {}).get("strict_lorenz_transfer_order", False)
            for row in archive_roots
        ),
        "archive_lorenz_improving_hall_roots": sum(
            row.get("hall_tangent", {}).get("strictly_lorenz_improving", False)
            for row in archive_roots
        ),
        "archive_saturated_selection_free_closing": sum(
            row.get("regime") == "saturated"
            and row.get("selection_free_closes_target", False)
            for row in archive_roots
        ),
        "archive_minimum_selection_free_margin": str(min(archive_selection_free)),
        "archive_selection_free_equalities": sum(
            margin == 0 for margin in archive_selection_free
        ),
        "positive_residual_records": len(positive_residual),
        "positive_residual_roots": len(residual_roots),
        "positive_residual_regimes": dict(sorted(distribution(residual_roots).items())),
        "positive_residual_saturated_with_aligned_row": sum(
            row.get("regime") == "saturated" and bool(row.get("aligned_rows"))
            for row in residual_roots
        ),
        "positive_residual_saturated_closing": sum(
            row.get("regime") == "saturated"
            and any(aligned["closes_target"] for aligned in row.get("aligned_rows", ()))
            for row in residual_roots
        ),
        "positive_residual_selection_free_closing": sum(
            row.get("regime") == "saturated"
            and row.get("selection_free_closes_target", False)
            for row in residual_roots
        ),
        "positive_residual_minimum_selection_free_margin": str(
            min(residual_selection_free)
        ),
        "positive_residual_selection_free_equalities": sum(
            margin == 0 for margin in residual_selection_free
        ),
        "fixed_roots": len(fixed_roots),
        "fixed_regimes": dict(sorted(distribution(fixed_roots).items())),
        "fixed_hall_obstruction_roots": sum(
            F(row.get("weighted_hall", {}).get("obstruction_margin", 0)) > 0
            for row in fixed_roots
        ),
    }
    expected_counts = {
        "archive_records": 374,
        "archive_roots": 703,
        "archive_regimes": {
            "intermediate": 27,
            "multiomission": 78,
            "saturated": 98,
            "unit": 500,
        },
        "archive_ordered_regimes": {"saturated": 89},
        "archive_intermediate_preclosure": {"direct": 27},
        "archive_hall_obstruction_roots": 527,
        "archive_hall_roots_with_tight_blocker": 35,
        "archive_hall_roots_with_root_free_blocker": 0,
        "archive_hall_roots_with_rooted_all_gainer_blocker": 35,
        "archive_strict_order_hall_roots": 7,
        "archive_lorenz_improving_hall_roots": 7,
        "archive_saturated_selection_free_closing": 89,
        "archive_minimum_selection_free_margin": "0",
        "archive_selection_free_equalities": 30,
        "positive_residual_records": 16,
        "positive_residual_roots": 16,
        "positive_residual_regimes": {"saturated": 16},
        "positive_residual_saturated_with_aligned_row": 16,
        "positive_residual_saturated_closing": 16,
        "positive_residual_selection_free_closing": 16,
        "positive_residual_minimum_selection_free_margin": "0",
        "positive_residual_selection_free_equalities": 7,
        "fixed_roots": 10,
        "fixed_regimes": {"multiomission": 4, "saturated": 4, "unit": 2},
        "fixed_hall_obstruction_roots": 2,
    }
    if counts != expected_counts:
        raise AssertionError(("co-star saturation census changed", counts))

    report = {
        "status": "exact rooted co-star saturation controls computed",
        "human_theorem": (
            "without a rooted multi-omission row, 1<=nu_r<=g/(g-1); "
            "equality forces a fractional decorated complete co-star with "
            "omission weight 1/(g-1) for every gainer; a Lorenz-improving Hall "
            "obstruction yields a root-free or rooted-all-gainer tight blocker; "
            "the saturated arm has a selection-free overlap bound priced by "
            "D-d_max-root_loss"
        ),
        "counts": counts,
        "positive_residual_rows": positive_residual,
        "fixed_controls": fixed,
        "relaxed_nonselector_control": relaxed_nonselector_control(),
        "scope": (
            "dimension-free counting theorem with exact finite scope audit; "
            "does not eliminate non-improving Hall obstructions, price the blocker, "
            "or prove the selection-free concentration condition universally"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

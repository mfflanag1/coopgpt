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
from audit_lmax_overcover import records, top_certificate  # noqa: E402
from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from audit_sign_coherent_staged_lifts import payoff_blocks  # noqa: E402
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


def minimum_lmax_root_certificate(values, x, z, target, root):
    """Minimize the Lmax root coefficient and expose its evaluated surplus."""
    n = len(z)
    full = (1 << n) - 1
    blocks = payoff_blocks(z, "max")
    stage = next(index for index, block in enumerate(blocks) if target in block)
    old = tuple(player for block in blocks[:stage] for player in block)
    current = blocks[stage]
    if root not in old and root not in current:
        raise AssertionError("ceiling root is not in the Lmax cumulative upper set")
    tight = tuple(
        coalition
        for coalition in range(1, full)
        if coalition_sum(z, coalition) == values[coalition]
    )
    m = len(tight)
    q_index = {player: m + index for index, player in enumerate(old)}
    r_index = {
        player: m + len(old) + index for index, player in enumerate(current)
    }
    c_index = m + len(old) + len(current)
    width = c_index + 1
    equalities = []
    equality_rhs = []
    for coordinate in range(n):
        row = [F(0)] * width
        for index, coalition in enumerate(tight):
            row[index] = F((coalition >> coordinate) & 1)
        if coordinate in q_index:
            row[q_index[coordinate]] = F(1)
        if coordinate in r_index:
            row[r_index[coordinate]] = F(-1)
        row[c_index] = F(-1)
        equalities.append(row)
        equality_rhs.append(F(coordinate == target))
    inequalities = []
    inequality_rhs = []
    for variable in tuple(range(m)) + tuple(r_index.values()):
        row = [F(0)] * width
        row[variable] = F(-1)
        inequalities.append(row)
        inequality_rhs.append(F(0))
    for variable in q_index.values():
        row = [F(0)] * width
        row[variable] = F(1)
        inequalities.append(row)
        inequality_rhs.append(F(0))
    objective = [F(0)] * width
    if root in q_index:
        objective[q_index[root]] = F(-1)
    else:
        objective[r_index[root]] = F(1)
    status, optimum, solution = exact_linprog(
        objective,
        inequalities,
        inequality_rhs,
        equalities,
        equality_rhs,
    )
    if status != "optimal" or optimum < 0:
        raise AssertionError("Lmax root-price minimization failed")
    reverse_terms = []
    for index, coalition in enumerate(tight):
        multiplier = solution[index]
        reverse_slack = coalition_sum(x, coalition) - coalition_sum(z, coalition)
        if multiplier < 0 or reverse_slack < 0:
            raise AssertionError("invalid Lmax coalition surplus term")
        if multiplier:
            reverse_terms.append(
                {
                    "coalition": coalition,
                    "multiplier": multiplier,
                    "reverse_slack": reverse_slack,
                    "payment": multiplier * reverse_slack,
                }
            )
    pin_terms = []
    for player, index in q_index.items():
        multiplier = -solution[index]
        gain = z[player] - x[player]
        if multiplier < 0:
            raise AssertionError("invalid old-pin Lmax surplus term")
        if multiplier and gain:
            if gain < 0 and player != root:
                raise AssertionError("a nongainer other than the root entered Lmax transport")
            pin_terms.append(
                {
                    "player": player,
                    "stage_side": "old",
                    "multiplier": multiplier,
                    "gain": gain,
                    "payment": multiplier * gain,
                }
            )
    for player, index in r_index.items():
        multiplier = solution[index]
        gain = z[player] - x[player]
        if multiplier < 0:
            raise AssertionError("invalid current-pin Lmax surplus term")
        if multiplier and gain:
            if gain < 0 and player != root:
                raise AssertionError("a nongainer other than the root entered Lmax transport")
            pin_terms.append(
                {
                    "player": player,
                    "stage_side": "current",
                    "multiplier": multiplier,
                    "gain": gain,
                    "payment": multiplier * gain,
                }
            )
    positive_surplus = sum(
        (term["payment"] for term in reverse_terms), F(0)
    ) + sum(
        (
            term["payment"]
            for term in pin_terms
            if term["player"] != root
        ),
        F(0),
    )
    root_terms = [term for term in pin_terms if term["player"] == root]
    if sum((term["multiplier"] for term in root_terms), F(0)) != optimum:
        raise AssertionError("reported Lmax root price misses the root pin term")
    if positive_surplus != optimum * (x[root] - z[root]) - (z[target] - x[target]):
        raise AssertionError("evaluated Lmax transport surplus decomposition failed")
    return {
        "price": optimum,
        "reverse_terms": reverse_terms,
        "pin_terms": pin_terms,
        "surplus": positive_surplus,
    }


def minimum_lmax_transport_cover(
    certificates, gains, gainers, omitted, root_loss, objective_kind="net"
):
    """Cover every nonomitted gainer by normalized Lmax relation bundles."""
    targets = tuple(gainers)
    demanded = tuple(player for player in gainers if player != omitted)
    bundle = {}
    reverse_credit = {}
    for target in targets:
        certificate = certificates[target]
        coefficients = {player: F(player == target) for player in gainers}
        for term in certificate["pin_terms"]:
            player = term["player"]
            if player in coefficients:
                coefficients[player] += term["multiplier"]
        bundle[target] = coefficients
        reverse_credit[target] = sum(
            (term["payment"] for term in certificate["reverse_terms"]), F(0)
        )
        net_cost = certificate["price"] * root_loss - reverse_credit[target]
        bundle_value = sum(
            (coefficients[player] * gains[player] for player in gainers), F(0)
        )
        if net_cost != bundle_value:
            raise AssertionError("Lmax relation bundle evaluation changed")
        if net_cost < 0:
            raise AssertionError("Lmax relation bundle has negative net cost")
    inequalities = []
    rhs = []
    for player in demanded:
        inequalities.append([-bundle[target][player] for target in targets])
        rhs.append(F(-1))
    for index in range(len(targets)):
        row = [F(0)] * len(targets)
        row[index] = F(-1)
        inequalities.append(row)
        rhs.append(F(0))
    if objective_kind == "net":
        objective = [
            certificates[target]["price"] * root_loss - reverse_credit[target]
            for target in targets
        ]
    elif objective_kind == "root":
        objective = [certificates[target]["price"] for target in targets]
    else:
        raise ValueError(f"unknown transport-cover objective {objective_kind!r}")
    status, optimum, solution = exact_linprog(objective, inequalities, rhs)
    if status != "optimal":
        raise AssertionError("Lmax transport bundle cover failed")
    loads = {
        player: sum(
            (solution[index] * bundle[target][player] for index, target in enumerate(targets)),
            F(0),
        )
        for player in gainers
    }
    if any(loads[player] < 1 for player in demanded):
        raise AssertionError("Lmax transport bundle left a demanded gainer uncovered")
    root_price = sum(
        (
            solution[index] * certificates[target]["price"]
            for index, target in enumerate(targets)
        ),
        F(0),
    )
    reverse = sum(
        (solution[index] * reverse_credit[target] for index, target in enumerate(targets)),
        F(0),
    )
    net_cost = root_price * root_loss - reverse
    if objective_kind == "net" and optimum != net_cost:
        raise AssertionError("Lmax bundle-cover objective decomposition failed")
    if objective_kind == "root" and optimum != root_price:
        raise AssertionError("Lmax bundle-cover root objective changed")
    if net_cost != sum((loads[player] * gains[player] for player in gainers), F(0)):
        raise AssertionError("Lmax bundle-cover gainer value changed")
    dual_prices = None
    if objective_kind == "root":
        dual_inequalities = []
        dual_rhs = []
        for target in targets:
            dual_inequalities.append(
                [bundle[target][player] for player in demanded]
            )
            dual_rhs.append(certificates[target]["price"])
        for index in range(len(demanded)):
            row = [F(0)] * len(demanded)
            row[index] = F(-1)
            dual_inequalities.append(row)
            dual_rhs.append(F(0))
        dual_status, dual_objective, dual_solution = exact_linprog(
            [F(-1)] * len(demanded), dual_inequalities, dual_rhs
        )
        if dual_status != "optimal" or -dual_objective != optimum:
            raise AssertionError("Lmax bundle-cover min-max identity failed")
        dual_prices = {
            player: dual_solution[index]
            for index, player in enumerate(demanded)
            if dual_solution[index]
        }
    return {
        "omitted": omitted,
        "weights": {
            target: solution[index]
            for index, target in enumerate(targets)
            if solution[index]
        },
        "loads": loads,
        "objective_kind": objective_kind,
        "objective_value": optimum,
        "net_cost": net_cost,
        "root_price": root_price,
        "reverse_credit": reverse,
        "dual_prices": dual_prices,
    }


def root_rows(values, x, z):
    n = len(x)
    total = sum(x, F(0))
    ceiling = max(z)
    gainers = tuple(player for player in range(n) if z[player] > x[player])
    gainer_set = set(gainers)
    support = tuple(full_tight_support(values, x))
    z_tight = set(full_tight_support(values, z))
    overcover = top_certificate(values, z)
    sparse_lmax_support = set(overcover["support"])
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
        if ordered:
            maximum_z = max(z)
            if any(z[player] == maximum_z for player in outsiders):
                raise AssertionError("an ordered outsider entered the Lmax top stratum")
            alpha = tuple(overcover["alpha"])
            root_loss = x[root] - z[root]
            weighted_top_gain = sum(
                (
                    alpha[player] * (z[player] - x[player])
                    for player in gainers
                    if z[player] == maximum_z
                ),
                F(0),
            )
            top_payment = alpha[root] * root_loss - weighted_top_gain
            anchor_surplus = sum(
                (alpha[player] * x[player] for player in range(n)), F(0)
            ) - maximum_z
            if top_payment != anchor_surplus or top_payment < 0:
                raise AssertionError("normalized Lmax top payment identity failed")
            row["lmax_top_payment"] = {
                "alpha": [str(value) for value in alpha],
                "root_loss_payment": str(alpha[root] * root_loss),
                "weighted_top_gainer_debt": str(weighted_top_gain),
                "surplus": str(top_payment),
                "nonroot_top_mass": str(1 - alpha[root]),
            }
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
                root_certificates = {
                    player: minimum_lmax_root_certificate(
                        values, x, z, player, root
                    )
                    for player in gainers
                }
                root_prices = {
                    player: certificate["price"]
                    for player, certificate in root_certificates.items()
                }
                for player, price in root_prices.items():
                    if z[player] - x[player] > price * root_loss:
                        raise AssertionError("minimal Lmax root price misses actual gain")
                maximum_gainers = tuple(
                    player
                    for player in gainers
                    if z[player] - x[player] == maximum_individual_gain
                )
                gains = {
                    player: z[player] - x[player] for player in gainers
                }
                transport_covers = tuple(
                    minimum_lmax_transport_cover(
                        root_certificates,
                        gains,
                        gainers,
                        omitted,
                        root_loss,
                    )
                    for omitted in maximum_gainers
                )
                transport_cover = min(
                    transport_covers,
                    key=lambda cover: (cover["net_cost"], cover["omitted"]),
                )
                root_price_covers = tuple(
                    minimum_lmax_transport_cover(
                        root_certificates,
                        gains,
                        gainers,
                        omitted,
                        root_loss,
                        objective_kind="root",
                    )
                    for omitted in maximum_gainers
                )
                root_price_cover = min(
                    root_price_covers,
                    key=lambda cover: (cover["root_price"], cover["omitted"]),
                )
                dual_tau = root_price_cover["root_price"]
                dual_y = {
                    player: root_price_cover["dual_prices"].get(player, F(0))
                    for player in gainers
                }
                if sum(dual_y.values(), F(0)) != dual_tau:
                    raise AssertionError("bundle-cover dual prices do not sum to tau")
                dual_separator_rows = {}
                if dual_tau > 1:
                    for relation_target, certificate in root_certificates.items():
                        weighted_row_value = F(0)
                        negative_rows = []
                        for term in certificate["reverse_terms"]:
                            coalition = term["coalition"]
                            row_value = (
                                -dual_tau * F(bool(coalition >> root & 1))
                                + sum(
                                    (
                                        dual_y[player]
                                        for player in gainers
                                        if coalition >> player & 1
                                    ),
                                    F(0),
                                )
                            )
                            weighted_row_value += term["multiplier"] * row_value
                            if row_value < 0:
                                omitted_price = sum(
                                    (
                                        dual_y[player]
                                        for player in gainers
                                        if not (coalition >> player & 1)
                                    ),
                                    F(0),
                                )
                                if not (coalition >> root & 1) or omitted_price <= 0:
                                    raise AssertionError("dual separator lost its rooted omission label")
                                negative_rows.append(
                                    {
                                        "coalition": coalition,
                                        "multiplier": term["multiplier"],
                                        "dual_row_value": row_value,
                                        "omitted_dual_price": omitted_price,
                                        "reverse_slack": term["reverse_slack"],
                                    }
                                )
                        bundle_dual_value = dual_y[relation_target] + sum(
                            (
                                term["multiplier"] * dual_y[term["player"]]
                                for term in certificate["pin_terms"]
                                if term["player"] in dual_y
                            ),
                            F(0),
                        )
                        expected_row_value = (
                            bundle_dual_value
                            - certificate["price"] * dual_tau
                        )
                        if weighted_row_value != expected_row_value:
                            raise AssertionError("bundle dual separator identity failed")
                        if weighted_row_value > certificate["price"] * (1 - dual_tau):
                            raise AssertionError("bundle dual constraint failed to separate")
                        if not negative_rows:
                            raise AssertionError("tau>1 relation has no negative rooted separator")
                        dual_separator_rows[relation_target] = negative_rows
                aggregate_candidates = {
                    omitted: sum(
                        (
                            price
                            for player, price in root_prices.items()
                            if player != omitted
                        ),
                        F(0),
                    )
                    for omitted in maximum_gainers
                }
                omitted_maximum_gainer = min(
                    aggregate_candidates,
                    key=lambda player: (aggregate_candidates[player], player),
                )
                aggregate_root_price = aggregate_candidates[omitted_maximum_gainer]
                cardinality_slack = (
                    F(n, g * (n - g)) - F(n, (n * n) // 4)
                ) * total
                transport_cover_reserve = (
                    root_loss + mu * average_decoration + cardinality_slack
                )
                transport_cover_margin = (
                    transport_cover_reserve - transport_cover["net_cost"]
                )
                root_price_cover_margin = (
                    transport_cover_reserve
                    - root_price_cover["root_price"] * root_loss
                )
                actual_nonomitted_gain = total_gain - maximum_individual_gain
                if transport_cover["net_cost"] < actual_nonomitted_gain:
                    raise AssertionError("Lmax bundle cover underprices actual demand")
                congestion_charge = (aggregate_root_price - 1) * root_loss
                congestion_margin = (
                    mu * average_decoration + cardinality_slack - congestion_charge
                )
                if noncommon_penalty > congestion_charge:
                    raise AssertionError("staged Lmax congestion misses PXC63 penalty")
                transport_surplus = sum(
                    (
                        root_prices[player] * root_loss
                        - (z[player] - x[player])
                        for player in gainers
                        if player != omitted_maximum_gainer
                    ),
                    F(0),
                )
                decomposed_transport_surplus = sum(
                    (
                        root_certificates[player]["surplus"]
                        for player in gainers
                        if player != omitted_maximum_gainer
                    ),
                    F(0),
                )
                if transport_surplus != decomposed_transport_surplus:
                    raise AssertionError("aggregate Lmax transport surplus changed")
                positive_reverse_rows = []
                positive_cross_gainer_pins = []
                for player, certificate in root_certificates.items():
                    if player == omitted_maximum_gainer:
                        continue
                    for term in certificate["reverse_terms"]:
                        if term["payment"] <= 0:
                            continue
                        coalition = term["coalition"]
                        missing_gainers = sum(
                            not (coalition >> gainer & 1) for gainer in gainers
                        )
                        if not (coalition >> root & 1):
                            pattern = "root_free"
                        elif missing_gainers == 0:
                            pattern = "rooted_all_gainers"
                        elif missing_gainers == 1:
                            pattern = "rooted_costar"
                        else:
                            pattern = "rooted_multiomission"
                        positive_reverse_rows.append(
                            {
                                "target": player,
                                "coalition": coalition,
                                "payment": term["payment"],
                                "root_pattern": pattern,
                            }
                        )
                    for term in certificate["pin_terms"]:
                        if term["player"] != root and term["payment"] > 0:
                            positive_cross_gainer_pins.append(
                                {
                                    "target": player,
                                    "source": term["player"],
                                    "payment": term["payment"],
                                    "stage_side": term["stage_side"],
                                }
                            )
                mixed_congestion_margin = congestion_margin + transport_surplus
                if mixed_congestion_margin != selection_free_floor - target:
                    raise AssertionError("mixed Lmin/Lmax congestion cancellation failed")
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
                    "lmax_minimum_root_prices": (
                        None
                        if not ordered
                        else {
                            str(player): str(price)
                            for player, price in root_prices.items()
                        }
                    ),
                    "lmax_aggregate_root_price_excluding_max_gain": (
                        None if not ordered else str(aggregate_root_price)
                    ),
                    "lmax_omitted_maximum_gainer": (
                        None if not ordered else omitted_maximum_gainer
                    ),
                    "lmax_transport_surplus": (
                        None if not ordered else str(transport_surplus)
                    ),
                    "lmax_transport_certificates": (
                        None
                        if not ordered
                        else {
                            str(player): {
                                "price": str(certificate["price"]),
                                "surplus": str(certificate["surplus"]),
                                "reverse_terms": [
                                    {
                                        key: (
                                            value if key == "coalition" else str(value)
                                        )
                                        for key, value in term.items()
                                    }
                                    for term in certificate["reverse_terms"]
                                ],
                                "pin_terms": [
                                    {
                                        key: (
                                            value
                                            if key in {"player", "stage_side"}
                                            else str(value)
                                        )
                                        for key, value in term.items()
                                    }
                                    for term in certificate["pin_terms"]
                                ],
                            }
                            for player, certificate in root_certificates.items()
                        }
                    ),
                    "lmax_transport_bundle_cover": (
                        None
                        if not ordered
                        else {
                            "omitted_maximum_gainer": transport_cover["omitted"],
                            "weights": {
                                str(player): str(weight)
                                for player, weight in transport_cover["weights"].items()
                            },
                            "gainer_loads": {
                                str(player): str(load)
                                for player, load in transport_cover["loads"].items()
                            },
                            "root_price": str(transport_cover["root_price"]),
                            "reverse_credit": str(transport_cover["reverse_credit"]),
                            "net_cost": str(transport_cover["net_cost"]),
                            "overcoverage_cost": str(
                                transport_cover["net_cost"]
                                - actual_nonomitted_gain
                            ),
                            "target_margin": str(transport_cover_margin),
                            "closes_target": transport_cover_margin >= 0,
                        }
                    ),
                    "lmax_root_price_bundle_cover": (
                        None
                        if not ordered
                        else {
                            "omitted_maximum_gainer": root_price_cover["omitted"],
                            "weights": {
                                str(player): str(weight)
                                for player, weight in root_price_cover["weights"].items()
                            },
                            "gainer_loads": {
                                str(player): str(load)
                                for player, load in root_price_cover["loads"].items()
                            },
                            "root_price": str(root_price_cover["root_price"]),
                            "reverse_credit": str(root_price_cover["reverse_credit"]),
                            "net_cost": str(root_price_cover["net_cost"]),
                            "dual_prices": {
                                str(player): str(price)
                                for player, price in root_price_cover[
                                    "dual_prices"
                                ].items()
                            },
                            "target_margin_without_reverse_credit": str(
                                root_price_cover_margin
                            ),
                            "closes_target_without_reverse_credit": (
                                root_price_cover_margin >= 0
                            ),
                            "dual_rooted_separator_rows": {
                                str(player): [
                                    {
                                        key: (
                                            value if key == "coalition" else str(value)
                                        )
                                        for key, value in term.items()
                                    }
                                    for term in rows
                                ]
                                for player, rows in dual_separator_rows.items()
                            },
                        }
                    ),
                    "lmax_positive_reverse_rows": (
                        None
                        if not ordered
                        else [
                            {
                                key: (
                                    value
                                    if key in {"target", "coalition", "root_pattern"}
                                    else str(value)
                                )
                                for key, value in term.items()
                            }
                            for term in positive_reverse_rows
                        ]
                    ),
                    "lmax_positive_cross_gainer_pins": (
                        None
                        if not ordered
                        else [
                            {
                                key: (
                                    value
                                    if key in {"target", "source", "stage_side"}
                                    else str(value)
                                )
                                for key, value in term.items()
                            }
                            for term in positive_cross_gainer_pins
                        ]
                    ),
                    "lmax_congestion_charge": (
                        None if not ordered else str(congestion_charge)
                    ),
                    "lmax_congestion_target_margin": (
                        None if not ordered else str(congestion_margin)
                    ),
                    "lmax_congestion_closes_target": (
                        ordered and congestion_margin >= 0
                    ),
                    "mixed_lmin_lmax_congestion_margin": (
                        None if not ordered else str(mixed_congestion_margin)
                    ),
                    "sparse_lmax_support": list(overcover["support"]),
                    "sparse_common_positive_rows": [
                        positive["coalition"]
                        for positive in positive_rows
                        if positive["coalition"] in sparse_lmax_support
                    ],
                    "sparse_rooted_multiomission_rows": [
                        coalition
                        for coalition in overcover["support"]
                        if coalition >> root & 1
                        and sum(
                            not (coalition >> player & 1) for player in gainers
                        )
                        >= 2
                    ],
                    "sparse_reverse_payments": {
                        str(coalition): str(
                            coalition_sum(x, coalition) - coalition_sum(z, coalition)
                        )
                        for coalition in overcover["support"]
                        if coalition_sum(x, coalition) > coalition_sum(z, coalition)
                    },
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
    archive_lmax_aggregate_prices = tuple(
        F(row["lmax_aggregate_root_price_excluding_max_gain"])
        for row in archive_roots
        if row.get("lmax_aggregate_root_price_excluding_max_gain") is not None
    )
    archive_lmax_congestion_margins = tuple(
        F(row["lmax_congestion_target_margin"])
        for row in archive_roots
        if row.get("lmax_congestion_target_margin") is not None
    )
    archive_mixed_congestion_margins = tuple(
        F(row["mixed_lmin_lmax_congestion_margin"])
        for row in archive_roots
        if row.get("mixed_lmin_lmax_congestion_margin") is not None
    )
    archive_transport_cover_margins = tuple(
        F(row["lmax_transport_bundle_cover"]["target_margin"])
        for row in archive_roots
        if row.get("lmax_transport_bundle_cover") is not None
    )
    archive_transport_cover_overcosts = tuple(
        F(row["lmax_transport_bundle_cover"]["overcoverage_cost"])
        for row in archive_roots
        if row.get("lmax_transport_bundle_cover") is not None
    )
    archive_transport_cover_root_prices = tuple(
        F(row["lmax_transport_bundle_cover"]["root_price"])
        for row in archive_roots
        if row.get("lmax_transport_bundle_cover") is not None
    )
    archive_transport_cover_reverse_credits = tuple(
        F(row["lmax_transport_bundle_cover"]["reverse_credit"])
        for row in archive_roots
        if row.get("lmax_transport_bundle_cover") is not None
    )
    archive_root_price_cover_margins = tuple(
        F(
            row["lmax_root_price_bundle_cover"][
                "target_margin_without_reverse_credit"
            ]
        )
        for row in archive_roots
        if row.get("lmax_root_price_bundle_cover") is not None
    )
    archive_root_price_cover_prices = tuple(
        F(row["lmax_root_price_bundle_cover"]["root_price"])
        for row in archive_roots
        if row.get("lmax_root_price_bundle_cover") is not None
    )
    congestion_failure_records = [
        {
            "source": record["source"],
            "trail": record["trail"],
            "preclosure": record["preclosure"],
            "roots": [
                row
                for row in record["roots"]
                if row.get("lmax_congestion_target_margin") is not None
                and F(row["lmax_congestion_target_margin"]) < 0
            ],
        }
        for record in archive
        if any(
            row.get("lmax_congestion_target_margin") is not None
            and F(row["lmax_congestion_target_margin"]) < 0
            for row in record["roots"]
        )
    ]
    congestion_failure_roots = tuple(
        row for record in congestion_failure_records for row in record["roots"]
    )
    transport_overcoverage_records = [
        {
            "source": record["source"],
            "trail": record["trail"],
            "preclosure": record["preclosure"],
            "roots": [
                row
                for row in record["roots"]
                if row.get("lmax_transport_bundle_cover") is not None
                and F(
                    row["lmax_transport_bundle_cover"]["overcoverage_cost"]
                )
                > 0
            ],
        }
        for record in archive
        if any(
            row.get("lmax_transport_bundle_cover") is not None
            and F(row["lmax_transport_bundle_cover"]["overcoverage_cost"]) > 0
            for row in record["roots"]
        )
    ]

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
        "archive_ordered_saturated_with_sparse_common_row": sum(
            row.get("regime") == "saturated"
            and row.get("ordered", False)
            and bool(row.get("sparse_common_positive_rows"))
            for row in archive_roots
        ),
        "archive_ordered_saturated_without_common_with_sparse_multiomission": sum(
            row.get("regime") == "saturated"
            and row.get("ordered", False)
            and not row.get("sparse_common_positive_rows")
            and bool(row.get("sparse_rooted_multiomission_rows"))
            for row in archive_roots
        ),
        "archive_ordered_saturated_with_nonroot_top_mass": sum(
            row.get("regime") == "saturated"
            and row.get("ordered", False)
            and F(row.get("lmax_top_payment", {}).get("nonroot_top_mass", 0)) > 0
            for row in archive_roots
        ),
        "archive_ordered_saturated_with_positive_top_surplus": sum(
            row.get("regime") == "saturated"
            and row.get("ordered", False)
            and F(row.get("lmax_top_payment", {}).get("surplus", 0)) > 0
            for row in archive_roots
        ),
        "archive_lmax_aggregate_root_price_at_most_one": sum(
            price <= 1 for price in archive_lmax_aggregate_prices
        ),
        "archive_lmax_aggregate_root_price_minimum": str(
            min(archive_lmax_aggregate_prices)
        ),
        "archive_lmax_aggregate_root_price_maximum": str(
            max(archive_lmax_aggregate_prices)
        ),
        "archive_lmax_congestion_closing": sum(
            margin >= 0 for margin in archive_lmax_congestion_margins
        ),
        "archive_lmax_congestion_minimum_margin": str(
            min(archive_lmax_congestion_margins)
        ),
        "archive_mixed_congestion_closing": sum(
            margin >= 0 for margin in archive_mixed_congestion_margins
        ),
        "archive_mixed_congestion_minimum_margin": str(
            min(archive_mixed_congestion_margins)
        ),
        "archive_transport_bundle_cover_closing": sum(
            margin >= 0 for margin in archive_transport_cover_margins
        ),
        "archive_transport_bundle_cover_minimum_margin": str(
            min(archive_transport_cover_margins)
        ),
        "archive_transport_bundle_cover_exact_demand": sum(
            overcost == 0 for overcost in archive_transport_cover_overcosts
        ),
        "archive_transport_bundle_cover_maximum_overcost": str(
            max(archive_transport_cover_overcosts)
        ),
        "archive_transport_bundle_cover_root_price_at_most_one": sum(
            price <= 1 for price in archive_transport_cover_root_prices
        ),
        "archive_transport_bundle_cover_root_price_maximum": str(
            max(archive_transport_cover_root_prices)
        ),
        "archive_transport_bundle_cover_with_reverse_credit": sum(
            credit > 0 for credit in archive_transport_cover_reverse_credits
        ),
        "archive_root_price_bundle_cover_closing_without_reverse": sum(
            margin >= 0 for margin in archive_root_price_cover_margins
        ),
        "archive_root_price_bundle_cover_minimum_margin": str(
            min(archive_root_price_cover_margins)
        ),
        "archive_root_price_bundle_cover_at_most_one": sum(
            price <= 1 for price in archive_root_price_cover_prices
        ),
        "archive_root_price_bundle_cover_maximum": str(
            max(archive_root_price_cover_prices)
        ),
        "archive_raw_congestion_failure_roots": len(congestion_failure_roots),
        "archive_raw_failure_with_positive_reverse_row": sum(
            bool(row["lmax_positive_reverse_rows"])
            for row in congestion_failure_roots
        ),
        "archive_raw_failure_with_pure_cross_gainer_surplus": sum(
            not row["lmax_positive_reverse_rows"]
            for row in congestion_failure_roots
        ),
        "archive_raw_failure_with_root_free_reverse_row": sum(
            any(
                term["root_pattern"] == "root_free"
                for term in row["lmax_positive_reverse_rows"]
            )
            for row in congestion_failure_roots
        ),
        "archive_raw_failure_with_rooted_multiomission_reverse_row": sum(
            any(
                term["root_pattern"] == "rooted_multiomission"
                for term in row["lmax_positive_reverse_rows"]
            )
            for row in congestion_failure_roots
        ),
        "archive_raw_failure_with_sparse_common_costar": sum(
            bool(row["sparse_common_positive_rows"])
            for row in congestion_failure_roots
        ),
        "positive_residual_raw_congestion_failure_roots": sum(
            record["preclosure"] == "positive_residual"
            for record in congestion_failure_records
            for _row in record["roots"]
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
        "archive_ordered_saturated_with_sparse_common_row": 88,
        "archive_ordered_saturated_without_common_with_sparse_multiomission": 1,
        "archive_ordered_saturated_with_nonroot_top_mass": 89,
        "archive_ordered_saturated_with_positive_top_surplus": 2,
        "archive_lmax_aggregate_root_price_at_most_one": 77,
        "archive_lmax_aggregate_root_price_minimum": "1",
        "archive_lmax_aggregate_root_price_maximum": "3",
        "archive_lmax_congestion_closing": 79,
        "archive_lmax_congestion_minimum_margin": "-25/12",
        "archive_mixed_congestion_closing": 89,
        "archive_mixed_congestion_minimum_margin": "0",
        "archive_transport_bundle_cover_closing": 89,
        "archive_transport_bundle_cover_minimum_margin": "0",
        "archive_transport_bundle_cover_exact_demand": 88,
        "archive_transport_bundle_cover_maximum_overcost": "1/10",
        "archive_transport_bundle_cover_root_price_at_most_one": 88,
        "archive_transport_bundle_cover_root_price_maximum": "4/3",
        "archive_transport_bundle_cover_with_reverse_credit": 0,
        "archive_root_price_bundle_cover_closing_without_reverse": 89,
        "archive_root_price_bundle_cover_minimum_margin": "0",
        "archive_root_price_bundle_cover_at_most_one": 88,
        "archive_root_price_bundle_cover_maximum": "4/3",
        "archive_raw_congestion_failure_roots": 10,
        "archive_raw_failure_with_positive_reverse_row": 3,
        "archive_raw_failure_with_pure_cross_gainer_surplus": 7,
        "archive_raw_failure_with_root_free_reverse_row": 2,
        "archive_raw_failure_with_rooted_multiomission_reverse_row": 1,
        "archive_raw_failure_with_sparse_common_costar": 9,
        "positive_residual_raw_congestion_failure_roots": 4,
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
            "D-d_max-root_loss; normalized Lmax transports split that penalty "
            "exactly into root-price congestion minus nonnegative transport surplus"
        ),
        "counts": counts,
        "transport_bundle_overcoverage_records": transport_overcoverage_records,
        "raw_congestion_failure_records": congestion_failure_records,
        "positive_residual_rows": positive_residual,
        "fixed_controls": fixed,
        "relaxed_nonselector_control": relaxed_nonselector_control(),
        "scope": (
            "dimension-free counting theorem with exact finite scope audit; "
            "does not eliminate non-improving Hall obstructions, price the blocker, "
            "or prove the mixed congestion-surplus condition universally"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

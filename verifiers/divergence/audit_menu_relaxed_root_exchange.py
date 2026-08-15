#!/usr/bin/env python3
r"""Exact controls for the menu-relaxed root-exchange cover (PXC69).

PXC67 prices the dispersed gain through one chosen system of normalized
staged Lmax relations.  The same evaluation argument accepts any nonnegative
combination of full-menu Lmax-tight rows, so the best cover-type certificate
is itself an exact linear program on the full menu.  Its dual is a core
tangent direction at the Lmax selection that raises the root by one unit,
lowers gainers, and raises strict outsiders; the optimum is the exact
root-versus-gainer exchange rate of that tangent cone.  This driver solves
both sides exactly on the archived ordered saturated roots and the fixed
controls.  Finite counts calibrate the certificate; they are not a universal
selection theorem.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_carrier_separator_payment import full_tight_support  # noqa: E402
from audit_ceiling_root_gainer_exclusion import rooted_packing  # noqa: E402
from audit_costar_saturation_dichotomy import (  # noqa: E402
    coalition_sum,
    lower_envelope_case,
    minimum_lmax_root_certificate,
    minimum_lmax_transport_cover,
)
from audit_direct_ceiling_common_hinge_trichotomy import has_direct_packet  # noqa: E402
from audit_lmax_overcover import records  # noqa: E402
from exactlp import exact_linprog  # noqa: E402
from verify_labelled_branch_duals import CASES  # noqa: E402


def menu_relaxed_exchange(values, x, z, root, gainers, outsiders, omitted_star):
    """Solve the primal cover and dual exchange programs on the full menu."""
    n = len(x)
    full = (1 << n) - 1
    tight = tuple(
        coalition
        for coalition in range(1, full)
        if coalition_sum(z, coalition) == values[coalition]
    )
    if any(x[player] < z[player] for player in outsiders):
        raise AssertionError("an outsider escaped the ordered comparison")
    strict_outsiders = tuple(
        player for player in outsiders if x[player] > z[player]
    )
    root_loss = x[root] - z[root]
    if root_loss <= 0:
        raise AssertionError("ordered saturated root lost its positive Lmax loss")
    gains = {player: z[player] - x[player] for player in gainers}
    demand = sum(
        (gains[player] for player in gainers if player != omitted_star), F(0)
    )

    m = len(tight)
    c0 = m
    q0 = m + 1
    width = m + 1 + n
    equalities = []
    equality_rhs = []
    for coordinate in range(n):
        row = [F(0)] * width
        for index, coalition in enumerate(tight):
            row[index] = F((coalition >> coordinate) & 1)
        row[c0] = F(-1)
        row[q0 + coordinate] = F(-1)
        equalities.append(row)
        equality_rhs.append(F(0))
    inequalities = []
    rhs = []
    for index in range(m):
        row = [F(0)] * width
        row[index] = F(-1)
        inequalities.append(row)
        rhs.append(F(0))
    for player in gainers:
        row = [F(0)] * width
        row[q0 + player] = F(-1)
        inequalities.append(row)
        rhs.append(F(0) if player == omitted_star else F(-1))
    for player in strict_outsiders:
        row = [F(0)] * width
        row[q0 + player] = F(1)
        inequalities.append(row)
        rhs.append(F(0))
    objective = [F(0)] * width
    objective[q0 + root] = F(1)
    status, tau, solution = exact_linprog(
        objective, inequalities, rhs, equalities, equality_rhs
    )
    if status != "optimal":
        raise AssertionError("menu-relaxed cover did not optimize")

    multipliers = solution[:m]
    ambient = solution[c0]
    coefficients = solution[q0 : q0 + n]
    if any(value < 0 for value in multipliers):
        raise AssertionError("menu-relaxed cover has a negative row multiplier")
    for coordinate in range(n):
        left = sum(
            (
                multipliers[index]
                for index, coalition in enumerate(tight)
                if coalition >> coordinate & 1
            ),
            F(0),
        )
        if left != ambient + coefficients[coordinate]:
            raise AssertionError("menu-relaxed cover coordinate identity failed")
    for player in gainers:
        floor = F(0) if player == omitted_star else F(1)
        if coefficients[player] < floor:
            raise AssertionError("menu-relaxed cover misses a demanded gainer")
    if any(coefficients[player] > 0 for player in strict_outsiders):
        raise AssertionError("menu-relaxed cover pays a strict outsider forward")
    if coefficients[root] != tau:
        raise AssertionError("menu-relaxed root price disagreed with the optimum")

    reverse_payment = sum(
        (
            multipliers[index]
            * (coalition_sum(x, coalition) - coalition_sum(z, coalition))
            for index, coalition in enumerate(tight)
        ),
        F(0),
    )
    if any(
        multipliers[index]
        and coalition_sum(x, coalition) < coalition_sum(z, coalition)
        for index, coalition in enumerate(tight)
    ):
        raise AssertionError("a used menu row lost its nonnegative reverse slack")
    evaluated = (
        tau * root_loss
        - sum((coefficients[player] * gains[player] for player in gainers), F(0))
        + sum(
            (
                coefficients[player] * (x[player] - z[player])
                for player in strict_outsiders
            ),
            F(0),
        )
    )
    if reverse_payment != evaluated or reverse_payment < 0:
        raise AssertionError("menu-relaxed evaluation identity failed")
    if demand > tau * root_loss:
        raise AssertionError("menu-relaxed cover underprices the dispersed gain")

    tied_outsiders = tuple(
        player for player in outsiders if player not in strict_outsiders
    )
    dual_equalities = []
    dual_equality_rhs = []
    row = [F(1)] * n
    dual_equalities.append(row)
    dual_equality_rhs.append(F(0))
    row = [F(0)] * n
    row[root] = F(1)
    dual_equalities.append(row)
    dual_equality_rhs.append(F(-1))
    for player in tied_outsiders:
        row = [F(0)] * n
        row[player] = F(1)
        dual_equalities.append(row)
        dual_equality_rhs.append(F(0))
    dual_inequalities = []
    dual_rhs = []
    for coalition in tight:
        dual_inequalities.append(
            [F((coalition >> coordinate) & 1) for coordinate in range(n)]
        )
        dual_rhs.append(F(0))
    for player in gainers:
        row = [F(0)] * n
        row[player] = F(-1)
        dual_inequalities.append(row)
        dual_rhs.append(F(0))
    for player in strict_outsiders:
        row = [F(0)] * n
        row[player] = F(1)
        dual_inequalities.append(row)
        dual_rhs.append(F(0))
    dual_objective = [F(0)] * n
    for player in gainers:
        if player != omitted_star:
            dual_objective[player] = F(-1)
    dual_status, dual_negative, direction = exact_linprog(
        dual_objective,
        dual_inequalities,
        dual_rhs,
        dual_equalities,
        dual_equality_rhs,
    )
    if dual_status != "optimal" or -dual_negative != tau:
        raise AssertionError("menu-relaxed strong duality failed")
    for coalition in tight:
        if coalition_sum(direction, coalition) > 0:
            raise AssertionError("exchange direction leaves the tangent cone")
    if sum(direction, F(0)) != 0 or direction[root] != -1:
        raise AssertionError("exchange direction lost its normalization")
    selector_direction = tuple(
        -(x[player] - z[player]) / root_loss for player in range(n)
    )
    return {
        "tight_menu_size": m,
        "root_price": tau,
        "demand": demand,
        "demand_ratio": demand / root_loss,
        "exchange_exact": tau * root_loss == demand,
        "reverse_payment": reverse_payment,
        "ambient": ambient,
        "support": [
            {"coalition": coalition, "multiplier": str(multipliers[index])}
            for index, coalition in enumerate(tight)
            if multipliers[index]
        ],
        "direction": [str(value) for value in direction],
        "direction_is_selector_pair": tuple(direction) == selector_direction,
    }


def ordered_saturated_roots(values, x, z):
    """Enumerate ordered saturated ceiling roots exactly as the PXC60 audit."""
    n = len(x)
    ceiling = max(z)
    gainers = tuple(player for player in range(n) if z[player] > x[player])
    gainer_set = set(gainers)
    support = tuple(full_tight_support(values, x))
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
        if any(len(players) >= 2 for players in omitted.values()):
            continue
        g = len(gainers)
        if g < 2 or nu != F(g, g - 1):
            continue
        outsiders = tuple(
            player
            for player in range(n)
            if player not in gainer_set and player != root
        )
        minimum_gainer = min(x[player] for player in gainers)
        ordered = all(x[root] >= x[player] for player in gainers) and all(
            minimum_gainer >= x[player] for player in outsiders
        )
        if not ordered:
            continue
        average_decoration = F(0)
        for coalition, weight in zip(rooted, weights):
            if not weight:
                continue
            average_decoration += weight * sum(
                (
                    x[player]
                    for player in outsiders
                    if coalition >> player & 1
                ),
                F(0),
            )
        answer.append((root, gainers, outsiders, average_decoration))
    return answer


def audit_root(values, x, z, root, gainers, outsiders, average_decoration):
    n = len(x)
    g = len(gainers)
    total = sum(x, F(0))
    root_loss = x[root] - z[root]
    gains = {player: z[player] - x[player] for player in gainers}
    maximum_gain = max(gains.values())
    maximum_gainers = tuple(
        player for player in gainers if gains[player] == maximum_gain
    )
    mu = F((g - 1) * n, g * (n - g))
    cardinality_slack = (F(n, g * (n - g)) - F(n, (n * n) // 4)) * total

    outsider_loss = sum((x[player] - z[player] for player in outsiders), F(0))
    if sum((x[player] - z[player] for player in range(n)), F(0)) != 0:
        raise AssertionError("selector pair lost efficiency")
    if outsider_loss + root_loss != sum(gains.values(), F(0)):
        raise AssertionError("root/outsider loss accounting failed")

    full = (1 << n) - 1
    total_gain = sum(gains.values(), F(0))
    strict_outsiders = tuple(
        player for player in outsiders if x[player] > z[player]
    )
    x_support = set(full_tight_support(values, x))
    aligned_rows = []
    for coalition in range(1, full):
        if coalition_sum(z, coalition) != values[coalition]:
            continue
        if not (coalition >> root & 1):
            continue
        if any(coalition >> player & 1 for player in strict_outsiders):
            continue
        for a_star in maximum_gainers:
            if coalition >> a_star & 1:
                continue
            if any(
                not (coalition >> player & 1)
                for player in gainers
                if player != a_star
            ):
                continue
            slack = coalition_sum(x, coalition) - coalition_sum(z, coalition)
            if slack != root_loss - (total_gain - gains[a_star]):
                raise AssertionError("aligned-row evaluation identity failed")
            if slack < 0:
                raise AssertionError("aligned row lost its core comparison")
            aligned_rows.append(
                {
                    "coalition": coalition,
                    "omitted": a_star,
                    "common": slack == 0,
                    "lmin_tight": coalition in x_support,
                }
            )
    if aligned_rows and total_gain - maximum_gain > root_loss:
        raise AssertionError("aligned row failed to price the dispersed gain")

    certificates = {
        player: minimum_lmax_root_certificate(values, x, z, player, root)
        for player in gainers
    }
    best = None
    for omitted_star in maximum_gainers:
        exchange = menu_relaxed_exchange(
            values, x, z, root, gainers, outsiders, omitted_star
        )
        canonical = minimum_lmax_transport_cover(
            certificates,
            gains,
            gainers,
            omitted_star,
            root_loss,
            objective_kind="root",
        )
        if exchange["root_price"] > canonical["root_price"]:
            raise AssertionError(
                "menu-relaxed cover exceeded the canonical staged cover"
            )
        row = {
            "omitted": omitted_star,
            "canonical_root_price": canonical["root_price"],
            **exchange,
        }
        if best is None or (row["root_price"], row["omitted"]) < (
            best["root_price"],
            best["omitted"],
        ):
            best = row
    tau = best["root_price"]
    margin = mu * average_decoration + cardinality_slack - (tau - 1) * root_loss
    return {
        "root": root,
        "gainer_count": g,
        "root_loss": str(root_loss),
        "maximum_gain": str(maximum_gain),
        "outsider_loss": str(outsider_loss),
        "unit_exchange_identity": outsider_loss == maximum_gain,
        "aligned_costar_rows": aligned_rows,
        "has_aligned_row": bool(aligned_rows),
        "has_common_aligned_row": any(row["common"] for row in aligned_rows),
        "has_lmin_tight_aligned_row": any(
            row["lmin_tight"] for row in aligned_rows
        ),
        "menu_root_price": str(tau),
        "canonical_root_price": str(best["canonical_root_price"]),
        "canonical_gap": str(best["canonical_root_price"] - tau),
        "demand_ratio": str(best["demand_ratio"]),
        "exchange_exact": best["exchange_exact"],
        "at_most_one": tau <= 1,
        "reverse_payment": str(best["reverse_payment"]),
        "direction_is_selector_pair": best["direction_is_selector_pair"],
        "direction": best["direction"],
        "support": best["support"],
        "target_margin": str(margin),
        "closes": margin >= 0,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    archive_rows = []
    for path in args.paths:
        payload = json.loads(path.read_text())
        for source, trail, values, x, z in records(payload, path):
            roots = ordered_saturated_roots(values, x, z)
            if not roots:
                continue
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
            for root, gainers, outsiders, average_decoration in roots:
                row = audit_root(
                    values, x, z, root, gainers, outsiders, average_decoration
                )
                row["source"] = source.name
                row["trail"] = trail
                row["preclosure"] = preclosure
                archive_rows.append(row)

    fixed_rows = []
    for case in CASES:
        values, x, z = lower_envelope_case(case)
        for root, gainers, outsiders, average_decoration in ordered_saturated_roots(
            values, x, z
        ):
            row = audit_root(
                values, x, z, root, gainers, outsiders, average_decoration
            )
            row["name"] = case["name"]
            fixed_rows.append(row)

    residual_rows = [
        row for row in archive_rows if row["preclosure"] == "positive_residual"
    ]
    summary = {
        "archive_ordered_saturated_roots": len(archive_rows),
        "archive_closing": sum(row["closes"] for row in archive_rows),
        "archive_minimum_target_margin": str(
            min((F(row["target_margin"]) for row in archive_rows), default=None)
        ),
        "archive_at_most_one": sum(row["at_most_one"] for row in archive_rows),
        "archive_maximum_root_price": str(
            max((F(row["menu_root_price"]) for row in archive_rows), default=None)
        ),
        "archive_exchange_exact": sum(row["exchange_exact"] for row in archive_rows),
        "archive_selector_pair_directions": sum(
            row["direction_is_selector_pair"] for row in archive_rows
        ),
        "archive_strict_canonical_gap": sum(
            F(row["canonical_gap"]) > 0 for row in archive_rows
        ),
        "archive_maximum_canonical_gap": str(
            max((F(row["canonical_gap"]) for row in archive_rows), default=None)
        ),
        "archive_positive_reverse_payment": sum(
            F(row["reverse_payment"]) > 0 for row in archive_rows
        ),
        "archive_unit_exchange_identity": sum(
            row["unit_exchange_identity"] for row in archive_rows
        ),
        "archive_aligned_row": sum(row["has_aligned_row"] for row in archive_rows),
        "archive_common_aligned_row": sum(
            row["has_common_aligned_row"] for row in archive_rows
        ),
        "archive_lmin_tight_aligned_row": sum(
            row["has_lmin_tight_aligned_row"] for row in archive_rows
        ),
        "residual_ordered_saturated_roots": len(residual_rows),
        "residual_closing": sum(row["closes"] for row in residual_rows),
        "residual_at_most_one": sum(row["at_most_one"] for row in residual_rows),
        "fixed_ordered_saturated_roots": len(fixed_rows),
        "fixed_rows": [
            {
                "name": row["name"],
                "root": row["root"],
                "menu_root_price": row["menu_root_price"],
                "target_margin": row["target_margin"],
                "exchange_exact": row["exchange_exact"],
                "unit_exchange_identity": row["unit_exchange_identity"],
                "has_common_aligned_row": row["has_common_aligned_row"],
                "has_lmin_tight_aligned_row": row["has_lmin_tight_aligned_row"],
                "closes": row["closes"],
            }
            for row in fixed_rows
        ],
    }

    expected = {
        "archive_ordered_saturated_roots": 89,
        "archive_closing": 89,
        "archive_minimum_target_margin": "0",
        "archive_at_most_one": 89,
        "archive_maximum_root_price": "1",
        "archive_exchange_exact": 89,
        "archive_strict_canonical_gap": 11,
        "archive_maximum_canonical_gap": "1",
        "archive_positive_reverse_payment": 0,
        "archive_unit_exchange_identity": 89,
        "archive_aligned_row": 89,
        "archive_common_aligned_row": 89,
        "archive_lmin_tight_aligned_row": 89,
        "residual_ordered_saturated_roots": 16,
        "residual_closing": 16,
        "residual_at_most_one": 16,
        "fixed_ordered_saturated_roots": 2,
    }
    for key, value in expected.items():
        if summary[key] != value:
            raise AssertionError(f"summary[{key!r}] = {summary[key]!r} != {value!r}")
    for row in summary["fixed_rows"]:
        if not (
            row["menu_root_price"] == "1"
            and row["target_margin"] == "0"
            and row["exchange_exact"]
            and row["unit_exchange_identity"]
            and row["has_common_aligned_row"]
            and row["has_lmin_tight_aligned_row"]
            and row["closes"]
        ):
            raise AssertionError(f"sharp orientation control drifted: {row!r}")

    payload = {
        "claim": (
            "menu-relaxed cover price bounds the dispersed gain and never "
            "exceeds the canonical staged bundle-cover price"
        ),
        "summary": summary,
        "archive_rows": archive_rows,
        "fixed_rows": fixed_rows,
    }
    rendered = json.dumps(payload, indent=2, default=str) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()

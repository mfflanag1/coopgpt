#!/usr/bin/env python3
r"""Exact controls for the saturated exchange boundary (PXC71).

The reverse packet inequality is dimension-free: core feasibility of the
Lmax selector on any Lmin-tight rooted co-star row omitting exactly gainer
`a` gives `z(C)-x(C)=(D-d_a)-ell_r-strictloss(C)>=0`.  Saturation supplies
rows of every type, so `D-d_max>=ell_r` and the menu-relaxed root price is
never below one.  This driver replays that identity on every positive-weight
maximum-gain packet row of the six-player archive and then replays two exact
seven-player lower-envelope controls that refute the unit-exchange bound,
universal aligned-row existence, menu exchange-exactness, and the universal
sufficiency of the menu-cover reserve condition (PXC69c), while both retain
the raw dispersed-gain reserve bound (PXC63b) and the hybrid target.
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
from audit_costar_saturation_dichotomy import coalition_sum  # noqa: E402
from audit_lmax_overcover import records  # noqa: E402
from audit_menu_relaxed_root_exchange import (  # noqa: E402
    audit_root,
    ordered_saturated_roots,
)
from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from certified_float_lp import certified_lp_min  # noqa: E402
from certified_leximin import leximin_core_certified  # noqa: E402
from leximin import leximax_core_exact, leximin_core_exact  # noqa: E402
from tugame import Game, exact_lp_min  # noqa: E402


WITNESSES = (
    {
        "name": "n7_symmetric_two_generator_exchange_boundary",
        "generators": ((2, 0, 6, 2, 0, 2, 0), (0, 4, 0, 0, 4, 0, 4)),
        "x": ("4/3", "4/3", "4", "4/3", "4/3", "4/3", "4/3"),
        "z": ("4/5", "12/5", "12/5", "4/5", "12/5", "4/5", "12/5"),
        "root": 2,
        "menu_root_price": "4/3",
        "exchange_exact": True,
        "pxc69c_margin": "9/5",
        "pxc63b_margin": "9/5",
        "overlap": "44/5",
    },
    {
        "name": "n7_three_generator_cover_reserve_failure",
        "generators": (
            (0, 7, 2, 0, 1, 2, 0),
            (4, 0, 0, 5, 0, 0, 3),
            (0, 11, 1, 0, 0, 0, 0),
        ),
        "x": ("2", "4", "1", "2", "1", "1", "1"),
        "z": ("14/5", "14/5", "3/5", "14/5", "3/5", "3/5", "9/5"),
        "root": 1,
        "menu_root_price": "2",
        "exchange_exact": False,
        "pxc69c_margin": "-37/60",
        "pxc63b_margin": "11/60",
        "overlap": "48/5",
    },
)


def certified_lp(objective, inequalities, rhs, equalities, equality_rhs):
    optimum, point, _info = certified_lp_min(
        objective, inequalities, rhs, equalities, equality_rhs
    )
    if optimum is None:
        optimum, point = exact_lp_min(
            objective, inequalities, rhs, equalities, equality_rhs
        )
    return optimum, point


def leximax_core_certified(game):
    """Exact Lmax via certified floating proposals with exact fallback."""
    n, grand, values = game.n, game.N, game.v
    fixed = {}

    def core_rows(width):
        rows, rhs = [], []
        for coalition in range(1, grand):
            row = [F(0)] * width
            for player in range(n):
                if coalition >> player & 1:
                    row[player] = F(-1)
            rows.append(row)
            rhs.append(-values[coalition])
        return rows, rhs

    def solve_ceiling(free):
        width = n + 1
        rows, rhs = core_rows(width)
        for player in free:
            row = [F(0)] * width
            row[player] = F(1)
            row[n] = F(-1)
            rows.append(row)
            rhs.append(F(0))
        equalities = [[F(1)] * n + [F(0)]]
        equality_rhs = [values[grand]]
        for player, value in fixed.items():
            row = [F(0)] * width
            row[player] = F(1)
            equalities.append(row)
            equality_rhs.append(value)
        objective = [F(0)] * width
        objective[n] = F(1)
        return certified_lp(objective, rows, rhs, equalities, equality_rhs)

    def min_player(player, free, ceiling):
        rows, rhs = core_rows(n)
        for other in free:
            row = [F(0)] * n
            row[other] = F(1)
            rows.append(row)
            rhs.append(ceiling)
        equalities = [[F(1)] * n]
        equality_rhs = [values[grand]]
        for other, value in fixed.items():
            row = [F(0)] * n
            row[other] = F(1)
            equalities.append(row)
            equality_rhs.append(value)
        objective = [F(0)] * n
        objective[player] = F(1)
        optimum, _ = certified_lp(objective, rows, rhs, equalities, equality_rhs)
        return optimum

    free = list(range(n))
    while free:
        optimum, _ = solve_ceiling(free)
        if optimum is None or optimum == "unbounded":
            raise AssertionError("certified Lmax stage did not optimize")
        pinned = [
            player
            for player in free
            if min_player(player, free, optimum) == optimum
        ]
        if not pinned:
            raise AssertionError("certified Lmax stage found no pinned player")
        for player in pinned:
            fixed[player] = optimum
            free.remove(player)
    return [fixed[player] for player in range(n)]


def reverse_identity_rows(values, x, z):
    """Replay the reverse packet identity on maximum-gain packet rows."""
    n = len(x)
    ceiling = max(z)
    gainers = tuple(player for player in range(n) if z[player] > x[player])
    gainer_set = set(gainers)
    support = tuple(full_tight_support(values, x))
    audited = []
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
        if not (
            all(x[root] >= x[player] for player in gainers)
            and all(minimum_gainer >= x[player] for player in outsiders)
        ):
            continue
        total_gain = sum((z[player] - x[player] for player in gainers), F(0))
        maximum_gain = max(z[player] - x[player] for player in gainers)
        root_loss = x[root] - z[root]
        if total_gain - maximum_gain < root_loss:
            raise AssertionError("reverse packet inequality failed")
        max_rows = 0
        aligned = 0
        for coalition, weight in zip(rooted, weights):
            if not weight:
                continue
            omitted_gainer = omitted[coalition][0]
            gain = z[omitted_gainer] - x[omitted_gainer]
            strict_loss = sum(
                (
                    x[player] - z[player]
                    for player in outsiders
                    if coalition >> player & 1
                ),
                F(0),
            )
            slack = coalition_sum(z, coalition) - coalition_sum(x, coalition)
            if slack != (total_gain - gain) - root_loss - strict_loss:
                raise AssertionError("reverse packet identity failed on a row")
            if slack < 0:
                raise AssertionError("packet row lost its Lmax core comparison")
            if gain != maximum_gain:
                continue
            max_rows += 1
            if slack == 0 and strict_loss == 0:
                aligned += 1
        audited.append(
            {
                "root": root,
                "maximum_type_rows": max_rows,
                "aligned_maximum_type_rows": aligned,
                "equality": total_gain - maximum_gain == root_loss,
            }
        )
    return audited


def witness_row(case):
    generators = tuple(
        tuple(F(value) for value in generator) for generator in case["generators"]
    )
    n = len(generators[0])
    totals = {sum(generator, F(0)) for generator in generators}
    if len(totals) != 1:
        raise AssertionError("witness generators lost their common total")
    for player in range(n):
        if min(generator[player] for generator in generators) != 0:
            raise AssertionError("witness lost singleton normalization")
    values = lower_envelope(generators)
    game = Game(n, list(values))
    x, _certificate = leximin_core_certified(game)
    if x is None:
        x = leximin_core_exact(game)
    z = leximax_core_certified(game)
    x = tuple(F(value) for value in x)
    z = tuple(F(value) for value in z)
    if x != tuple(F(value) for value in case["x"]):
        raise AssertionError("witness Lmin selector changed")
    if z != tuple(F(value) for value in case["z"]):
        raise AssertionError("witness Lmax selector changed")
    roots = ordered_saturated_roots(values, x, z)
    if len(roots) != 1 or roots[0][0] != case["root"]:
        raise AssertionError("witness ordered saturated root changed")
    root, gainers, outsiders, average_decoration = roots[0]
    row = audit_root(values, x, z, root, gainers, outsiders, average_decoration)
    if row["has_aligned_row"]:
        raise AssertionError("witness unexpectedly grew an aligned co-star row")
    if row["unit_exchange_identity"]:
        raise AssertionError("witness unexpectedly satisfies unit exchange")
    if row["menu_root_price"] != case["menu_root_price"]:
        raise AssertionError("witness menu-relaxed root price changed")
    if row["exchange_exact"] != case["exchange_exact"]:
        raise AssertionError("witness exchange-exactness changed")
    if F(row["menu_root_price"]) <= 1:
        raise AssertionError("witness no longer refutes the unit bound")
    if row["target_margin"] != case["pxc69c_margin"]:
        raise AssertionError("witness PXC69c margin changed")
    if (F(row["target_margin"]) >= 0) != (F(case["pxc69c_margin"]) >= 0):
        raise AssertionError("witness PXC69c verdict changed")

    n_players = len(x)
    g = len(gainers)
    total = sum(x, F(0))
    total_gain = sum((z[player] - x[player] for player in gainers), F(0))
    maximum_gain = max(z[player] - x[player] for player in gainers)
    root_loss = x[root] - z[root]
    penalty = total_gain - maximum_gain - root_loss
    if penalty <= 0:
        raise AssertionError("witness lost its strict reverse inequality")
    mu = F((g - 1) * n_players, g * (n_players - g))
    slack = (
        F(n_players, g * (n_players - g)) - F(n_players, (n_players**2) // 4)
    ) * total
    margin63 = mu * average_decoration + slack - penalty
    if str(margin63) != case["pxc63b_margin"] or margin63 < 0:
        raise AssertionError("witness PXC63b margin changed")
    overlap = sum((min(a, b) for a, b in zip(x, z)), F(0))
    target = F(n_players, (n_players**2) // 4) * total
    if str(overlap) != case["overlap"] or overlap < target:
        raise AssertionError("witness overlap or hybrid target changed")
    return {
        "name": case["name"],
        "generators": [
            [str(value) for value in generator] for generator in generators
        ],
        "x": [str(value) for value in x],
        "z": [str(value) for value in z],
        "root": root,
        "gainers": list(gainers),
        "menu_root_price": row["menu_root_price"],
        "demand_ratio": row["demand_ratio"],
        "exchange_exact": row["exchange_exact"],
        "reverse_penalty": str(penalty),
        "pxc69c_margin": row["target_margin"],
        "pxc63b_margin": str(margin63),
        "overlap": str(overlap),
        "hybrid_target": str(target),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    archive = []
    for path in args.paths:
        payload = json.loads(path.read_text())
        for source, trail, values, x, z in records(payload, path):
            for row in reverse_identity_rows(values, x, z):
                row["source"] = source.name
                row["trail"] = trail
                archive.append(row)

    witnesses = [witness_row(case) for case in WITNESSES]

    summary = {
        "archive_ordered_saturated_roots": len(archive),
        "archive_equality": sum(row["equality"] for row in archive),
        "archive_maximum_type_rows": sum(
            row["maximum_type_rows"] for row in archive
        ),
        "archive_aligned_maximum_type_rows": sum(
            row["aligned_maximum_type_rows"] for row in archive
        ),
        "witnesses": [
            {
                "name": row["name"],
                "menu_root_price": row["menu_root_price"],
                "pxc69c_margin": row["pxc69c_margin"],
                "pxc63b_margin": row["pxc63b_margin"],
            }
            for row in witnesses
        ],
    }
    expected = {
        "archive_ordered_saturated_roots": 89,
        "archive_equality": 89,
        "archive_maximum_type_rows": 202,
        "archive_aligned_maximum_type_rows": 202,
    }
    for key, value in expected.items():
        if summary[key] != value:
            raise AssertionError(f"summary[{key!r}] = {summary[key]!r} != {value!r}")

    payload = {
        "claim": (
            "reverse packet inequality holds archive-wide; the unit exchange "
            "bound, aligned-row existence, exchange-exactness, and universal "
            "PXC69c closure fail at seven players while PXC63b and the hybrid "
            "target hold on both controls"
        ),
        "summary": summary,
        "archive_rows": archive,
        "witnesses": witnesses,
    }
    rendered = json.dumps(payload, indent=2, default=str) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()

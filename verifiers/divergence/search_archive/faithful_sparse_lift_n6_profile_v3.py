#!/usr/bin/env python3
"""Exact constraint-profile search in the n=6 single-heavy s=2 cell.

The exhaustive cell is explicit: denominator-seven selector profiles

    x=(6,4,2,2,2,2), z=(t,t,s,s,o,o)/7,

with total 18, strict top/subtop/outsider order, and the three PXC88 staged
Lmin rows feasible.  For every such profile the driver tests the maximal
comparison-compatible z-row menu.  This is exhaustive only for that finite
profile/maximal-menu cell.  If a reserve+direct failure is promoted, every
strictly-positive extreme top cover of size at most n-2=4 is enumerated and
its exact minimal lift with the fixed complete staged certificate is audited.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
COOPGAMES = HERE.parents[3]
DIV = COOPGAMES / "verifiers" / "divergence"
sys.path[:0] = [str(COOPGAMES / "src"), str(DIV)]

from audit_direct_ceiling_common_hinge_trichotomy import has_direct_packet  # noqa: E402
from audit_menu_relaxed_root_exchange import ordered_saturated_roots  # noqa: E402
from audit_spectral_or_reserve import selectors as project_selectors  # noqa: E402
from exactlp import exact_linprog  # noqa: E402
from simplex import lp_max, lp_min  # noqa: E402


N = 6
FULL = (1 << N) - 1
TOTAL = F(18)
TARGET = F(2, 3)
X = tuple(F(q) for q in (6, 4, 2, 2, 2, 2))
R, H = 0, 1


def mask(*players: int) -> int:
    return sum(1 << player for player in players)


CX = {mask(0, 1, 2): F(12), mask(0, 1, 3): F(12), mask(0, 2, 3): F(10)}


def csum(point, coalition):
    return sum((point[i] for i in range(N) if coalition >> i & 1), F(0))


def coalition_minimum(constraints, coalition):
    aub, bub = [], []
    for row, bound in constraints.items():
        aub.append([-F(int(bool(row >> i & 1))) for i in range(N)])
        bub.append(-bound)
    for player in range(N):
        row = [F(0)] * N
        row[player] = -1
        aub.append(row); bub.append(F(0))
    objective = [F(int(bool(coalition >> i & 1))) for i in range(N)]
    status, value, _ = exact_linprog(objective, aub, bub, [[F(1)] * N], [TOTAL])
    if status != "optimal":
        raise AssertionError(("coalition LP", coalition, status))
    return value


def values(constraints):
    return tuple(coalition_minimum(constraints, row) for row in range(1 << N))


def selector(constraints, mode):
    pinned, free = {}, set(range(N))

    def base():
        rows, rhs = [], []
        total = [F(1)] * N + [F(0)]
        rows += [total, [-q for q in total]]; rhs += [TOTAL, -TOTAL]
        for coalition, bound in constraints.items():
            row = [-F(int(bool(coalition >> i & 1))) for i in range(N)] + [F(0)]
            rows.append(row); rhs.append(-bound)
        for player, bound in pinned.items():
            row = [F(0)] * (N + 1); row[player] = 1
            rows += [row, [-q for q in row]]; rhs += [bound, -bound]
        return rows, rhs

    while free:
        rows, rhs = base()
        for player in free:
            row = [F(0)] * (N + 1)
            row[player], row[N] = ((-1, 1) if mode == "min" else (1, -1))
            rows.append(row); rhs.append(F(0))
        objective = [F(0)] * (N + 1); objective[N] = 1
        level, _ = (lp_max(objective, rows, rhs) if mode == "min"
                    else lp_min(objective, rows, rhs))
        if isinstance(level, str): raise AssertionError((mode, level))
        rows, rhs = base()
        for player in free:
            row = [F(0)] * (N + 1); row[player] = -1 if mode == "min" else 1
            rows.append(row); rhs.append(-level if mode == "min" else level)
        newly = []
        for player in sorted(free):
            objective = [F(0)] * (N + 1); objective[player] = 1
            trial, _ = (lp_max(objective, rows, rhs) if mode == "min"
                        else lp_min(objective, rows, rhs))
            if trial == level: newly.append(player)
        if not newly: raise AssertionError(("no selector pin", mode, level))
        for player in newly: pinned[player] = level; free.remove(player)
    return tuple(pinned[i] for i in range(N))


def selectors(constraints):
    return selector(constraints, "min"), selector(constraints, "max")


def solve_unique(matrix, rhs, width):
    aug = [list(map(F, row)) + [F(bound)] for row, bound in zip(matrix, rhs)]
    pivots, cursor = [], 0
    for column in range(width):
        pivot = next((r for r in range(cursor, len(aug)) if aug[r][column]), None)
        if pivot is None: continue
        aug[cursor], aug[pivot] = aug[pivot], aug[cursor]
        scale = aug[cursor][column]; aug[cursor] = [q / scale for q in aug[cursor]]
        for r in range(len(aug)):
            if r != cursor and aug[r][column]:
                scale = aug[r][column]
                aug[r] = [a - scale * b for a, b in zip(aug[r], aug[cursor])]
        pivots.append(column); cursor += 1
    if any(not any(row[:width]) and row[width] for row in aug): return None
    if len(pivots) != width: return None
    answer = [F(0)] * width
    for r, column in enumerate(pivots): answer[column] = aug[r][width]
    return tuple(answer)


def cover(rows):
    matrix, rhs = [], []
    for player in range(2, N):
        matrix.append([*(int(bool(row >> player & 1)) for row in rows), -1]); rhs.append(0)
    matrix.append([*(int(bool(row & 1)) + int(bool(row & 2)) for row in rows), -2]); rhs.append(1)
    width = len(rows) + 1
    solution = solve_unique(matrix, rhs, width)
    if solution is None: return None
    weights, eta = solution[:-1], solution[-1]
    loads = tuple(sum((w for w, row in zip(weights, rows) if row >> i & 1), F(0)) for i in range(N))
    alpha = (loads[0] - eta, loads[1] - eta)
    if min(weights) <= 0 or eta < 0 or min(alpha) <= 0 or sum(alpha, F(0)) != 1: return None
    if loads != (eta + alpha[0], eta + alpha[1], eta, eta, eta, eta):
        raise AssertionError("cover exact replay failed")
    return weights, eta, alpha


_GLOBAL_COVERS = None


def global_covers():
    """Enumerate every labelled n=6 positive extreme cover through size four."""
    global _GLOBAL_COVERS
    if _GLOBAL_COVERS is not None:
        return _GLOBAL_COVERS
    proper = tuple(row for row in range(1, FULL) if row.bit_count() >= 2)
    answer = []
    for size in range(1, 5):
        for rows in itertools.combinations(proper, size):
            certificate = cover(rows)
            if certificate is not None:
                answer.append((rows, certificate))
    _GLOBAL_COVERS = tuple(answer)
    return _GLOBAL_COVERS


def all_covers(rows):
    allowed = set(rows)
    answer = [item for item in global_covers() if set(item[0]) <= allowed]
    counts = Counter(len(support) for support, _certificate in answer)
    return answer, dict(counts)


def reserve_margin(x, z, root, gainers, decoration):
    g = len(gainers); gain = sum((z[i] - x[i] for i in gainers), F(0))
    penalty = gain - max(z[i] - x[i] for i in gainers) - (x[root] - z[root])
    return F((g - 1) * N, g * (N - g)) * decoration + (F(N, g * (N - g)) - TARGET) * TOTAL - penalty


def fidelity_audit(constraints, game_values, z):
    tight = tuple(row for row in range(1, FULL) if csum(z, row) == game_values[row])
    covers, counts = all_covers(tight); statuses = Counter(); examples = {}
    for support, certificate in covers:
        lift = dict(CX); lift.update({row: csum(z, row) for row in support})
        singleton = tuple(coalition_minimum(lift, 1 << i) for i in range(N))
        if any(singleton): status = "singleton_loss"
        else:
            lx, lz = selectors(lift)
            status = "faithful" if lx == X and lz == z else "selector_loss"
            examples.setdefault(status, {"rows": list(support), "lmin": list(map(str, lx)), "lmax": list(map(str, lz))})
        statuses[status] += 1
    if not covers: raise AssertionError("promoted candidate has no positive extreme cover <=4")
    return {"tight_rows": len(tight), "cover_counts": counts, "statuses": dict(statuses),
            "faithful_exists": bool(statuses["faithful"]), "examples": examples}


def profiles():
    for top in range(1, 64):
        for sub in range(1, top):
            outsider = 63 - top - sub
            if not (0 <= outsider < sub): continue
            z = tuple(F(q, 7) for q in (top, top, sub, sub, outsider, outsider))
            if all(csum(z, row) >= bound for row, bound in CX.items()): yield (top, sub, outsider), z


def support_union_cell(profile_list):
    """Exhaust one-/two-extreme-cover menus on the central top grid."""
    stats = Counter(); promoted = []
    for numerators, z in profile_list:
        if not 29 <= numerators[0] <= 31:
            continue
        stats["profiles"] += 1
        compatible = tuple(row for row in range(1, FULL)
                           if row.bit_count() >= 2 and csum(X, row) >= csum(z, row))
        covers, counts = all_covers(compatible)
        stats["positive_extreme_covers"] += len(covers)
        for size, count in counts.items(): stats[f"covers_size_{size}"] += count
        supports = tuple(support for support, _ in covers)
        menus = {tuple(sorted(set(left) | set(right)))
                 for i, left in enumerate(supports)
                 for right in supports[i:]}
        menus.update(supports)
        stats["distinct_one_two_cover_menus"] += len(menus)
        for menu_rows in sorted(menus):
            constraints = dict(CX)
            constraints.update({row: csum(z, row) for row in menu_rows})
            if any(coalition_minimum(constraints, 1 << i) for i in range(N)):
                stats["singleton_failures"] += 1; continue
            x0, z0 = selectors(constraints)
            if x0 != X or z0 != z:
                stats["selector_failures"] += 1; continue
            stats["selector_matched"] += 1
            game_values = values(constraints)
            for root, gainers, outsiders, decoration in ordered_saturated_roots(game_values, x0, z0):
                if (root, gainers, outsiders) != (0, (1, 2, 3), (4, 5)): continue
                stats["ordered_single_heavy_s2"] += 1
                margin = reserve_margin(x0, z0, root, gainers, decoration)
                if margin >= 0: continue
                stats["reserve_failures"] += 1
                if has_direct_packet(x0, z0, TARGET): continue
                stats["reserve_direct_failures"] += 1
                promoted.append({
                    "profile_numerators": numerators, "menu_rows": list(menu_rows),
                    "reserve_margin": str(margin),
                    "fidelity": fidelity_audit(constraints, game_values, z0),
                })
    return {"stats": dict(stats), "promoted": promoted,
            "scope": "exhaustive for all one- and two-extreme-cover unions on profiles with top numerator 29..31"}


def calibrations():
    # Dimension-independent incidence normalization used in PXC88/PXC90.
    rows88, weights88 = (27, 39, 66), (F(1, 3),) * 3
    loads88 = tuple(sum((w for w, row in zip(weights88, rows88) if row >> i & 1), F(0)) for i in range(7))
    if loads88 != (F(2, 3), F(1), F(1, 3), F(1, 3), F(1, 3), F(1, 3), F(1, 3)):
        raise AssertionError("PXC88 incidence calibration failed")
    # PXC90 is seven-dimensional; replay its arithmetic directly here.
    rows, weights = (23, 27, 39, 75, 114), tuple(F(q, 7) for q in (1, 1, 2, 2, 1))
    loads = tuple(sum((w for w, row in zip(weights, rows) if row >> i & 1), F(0)) for i in range(7))
    if loads != (F(6, 7), F(1), F(3, 7), F(3, 7), F(3, 7), F(3, 7), F(3, 7)):
        raise AssertionError("PXC90 incidence calibration failed")
    def seven_values(constraints):
        answer = []
        for coalition in range(128):
            aub, bub = [], []
            for row, bound in constraints.items():
                aub.append([-F(int(bool(row >> i & 1))) for i in range(7)]); bub.append(-bound)
            for player in range(7):
                row = [F(0)] * 7; row[player] = -1; aub.append(row); bub.append(F(0))
            objective = [F(int(bool(coalition >> i & 1))) for i in range(7)]
            status, value, _ = exact_linprog(objective, aub, bub, [[F(1)] * 7], [F(20)])
            if status != "optimal": raise AssertionError(("7d calibration LP", status))
            answer.append(value)
        return tuple(answer)
    x7 = tuple(F(q) for q in (6, 4, 2, 2, 2, 2, 2))
    z88 = tuple(F(q, 7) for q in (29, 29, 27, 27, 4, 12, 12))
    z90 = tuple(F(q, 7) for q in (29, 29, 28, 28, 8, 9, 9))
    cx7 = {7: F(12), 11: F(12), 13: F(10)}
    c88 = dict(cx7); c88.update({row: sum((z88[i] for i in range(7) if row >> i & 1), F(0))
                                 for row in (27, 39, 66, 71, 75)})
    c90 = dict(cx7); c90.update({row: sum((z90[i] for i in range(7) if row >> i & 1), F(0))
                                 for row in (23, 27, 39, 75, 114)})
    observed88 = project_selectors(seven_values(c88), 7)
    observed90 = project_selectors(seven_values(c90), 7)
    if observed88 != (x7, z88) or observed90 != (x7, z90):
        raise AssertionError(("PXC selector calibration failed", observed88, observed90))
    return {"PXC88": {"selectors": [list(map(str, observed88[0])), list(map(str, observed88[1]))],
                       "weights": ["1/3"] * 3, "eta": "1/3", "alpha": ["1/3", "2/3"]},
            "PXC90": {"weights": ["1/7", "1/7", "2/7", "2/7", "1/7"],
                      "selectors": [list(map(str, observed90[0])), list(map(str, observed90[1]))],
                      "loads": list(map(str, loads))}}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path); args = parser.parse_args()
    cx_lmin, _ = selectors(CX)
    if cx_lmin != X: raise AssertionError(("Cx failed", cx_lmin))
    stats = Counter(); promoted = []
    profile_list = list(profiles())
    for numerators, z in profile_list:
        stats["profiles"] += 1
        menu = {row: csum(z, row) for row in range(1, FULL)
                if row.bit_count() >= 2 and csum(X, row) >= csum(z, row)}
        menu.update(CX); stats["maximal_menus"] += 1
        if any(coalition_minimum(menu, 1 << i) for i in range(N)):
            stats["singleton_failures"] += 1; continue
        x0, z0 = selectors(menu)
        if x0 != X or z0 != z: stats["selector_failures"] += 1; continue
        stats["selector_matched"] += 1
        game_values = values(menu)
        for root, gainers, outsiders, decoration in ordered_saturated_roots(game_values, x0, z0):
            if (root, gainers, outsiders) != (0, (1, 2, 3), (4, 5)): continue
            stats["ordered_single_heavy_s2"] += 1
            margin = reserve_margin(x0, z0, root, gainers, decoration)
            if margin >= 0: continue
            stats["reserve_failures"] += 1
            if has_direct_packet(x0, z0, TARGET): continue
            stats["reserve_direct_failures"] += 1
            audit = fidelity_audit(menu, game_values, z0)
            promoted.append({"profile_numerators": numerators, "reserve_margin": str(margin), "fidelity": audit})
    unions = support_union_cell(profile_list)
    payload = {"claim": "exact n=6 constraint-profile faithful-lift search",
               "complete_Cx": {str(k): str(v) for k, v in CX.items()},
               "calibrations": calibrations(),
               "maximal_menu_cell": {"stats": dict(stats), "promoted": promoted,
                    "scope": "all 186 denominator-seven symmetric-outsider profiles and their maximal comparison-compatible menu"},
               "one_two_cover_union_cell": unions,
               "scope": "two explicit exhaustive finite cells; not all exact games or all tight-row menus"}
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output: args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__": main()

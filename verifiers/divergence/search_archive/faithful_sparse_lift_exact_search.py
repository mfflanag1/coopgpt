#!/usr/bin/env python3
"""Bounded exact search for a failure of the faithful sparse-lift conjecture.

This is discovery code, not a proof of universal coverage.  It fixes the
seven-player PXC88 staged Lmin certificate, constructs richer exact games from
unions (or the maximal menu) of prescribed-z tight rows, and then independently
enumerates every strictly-positive extreme normalized two-top cover of support
at most five in the resulting game.  Each cover is minimally lifted together
with the complete staged Lmin certificate and both selectors are recomputed by
the project's solver-free rational simplex.

Floating point is used only to accelerate rational reconstruction of incidence
systems.  Every accepted solution is checked in exact arithmetic, and failed
reconstruction falls back to exact elimination.
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
import sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve()
COOPGAMES = HERE.parents[3]
DIV = COOPGAMES / "verifiers" / "divergence"
sys.path[:0] = [str(COOPGAMES / "src"), str(DIV)]

from exactlp import exact_linprog  # noqa: E402
from simplex import lp_max, lp_min  # noqa: E402


N = 7
FULL = (1 << N) - 1
TOTAL = F(20)
R, H, A, B = 0, 1, 2, 3
OUTSIDERS = (4, 5, 6)
X = tuple(F(q) for q in (6, 4, 2, 2, 2, 2, 2))
Z88 = tuple(F(q, 7) for q in (29, 29, 27, 27, 4, 12, 12))
Z90 = tuple(F(q, 7) for q in (29, 29, 28, 28, 8, 9, 9))


def mask(*players: int) -> int:
    return sum(1 << player for player in players)


LMIN_ROWS = {
    mask(R, H, A): F(12),
    mask(R, H, B): F(12),
    mask(R, A, B): F(10),
}
PXC88_ROWS = (mask(R, H, B, 4), mask(R, H, A, 5), mask(H, 6),
              mask(R, H, A, 6), mask(R, H, B, 6))
PXC90_ROWS = (23, 27, 39, 75, 114)


def csum(point: tuple[F, ...], coalition: int) -> F:
    return sum((point[i] for i in range(N) if coalition >> i & 1), F(0))


def solve_unique(matrix: list[list[F]], rhs: list[F], width: int):
    aug = [row[:] + [value] for row, value in zip(matrix, rhs)]
    pivot_row = 0
    pivots: list[int] = []
    for column in range(width):
        pivot = next((r for r in range(pivot_row, len(aug)) if aug[r][column]), None)
        if pivot is None:
            continue
        aug[pivot_row], aug[pivot] = aug[pivot], aug[pivot_row]
        scale = aug[pivot_row][column]
        aug[pivot_row] = [q / scale for q in aug[pivot_row]]
        for row in range(len(aug)):
            if row != pivot_row and aug[row][column]:
                scale = aug[row][column]
                aug[row] = [u - scale * v for u, v in zip(aug[row], aug[pivot_row])]
        pivots.append(column)
        pivot_row += 1
    if any(not any(row[:width]) and row[width] for row in aug):
        return None
    if len(pivots) != width:
        return None
    answer = [F(0)] * width
    for row, column in enumerate(pivots):
        answer[column] = aug[row][width]
    return tuple(answer)


def normalized_cover(rows: tuple[int, ...]):
    """Unique normalized cover on this support, or None if non-extreme."""
    integer_matrix = []
    integer_rhs = []
    for player in range(2, N):
        integer_matrix.append([
            *(int(bool(row >> player & 1)) for row in rows), -1
        ])
        integer_rhs.append(0)
    integer_matrix.append([
        *(int(bool(row & 1)) + int(bool(row & 2)) for row in rows), -2
    ])
    integer_rhs.append(1)
    width = len(rows) + 1

    approximate, _, rank, _ = np.linalg.lstsq(
        np.asarray(integer_matrix, dtype=float),
        np.asarray(integer_rhs, dtype=float), rcond=None,
    )
    solution = None
    if rank == width:
        trial = tuple(F(float(q)).limit_denominator(1_000_000) for q in approximate)
        if all(sum((F(a) * b for a, b in zip(row, trial)), F(0)) == F(target)
               for row, target in zip(integer_matrix, integer_rhs)):
            solution = trial
    if solution is None:
        solution = solve_unique(
            [[F(q) for q in row] for row in integer_matrix],
            [F(q) for q in integer_rhs], width,
        )
    if solution is None:
        return None
    weights, eta = solution[:-1], solution[-1]
    root_load = sum((w for w, row in zip(weights, rows) if row & 1), F(0))
    heavy_load = sum((w for w, row in zip(weights, rows) if row & 2), F(0))
    alpha = (root_load - eta, heavy_load - eta)
    if min(weights) <= 0 or eta < 0 or min(alpha) <= 0 or sum(alpha, F(0)) != 1:
        return None
    # Fail closed: independently replay all seven load equations.
    loads = tuple(sum((w for w, row in zip(weights, rows) if row >> i & 1), F(0))
                  for i in range(N))
    if loads != (eta + alpha[0], eta + alpha[1], eta, eta, eta, eta, eta):
        raise AssertionError("accepted cover failed its exact incidence replay")
    return weights, eta, alpha


def coalition_values(constraints: dict[int, F]) -> tuple[F, ...]:
    inequalities = []
    inequality_rhs = []
    for coalition, bound in constraints.items():
        inequalities.append([-F(int(bool(coalition >> i & 1))) for i in range(N)])
        inequality_rhs.append(-bound)
    for player in range(N):
        row = [F(0)] * N
        row[player] = -1
        inequalities.append(row)
        inequality_rhs.append(F(0))
    equality = [[F(1)] * N]
    values = []
    for coalition in range(1 << N):
        objective = [F(int(bool(coalition >> i & 1))) for i in range(N)]
        status, value, _ = exact_linprog(
            objective, inequalities, inequality_rhs, equality, [TOTAL]
        )
        if status != "optimal":
            raise AssertionError(("coalition LP failed", coalition, status))
        values.append(value)
    return tuple(values)


def selector_from_constraints(constraints: dict[int, F], mode: str) -> tuple[F, ...]:
    """Exact staged selector on the defining polytope, without redundant rows.

    The lower-envelope game's core equals this polytope: the defining rows are
    among its coalition inequalities, while every point of the polytope clears
    every coalition minimum.  Thus this is the same selector as a 127-row game
    replay, but materially faster and still solver-free/rational.
    """
    pinned: dict[int, F] = {}
    free = set(range(N))

    def base_rows(width: int):
        rows, bounds = [], []
        total = [F(1)] * N + [F(0)] * (width - N)
        rows.extend((total, [-q for q in total]))
        bounds.extend((TOTAL, -TOTAL))
        for coalition, bound in constraints.items():
            row = [-F(int(bool(coalition >> i & 1))) for i in range(N)]
            row += [F(0)] * (width - N)
            rows.append(row)
            bounds.append(-bound)
        for player, value in pinned.items():
            row = [F(0)] * width
            row[player] = 1
            rows.extend((row, [-q for q in row]))
            bounds.extend((value, -value))
        return rows, bounds

    while free:
        width = N + 1
        rows, bounds = base_rows(width)
        for player in free:
            row = [F(0)] * width
            if mode == "min":
                row[player], row[N] = -1, 1
            else:
                row[player], row[N] = 1, -1
            rows.append(row)
            bounds.append(F(0))
        objective = [F(0)] * width
        objective[N] = 1
        level, _ = (lp_max(objective, rows, bounds)
                    if mode == "min" else lp_min(objective, rows, bounds))
        if isinstance(level, str):
            raise AssertionError(("selector stage failed", mode, level))

        rows, bounds = base_rows(width)
        for player in free:
            row = [F(0)] * width
            row[player] = -1 if mode == "min" else 1
            rows.append(row)
            bounds.append(-level if mode == "min" else level)
        newly = []
        for player in sorted(free):
            objective = [F(0)] * width
            objective[player] = 1
            trial, _ = (lp_max(objective, rows, bounds)
                        if mode == "min" else lp_min(objective, rows, bounds))
            if isinstance(trial, str):
                raise AssertionError(("selector pin failed", mode, trial))
            if trial == level:
                newly.append(player)
        if not newly:
            raise AssertionError(("selector stage pinned nobody", mode, level))
        for player in newly:
            pinned[player] = level
            free.remove(player)
    return tuple(pinned[i] for i in range(N))


def selectors(constraints: dict[int, F]) -> tuple[tuple[F, ...], tuple[F, ...]]:
    return selector_from_constraints(constraints, "min"), selector_from_constraints(constraints, "max")


def direct_packet_exists(x: tuple[F, ...], z: tuple[F, ...]) -> bool:
    """Independent exact expansion of the target-reaching direct criterion."""
    target = F(7, 12)
    gainers = tuple(i for i in range(N) if z[i] > x[i])
    nongainers = tuple(i for i in range(N) if z[i] <= x[i])
    for h_size in range(1, len(nongainers)):
        for h_set in itertools.combinations(nongainers, h_size):
            p_set = tuple(i for i in nongainers if i not in h_set)
            p, g, h = len(p_set), len(gainers), len(h_set)
            q = g + h
            for packet_size in range(g):
                for packet in itertools.combinations(gainers, packet_size):
                    denominator = p + g - packet_size
                    if F(1) - F(g * p, q * denominator) < target:
                        continue
                    high_z = sum((z[i] for i in gainers + h_set), F(0)) / q
                    gain = sum((z[i] - x[i] for i in packet), F(0))
                    loss = sum((x[i] - z[i] for i in h_set), F(0))
                    budget = ((p - packet_size) * sum((x[i] for i in gainers), F(0))
                              - g * sum((x[i] for i in p_set), F(0))
                              + (p - packet_size) *
                              (sum((z[i] for i in h_set), F(0)) - h * high_z)
                              + g * packet_size * high_z) / g
                    if loss <= gain <= budget:
                        return True
    return False


def branch_ok(x: tuple[F, ...], z: tuple[F, ...]) -> bool:
    """The ordered saturated single-heavy s=2 reserve/direct-failing cell."""
    if x != X or not (z[R] == z[H] == max(z)):
        return False
    gainers = tuple(i for i in range(N) if z[i] > x[i])
    if gainers != (H, A, B) or not (z[A] == z[B] < z[R]):
        return False
    if not all(z[i] < z[A] for i in OUTSIDERS):
        return False
    gains = tuple(z[i] - x[i] for i in gainers)
    packet_margin = x[R] - z[R] - (sum(gains, F(0)) - max(gains))
    return packet_margin < 0 and not direct_packet_exists(x, z)


def incidence_key(row: int) -> tuple[int, ...]:
    return tuple((row >> i) & 1 for i in range(2, N)) + (
        int(bool(row & 1)) + int(bool(row & 2)),
    )


def enumerate_extreme_covers(rows: tuple[int, ...], max_support: int = 5):
    """Enumerate labelled extreme supports; duplicate incidence columns cannot coexist."""
    columns: dict[tuple[int, ...], list[int]] = {}
    for row in rows:
        if row.bit_count() >= 2:
            columns.setdefault(incidence_key(row), []).append(row)
    items = tuple(columns.values())
    answer = []
    by_size = Counter()
    for size in range(1, min(max_support, len(items)) + 1):
        for indices in itertools.combinations(range(len(items)), size):
            representatives = tuple(items[i][0] for i in indices)
            if normalized_cover(representatives) is None:
                continue
            for labelled in itertools.product(*(items[i] for i in indices)):
                support = tuple(sorted(labelled))
                cover = normalized_cover(support)
                if cover is not None:
                    answer.append((support, cover))
                    by_size[size] += 1
    return tuple(answer), dict(sorted(by_size.items()))


def lift_status(support: tuple[int, ...], z: tuple[F, ...]) -> dict:
    constraints = dict(LMIN_ROWS)
    constraints.update({row: csum(z, row) for row in support})
    values = coalition_values(constraints)
    singletons = tuple(values[1 << i] for i in range(N))
    if any(singletons):
        return {"status": "singleton", "singletons": [str(q) for q in singletons]}
    x2, z2 = selectors(constraints)
    faithful = x2 == X and z2 == z
    return {
        "status": "faithful" if faithful else "selector_loss",
        "preserves_lmin": x2 == X,
        "preserves_lmax": z2 == z,
        "lmin": [str(q) for q in x2],
        "lmax": [str(q) for q in z2],
    }


def audit_game(name: str, constraints: dict[int, F], require_branch: bool = True) -> dict:
    values = coalition_values(constraints)
    if any(values[1 << i] for i in range(N)):
        raise AssertionError((name, "candidate is not singleton-normalized"))
    x, z = selectors(constraints)
    if require_branch and not branch_ok(x, z):
        raise AssertionError((name, "candidate left requested branch", x, z))
    tight = tuple(row for row in range(1, FULL) if csum(z, row) == values[row])
    covers, counts = enumerate_extreme_covers(tight)
    statuses = Counter()
    faithful = []
    examples = {}
    for support, (weights, eta, alpha) in covers:
        result = lift_status(support, z)
        statuses[result["status"]] += 1
        examples.setdefault(result["status"], {"rows": list(support), **result})
        if result["status"] == "faithful":
            faithful.append({
                "rows": list(support), "weights": [str(q) for q in weights],
                "eta": str(eta), "alpha": [str(q) for q in alpha],
            })
    if not covers:
        raise AssertionError((name, "no strictly-positive extreme top cover <=5"))
    return {
        "name": name,
        "constraint_count": len(constraints),
        "lmin": [str(q) for q in x], "lmax": [str(q) for q in z],
        "branch_ok": branch_ok(x, z), "z_tight_rows": len(tight),
        "extreme_cover_counts": {str(k): v for k, v in counts.items()},
        "lift_status_counts": dict(sorted(statuses.items())),
        "faithful_exists": bool(faithful),
        "first_faithful": faithful[0] if faithful else None,
        "status_examples": examples,
    }


def calibration_constraints() -> tuple[tuple[str, dict[int, F]], ...]:
    p88 = dict(LMIN_ROWS)
    p88.update({row: csum(Z88, row) for row in PXC88_ROWS})
    p90 = dict(LMIN_ROWS)
    p90.update({row: csum(Z90, row) for row in PXC90_ROWS})
    return (("PXC88", p88), ("PXC90", p90))


def profile_grid(radius: int) -> tuple[tuple[F, ...], ...]:
    base = (29, 29, 28, 28, 8, 9, 9)
    profiles = set()
    for top_delta in range(-radius, radius + 1):
        for sub_delta in range(-radius, radius + 1):
            top, sub = 29 + top_delta, 28 + sub_delta
            remainder = 140 - 2 * top - 2 * sub
            for o4 in range(max(0, remainder - 2 * (sub - 1)), min(sub, remainder + 1)):
                for o5 in range(o4, sub):
                    o6 = remainder - o4 - o5
                    if o5 <= o6 < sub:
                        nums = (top, top, sub, sub, o4, o5, o6)
                        if sum(abs(a - b) for a, b in zip(nums, base)) <= 4 * radius:
                            profiles.add(tuple(F(q, 7) for q in nums))
    return tuple(sorted(profiles))


def candidate_search(rounds: int, radius: int, seed: int) -> dict:
    """Bounded menu-union/maximal-menu search; every promoted hit gets full audit."""
    rng = random.Random(seed)
    profiles = list(profile_grid(radius))
    rng.shuffle(profiles)
    tested = promoted = 0
    failures = []
    for prescribed_z in profiles[:rounds]:
        compatible = tuple(row for row in range(1, FULL)
                           if row.bit_count() >= 2 and csum(X, row) >= csum(prescribed_z, row))
        covers, _ = enumerate_extreme_covers(compatible)
        menus = [compatible]
        if covers:
            for _ in range(3):
                chosen = rng.sample(covers, min(3, len(covers)))
                menus.append(tuple(sorted({row for support, _ in chosen for row in support})))
        for menu_index, menu in enumerate(menus):
            tested += 1
            constraints = dict(LMIN_ROWS)
            constraints.update({row: csum(prescribed_z, row) for row in menu})
            values = coalition_values(constraints)
            if any(values[1 << i] for i in range(N)):
                continue
            x, z = selectors(constraints)
            if not branch_ok(x, z):
                continue
            promoted += 1
            report = audit_game(f"search-{tested}-menu-{menu_index}", constraints)
            if not report["faithful_exists"]:
                report["defining_constraints"] = {
                    str(row): str(bound) for row, bound in sorted(constraints.items())
                }
                failures.append(report)
                return {
                    "profiles_available": len(profiles), "menus_tested": tested,
                    "branch_candidates": promoted, "counterexamples": failures,
                }
    return {
        "profiles_available": len(profiles), "menus_tested": tested,
        "branch_candidates": promoted, "counterexamples": failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=0,
                        help="number of nearby prescribed profiles (each has four menus)")
    parser.add_argument("--radius", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20260821)
    parser.add_argument("--calibrations-only", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    certificate_lmin, _ = selectors(dict(LMIN_ROWS))
    if certificate_lmin != X:
        raise AssertionError("the three-row staged certificate no longer pins Lmin")

    calibrations = [audit_game(name, constraints) for name, constraints in calibration_constraints()]
    expected = {"PXC88": False, "PXC90": True}
    if any(result["faithful_exists"] != expected[result["name"]]
           for result in calibrations):
        raise AssertionError("PXC88/PXC90 exact calibration outcome changed")
    search = None if args.calibrations_only else candidate_search(args.rounds, args.radius, args.seed)
    calibration_failures = [result for result in calibrations if not result["faithful_exists"]]
    payload = {
        "claim": "bounded exact faithful sparse-lift falsification search",
        "complete_staged_lmin_certificate": {
            "rows": {str(row): str(bound) for row, bound in sorted(LMIN_ROWS.items())},
            "pins_lmin": [str(q) for q in certificate_lmin],
        },
        "calibrations": calibrations,
        "search": search,
        "counterexample_found": bool(calibration_failures or (search and search["counterexamples"])),
        "counterexample_note": (
            "With the three chosen staged Lmin rows stated in the PXC91 scope, "
            "PXC88 itself has no faithful strict-positive extreme support <=5. "
            "Thus it is not a positive faithful-lift calibration; PXC90 is."
        ),
        "scope": (
            "exact exhaustive support audit (sizes <=5) within each tested game; "
            "bounded nearby-profile/menu construction search only, not universal coverage"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

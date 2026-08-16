#!/usr/bin/env python3
"""Hill-climb the combined packet/spectral failure margin.

Objective at a generator tuple: the maximum over ordered saturated ceiling
roots of min(packet violation, spectral deficit), where
packet violation = penalty - mu*A_rho - slack and
spectral deficit = target_ratio - sharpened_spectral_bound_ratio (times T).
A positive value refutes the spectral-or-reserve alternative.
Secondary log: any divergent game with overlap below the hybrid target.
"""
import json
import random
import sys
import time
from fractions import Fraction as F
from pathlib import Path

REPO = Path("/private/tmp/coop-hybrid-20260812/coopgames")
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "verifiers" / "divergence"))

from tugame import Game  # noqa: E402
from certified_leximin import leximin_core_certified  # noqa: E402
from leximin import leximin_core_exact  # noqa: E402
from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from audit_menu_relaxed_root_exchange import ordered_saturated_roots  # noqa: E402
from audit_spectral_label_currency import spectral_decomposition  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from design_search_aligned_row import leximax_core_certified  # noqa: E402


CACHE = {}


def evaluate(generators):
    if generators in CACHE:
        return CACHE[generators]
    n = len(generators[0])
    if any(min(g[p] for g in generators) != 0 for p in range(n)):
        CACHE[generators] = None
        return None
    values = lower_envelope(tuple(tuple(F(q) for q in g) for g in generators))
    game = Game(n, list(values))
    x, _ = leximin_core_certified(game)
    if x is None:
        x = leximin_core_exact(game)
    z = leximax_core_certified(game)
    if x is None or z is None:
        CACHE[generators] = None
        return None
    x = tuple(F(q) for q in x)
    z = tuple(F(q) for q in z)
    if x == z:
        CACHE[generators] = None
        return None
    T = sum(x, F(0))
    target = F(n, (n * n) // 4) * T
    overlap = sum(min(a, b) for a, b in zip(x, z))
    if overlap < target:
        print("TARGET VIOLATION:", generators, [str(q) for q in x],
              [str(q) for q in z], "O", overlap, "target", target, flush=True)
    try:
        roots = ordered_saturated_roots(values, x, z)
    except AssertionError:
        CACHE[generators] = None
        return None
    if not roots:
        CACHE[generators] = None
        return None
    try:
        spec = spectral_decomposition("h", values, x, z)
        spectral_deficit = (
            F(spec["target_ratio"]) - F(spec["sharpened_spectral_bound_ratio"])
        ) * T
    except AssertionError:
        spectral_deficit = F(10**6)
    best = None
    for root, gainers, outsiders, decoration in roots:
        g = len(gainers)
        D = sum(z[p] - x[p] for p in gainers)
        dmax = max(z[p] - x[p] for p in gainers)
        ell = x[root] - z[root]
        penalty = D - dmax - ell
        mu = F((g - 1) * n, g * (n - g))
        slack = (F(n, g * (n - g)) - F(n, (n * n) // 4)) * T
        packet_violation = penalty - mu * decoration - slack
        value = min(packet_violation, spectral_deficit)
        if best is None or value > best[0]:
            best = (value, packet_violation, spectral_deficit, root, x, z)
    CACHE[generators] = best
    return best


def neighbors(generators, rng):
    n = len(generators[0])
    moves = []
    for gi in range(len(generators)):
        for i in range(n):
            if generators[gi][i] < 1:
                continue
            for j in range(n):
                if i != j:
                    moves.append((gi, i, j))
    rng.shuffle(moves)
    for gi, i, j in moves:
        new = [list(g) for g in generators]
        new[gi][i] -= 1
        new[gi][j] += 1
        yield tuple(tuple(g) for g in new)


def climb(start, rng, budget):
    current = tuple(tuple(int(q) for q in g) for g in start)
    outcome = evaluate(current)
    best_value = outcome[0] if outcome else None
    evaluations = 0
    improved = True
    while improved and evaluations < budget:
        improved = False
        for candidate in neighbors(current, rng):
            if evaluations >= budget:
                break
            result = evaluate(candidate)
            evaluations += 1
            if result is None:
                continue
            if best_value is None or result[0] > best_value:
                best_value = result[0]
                current = candidate
                improved = True
                print(
                    f"improve combined={result[0]} packet={result[1]} "
                    f"spectral_deficit={result[2]} at {current}",
                    flush=True,
                )
                if result[0] > 0:
                    print("COMBINED COUNTEREXAMPLE:", current,
                          [str(q) for q in result[4]],
                          [str(q) for q in result[5]], flush=True)
                break
    return current, best_value, evaluations


def main():
    rng = random.Random(20260817)
    seeds = [
        ((2, 0, 7, 2, 0, 1, 0), (0, 4, 0, 0, 4, 0, 4)),
        ((6, 0, 3, 3, 0, 0, 0), (0, 1, 0, 0, 8, 1, 2)),
        ((0, 3, 0, 0, 0, 3, 6), (1, 0, 1, 2, 8, 0, 0)),
        ((8, 2, 1, 0, 0, 0, 1), (0, 0, 0, 3, 3, 6, 0)),
        ((1, 2, 0, 0, 0, 2, 7), (0, 0, 4, 4, 4, 0, 0)),
    ]
    start = time.time()
    for seed in seeds:
        current, value, used = climb(seed, rng, budget=900)
        print(
            f"seed done: best combined {value} after {used} evals "
            f"({time.time() - start:.0f}s) final {current}",
            flush=True,
        )


if __name__ == "__main__":
    main()

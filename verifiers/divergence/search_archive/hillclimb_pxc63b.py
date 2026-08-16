#!/usr/bin/env python3
"""Hill-climb the PXC63b violation margin over integer lower envelopes.

Objective at a generator tuple: the maximum over ordered saturated ceiling
roots of penalty - reserve, where penalty = D - d_max - ell_r and
reserve = mu*A_rho + cardinality slack.  A positive value refutes PXC63b.
Mutations move one unit between two coordinates of one generator, preserving
common totals; singleton normalization is enforced as a filter.
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

from tugame import Game, exact_lp_min  # noqa: E402
from certified_leximin import leximin_core_certified  # noqa: E402
from leximin import leximin_core_exact  # noqa: E402
from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from audit_menu_relaxed_root_exchange import ordered_saturated_roots  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from design_search_aligned_row import leximax_core_certified  # noqa: E402


CACHE = {}


def margin(generators):
    key = generators
    if key in CACHE:
        return CACHE[key]
    n = len(generators[0])
    if any(min(g[p] for g in generators) != 0 for p in range(n)):
        CACHE[key] = None
        return None
    values = lower_envelope(tuple(tuple(F(q) for q in g) for g in generators))
    game = Game(n, list(values))
    x, _ = leximin_core_certified(game)
    if x is None:
        x = leximin_core_exact(game)
    z = leximax_core_certified(game)
    if x is None or z is None:
        CACHE[key] = None
        return None
    x = tuple(F(q) for q in x)
    z = tuple(F(q) for q in z)
    if x == z:
        CACHE[key] = None
        return None
    try:
        roots = ordered_saturated_roots(values, x, z)
    except AssertionError:
        CACHE[key] = None
        return None
    best = None
    total = sum(x, F(0))
    for root, gainers, outsiders, decoration in roots:
        g = len(gainers)
        D = sum(z[p] - x[p] for p in gainers)
        dmax = max(z[p] - x[p] for p in gainers)
        ell = x[root] - z[root]
        penalty = D - dmax - ell
        mu = F((g - 1) * n, g * (n - g))
        slack = (F(n, g * (n - g)) - F(n, (n * n) // 4)) * total
        value = penalty - mu * decoration - slack
        if best is None or value > best[0]:
            best = (value, root, x, z)
    CACHE[key] = best
    return best


def neighbors(generators, rng):
    n = len(generators[0])
    moves = []
    for gi in range(len(generators)):
        for i in range(n):
            if generators[gi][i] < 1:
                continue
            for j in range(n):
                if i == j:
                    continue
                moves.append((gi, i, j))
    rng.shuffle(moves)
    for gi, i, j in moves:
        new = [list(g) for g in generators]
        new[gi][i] -= 1
        new[gi][j] += 1
        yield tuple(tuple(g) for g in new)


def climb(start, rng, budget, log):
    current = tuple(tuple(int(q) for q in g) for g in start)
    result = margin(current)
    best_value = result[0] if result else None
    evaluations = 0
    improved = True
    while improved and evaluations < budget:
        improved = False
        for candidate in neighbors(current, rng):
            if evaluations >= budget:
                break
            outcome = margin(candidate)
            evaluations += 1
            if outcome is None:
                continue
            if best_value is None or outcome[0] > best_value:
                best_value = outcome[0]
                current = candidate
                improved = True
                log.append(
                    {
                        "generators": [list(g) for g in current],
                        "margin": str(outcome[0]),
                        "root": outcome[1],
                        "x": [str(q) for q in outcome[2]],
                        "z": [str(q) for q in outcome[3]],
                    }
                )
                print(
                    f"improve margin={outcome[0]} at {current}",
                    flush=True,
                )
                break
    return current, best_value, evaluations


def main():
    rng = random.Random(20260816)
    seeds = [
        ((0, 7, 2, 0, 1, 2, 0), (4, 0, 0, 5, 0, 0, 3), (0, 11, 1, 0, 0, 0, 0)),
        ((2, 0, 6, 2, 0, 2, 0), (0, 4, 0, 0, 4, 0, 4)),
    ]
    log = []
    start = time.time()
    for seed in seeds:
        current, value, used = climb(seed, rng, budget=700, log=log)
        print(
            f"seed done: best margin {value} after {used} evals "
            f"({time.time() - start:.0f}s)",
            flush=True,
        )
        print("final:", current, flush=True)
    Path("hillclimb_pxc63b_log.json").write_text(json.dumps(log, indent=2))


if __name__ == "__main__":
    main()

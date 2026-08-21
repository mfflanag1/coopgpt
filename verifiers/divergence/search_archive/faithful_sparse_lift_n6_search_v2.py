#!/usr/bin/env python3
"""Corrected exact n=6 search for the faithful sparse-lift frontier.

At n=6 the s=2 branch has three gainers and two outsiders.  This driver
first replays that predicate on both pinned six-player archives, then scans a
symmetry-reduced two-block lower-envelope grid and seeded multi-generator
perturbations.  It promotes only ordered saturated roots for which the exact
packet reserve and the direct arm both fail.

This is bounded falsification evidence, never an all-games enumeration.
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
import sys
from fractions import Fraction as F
from pathlib import Path


HERE = Path(__file__).resolve()
COOPGAMES = HERE.parents[3]
DIV = COOPGAMES / "verifiers" / "divergence"
sys.path[:0] = [str(COOPGAMES / "src"), str(DIV)]

from audit_direct_ceiling_common_hinge_trichotomy import has_direct_packet  # noqa: E402
from audit_lmax_overcover import records  # noqa: E402
from audit_menu_relaxed_root_exchange import ordered_saturated_roots  # noqa: E402
from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from audit_spectral_or_reserve import selectors  # noqa: E402


N = 6
TARGET = F(2, 3)
ARCHIVES = (
    COOPGAMES / "verifiers" / "s6" / "harvest6_601.json",
    COOPGAMES / "verifiers" / "s6" / "harvest6_602.json",
)


def reserve_margin(x, z, root, gainers, decoration) -> F:
    g = len(gainers)
    gain = sum((z[i] - x[i] for i in gainers), F(0))
    penalty = gain - max(z[i] - x[i] for i in gainers) - (x[root] - z[root])
    mu = F((g - 1) * N, g * (N - g))
    slack = (F(N, g * (N - g)) - TARGET) * sum(x, F(0))
    return mu * decoration + slack - penalty


def single_heavy_profile(z, root, gainers, outsiders) -> bool:
    """Two-player ceiling: root plus one heavy gainer; equal two-player subtop."""
    ceiling = max(z)
    heavy = tuple(i for i in gainers if z[i] == ceiling)
    if z[root] != ceiling or len(heavy) != 1:
        return False
    subtop = tuple(i for i in gainers if i != heavy[0])
    return (len(subtop) == 2 and z[subtop[0]] == z[subtop[1]]
            and all(z[j] < z[subtop[0]] for j in outsiders))


def classify(values, x, z, provenance, stats, candidates) -> None:
    direct = None
    for root, gainers, outsiders, decoration in ordered_saturated_roots(values, x, z):
        stats["ordered_saturated_roots"] += 1
        if (len(gainers), len(outsiders)) != (3, 2):
            continue
        stats["g3_k2_roots"] += 1
        single_heavy = single_heavy_profile(z, root, gainers, outsiders)
        if single_heavy:
            stats["single_heavy_s2_roots"] += 1
        margin = reserve_margin(x, z, root, gainers, decoration)
        if margin >= 0:
            continue
        stats["g3_k2_reserve_failures"] += 1
        if not single_heavy:
            continue
        stats["single_heavy_reserve_failures"] += 1
        if direct is None:
            direct = has_direct_packet(x, z, TARGET)
        if direct:
            continue
        stats["single_heavy_reserve_and_direct_failures"] += 1
        candidates.append({
            "provenance": provenance, "root": root,
            "gainers": list(gainers), "outsiders": list(outsiders),
            "single_heavy_s2": True,
            "reserve_margin": str(margin),
            "lmin": [str(q) for q in x], "lmax": [str(q) for q in z],
        })


def replay_archives() -> dict:
    stats = {
        "selected_games": 0, "ordered_saturated_roots": 0,
        "g3_k2_roots": 0, "single_heavy_s2_roots": 0,
        "g3_k2_reserve_failures": 0, "single_heavy_reserve_failures": 0,
        "single_heavy_reserve_and_direct_failures": 0,
    }
    candidates = []
    for path in ARCHIVES:
        payload = json.loads(path.read_text())
        for source, trail, values, x, z in records(payload, path):
            stats["selected_games"] += 1
            classify(values, x, z, {"source": source.name, "trail": trail}, stats, candidates)
    # This calibration catches the prior g=2/k=3 transposition.
    if stats["g3_k2_roots"] != 35:
        raise AssertionError(("corrected n=6 s=2 archive count changed", stats))
    if stats["g3_k2_reserve_failures"] or candidates:
        raise AssertionError("pinned n=6 archive unexpectedly crossed the reserve gate")
    return {"stats": stats, "candidates": candidates}


def partitions3(total: int):
    for a in range(total, 0, -1):
        for b in range(min(a, total - a), 0, -1):
            c = total - a - b
            if 1 <= c <= b:
                yield (a, b, c)


def block_grid(total_max: int):
    """Symmetry-reduced two-generator (3-gainer)/(2-outsider) block grid."""
    for total in range(6, total_max + 1):
        for a in partitions3(total):
            for heavy in range(1, total + 1):
                remainder = total - heavy
                for w0 in range((remainder + 1) // 2, remainder + 1):
                    w = (w0, remainder - w0)
                    yield (
                        tuple(F(q) for q in (0, *a, 0, 0)),
                        tuple(F(q) for q in (heavy, 0, 0, 0, *w)),
                    )


def random_generators(rng: random.Random, total_max: int):
    total = rng.randint(6, total_max)
    count = rng.randint(3, 7)
    points = []
    # Cyclic two-zero schedule guarantees all singleton minima are zero.
    for index in range(count):
        zeros = {index % N, (index + count) % N}
        allowed = [i for i in range(N) if i not in zeros]
        point = [0] * N
        for _ in range(total):
            point[rng.choice(allowed)] += 1
        points.append(tuple(F(q) for q in point))
    if any(min(point[i] for point in points) for i in range(N)):
        return None
    return tuple(points)


def search(total_max: int, random_rounds: int, seed: int) -> dict:
    stats = {
        "games": 0, "block_grid_games": 0, "random_games": 0,
        "divergent_games": 0, "ordered_saturated_roots": 0,
        "g3_k2_roots": 0, "single_heavy_s2_roots": 0,
        "g3_k2_reserve_failures": 0, "single_heavy_reserve_failures": 0,
        "single_heavy_reserve_and_direct_failures": 0,
    }
    candidates = []

    def audit(generators, provenance):
        values = lower_envelope(generators)
        x, z = selectors(values, N)
        if x is None or z is None:
            return
        x, z = tuple(F(q) for q in x), tuple(F(q) for q in z)
        stats["games"] += 1
        if x == z:
            return
        stats["divergent_games"] += 1
        before = len(candidates)
        classify(values, x, z, provenance, stats, candidates)
        if len(candidates) > before:
            candidates[-1]["generators"] = [[str(q) for q in point] for point in generators]

    for index, game in enumerate(block_grid(total_max)):
        stats["block_grid_games"] += 1
        audit(game, {"family": "symmetry-reduced-two-block", "index": index})
    rng = random.Random(seed)
    for index in range(random_rounds):
        game = random_generators(rng, total_max)
        if game is None:
            continue
        stats["random_games"] += 1
        audit(game, {"family": "seeded-multigenerator", "round": index})
    return {"stats": stats, "candidates": candidates}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--total-max", type=int, default=14)
    parser.add_argument("--random-rounds", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=20260821)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    archive = replay_archives()
    designed = search(args.total_max, args.random_rounds, args.seed)
    if designed["candidates"]:
        raise AssertionError(
            "reserve+direct candidate reached: run complete staged-Cx extraction "
            "and exhaustive positive extreme-cover fidelity audit before reporting"
        )
    payload = {
        "claim": "corrected bounded exact n=6 faithful sparse-lift candidate search",
        "dimension_cell": {"n": 6, "s": 2, "gainers": 3, "outsiders": 2},
        "archive_calibration": archive,
        "designed_search": designed,
        "parameters": {
            "total_max": args.total_max, "random_rounds": args.random_rounds,
            "seed": args.seed,
        },
        "candidate_found": False,
        "fidelity_audits_run": 0,
        "scope": (
            "complete replay of the two pinned n=6 archives, exhaustive only for the "
            "stated symmetry-reduced two-block integer grid, plus a seeded bounded "
            "multi-generator campaign; not an exclusion over all six-player exact games"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

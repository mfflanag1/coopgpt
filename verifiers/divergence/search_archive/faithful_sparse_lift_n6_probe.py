#!/usr/bin/env python3
"""Bounded exact n=6 lower-envelope probe for the faithful-lift frontier.

The probe is deliberately a falsification search, not an n=6 exclusion.  It
samples singleton-normalized integer lower envelopes, recomputes both selectors
exactly, and isolates ordered saturated s=2,k=2 roots for which both the packet
reserve and the direct arm fail.  Such a root would be passed to the sparse
lift audit; in the pinned run no such root occurs.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from fractions import Fraction as F
from pathlib import Path


HERE = Path(__file__).resolve()
COOPGAMES = HERE.parents[3]
sys.path[:0] = [str(COOPGAMES / "src"), str(COOPGAMES / "verifiers" / "divergence")]

from audit_direct_ceiling_common_hinge_trichotomy import has_direct_packet  # noqa: E402
from audit_menu_relaxed_root_exchange import ordered_saturated_roots  # noqa: E402
from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from audit_spectral_or_reserve import selectors  # noqa: E402


N = 6
TARGET = F(2, 3)


def composition(rng: random.Random, total: int, zeros: tuple[int, ...]) -> tuple[F, ...]:
    point = [0] * N
    allowed = [i for i in range(N) if i not in zeros]
    for _ in range(total):
        point[rng.choice(allowed)] += 1
    return tuple(F(q) for q in point)


def generators(rng: random.Random, total: int, count: int):
    # A cyclic zero schedule guarantees singleton normalization exactly.
    answer = []
    for index in range(count):
        zeros = (index % N, (index + count) % N)
        answer.append(composition(rng, total, zeros))
    if any(min(point[i] for point in answer) != 0 for i in range(N)):
        return None
    return tuple(answer)


def root_reserve_margin(x, z, root, gainers, decoration) -> F:
    g = len(gainers)
    gain = sum((z[i] - x[i] for i in gainers), F(0))
    penalty = gain - max(z[i] - x[i] for i in gainers) - (x[root] - z[root])
    mu = F((g - 1) * N, g * (N - g))
    cardinality_slack = (F(N, g * (N - g)) - TARGET) * sum(x, F(0))
    return mu * decoration + cardinality_slack - penalty


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=300)
    parser.add_argument("--seed", type=int, default=20260821)
    parser.add_argument("--total-min", type=int, default=8)
    parser.add_argument("--total-max", type=int, default=18)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    stats = {
        "games": 0, "divergent": 0, "ordered_saturated_roots": 0,
        "s2_k2_roots": 0, "reserve_failures": 0,
        "reserve_and_direct_failures": 0,
    }
    candidates = []
    for round_index in range(args.rounds):
        count = rng.choice((3, 4, 5, 6))
        game_generators = generators(
            rng, rng.randint(args.total_min, args.total_max), count
        )
        if game_generators is None:
            continue
        values = lower_envelope(game_generators)
        x, z = selectors(values, N)
        if x is None or z is None:
            continue
        x, z = tuple(F(q) for q in x), tuple(F(q) for q in z)
        stats["games"] += 1
        if x == z:
            continue
        stats["divergent"] += 1
        direct = has_direct_packet(x, z, TARGET)
        for root, gainers, outsiders, decoration in ordered_saturated_roots(values, x, z):
            stats["ordered_saturated_roots"] += 1
            # Single-heavy s=2 means one heavy plus two sub-top gainers;
            # with n=6 the remaining outsider count is k=2.
            if len(gainers) != 3 or len(outsiders) != 2:
                continue
            stats["s2_k2_roots"] += 1
            margin = root_reserve_margin(x, z, root, gainers, decoration)
            if margin >= 0:
                continue
            stats["reserve_failures"] += 1
            if direct:
                continue
            stats["reserve_and_direct_failures"] += 1
            candidates.append({
                "round": round_index, "root": root,
                "gainers": list(gainers), "outsiders": list(outsiders),
                "reserve_margin": str(margin),
                "lmin": [str(q) for q in x], "lmax": [str(q) for q in z],
                "generators": [[str(q) for q in point] for point in game_generators],
                "sparse_lift_audit": "required; candidate gate reached",
            })
    payload = {
        "claim": "bounded exact n=6 lower-envelope faithful-lift candidate probe",
        "seed": args.seed, "rounds": args.rounds, "stats": stats,
        "candidates": candidates,
        "existing_evidence": (
            "the pinned exact n=6 archive has 89 ordered saturated roots and "
            "the reserve closes all 89; this is finite evidence, not a domain theorem"
        ),
        "scope": (
            "random integer envelopes with 3--6 generators and the stated total grid; "
            "absence of a candidate does not exclude n=6"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

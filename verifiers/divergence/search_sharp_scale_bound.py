#!/usr/bin/env python3
"""Exact falsification search for a first-stage selector scale bound.

For random singleton-normalized lower-envelope games, compute both staged
selectors exactly and test M <= (n-1) mu.  This is discovery evidence only:
passing samples do not prove the inequality, while one exact violating game
is a decisive falsifier and is printed with all generators.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXACTSEL = HERE / "search_archive" / "s7_frontier_20260826"
sys.path.insert(0, str(EXACTSEL))
from exactsel import analyze  # noqa: E402


def composition(total: int, parts: int, rng: random.Random) -> list[int]:
    cuts = sorted(rng.sample(range(total + parts - 1), parts - 1))
    bars = [-1, *cuts, total + parts - 1]
    return [bars[i + 1] - bars[i] - 1 for i in range(parts)]


def random_generators(
    n: int, generator_count: int, total: int, rng: random.Random
) -> list[list[int]]:
    # The first n rows force singleton normalization coordinate by coordinate.
    rows: list[list[int]] = []
    for zero in range(n):
        positive = composition(total, n - 1, rng)
        row = positive[:zero] + [0] + positive[zero:]
        rows.append(row)
    for _ in range(generator_count - n):
        rows.append(composition(total, n, rng))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260830)
    parser.add_argument("--trials", type=int, default=40)
    parser.add_argument("--n-min", type=int, default=5)
    parser.add_argument("--n-max", type=int, default=8)
    parser.add_argument("--total", type=int, default=24)
    parser.add_argument("--extra-generators", type=int, default=2)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    pxc116 = analyze([
        [0, 13, 1, 3, 0, 1],
        [12, 0, 0, 1, 1, 4],
        [12, 5, 0, 0, 0, 1],
        [4, 10, 1, 0, 0, 3],
        [11, 3, 0, 1, 0, 3],
        [3, 11, 1, 3, 0, 0],
    ], verbose=False)
    pxc116_mu = min(pxc116["x"])
    pxc116_ceiling = max(pxc116["z"])
    assert (pxc116_mu, pxc116_ceiling) == (Fraction(1, 2), Fraction(6))
    records = []
    worst = None
    violations = []
    for n in range(args.n_min, args.n_max + 1):
        for trial in range(args.trials):
            gens = random_generators(n, n + args.extra_generators, args.total, rng)
            result = analyze(gens, verbose=False)
            mu = min(result["x"])
            ceiling = max(result["z"])
            if mu == 0:
                status = "zero_floor"
                ratio = None
            else:
                ratio = ceiling / (n * mu)
                status = "violates_n_minus_1" if ceiling > (n - 1) * mu else "passes"
            record = {
                "n": n,
                "trial": trial,
                "mu": str(mu),
                "M": str(ceiling),
                "M_over_n_mu": None if ratio is None else str(ratio),
                "status": status,
            }
            records.append(record)
            if ratio is not None and (worst is None or ratio > worst[0]):
                worst = (ratio, gens, result, record)
            if status == "violates_n_minus_1":
                violations.append((gens, result, record))
                break
        if violations:
            break

    payload = {
        "claim_tested": "M <= (n-1) mu",
        "evidence_tier": "exact exploratory falsification search; null result is not proof",
        "seed": args.seed,
        "parameters": {
            "trials_per_n": args.trials,
            "n_min": args.n_min,
            "n_max": args.n_max,
            "total": args.total,
            "extra_generators": args.extra_generators,
        },
        "tested": len(records),
        "violations": len(violations),
        "negative_control": {
            "name": "PXC116",
            "purpose": "exact falsifier of M <= (n-1) mu",
            "n": 6,
            "mu": str(pxc116_mu),
            "M": str(pxc116_ceiling),
            "M_over_n_mu": str(pxc116_ceiling / (6 * pxc116_mu)),
            "Lmin": [str(q) for q in pxc116["x"]],
            "Lmax": [str(q) for q in pxc116["z"]],
        },
        "worst": None,
        "records": records,
    }
    if worst is not None:
        ratio, gens, result, record = worst
        payload["worst"] = {
            **record,
            "generators": gens,
            "Lmin": [str(q) for q in result["x"]],
            "Lmax": [str(q) for q in result["z"]],
            "overlap": str(result["O"]),
            "rho": str(result["rho"]),
        }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")
    if violations:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Seeded falsification search for unrestricted PXC91c at n=5,6.

Discovery uses certified selector routines for speed.  Games themselves are
exact lower envelopes of displayed integer allocations.  Any hit is only a
candidate until replayed by the solver-free independent verifier.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]
DIV = ROOT / "verifiers" / "divergence"
sys.path[:0] = [str(ROOT / "src"), str(DIV), str(HERE.parent)]

from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from audit_spectral_or_reserve import selectors  # noqa: E402
from unrestricted_pxc91c_exact_search import (  # noqa: E402
    audit_game, covers, csum, matrix_rank, selector_pair, tight_rows,
)


def random_allocation(rng, n, total, forced_zero):
    point = [0] * n
    allowed = [i for i in range(n) if i != forced_zero]
    for _ in range(total):
        point[rng.choice(allowed)] += 1
    return tuple(F(q) for q in point)


def capped_two_top_generators(rng, n, total, count):
    """Exact singleton witnesses with capped non-top coordinates."""
    caps = [total] * 2 + [rng.randint(1, max(1, total // 4)) for _ in range(n - 2)]
    answer = []
    for index in range(max(n, count)):
        forced_zero = index % n
        point = [0] * n
        for player in range(2, n):
            if player != forced_zero:
                point[player] = rng.randint(0, caps[player])
        residual = total - sum(point)
        if forced_zero == 0:
            point[1] = residual
        elif forced_zero == 1:
            point[0] = residual
        else:
            point[0] = rng.randint(0, residual)
            point[1] = residual - point[0]
        answer.append(tuple(F(q) for q in point))
    return tuple(answer)


def fast_lift(constraints, n, total):
    """Floating discovery replay; never sufficient to promote a hit."""
    aub = [] ; bub = []
    for mask, bound in constraints.items():
        aub.append([-float((mask >> i) & 1) for i in range(n)])
        bub.append(-float(bound))
    answer = []
    for mask in range(1 << n):
        objective = [float((mask >> i) & 1) for i in range(n)]
        result = linprog(objective, A_ub=np.asarray(aub), b_ub=np.asarray(bub),
                         A_eq=np.ones((1, n)), b_eq=[float(total)],
                         bounds=[(0, None)] * n, method="highs")
        if not result.success:
            return None
        answer.append(F(float(result.fun)).limit_denominator(1_000_000))
    left, right = selectors(tuple(answer), n)
    return tuple(map(F, left)), tuple(map(F, right))


def discovery_audit(values, x, z, cx=None):
    n = len(x); total = sum(x, F(0)); cs = covers(values, z)
    # The full x-tight menu is fixed complete certificate data; promoted hits
    # must additionally replay its staged Farkas certificates exactly.
    cx = tight_rows(values, x) if cx is None else tuple(cx)
    if not cs:
        return {"no_qualifying_cover": True, "fixed_faithful_cover_exists": False,
                "canonical_cx": list(cx), "cover_count": 0}
    top = tuple(i for i, q in enumerate(z) if q == max(z))
    outsiders = tuple(i for i in range(n) if i not in top)
    outcomes = []; automatic = 0
    for rows, cert in cs:
        _weights, eta, _alpha = cert
        incidence = [[F((row >> i) & 1) for row in rows] for i in outsiders]
        compatible = all(csum(x, row) >= csum(z, row) for row in rows)
        if eta > 0 and compatible and matrix_rank(incidence) == n - 2:
            faithful = True; automatic += 1
        else:
            constraints = {row: csum(x, row) for row in cx}
            constraints.update({row: csum(z, row) for row in rows})
            pair = fast_lift(constraints, n, total)
            faithful = pair == (x, z)
        outcomes.append({"rows": list(rows), "eta": str(eta), "faithful": faithful})
    return {"no_qualifying_cover": False,
            "fixed_faithful_cover_exists": any(q["faithful"] for q in outcomes),
            "canonical_cx": list(cx), "cover_count": len(cs),
            "automatic_full_rank_cover_count": automatic, "covers": outcomes}


def greedy_cx(values, x, rng):
    n = len(x); total = sum(x, F(0)); rows = list(tight_rows(values, x))
    rng.shuffle(rows)
    kept = rows[:]
    for row in rows:
        trial = tuple(q for q in kept if q != row)
        constraints = {q: csum(x, q) for q in trial}
        pair = fast_lift(constraints, n, total)
        if pair is not None and pair[0] == x:
            kept.remove(row)
    return tuple(sorted(kept))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, choices=(5, 6), required=True)
    parser.add_argument("--rounds", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260821)
    parser.add_argument("--total-min", type=int, default=6)
    parser.add_argument("--total-max", type=int, default=18)
    parser.add_argument("--generators-min", type=int, default=3)
    parser.add_argument("--generators-max", type=int, default=8)
    parser.add_argument("--top-symmetric", action="store_true")
    parser.add_argument("--capped-outsiders", action="store_true")
    parser.add_argument("--stop-after", type=int, default=1)
    parser.add_argument("--cx-greedy-orders", type=int, default=1)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rng = random.Random(args.seed); stats = Counter(); hits = []; hard_profiles = []
    for round_index in range(args.rounds):
        count = rng.randint(args.generators_min, args.generators_max)
        total = rng.randint(args.total_min, args.total_max)
        if args.capped_outsiders:
            generators = capped_two_top_generators(rng, args.n, total, count)
        elif args.top_symmetric:
            base = tuple(
                random_allocation(rng, args.n, total, j % args.n)
                for j in range(max(args.n, (count + 1) // 2))
            )
            swapped = tuple((g[1], g[0], *g[2:]) for g in base)
            generators = base + swapped
        else:
            generators = tuple(
                random_allocation(rng, args.n, total, j % args.n)
                for j in range(count)
            )
        if any(min(g[i] for g in generators) != 0 for i in range(args.n)):
            continue
        values = lower_envelope(generators); stats["games"] += 1
        approximate_x, approximate_z = selectors(values, args.n)
        if approximate_x is None or approximate_z is None:
            continue
        approximate_x, approximate_z = tuple(map(F, approximate_x)), tuple(map(F, approximate_z))
        if approximate_x == approximate_z:
            continue
        stats["floating_divergent"] += 1
        if sum(q == max(approximate_z) for q in approximate_z) != 2:
            continue
        stats["floating_two_top"] += 1
        constraints = {m: values[m] for m in range(1, (1 << args.n) - 1)
                       if values[m]}
        replay, x, z = selector_pair(constraints, args.n, F(total))
        if replay != values:
            raise AssertionError("integer-envelope exact replay changed")
        if x == z or sum(q == max(z) for q in z) != 2:
            stats["floating_filter_false_positives"] += 1
            continue
        stats["exact_divergent_two_top"] += 1
        if args.top_symmetric and not (z[0] == z[1] == max(z)):
            continue
        item = discovery_audit(values, x, z)
        item.update({"label": f"random_n{args.n}_seed{args.seed}_round{round_index}",
                     "n": args.n, "total": str(sum(x, F(0))),
                     "x": list(map(str, x)), "z": list(map(str, z))})
        failed = item.get("no_qualifying_cover", False) or not item.get(
            "fixed_faithful_cover_exists", False
        )
        if item.get("automatic_full_rank_cover_count", 0):
            stats["profiles_with_automatic_full_rank_cover"] += 1
        else:
            stats["profiles_without_automatic_full_rank_cover"] += 1
            exact_item = audit_game(
                item["label"] + "_allCx", values, x, z,
                pool_max=30, replay_exact=False,
            )
            if exact_item is None or not exact_item["cx_subsets_exhausted"]:
                raise AssertionError("hard profile lost complete exact Cx enumeration")
            exact_item["generators"] = [[str(q) for q in g] for g in generators]
            exact_item["full_game_replayed"] = True
            hard_profiles.append(exact_item)
            stats["hard_profiles_all_cx_exhausted"] += 1
            if exact_item["strong_fixed_cx_counterexample"]:
                hits.append(exact_item)
            if len(hits) >= args.stop_after:
                break
        stats["fixed_failures" if failed else "fixed_successes"] += 1
        if failed:
            item["generators"] = [[str(q) for q in g] for g in generators]
            item["promotion_status"] = (
                "candidate only: requires solver-free full-game and staged-Cx replay"
            )
            hits.append(item)
            if len(hits) >= args.stop_after:
                break
    payload = {
        "claim": "seeded exact-envelope falsification search; not a theorem",
        "parameters": vars(args) | {"output": str(args.output) if args.output else None},
        "stats": dict(stats), "hits": hits, "hard_profiles": hard_profiles,
        "scope": (
            "seeded integer-generator discovery; floating selectors are filters "
            "only and every retained target profile is reclassified by exact "
            "selector_pair. Qualifying extreme covers are exhaustive per tested "
            "profile; profiles without an automatic full-rank cover exhaust all "
            "Cx subsets exactly. This remains a bounded falsification search, "
            "and every hit requires independent exact promotion"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

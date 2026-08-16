#!/usr/bin/env python3
"""Design search: split-top violations with partially fed omitted-types.

Question (objective 3): does the PXC80 collapsing-denominator technique
extend to the split-top geometry?  I.e. at a single-heavy split-top
packet violation with >=2 (but not all) fed omitted-types and a tight
heavy-block row, does the canonical dispersion still obey
theta <= s(k-1)/(sk+k-s), and does the PXC78 chain close?

Also logs class-B/C shapes: violations with <2 fed types, or missing
heavy block, or multiple heavies -- and their PXC79-disjunct coverage.
"""
import argparse
import json
import random
import sys
import time
from fractions import Fraction as F
from pathlib import Path

REPO = Path("/private/tmp/coop-hybrid-20260812/coopgames")
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "verifiers" / "divergence"))

from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from audit_spectral_or_reserve import selectors, margins  # noqa: E402
from audit_costar_saturation_dichotomy import coalition_sum  # noqa: E402
from audit_menu_relaxed_root_exchange import ordered_saturated_roots  # noqa: E402
from audit_lmax_overcover import top_certificate  # noqa: E402
from audit_spectral_label_currency import spectral_decomposition  # noqa: E402
from audit_direct_ceiling_common_hinge_trichotomy import has_direct_packet  # noqa: E402
from audit_chosen_family_costar_closure import best_family_margin  # noqa: E402

SPLIT_SEEDS = (
    ((0, 6, 3, 3, 0, 0, 0), (8, 0, 0, 0, 2, 1, 1)),
    ((0, 6, 3, 3, 0, 0, 0), (8, 0, 0, 0, 1, 1, 2)),
    ((0, 8, 4, 4, 0, 0, 0), (10, 0, 0, 0, 3, 2, 1)),
    ((0, 6, 3, 3, 3, 0, 0, 0), (9, 0, 0, 0, 0, 2, 2, 2)),
    ((0, 10, 5, 5, 0, 0, 0), (12, 0, 0, 0, 4, 2, 2)),
)


def perturbed(rng, extra, base):
    n = len(base[0])
    out = [tuple(F(q) for q in g) for g in base]
    for _ in range(extra):
        source = list(base[rng.randrange(len(base))])
        support = [p for p in range(n) if source[p] > 0]
        for _move in range(rng.randint(1, 2)):
            donors = [p for p in support if source[p] >= 1]
            if not donors:
                break
            i = rng.choice(donors)
            j = rng.choice(support)
            if i == j:
                continue
            source[i] -= 1
            source[j] += 1
        out.append(tuple(F(q) for q in source))
    if any(min(g[p] for g in out) != 0 for p in range(n)):
        return None
    return tuple(out)


def audit(generators, tag, findings, stats):
    n = len(generators[0])
    values = lower_envelope(generators)
    x, z = selectors(values, n)
    if x is None or z is None or x == z:
        return
    for root, gainers, outsiders, _dec in ordered_saturated_roots(
        values, x, z
    ):
        stats["roots"] += 1
        m = margins(values, x, z)
        if m["packet_margin"] >= 0:
            continue
        M = max(z)
        tops = [a for a in gainers if z[a] == M]
        subs = [a for a in gainers if z[a] < M]
        if z[root] != M or not tops or not subs:
            continue
        if len({z[a] for a in subs}) != 1:
            continue
        sub_level = z[subs[0]]
        if not all(z[j] < sub_level for j in outsiders):
            continue
        stats["split_violations"] += 1
        s, k = len(subs), len(outsiders)
        # fed omitted-types: c in subs with every double co-star tight
        fed = []
        for c in subs:
            rows_tight = all(
                coalition_sum(z, cl) == values[cl]
                for j in outsiders
                for cl in [(1 << root) | (1 << j)
                           | sum(1 << a for a in tops)
                           | sum(1 << b for b in subs if b != c)]
            )
            if rows_tight:
                fed.append(c)
        hb = sum(1 << a for a in tops) + sum(1 << j for j in outsiders)
        heavy_block = coalition_sum(z, hb) == values[hb]
        cap = all(x[i] <= M for i in range(n) if i != root)
        cert = top_certificate(values, z)
        theta = F(cert["theta"])
        bound = (F(s * (k - 1), s * k + k - s)
                 if (s >= 2 and k >= 2) else None)
        chain_closes = None
        if bound is not None and cap:
            f = min(x)
            total = sum(x, F(0))
            residual = s * f + sum(min(z[j], f) for j in outsiders)
            chain = (M - f) / bound + 2 * f + residual + M - x[root]
            target = F(n, (n * n) // 4) * total
            chain_closes = chain >= target
        direct = has_direct_packet(x, z, F(n, (n * n) // 4))
        family = best_family_margin(values, x, z, root, gainers, outsiders)
        key = (len(tops), s, k, len(fed), heavy_block)
        stats["shapes"][str(key)] = stats["shapes"].get(str(key), 0) + 1
        interesting = (
            (2 <= len(fed) < s)                      # partial feeding
            or (len(fed) < 2)                        # class-B unfed
            or not heavy_block                       # class-C
            or len(tops) > 1                         # multi-heavy
            or (bound is not None and theta > bound)  # dispersion escape
        )
        if interesting:
            findings.append({
                "tag": tag, "tops": len(tops), "s": s, "k": k,
                "fed_types": len(fed), "heavy_block": heavy_block,
                "cap": cap, "theta": str(theta),
                "bound": None if bound is None else str(bound),
                "theta_le_bound": None if bound is None else theta <= bound,
                "chain_closes": chain_closes,
                "packet_margin": str(m["packet_margin"]),
                "direct": direct,
                "chosen_family": None if family is None else str(family),
                "generators": [[str(q) for q in g] for g in generators],
            })
            print(json.dumps(findings[-1]), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260825)
    parser.add_argument("--rounds", type=int, default=8000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    findings = []
    stats = {"roots": 0, "split_violations": 0, "shapes": {}}
    start = time.time()
    for index in range(args.rounds):
        base = SPLIT_SEEDS[rng.randrange(len(SPLIT_SEEDS))]
        gens = perturbed(rng, rng.randint(1, 5), base)
        if gens is None:
            continue
        try:
            audit(gens, f"split[{index}]k{len(gens)}", findings, stats)
        except AssertionError:
            continue
        if (index + 1) % 100 == 0:
            print(f"[{index + 1}/{args.rounds}] "
                  f"{time.time() - start:.0f}s " + json.dumps(stats),
                  flush=True)
    if args.output:
        args.output.write_text(json.dumps(
            {"stats": stats, "findings": findings, "seed": args.seed},
            indent=2) + "\n")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()

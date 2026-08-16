#!/usr/bin/env python3
"""Wide probe: 4-8 generator envelopes against PXC79 and the feeding law.

Every singleton-normalized exact game is a lower envelope of its core
witnesses; the campaign's designed evidence used only 2-3 generators.
This probe samples envelopes of 4-8 generators (random supports, plus
known 2-generator violation shapes with extra noise generators) and, at
every ordered saturated ceiling root, tests the five PXC79 disjuncts:
reserve, direct, PXC75 hypotheses, PXC78 (class-A) hypotheses, and the
chosen-family certificate.  Logged findings: PXC79 escapes, feeding
counterexamples (top-uniform violation with an unfed co-star), and
ordered-unsaturated roots.
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
from audit_carrier_separator_payment import full_tight_support  # noqa: E402
from audit_ceiling_root_gainer_exclusion import rooted_packing  # noqa: E402
from audit_direct_ceiling_common_hinge_trichotomy import has_direct_packet  # noqa: E402
from audit_chosen_family_costar_closure import best_family_margin  # noqa: E402

VIOLATION_SEEDS = (
    ((0, 5, 5, 5, 0, 0, 0, 0), (8, 0, 0, 0, 4, 1, 1, 1)),
    ((0, 5, 5, 5, 5, 0, 0, 0), (5, 0, 0, 0, 0, 13, 1, 1)),
    ((0, 5, 5, 5, 5, 0, 0, 0), (13, 0, 0, 0, 0, 5, 1, 1)),
    ((0, 4, 4, 4, 4, 0, 0, 0), (11, 0, 0, 0, 0, 2, 2, 1)),
    ((0, 5, 5, 5, 5, 0, 0, 0), (13, 0, 0, 0, 0, 3, 2, 2)),
    ((0, 6, 3, 3, 0, 0, 0, 0), (8, 0, 0, 0, 1, 1, 1, 1)),
)


def composition(rng, support, total):
    k = len(support)
    cuts = sorted(rng.sample(range(1, total), k - 1)) if k > 1 else []
    parts, prev = [], 0
    for cut in cuts + [total]:
        parts.append(cut - prev)
        prev = cut
    return dict(zip(support, parts))


def random_envelope(rng, n, gens, total):
    while True:
        supports = []
        for _ in range(gens):
            size = rng.randint(2, n - 1)
            supports.append(tuple(sorted(rng.sample(range(n), size))))
        if any(all(p in s for s in supports) for p in range(n)):
            continue
        out = []
        for s in supports:
            weights = composition(rng, s, total)
            out.append(tuple(F(weights.get(p, 0)) for p in range(n)))
        return tuple(out)


def seeded_envelope(rng, extra, total):
    """Envelope of perturbed copies of a violation shape's generators."""
    base = VIOLATION_SEEDS[rng.randrange(len(VIOLATION_SEEDS))]
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


def pair_graph(values, z, root, gainers, outsiders):
    """Bipartite tightness graph of decorated co-star pairs."""
    edges = []
    for a in gainers:
        for j in outsiders:
            cl = (1 << root) | (1 << j)
            for b in gainers:
                if b != a:
                    cl |= 1 << b
            if coalition_sum(z, cl) == values[cl]:
                edges.append((a, j))
    return edges


def pxc75_hyp(values, x, z, root, gainers, outsiders):
    """PXC81 condition: every outsider in some tight pair, two types."""
    n = len(x)
    M = max(z)
    if not (z[root] == M and all(z[a] == M for a in gainers)
            and all(z[j] < M for j in outsiders)):
        return False
    if any(x[i] > M for i in range(n) if i != root):
        return False
    edges = pair_graph(values, z, root, gainers, outsiders)
    columns = {j for _a, j in edges}
    rows = {a for a, _j in edges}
    return columns == set(outsiders) and len(rows) >= 2


def pxc78_hyp(values, x, z, root, gainers, outsiders):
    n = len(x)
    M = max(z)
    tops = [a for a in gainers if z[a] == M]
    subs = [a for a in gainers if z[a] < M]
    if z[root] != M or len(tops) != 1 or len(subs) < 2:
        return False
    if len({z[a] for a in subs}) != 1:
        return False
    if not all(z[j] < min(z[a] for a in subs) for j in outsiders):
        return False
    if len(outsiders) < 2:
        return False
    if any(x[i] > M for i in range(n) if i != root):
        return False
    for c in subs:
        for j in outsiders:
            cl = (1 << root) | (1 << j) | (1 << tops[0])
            for b in subs:
                if b != c:
                    cl |= 1 << b
            if coalition_sum(z, cl) != values[cl]:
                return False
    hb = (1 << tops[0])
    for j in outsiders:
        hb |= 1 << j
    return coalition_sum(z, hb) == values[hb]


def audit_game(generators, tag, findings, stats):
    n = len(generators[0])
    values = lower_envelope(generators)
    x, z = selectors(values, n)
    if x is None or z is None:
        return
    x = tuple(F(q) for q in x)
    z = tuple(F(q) for q in z)
    stats["games"] += 1
    if x == z:
        return
    stats["divergent"] += 1
    # ordered-unsaturated detection
    ceiling = max(z)
    gset = {p for p in range(n) if z[p] > x[p]}
    support = tuple(full_tight_support(values, x))
    for root in range(n):
        if z[root] != ceiling or x[root] < ceiling or root in gset:
            continue
        rooted, nu, _w, _c = rooted_packing(support, n, root)
        om = {c: tuple(p for p in gset if not (c >> p & 1)) for c in rooted}
        if any(len(v_) >= 2 for v_ in om.values()):
            continue
        g = len(gset)
        if g < 2:
            continue
        outs = [p for p in range(n) if p not in gset and p != root]
        ming = min(x[p] for p in gset)
        ordered = all(x[root] >= x[p] for p in gset) and all(
            ming >= x[p] for p in outs
        )
        if ordered and nu != F(g, g - 1):
            findings.append({"kind": "ORDERED_UNSATURATED", "tag": tag,
                             "generators": [[str(q) for q in gg]
                                            for gg in generators]})
            print(json.dumps(findings[-1]), flush=True)
    for root, gainers, outsiders, _dec in ordered_saturated_roots(
        values, x, z
    ):
        stats["roots"] += 1
        m = margins(values, x, z)
        if m["packet_margin"] >= 0:
            stats["reserve"] += 1
            continue
        stats["violations"] += 1
        M0 = max(z)
        if (z[root] == M0 and all(z[a] == M0 for a in gainers)
                and all(z[j] < M0 for j in outsiders)):
            edges = pair_graph(values, z, root, gainers, outsiders)
            key = (len(gainers), len(outsiders),
                   tuple(sorted((gainers.index(a) if a in gainers else -1,
                                 sorted(outsiders).index(j))
                                for a, j in edges)))
            stats.setdefault("graphs", {})
            stats["graphs"][str(key)] = stats["graphs"].get(str(key), 0) + 1
        direct = has_direct_packet(x, z, F(n, (n * n) // 4))
        h75 = pxc75_hyp(values, x, z, root, gainers, outsiders)
        h78 = pxc78_hyp(values, x, z, root, gainers, outsiders)
        M = max(z)
        top_uniform = (z[root] == M and all(z[a] == M for a in gainers)
                       and all(z[j] < M for j in outsiders))
        if top_uniform and not h75:
            fed = all(
                coalition_sum(z, cl) == values[cl]
                for a in gainers for j in outsiders
                for cl in [(1 << root) | (1 << j)
                           | sum(1 << b for b in gainers if b != a)]
            )
            if not fed:
                findings.append({"kind": "FEEDING_COUNTEREXAMPLE",
                                 "tag": tag,
                                 "generators": [[str(q) for q in gg]
                                                for gg in generators],
                                 "x": [str(q) for q in x],
                                 "z": [str(q) for q in z]})
                print(json.dumps(findings[-1]), flush=True)
        if direct or h75 or h78:
            stats["covered"] += 1
            continue
        best = best_family_margin(values, x, z, root, gainers, outsiders)
        if best is not None and best >= 0:
            stats["chosen_family"] += 1
            continue
        findings.append({"kind": "PXC79_ESCAPE", "tag": tag,
                         "generators": [[str(q) for q in gg]
                                        for gg in generators],
                         "x": [str(q) for q in x],
                         "z": [str(q) for q in z], "root": root,
                         "packet_margin": str(m["packet_margin"]),
                         "chosen_family": None if best is None else str(best)})
        print(json.dumps(findings[-1]), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260822)
    parser.add_argument("--rounds", type=int, default=20000)
    parser.add_argument("--total", type=int, default=12)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    findings = []
    stats = {"games": 0, "divergent": 0, "roots": 0, "reserve": 0,
             "violations": 0, "covered": 0, "chosen_family": 0}
    start = time.time()
    for index in range(args.rounds):
        if index % 2 == 0:
            gens = seeded_envelope(rng, rng.randint(2, 6), args.total)
            if gens is None:
                continue
            tag = f"seeded[{index}]k{len(gens)}"
        else:
            k = rng.randint(4, 8)
            gens = random_envelope(rng, 8, k, args.total)
            tag = f"random[{index}]k{k}"
            if index % 4 == 3:
                # widen supports: mostly-large generators
                gens = None
                while gens is None:
                    supports = []
                    for gi in range(k):
                        size = rng.randint(2, 7) if gi < 2 else rng.randint(6, 7)
                        supports.append(tuple(sorted(rng.sample(range(8), size))))
                    if any(all(p in sp for sp in supports) for p in range(8)):
                        continue
                    built = []
                    for sp in supports:
                        weights = composition(rng, sp, args.total)
                        built.append(tuple(F(weights.get(p, 0)) for p in range(8)))
                    gens = tuple(built)
                tag = f"wide[{index}]k{k}"
        try:
            audit_game(gens, tag, findings, stats)
        except AssertionError:
            continue
        if (index + 1) % 100 == 0:
            print(f"[{index + 1}/{args.rounds}] {time.time() - start:.0f}s "
                  + json.dumps(stats), flush=True)
    if args.output:
        args.output.write_text(json.dumps(
            {"stats": stats, "findings": findings, "seed": args.seed},
            indent=2) + "\n")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()

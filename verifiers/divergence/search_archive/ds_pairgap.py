#!/usr/bin/env python3
"""Refutation hunt for the class-B closure conjecture.

From archived class-B witnesses (split-top violation, heavy block
slack, top pair tight), random-walk the generators hunting for a
class-B violation whose top pair is SLACK (gap = 2M - v({r,h}) > 0).
Any hit refutes the conjecture as stated.  Also logs the gap
distribution and what closes any gap>0 instances.
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

from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from audit_spectral_or_reserve import selectors, margins  # noqa: E402
from audit_costar_saturation_dichotomy import coalition_sum  # noqa: E402
from audit_menu_relaxed_root_exchange import ordered_saturated_roots  # noqa: E402


def classify(gens):
    """Return None or (is_class_b, pair_tight, packet_margin)."""
    n = len(gens[0])
    values = lower_envelope(gens)
    x, z = selectors(values, n)
    if x is None or z is None or x == z:
        return None
    roots = ordered_saturated_roots(values, x, z)
    if len(roots) != 1:
        return None
    root, gainers, outsiders, _ = roots[0]
    m = margins(values, x, z)
    if m["packet_margin"] >= 0:
        return None
    M = max(z)
    tops = [a for a in gainers if z[a] == M]
    subs = [a for a in gainers if z[a] < M]
    if z[root] != M or len(tops) != 1 or not subs:
        return None
    if len({z[a] for a in subs}) != 1:
        return None
    if not all(z[j] < z[subs[0]] for j in outsiders):
        return None
    h = tops[0]
    hb = (1 << h) + sum(1 << j for j in outsiders)
    heavy_block = coalition_sum(z, hb) == values[hb]
    if heavy_block:
        return None                      # class A side, not our prey
    pair = (1 << root) | (1 << h)
    gap = (z[root] + z[h]) - values[pair]
    return (str(gap), gap > 0, str(m["packet_margin"]))


def mutate(rng, base):
    n = len(base[0])
    out = [list(g) for g in base]
    for _ in range(rng.randint(1, 3)):
        gi = rng.randrange(len(out))
        g = out[gi]
        support = [p for p in range(n) if g[p] > 0]
        donors = [p for p in support if g[p] >= 1]
        if not donors:
            continue
        i = rng.choice(donors)
        j = rng.randrange(n)
        if i == j:
            continue
        g[i] -= 1
        g[j] += 1
    if rng.random() < 0.3 and len(out) < 9:
        out.append(list(out[rng.randrange(len(out))]))
    if any(min(g[p] for g in out) != 0 for p in range(n)):
        return None
    return tuple(tuple(F(q) for q in g) for g in out)


def main():
    seed_file = REPO / "verifiers/divergence/search_archive/ds_split_b.json"
    d = json.loads(seed_file.read_text())
    bases = [tuple(tuple(F(q) for q in g) for g in r["generators"])
             for r in d["findings"] if not r["heavy_block"]]
    rng = random.Random(20260832)
    stats = {"tries": 0, "class_b": 0, "gap_zero": 0, "gap_positive": 0}
    findings = []
    start = time.time()
    rounds = 12000
    for index in range(rounds):
        base = bases[rng.randrange(len(bases))]
        gens = mutate(rng, base)
        if gens is None:
            continue
        stats["tries"] += 1
        try:
            res = classify(gens)
        except AssertionError:
            continue
        if res is None:
            continue
        gap, positive, packet = res
        stats["class_b"] += 1
        if positive:
            stats["gap_positive"] += 1
            findings.append({"kind": "PAIR_SLACK_CLASS_B", "gap": gap,
                             "packet_margin": packet,
                             "generators": [[str(q) for q in g]
                                            for g in gens]})
            print(json.dumps(findings[-1]), flush=True)
        else:
            stats["gap_zero"] += 1
        if (index + 1) % 200 == 0:
            print(f"[{index + 1}/{rounds}] {time.time() - start:.0f}s "
                  + json.dumps(stats), flush=True)
    out = Path(__file__).parent / "ds_pairgap.json"
    out.write_text(json.dumps({"stats": stats, "findings": findings},
                              indent=2) + "\n")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()

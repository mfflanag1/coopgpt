#!/usr/bin/env python3
"""Engineer exotic blocking families against the class-B conjecture.

Take archived class-B witnesses and ADD a generator concentrated on
{h, sub-gainer, outsider} (value split matched to the current z there,
remainder spread on the other players), aiming to create tight mixed
rows through h that could block the egalitarian descent WITHOUT the
heavy block or the top pair.  Then re-audit: if a single-heavy
split-top packet violation appears with heavy block slack AND top pair
slack, the class-B closure conjecture is refuted.
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


def analyze(gens):
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
    pair = (1 << root) | (1 << h)
    pair_tight = coalition_sum(z, pair) == values[pair]
    return {
        "root": root, "h": h, "subs": subs, "outsiders": list(outsiders),
        "heavy_block": heavy_block, "pair_tight": pair_tight,
        "packet_margin": str(m["packet_margin"]),
        "x": [str(q) for q in x], "z": [str(q) for q in z],
        "values": values, "M": M,
    }


def engineer(rng, base, info):
    """Add a generator concentrated near z on {h, sub, outsider}."""
    n = len(base[0])
    total = sum(base[0], F(0))
    h = info["h"]
    c = rng.choice(info["subs"])
    j = rng.choice(info["outsiders"])
    zv = [F(q) for q in info["z"]]
    import math
    y = [F(0)] * n
    y[h] = F(math.floor(zv[h])) + rng.randint(0, 1)
    y[c] = F(math.floor(zv[c]))
    y[j] = F(max(0, math.floor(zv[j])))
    rest = total - y[h] - y[c] - y[j]
    if rest < 0:
        return None
    others = [p for p in range(n) if p not in (h, c, j)]
    rng.shuffle(others)
    others = others[:max(1, len(others) - 1)]
    while rest > 0:
        p = others[rng.randrange(len(others))]
        y[p] += 1
        rest -= 1
    out = list(base) + [tuple(y)]
    if any(min(g[p] for g in out) != 0 for p in range(n)):
        return None
    return tuple(out)


def main():
    seed_file = REPO / "verifiers/divergence/search_archive/ds_split_b.json"
    d = json.loads(seed_file.read_text())
    bases = [tuple(tuple(F(q) for q in g) for g in r["generators"])
             for r in d["findings"] if not r["heavy_block"]][:120]
    rng = random.Random(20260833)
    stats = {"tries": 0, "split_violations": 0, "class_b": 0,
             "pair_slack": 0, "exotic_menus": 0}
    findings = []
    start = time.time()
    rounds = 8000
    base_cache = {}
    for index in range(rounds):
        bi = rng.randrange(len(bases))
        base = bases[bi]
        if bi not in base_cache:
            base_cache[bi] = analyze(base)
        base_info = base_cache[bi]
        if base_info is None:
            continue
        gens = engineer(rng, base, base_info)
        if gens is None:
            continue
        stats["tries"] += 1
        try:
            info = analyze(gens)
        except AssertionError:
            continue
        if info is None:
            continue
        stats["split_violations"] += 1
        if not info["heavy_block"]:
            stats["class_b"] += 1
            if not info["pair_tight"]:
                stats["pair_slack"] += 1
                findings.append({
                    "kind": "PAIR_SLACK_CLASS_B", "index": index,
                    "packet_margin": info["packet_margin"],
                    "x": info["x"], "z": info["z"],
                    "generators": [[str(q) for q in g] for g in gens],
                })
                print(json.dumps(findings[-1]), flush=True)
        if (index + 1) % 200 == 0:
            print(f"[{index + 1}/{rounds}] {time.time() - start:.0f}s "
                  + json.dumps(stats), flush=True)
    out = Path(__file__).parent / "ds_exotic.json"
    out.write_text(json.dumps({"stats": stats, "findings": findings},
                              indent=2) + "\n")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()

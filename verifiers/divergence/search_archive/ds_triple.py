#!/usr/bin/env python3
"""Design search: rooted sub-top menus (sixth-mechanism candidate).

Seeded on the pinned triple-menu escape.  At every uniform-top packet
violation, classify the Lmax-tight menu; when every tight row is a
rooted undecorated subset {r} u P with P a proper gainer subset, test
the sixth-mechanism candidate: theta <= 1/(p_min+1) where p_min is the
smallest |P|, and the PXC75-style chain with that dispersion closes.
Log any rooted-menu violation where the dispersion or chain fails, and
any violation whose menu is neither pair-supported nor rooted (mixed).
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

ESCAPE = (
    (0, 4, 4, 4, 4, 0, 0, 0), (11, 0, 0, 0, 0, 2, 2, 1),
    (10, 0, 0, 0, 0, 1, 4, 1), (11, 0, 0, 0, 0, 3, 2, 0),
    (10, 0, 0, 0, 0, 3, 1, 2), (0, 5, 3, 5, 3, 0, 0, 0),
    (12, 0, 0, 0, 0, 1, 1, 2), (12, 0, 0, 0, 0, 2, 1, 1),
)


def perturbed(rng, base, extra):
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


def subset_menu(rng, base, drop):
    """Random sub-multiset of the escape's generators plus perturbations."""
    keep = [g for g in base if rng.random() > drop]
    if len(keep) < 3:
        return None
    return perturbed(rng, tuple(keep), rng.randint(0, 3))


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
        if not (z[root] == M and all(z[a] == M for a in gainers)
                and all(z[j] < M for j in outsiders)):
            continue
        stats["violations"] += 1
        gset = set(gainers)
        top_mask = (1 << root) | sum(1 << a for a in gainers)
        tight = [c for c in range(1, (1 << n) - 1)
                 if coalition_sum(z, c) == values[c]]
        rooted, decorated, other = [], [], []
        for c in tight:
            members = {p for p in range(n) if c >> p & 1}
            if root in members and members <= (gset | {root}) \
                    and members != gset | {root}:
                rooted.append(sorted(members))
            elif root in members and len(members & set(outsiders)) == 1 \
                    and len(gset - members) == 1 and members - {root} \
                    - gset <= set(outsiders):
                decorated.append(sorted(members))
            else:
                other.append(sorted(members))
        kind = ("rooted" if rooted and not decorated and not other
                else "pair" if decorated and not rooted and not other
                else "mixed")
        stats[kind] = stats.get(kind, 0) + 1
        if kind != "rooted":
            if kind == "mixed":
                findings.append({"kind": "MIXED_MENU", "tag": tag,
                                 "rooted": rooted[:6],
                                 "decorated": decorated[:6],
                                 "other": other[:6],
                                 "generators": [[str(q) for q in gg]
                                                for gg in generators]})
                print(json.dumps(findings[-1]), flush=True)
            continue
        p_min = min(len(row) - 1 for row in rooted)
        cert = top_certificate(values, z)
        theta = F(cert["theta"])
        bound = F(1, p_min + 1)
        f = min(x)
        total = sum(x, F(0))
        g = len(gainers)
        residual = sum(min(z[j], f) for j in outsiders)
        chain = (M - f) / bound + (g + 1) * f + residual + M - x[root]
        target = F(n, (n * n) // 4) * total
        cap = all(x[i] <= M for i in range(n) if i != root)
        ok = theta <= bound and (not cap or chain >= target)
        stats["rooted_ok"] = stats.get("rooted_ok", 0) + int(ok)
        if not ok:
            findings.append({
                "kind": "ROOTED_MENU_FAIL", "tag": tag,
                "theta": str(theta), "bound": str(bound),
                "chain": str(chain), "target": str(target), "cap": cap,
                "menu": rooted,
                "x": [str(q) for q in x], "z": [str(q) for q in z],
                "generators": [[str(q) for q in gg] for gg in generators],
            })
            print(json.dumps(findings[-1]), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260828)
    parser.add_argument("--rounds", type=int, default=8000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    findings = []
    stats = {"roots": 0, "violations": 0}
    start = time.time()
    for index in range(args.rounds):
        if index % 3 == 2:
            gens = subset_menu(rng, ESCAPE, 0.3)
        else:
            gens = perturbed(rng, ESCAPE, rng.randint(1, 4))
        if gens is None:
            continue
        try:
            audit(gens, f"triple[{index}]k{len(gens)}", findings, stats)
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

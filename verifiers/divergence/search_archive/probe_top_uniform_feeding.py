#!/usr/bin/env python3
"""Mutation probe: are top-uniform packet violations always co-star fed?

Enumerates every one-unit generator mutation of the four known
top-uniform packet-violation shapes (normalization-preserving), recomputes
exact selectors, and checks feeding at each resulting top-uniform packet
violation.  Output on 2026-08-16:

    top-uniform violations checked: 20; unfed found: 0

Together with the eighteen previously audited top-uniform violations,
the conjecture "violation and top-uniformity force every decorated
co-star Lmax-tight" stands at 38 for 38.  It remains a conjecture.
"""
import itertools
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
COOPGAMES = HERE.parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))
sys.path.insert(0, str(COOPGAMES / "verifiers" / "divergence"))

from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from audit_spectral_or_reserve import selectors, margins  # noqa: E402
from audit_costar_saturation_dichotomy import coalition_sum  # noqa: E402
from audit_menu_relaxed_root_exchange import ordered_saturated_roots  # noqa: E402

SEEDS = (
    ((0, 4, 4, 4, 0, 0, 0), (7, 0, 0, 0, 3, 1, 1)),
    ((0, 4, 4, 4, 0, 0, 0), (7, 0, 0, 0, 2, 2, 1)),
    ((0, 6, 6, 6, 0, 0, 0), (10, 0, 0, 0, 4, 2, 2)),
    ((0, 4, 4, 4, 4, 0, 0, 0), (11, 0, 0, 0, 0, 2, 2, 1)),
)


def probe(generators):
    generators = tuple(tuple(F(q) for q in g) for g in generators)
    n = len(generators[0])
    values = lower_envelope(generators)
    x, z = selectors(values, n)
    if x == z:
        return []
    results = []
    for root, gainers, outsiders, _dec in ordered_saturated_roots(
        values, x, z
    ):
        if margins(values, x, z)["packet_margin"] >= 0:
            continue
        ceiling = max(z)
        top_uniform = (
            z[root] == ceiling
            and all(z[a] == ceiling for a in gainers)
            and all(z[j] < ceiling for j in outsiders)
        )
        if not top_uniform:
            continue
        fed = True
        for a in gainers:
            for j in outsiders:
                coalition = (1 << root) | (1 << j)
                for b in gainers:
                    if b != a:
                        coalition |= 1 << b
                if coalition_sum(z, coalition) != values[coalition]:
                    fed = False
        results.append(fed)
    return results


def main():
    checked = unfed = 0
    for seed in SEEDS:
        base = [list(g) for g in seed]
        mutations = [tuple(tuple(r) for r in base)]
        for gi in range(2):
            for i in range(len(base[0])):
                if base[gi][i] < 1:
                    continue
                for j in range(len(base[0])):
                    if i == j:
                        continue
                    nb = [list(g) for g in base]
                    nb[gi][i] -= 1
                    nb[gi][j] += 1
                    if any(
                        min(nb[0][p], nb[1][p]) != 0
                        for p in range(len(nb[0]))
                    ):
                        continue
                    mutations.append(tuple(tuple(r) for r in nb))
        for generators in mutations:
            for fed in probe(generators):
                checked += 1
                unfed += not fed
    print(f"top-uniform violations checked: {checked}; unfed found: {unfed}")


if __name__ == "__main__":
    main()

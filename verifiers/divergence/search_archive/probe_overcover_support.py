#!/usr/bin/env python3
"""Classify the canonical stage-1 over-cover support at uniform-top violations.

Motivated by the feeding implication: if the canonical over-cover were
always supported on single-omission single-decoration co-stars, coverage
of every outsider would force tight decorated rows per outsider.  Result
on the two-generator family grid (2026-08-16):

    uniform-top packet violations: 20
    support entirely single-omission single-decoration co-stars: 14
    positive ambient level eta: 18

The six exceptions (k=2 shapes with extreme outsider weights such as
(5,5,5,5;5;(13,2))) use rooted pairs, rooted multi-omission subsets of
the top block, and rootless gainer-outsider rows, while remaining fed.
The support-classification route therefore cannot prove the feeding
implication by itself; two one-line lemmas survive (no rootless subset
of the gainer block is ever Lmax-tight, and clean co-stars and the full
top block are never Lmax-tight at a violation).
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
from audit_spectral_or_reserve import (  # noqa: E402
    selectors, family_instance, margins,
)
from audit_menu_relaxed_root_exchange import ordered_saturated_roots  # noqa: E402
from audit_lmax_overcover import top_certificate  # noqa: E402


def main():
    shapes = []
    for g_, k_ in ((2, 3), (3, 2), (2, 4), (4, 2), (3, 3), (3, 4), (4, 3)):
        for c_ in range(2, 6):
            total = g_ * c_
            for H in range(c_, total - k_ + 1):
                rest = total - H
                for w in itertools.combinations_with_replacement(
                    range(1, rest + 1), k_
                ):
                    if sum(w) == rest:
                        shapes.append(
                            ((c_,) * g_, H, tuple(sorted(w, reverse=True)))
                        )
    counts = {"uniform_violations": 0, "support_all_single_dec": 0,
              "eta_positive": 0}
    for a, H, w in shapes:
        generators = family_instance(a, H, w)
        n = len(generators[0])
        values = lower_envelope(generators)
        x, z = selectors(values, n)
        if x == z:
            continue
        roots = ordered_saturated_roots(values, x, z)
        if len(roots) != 1:
            continue
        root, gainers, outsiders, _dec = roots[0]
        if margins(values, x, z)["packet_margin"] >= 0:
            continue
        ceiling = max(z)
        if not (z[root] == ceiling
                and all(z[q] == ceiling for q in gainers)
                and all(z[j] < ceiling for j in outsiders)):
            continue
        counts["uniform_violations"] += 1
        certificate = top_certificate(values, z)
        clean = True
        for coalition in certificate["support"]:
            omitted = [q for q in gainers if not (coalition >> q & 1)]
            decorations = [j for j in outsiders if coalition >> j & 1]
            rooted = bool(coalition >> root & 1)
            if not (rooted and len(omitted) == 1 and len(decorations) == 1):
                clean = False
        counts["support_all_single_dec"] += clean
        counts["eta_positive"] += F(certificate["eta"]) > 0
    print(counts)


if __name__ == "__main__":
    main()

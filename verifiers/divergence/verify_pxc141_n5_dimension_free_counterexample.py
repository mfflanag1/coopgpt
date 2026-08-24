#!/usr/bin/env python3
"""Exact primary audit of the smallest counterexample to the literal all-n target.

The game is the lower envelope of the two allocations in Theorem n=5.  The
audit recomputes the complete game, both staged selectors, every complete
proper-row Lmin certificate, and the spectral decomposition.  The cover
program PXC112/PXC114 is explicitly inapplicable: Lmax has four, not two,
top players.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / "verifiers" / "divergence"),
                str(ROOT / "verifiers" / "divergence" / "search_archive")]

from audit_spectral_label_currency import spectral_decomposition  # noqa: E402
from unrestricted_pxc91c_exact_search import (  # noqa: E402
    complete_cx_subsets, selector_from_constraints,
)

N, TOTAL = 5, F(4)
G1 = tuple(map(F, (1, 0, 0, 1, 2)))
G2 = tuple(map(F, (0, 1, 3, 0, 0)))
X = tuple(map(F, (F(1, 2), F(1, 2), F(5, 4), F(1, 2), F(5, 4))))
Z = tuple(map(F, (1, 0, 1, 1, 1)))


def csum(point, mask):
    return sum((point[i] for i in range(N) if mask >> i & 1), F(0))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    values = tuple(min(csum(G1, s), csum(G2, s)) for s in range(1 << N))
    constraints = {s: values[s] for s in range(1, (1 << N) - 1) if values[s]}
    x = selector_from_constraints(constraints, N, TOTAL, "min")
    z = selector_from_constraints(constraints, N, TOTAL, "max")
    if (x, z) != (X, Z):
        raise AssertionError((x, z))
    if any(values[1 << i] for i in range(N)):
        raise AssertionError("not singleton normalized")
    if values[(1 << N) - 1] != TOTAL:
        raise AssertionError("wrong total")

    overlap = sum((min(a, b) for a, b in zip(x, z)), F(0))
    distance = sum((abs(a - b) for a, b in zip(x, z)), F(0))
    target = F(N, (N * N) // 4) * TOTAL
    if not overlap == TOTAL - distance / 2 == F(3) < target == F(10, 3):
        raise AssertionError("counterexample arithmetic")

    pool, complete = complete_cx_subsets(values, x, 10)
    expected_pool = (3, 10, 21, 28)
    if pool != expected_pool or complete is None:
        raise AssertionError((pool, complete))
    subset_selectors = {}
    for bits in range(1 << len(pool)):
        rows = tuple(pool[i] for i in range(len(pool)) if bits >> i & 1)
        lx = selector_from_constraints({s: values[s] for s in rows}, N, TOTAL, "min")
        subset_selectors[",".join(map(str, rows)) or "empty"] = list(map(str, lx))
    if tuple(rows for rows in complete if rows == pool) != (pool,):
        raise AssertionError("full tight pool must be a complete certificate")

    top = tuple(i for i, q in enumerate(z) if q == max(z))
    if top != (0, 2, 3, 4):
        raise AssertionError(top)
    spectral = spectral_decomposition("PXC141 n=5 literal counterexample", values, x, z)
    if spectral["overlap_ratio"] != "3/4" or spectral["target_ratio"] != "5/6":
        raise AssertionError(spectral)

    payload = {
        "claim": "PXC141 smallest counterexample to the literal all-n hybrid-overlap coefficient",
        "game": {"n": N, "total": str(TOTAL), "generators": [list(map(str, G1)), list(map(str, G2))],
                 "values": list(map(str, values)), "singleton_normalized": True,
                 "exactness": "lower-envelope lemma; every coalition minimum is attained by a generator"},
        "selectors": {"Lmin": list(map(str, x)), "Lmax": list(map(str, z)),
                      "Lmax_top": list(top)},
        "failure": {"overlap": str(overlap), "l1_distance": str(distance),
                    "overlap_ratio": str(overlap / TOTAL), "c_n": str(F(5, 6)),
                    "required_overlap": str(target), "margin": str(overlap - target)},
        "certificate_exhaustion": {"proper_x_tight_pool": list(pool),
                    "complete_subsets": [list(rows) for rows in complete],
                    "all_16_subset_selectors": subset_selectors},
        "mechanism_scope": {"two_top_cover_program_applicable": False,
                    "reason": "Top(Lmax) has four players; PXC112/PXC114 require Top(z)={r,h}",
                    "spectral_top_assignments_exhausted": True,
                    "spectral": spectral},
        "minimality": "the proved n<=4 coincidence theorem gives overlap=T; hence n=5 is smallest",
        "status": "falsifies the literal all-n target; the corrected n>=6 target remains open",
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

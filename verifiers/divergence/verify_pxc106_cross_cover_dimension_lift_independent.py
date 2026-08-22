#!/usr/bin/env python3
"""Independent dimension-free algebra audit for PXC106.

No project LP, selector, cover, family, or discovery module is imported.
The exact n=6 active-set calibration is supplied separately by PXC104/105.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def players_mask(players):
    answer = 0
    for player in players:
        answer |= 1 << player
    return answer


def verify_dimension(n):
    m = n - 4
    p, q = 1, m - 1
    A = 4 + F(1, m + 1)
    J = tuple(range(4, 4 + p))
    K = tuple(range(4 + p, n))
    rh = (0, 1)
    row_a = players_mask(rh + (2,))
    row_b = players_mask(rh + (3,))
    row_J = players_mask(rh + J)
    row_aJ = players_mask(rh + (2,) + J)
    row_K = players_mask(rh + K)
    row_aK = players_mask(rh + (2,) + K)
    pair = players_mask(rh)
    rows = (pair, row_b, row_J, row_aJ, row_K, row_aK)
    covers = ((pair,), (row_b, row_J, row_aK),
              (row_b, row_aJ, row_K))

    total = 16 + A + m
    u = (A + m) / (m + 1)
    top = (16 - u) / 2
    x = (top, top) + (u,) * (m + 2)
    z = (F(6), F(6), A, F(4)) + (F(1),) * m
    if sum(x) != total or sum(z) != total or not top > u > 0:
        raise AssertionError(("selector totals/order", n))

    slack_J = p * (A - 1) / (m + 1) - (A - 4)
    slack_K = q * (A - 1) / (m + 1) - (A - 4)
    if not (4 < A < 6 and slack_J > 0 and slack_K > 0):
        raise AssertionError(("chamber", n, A, slack_J, slack_K))

    def coal(point, row):
        return sum(point[i] for i in range(n) if row >> i & 1)

    bounds = {
        row_a: F(16), row_b: F(16),
        row_J: F(12 + p), row_aJ: F(12 + p) + A,
        row_K: F(12 + q), row_aK: F(12 + q) + A,
    }
    if coal(x, row_a) != 16 or coal(x, row_b) != 16:
        raise AssertionError(("Cx tightness", n))
    if any(coal(x, row) <= bound for row, bound in bounds.items()
           if row not in (row_a, row_b)):
        raise AssertionError(("other x row not strict", n))
    if any(coal(z, row) != bound for row, bound in bounds.items()
           if row != row_a) or not coal(z, row_a) > 16:
        raise AssertionError(("z menu", n))

    # Explicit singleton witnesses.
    witness_r = (F(0), F(12), A, F(4)) + (F(1),) * m
    witness_h = (F(12), F(0), A, F(4)) + (F(1),) * m
    all_root = (total,) + (F(0),) * (n - 1)
    for witness in (witness_r, witness_h, all_root):
        if sum(witness) != total or any(coal(witness, row) < bound
                                        for row, bound in bounds.items()):
            raise AssertionError(("singleton witness", n, witness))

    # Both positive covers partition the non-top players and contain both tops
    # three times. Thus weights 1/4 give eta=1/4 and alpha=(1/2,1/2).
    for cover in covers[1:]:
        for player in range(2, n):
            if sum((row >> player) & 1 for row in cover) != 1:
                raise AssertionError(("outsider load", n, cover, player))
        for player in (0, 1):
            if sum((row >> player) & 1 for row in cover) != 3:
                raise AssertionError(("top load", n, cover, player))

    avg_all = 1 + (A - 4) / m
    avg_J = 1 + (A - 4) / p
    avg_K = 1 + (A - 4) / q
    reduced = (
        (F(6), F(6), F(4), F(4)) + (avg_all,) * m,
        (F(6), F(6), F(4), F(4)) + (F(1),) * p + (avg_K,) * q,
        (F(6), F(6), F(4), F(4)) + (avg_J,) * p + (F(1),) * q,
    )
    for point in reduced:
        if sum(point) != total or point == z:
            raise AssertionError(("reduced selector", n, point))
        if any(coal(point, row) < bound for row, bound in bounds.items()
               if row in (row_a, row_b)):
            raise AssertionError(("Cx feasibility", n, point))

    # Cross blocking: cover 1 shifts A-4 from a to K; cover 2 shifts it to J.
    d_left = tuple(reduced[1][i] - z[i] for i in range(n))
    d_right = tuple(reduced[2][i] - z[i] for i in range(n))
    if not (coal(d_left, row_aJ) < 0 and coal(d_left, row_aK) == 0
            and coal(d_right, row_aK) < 0 and coal(d_right, row_aJ) == 0):
        raise AssertionError(("cross blockers", n))

    return {
        "n": n, "p": p, "q": q, "A": str(A),
        "total": str(total), "u": str(u), "top": str(top),
        "slack_J": str(slack_J), "slack_K": str(slack_K),
        "rows": list(rows), "covers": [list(c) for c in covers],
        "reduced_lmax": [list(map(str, point)) for point in reduced],
        "cover_union_exhausts_z_tight_menu": True,
        "common_staged_descent": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    dimensions = [verify_dimension(n) for n in range(6, 65)]
    payload = {
        "claim": "independent algebraic PXC106 all-n cross-cover audit",
        "dimensions_checked": [6, 64],
        "explicit_specialization": "p=1, q=n-5, A=4+1/(n-3)",
        "checks": dimensions,
        "proof_interfaces": {
            "lmin": (
                "R-sum(JK)>=16-A-(p+q) gives floor "
                "u=(A+p+q)/(p+q+1); equality pins every non-top coordinate"
            ),
            "lmax": (
                "either three-row cover gives R>=12; residual row bounds "
                "pin b=4, a=A, sum(J)=p, sum(K)=q and block equalization"
            ),
            "classification": (
                "the cover union exhausts the z-tight menu; its equations pin "
                "a,b and both block sums, leaving no staged descent"
            ),
        },
        "independence": (
            "standalone Fraction incidence/algebra checker; no project LP, "
            "selector, cover, family, or discovery imports"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

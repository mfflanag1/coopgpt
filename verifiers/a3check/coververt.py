"""Vertices of the fractional-cover polyhedron at n = 5.

P = { w in R^{31}_{>=0} : sum_{S ni i} w_S >= 1 for every i in N },
the columns running over ALL nonempty S subseteq N (including N itself).

Why vertices suffice.  In the reduction of route1 (P9), the M-side of A3 holds
at v iff  min_{w in P} sum_S w_S h(S) >= h(N)  with h(S) = nu|S| - v(S) >= 0.
P is contained in the nonnegative orthant, so it has no lines and its recession
cone is that orthant; since h >= 0 the objective is bounded below on it, so the
minimum is attained at a VERTEX.  A vertex has |supp(w)| <= n = 5 (a vertex
needs 31 active constraints, of which at most 5 are cover rows), its support
must cover N, and it is the unique solution of A[I,W] w = 1 for some set I of
|W| tight rows.  Enumerating (W, I) therefore enumerates all vertices.
"""
from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction as F

N = 5
FULL = (1 << N) - 1
SETS = list(range(1, FULL + 1))


def solve(A, b):
    k = len(A)
    M = [[F(x) for x in A[r]] + [F(b[r])] for r in range(k)]
    ncol = len(A[0])
    piv = []
    rr = 0
    for c in range(ncol):
        p = next((r for r in range(rr, k) if M[r][c] != 0), None)
        if p is None:
            return None
        M[rr], M[p] = M[p], M[rr]
        pv = M[rr][c]
        M[rr] = [q / pv for q in M[rr]]
        for r in range(k):
            if r != rr and M[r][c] != 0:
                f = M[r][c]
                M[r] = [M[r][j] - f * M[rr][j] for j in range(ncol + 1)]
        piv.append(c)
        rr += 1
    if len(piv) != ncol:
        return None
    return [M[i][ncol] for i in range(ncol)]


def main():
    verts = set()
    for k in range(1, N + 1):
        seen = 0
        for W in itertools.combinations(SETS, k):
            u = 0
            for S in W:
                u |= S
            if u != FULL:
                continue
            seen += 1
            for I in itertools.combinations(range(N), k):
                A = [[1 if S >> i & 1 else 0 for S in W] for i in I]
                w = solve(A, [1] * k)
                if w is None or any(x <= 0 for x in w):
                    continue
                if any(sum(w[j] for j, S in enumerate(W) if S >> i & 1) < 1
                       for i in range(N)):
                    continue
                verts.add(tuple(sorted((S, w[j]) for j, S in enumerate(W))))
        print(f"  |supp| = {k}: {seen} covering supports, "
              f"{len(verts)} vertices so far", flush=True)
    print(f"total vertices of P: {len(verts)}")
    out = [[[S, str(x)] for S, x in v] for v in sorted(verts)]
    json.dump(out, open(
        "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/"
        "scratchpad/sel/a3check/coververts.json", "w"))
    # excess profile: how many are balanced (excess 0)?
    bal = 0
    for v in verts:
        c = [sum(x for S, x in v if S >> i & 1) for i in range(N)]
        if all(y == 1 for y in c):
            bal += 1
    print(f"  of which balanced (all loads exactly 1): {bal}; "
          f"strictly over-covering: {len(verts) - bal}")


if __name__ == "__main__":
    main()

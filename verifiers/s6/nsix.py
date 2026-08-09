"""Task #32 Phase 1: general-n machinery for the s(6) recon.

Everything here is the n-agnostic form of what #22/#27 built at n=5.  Two
things from n=5 are DELIBERATELY ABSENT because they depend on A3, which is
FALSE on the M-side from n=6 (paper5 obs:Mside):
  * the anchor conditions (lem:anchors (a),(b) as disjunctions over attaining
    coalitions) -- these presuppose nu = M and lambda = mu;
  * L3 (2M + 3mu <= T), whose proof goes through the ceiling anchor.
What survives unchanged, because every proof is a perturbation inside the core
and never mentions the number of players:
  L5, L6, L7, L7', L1'', L11, L12, L13, L14-L17, and L4.
The two pieces of pipeline 2 are likewise dimension-free: Theorem A (exactness
is existential and linear) and the staged Farkas certificates with their mirror.

Nothing here assumes A3 anywhere.
"""
from __future__ import annotations
import itertools
from fractions import Fraction as F

import z3


def compositions(n):
    out = []
    for k in range(1, n + 1):
        for cut in itertools.combinations(range(1, n), k - 1):
            p = (0,) + cut + (n,)
            out.append(tuple(p[i + 1] - p[i] for i in range(k)))
    return out


def tables(r, c):
    A, B = len(r), len(c)

    def rows(tot, colrem, j, acc):
        if j == B:
            if tot == 0:
                yield list(acc)
            return
        for x in range(min(tot, colrem[j]) + 1):
            yield from rows(tot - x, colrem, j + 1, acc + [x])

    def rec(k, colrem):
        if k == A:
            if all(v == 0 for v in colrem):
                yield []
            return
        for row in rows(r[k], colrem, 0, []):
            yield from ([row] + rest
                        for rest in rec(k + 1,
                                        [colrem[j] - row[j] for j in range(B)]))
    return list(rec(0, list(c)))


def q(x):
    x = F(x)
    return z3.RealVal(f"{x.numerator}/{x.denominator}")


def layout(n, r, c, tbl):
    cell = []
    for k in range(len(r)):
        for l in range(len(c)):
            cell += [(k, l)] * tbl[k][l]
    assert len(cell) == n
    return cell


def levels(n, r, c, s):
    """Level variables with the stratum orderings and totals."""
    A, B = len(r), len(c)
    m = [z3.Real(f"m{k}") for k in range(A)]
    Mv = [z3.Real(f"M{l}") for l in range(B)]
    s.add(m[0] >= 0, Mv[0] >= 0)
    s.add(z3.Sum([q(r[k]) * m[k] for k in range(A)]) == 1)
    s.add(z3.Sum([q(c[l]) * Mv[l] for l in range(B)]) == 1)
    s += [m[k] < m[k + 1] for k in range(A - 1)]
    s += [Mv[l] < Mv[l + 1] for l in range(B - 1)]
    return m, Mv


def handnet(n, r, c, tbl, R):
    """The A3-FREE hand net: levels + L1'' + L7 + L7' + L11 + L12, against
    ratio >= R.  Returns 'L1-excluded' | 'killed' | 'survives'."""
    if c[-1] == 1:
        return "L1-excluded"                                      # L1''
    FULL = (1 << n) - 1
    cell = layout(n, r, c, tbl)
    s = z3.Solver()
    m, Mv = levels(n, r, c, s)
    A, B = len(r), len(c)
    x = [m[cell[i][0]] for i in range(n)]
    z = [Mv[cell[i][1]] for i in range(n)]
    mu, Mx = m[0], Mv[B - 1]
    s.add(z3.Or([m[k] >= Mx for k in range(A) if tbl[k][B - 1]]))  # L7 at x
    s.add(z3.Or([Mv[l] <= mu for l in range(B) if tbl[0][l]]))     # L7' at z
    xS = lambda S: z3.Sum([x[i] for i in range(n) if S >> i & 1])
    zS = lambda S: z3.Sum([z[i] for i in range(n) if S >> i & 1])
    for i in range(n):
        for j in range(n):
            subs = [S for S in range(1, FULL)
                    if (S >> j & 1) and not (S >> i & 1)]
            if cell[i][0] < cell[j][0]:                            # L11
                s.add(z3.Or([xS(S) <= zS(S) for S in subs]))
            if cell[i][1] < cell[j][1]:                            # L12
                s.add(z3.Or([zS(S) <= xS(S) for S in subs]))
    s.add(z3.Sum([q(tbl[k][l]) * z3.Abs(m[k] - Mv[l])
                  for k in range(A) for l in range(B) if tbl[k][l]]) >= q(R))
    res = s.check()
    assert res in (z3.sat, z3.unsat), f"z3 returned {res}"
    return "survives" if res == z3.sat else "killed"


def pipeline2(n, r, c, tbl, R, fail=True, certs=True):
    """Theorem A exactness + staged Farkas certificates for Lmin and Lmax.
    No A3, no facet catalogue.  Returns a z3 Solver."""
    FULL = (1 << n) - 1
    PROPER = list(range(1, FULL))
    SZ = [bin(S).count("1") for S in range(1 << n)]
    cell = layout(n, r, c, tbl)
    A, B = len(r), len(c)
    s = z3.Solver()
    m, Mv = levels(n, r, c, s)
    x = [m[cell[i][0]] for i in range(n)]
    z = [Mv[cell[i][1]] for i in range(n)]
    v = [z3.Real(f"v{S}") for S in range(1 << n)]
    s.add(v[0] == 0, v[FULL] == 1)
    for i in range(n):
        s.add(v[1 << i] == 0)
    xS = lambda S: z3.Sum([x[i] for i in range(n) if S >> i & 1])
    zS = lambda S: z3.Sum([z[i] for i in range(n) if S >> i & 1])
    for S in PROPER:
        s.add(v[S] <= xS(S))
        s.add(v[S] <= zS(S))
    # Theorem A: one attaining core point per proper coalition
    for S in PROPER:
        w = [z3.Real(f"w{S}_{i}") for i in range(n)]
        s.add(z3.Sum(w) == 1)
        for Aa in PROPER:
            s.add(z3.Sum([w[i] for i in range(n) if Aa >> i & 1]) >= v[Aa])
        s.add(z3.Sum([w[i] for i in range(n) if S >> i & 1]) == v[S])
    if certs:
        rowmask = [[i for i in range(n) if cell[i][0] == k] for k in range(A)]
        colmask = [[i for i in range(n) if cell[i][1] == l] for l in range(B)]
        _farkas(s, n, v, x, rowmask, False, "F", PROPER)
        _farkas(s, n, v, z, colmask[::-1], True, "C", PROPER)
    ratio = z3.Sum([q(tbl[k][l]) * z3.Abs(m[k] - Mv[l])
                    for k in range(A) for l in range(B) if tbl[k][l]])
    s.add(ratio > q(R) if fail else ratio <= q(R))
    return s, v, m, Mv, ratio


def _farkas(s, n, v, phi, blocks, ceiling, tag, PROPER):
    sgn = +1 if ceiling else -1
    rhs = -1 if ceiling else +1
    phiS = lambda S: z3.Sum([phi[i] for i in range(n) if S >> i & 1])
    pinned = []
    for t, Bt in enumerate(blocks):
        for i in Bt:
            y = {Aa: z3.Real(f"{tag}y{t}_{i}_{Aa}") for Aa in PROPER}
            eta = z3.Real(f"{tag}e{t}_{i}")
            rho = {l: z3.Real(f"{tag}r{t}_{i}_{l}") for l in pinned}
            sig = {cc: z3.Real(f"{tag}s{t}_{i}_{cc}") for cc in Bt}
            for Aa in PROPER:
                s.add(y[Aa] >= 0)
                s.add(z3.Or(y[Aa] == 0, phiS(Aa) == v[Aa]))
            for cc in Bt:
                s.add(sig[cc] >= 0)
            for j in range(n):
                e = -z3.Sum([y[Aa] for Aa in PROPER if Aa >> j & 1]) + eta
                if j in pinned:
                    e = e + rho[j]
                if j in Bt:
                    e = e + sgn * sig[j]
                s.add(e == z3.RealVal(rhs if j == i else 0))
        pinned = pinned + list(Bt)

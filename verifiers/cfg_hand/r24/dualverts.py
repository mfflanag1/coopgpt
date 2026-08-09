"""ROUTE 2: enumerate the vertices of the (game-free) dual polyhedron for (R).

    Q = { (eta, gamma) : gamma >= 0 on the 30 proper coalitions,
                         eta + Gamma_k >= w_k for every player k },
    w = 2 at p, 1 at q, 0 at x, y, z.       cost(eta, gamma) = eta*T + sum gamma_S f(S).

(R) says min over Q of the cost is >= 3*lambda.  Q does not depend on the game,
so its vertices are a finite game-free list.

DIMENSION COUNT.  dim Q = 31.  A vertex needs 31 tight constraints among
{gamma_S >= 0 (30 of them), eta + Gamma_k >= w_k (5)}.  If m = |supp gamma|
then 30 - m of the first kind are tight, so exactly m + 1 of the second kind
are, whence m <= 4.  Enumerate m = 0..4, choose the support and the m+1 tight
players, solve the (m+1)x(m+1) system, keep feasible nonsingular solutions.

PRUNING (valid).  cost is nondecreasing in eta (T > 0) and in each gamma_S
(f >= 0).  So if vertex A >= vertex B componentwise, A can be discarded: B is
feasible and never costlier.  The retained list still contains a minimiser.

Lemma D disposes of every vertex with eta >= 0.  We print the eta < 0 ones.
"""
import itertools
from fractions import Fraction as F

P, Q, X, Y, Z = 0, 1, 2, 3, 4
W = [F(2), F(1), F(0), F(0), F(0)]
PROPER = list(range(1, 31))
NAMES = "pqxyz"


def nm(S):
    return "".join(NAMES[i] for i in range(5) if S >> i & 1)


def solve(M, rhs):
    """Exact square solve; None if singular."""
    k = len(M)
    A = [M[i][:] + [rhs[i]] for i in range(k)]
    for c in range(k):
        p = next((i for i in range(c, k) if A[i][c] != 0), None)
        if p is None:
            return None
        A[c], A[p] = A[p], A[c]
        d = A[c][c]
        A[c] = [t / d for t in A[c]]
        for i in range(k):
            if i != c and A[i][c] != 0:
                fac = A[i][c]
                A[i] = [A[i][j] - fac * A[c][j] for j in range(k + 1)]
    return [A[i][k] for i in range(k)]


def enumerate_vertices():
    verts = {}
    for m in range(0, 5):
        for supp in itertools.combinations(PROPER, m):
            for tight in itertools.combinations(range(5), m + 1):
                M, rhs = [], []
                for k in tight:
                    M.append([F(1)] + [F(1) if S >> k & 1 else F(0)
                                       for S in supp])
                    rhs.append(W[k])
                sol = solve(M, rhs)
                if sol is None:
                    continue
                eta, gam = sol[0], sol[1:]
                if any(g <= 0 for g in gam):
                    continue          # support must be strictly positive
                G = [sum(gam[j] for j, S in enumerate(supp) if S >> k & 1)
                     for k in range(5)]
                if any(eta + G[k] < W[k] for k in range(5)):
                    continue
                key = (eta, tuple(sorted(zip(supp, gam))))
                verts[key] = (eta, dict(zip(supp, gam)), G)
    return list(verts.values())


def dominates(a, b):
    """a >= b componentwise (so a is discardable)."""
    ea, ga, _ = a
    eb, gb, _ = b
    if ea < eb:
        return False
    for S, g in gb.items():
        if ga.get(S, F(0)) < g:
            return False
    return True


def main():
    V = enumerate_vertices()
    print(f"vertices of Q: {len(V)}")
    neg = [v for v in V if v[0] < 0]
    print(f"  with eta >= 0 (killed by Lemma D): {len(V) - len(neg)}")
    print(f"  with eta < 0  (the live branch)  : {len(neg)}")

    # prune dominated vertices among ALL vertices (a dominated vertex is never
    # a strict minimiser)
    keep = []
    for i, a in enumerate(V):
        if any(j != i and dominates(a, b) and not dominates(b, a)
               for j, b in enumerate(V)):
            continue
        keep.append(a)
    kneg = [v for v in keep if v[0] < 0]
    print(f"after domination pruning: {len(keep)} vertices, "
          f"{len(kneg)} with eta < 0")

    # canonicalise the eta<0 survivors up to permuting x, y, z
    perms = list(itertools.permutations([X, Y, Z]))
    shapes = {}
    for eta, gam, G in kneg:
        best = None
        for pm in perms:
            mp = {P: P, Q: Q, X: pm[0], Y: pm[1], Z: pm[2]}
            g2 = {}
            for S, g in gam.items():
                S2 = 0
                for k in range(5):
                    if S >> k & 1:
                        S2 |= 1 << mp[k]
                g2[S2] = g
            key = (eta, tuple(sorted(g2.items())))
            if best is None or key < best:
                best = key
        shapes.setdefault(best, 0)
        shapes[best] += 1
    print(f"\neta < 0 shapes up to relabelling x,y,z: {len(shapes)}")
    for (eta, gitems), cnt in sorted(shapes.items(), key=lambda kv: (kv[0][0],
                                                                    len(kv[0][1]))):
        gs = "  ".join(f"{g}*f({nm(S)})" for S, g in gitems)
        tot = sum(g * bin(S).count("1") for S, g in gitems)
        loads = [sum(g for S, g in gitems if S >> k & 1) for k in range(5)]
        print(f"  eta={eta}  cost = {eta}*T + {gs}"
              f"   [sum g|S| = {tot}, loads {loads}, orbit {cnt}]")


if __name__ == "__main__":
    main()

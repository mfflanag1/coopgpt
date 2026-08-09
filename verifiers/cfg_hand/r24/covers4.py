"""IS THE COVER RESIDUE EMPTY AT n = 4 (and n = 3)?

Same reduction as REPORT_A3's:  mu >= lambda  iff  for every vertex beta of the
fractional-cover polyhedron on PROPER coalitions
        sum_S beta_S g(S) >= g(N),      g(S) = f(S) - lambda|S| >= 0,
                                        g(N) = T - n*lambda >= 0.
Free lemmas, in the exact form each one needs:
  B   (all loads = 1)  needs only a core point.
  E1  (|E| = 1, E = {k}, E = excess set) needs a core point with y_k >= lambda.
  C   (excess weights constant on E) needs a core point with y(E) >= lambda|E|.
E1 and C are both instances of
        (EXlam)   max over the core of y(E) >= lambda|E|   for every E,
which EXACT games satisfy trivially (max = f(E) >= lambda|E|) and which is
STRICTLY weaker than exactness.

If B + C + E1 kill every cover vertex at n = 4, then:
   THEOREM(4).  Any four-player game with a nonempty core satisfying (EXlam)
   has mu >= lambda.
That is the four-player input the round-24 slice reduction needs.
"""
import itertools
from fractions import Fraction as F


def solve(M, rhs):
    k = len(M)
    if k == 0:
        return []
    A = [M[i][:] + [rhs[i]] for i in range(k)]
    ncol = len(M[0])
    for c in range(min(k, ncol)):
        p = next((i for i in range(c, k) if A[i][c] != 0), None)
        if p is None:
            return None
        A[c], A[p] = A[p], A[c]
        d = A[c][c]
        A[c] = [t / d for t in A[c]]
        for i in range(k):
            if i != c and A[i][c] != 0:
                fac = A[i][c]
                A[i] = [A[i][j] - fac * A[c][j] for j in range(ncol + 1)]
    return [A[i][ncol] for i in range(k)]


def cover_vertices(n):
    full = (1 << n) - 1
    proper = list(range(1, full))
    m = len(proper)
    verts = set()
    # a vertex of {beta >= 0, load_k >= 1} has m tight constraints among
    # {beta_S = 0 (m), load_k >= 1 (n)}; support size s => s tight loads,
    # so s <= n.
    for s in range(0, n + 1):
        for supp in itertools.combinations(proper, s):
            for tight in itertools.combinations(range(n), s):
                M = [[F(1) if S >> k & 1 else F(0) for S in supp]
                     for k in tight]
                sol = solve(M, [F(1)] * s)
                if sol is None or any(b <= 0 for b in sol):
                    continue
                load = [sum(b for b, S in zip(sol, supp) if S >> k & 1)
                        for k in range(n)]
                if any(l < 1 for l in load):
                    continue
                verts.add(tuple(sorted(zip(supp, sol))))
    return sorted(verts)


def classify(n, verts):
    full = (1 << n) - 1
    counts = dict(balanced=0, E1=0, C=0, residue=0)
    residue = []
    for vt in verts:
        load = [sum(b for S, b in vt if S >> k & 1) for k in range(n)]
        E = [k for k in range(n) if load[k] > 1]
        if not E:
            counts["balanced"] += 1
        elif len(E) == 1:
            counts["E1"] += 1
        elif len(set(load[k] for k in E)) == 1:
            counts["C"] += 1
        else:
            counts["residue"] += 1
            residue.append((vt, load, E))
    return counts, residue


for n in (3, 4, 5):
    V = cover_vertices(n)
    c, res = classify(n, V)
    print(f"n = {n}:  cover vertices {len(V)}   balanced {c['balanced']}  "
          f"|E|=1 {c['E1']}  equal-excess {c['C']}  RESIDUE {c['residue']}")
    seen = set()
    for vt, load, E in res[:400]:
        shape = tuple(sorted((bin(S).count("1"), str(b)) for S, b in vt))
        key = (shape, tuple(sorted(str(load[k]) for k in E)))
        if key in seen:
            continue
        seen.add(key)
        if len(seen) <= 6:
            print("     residue shape:",
                  "  ".join(f"{b}*[{''.join('abcde'[i] for i in range(n) if S >> i & 1)}]"
                            for S, b in vt),
                  " loads", [str(x) for x in load])
    if res:
        print(f"     distinct residue shapes (by size profile): {len(seen)}")

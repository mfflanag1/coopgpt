"""Exact verification of the candidate SPLIT packet at a slack h=2 boundary.

Core polytope   C = {x >= 0 : x(N) = 7,
                    x(abe) >= 4, x(abd) >= 4, x(ade) >= 5, x(bde) >= 5}
with a = 0, b = 1, c = 2, d = 3, e = 4.  v(S) = min_C x(S) is exact with
Core(v) = C.  Claim: v is singleton-normalized, Lmin(v) = (1,1,1,2,2),
H = {d,e} is a slack strict richer suffix, and BOTH proper traces {d}, {e}
carry phi-tight coalitions, giving a split packet with delta > 0.
"""
from __future__ import annotations

import itertools
import sys
from fractions import Fraction as F

SCR = "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad"
sys.path.insert(0, SCR)
import audit
import catalogue
import pack
import sbcheck

n = 5
V = F(7)
CONS = [(0b10011, F(4)), (0b01011, F(4)), (0b11001, F(5)), (0b11010, F(5))]


def nm(mask):
    return "".join("abcde"[i] for i in range(n) if mask >> i & 1) or "0"


def vertices():
    ineq = [([F(1) if T >> i & 1 else F(0) for i in range(n)], r) for T, r in CONS]
    ineq += [([F(1) if i == j else F(0) for i in range(n)], F(0)) for j in range(n)]
    eq = ([F(1)] * n, V)
    out = set()
    for combo in itertools.combinations(range(len(ineq)), n - 1):
        A = [eq[0]] + [ineq[c][0] for c in combo]
        b = [eq[1]] + [ineq[c][1] for c in combo]
        x = audit.solve(A, b)
        if x is None:
            continue
        if all(sum(a[i] * x[i] for i in range(n)) >= rhs for a, rhs in ineq):
            out.add(tuple(x))
    return sorted(out)


def main():
    verts = vertices()
    print(f"core vertices ({len(verts)}):")
    for x in verts:
        print("   ", [str(q) for q in x])
    full = (1 << n) - 1
    v = [F(0)] * (1 << n)
    for S in range(1, full):
        v[S] = min(sum(x[i] for i in range(n) if S >> i & 1) for x in verts)
    v[full] = V
    print("\nsingleton values:", [str(v[1 << i]) for i in range(n)])
    assert all(v[1 << i] == 0 for i in range(n)), "not singleton-normalized"
    assert audit.is_exact(n, v, verts), "not exact"
    print("exact: yes   singleton-normalized: yes")

    phi = audit.lmin(n, v)
    print("Lmin =", [str(q) for q in phi])
    blocks = audit.strata(phi)
    print("strata (poorest first):", [[nm(1 << i) for i in b] for b in blocks])
    Hmask = sum(1 << i for i in blocks[-1])
    s = sum(phi[i] for i in range(n) if Hmask >> i & 1) - v[Hmask]
    print(f"H = {nm(Hmask)}   v(H) = {v[Hmask]}   phi(H) = "
          f"{sum(phi[i] for i in range(n) if Hmask>>i&1)}   slack = {s}")
    assert s > 0

    tight = [S for S in range(1, full)
             if sum(phi[i] for i in range(n) if S >> i & 1) == v[S]]
    print("tight proper coalitions:", sorted(nm(S) for S in tight))
    print("traces on H:", sorted({nm(S & Hmask) for S in tight if S & Hmask}))

    pks, _ = pack.packets(n, v, phi, Hmask)
    table, _ = catalogue.index(n)
    print(f"\npackets with delta>0: {len(pks)}")
    seen = {}
    for p in pks:
        seen.setdefault(catalogue.canon(n, p["lam"]), []).append(p)
    for key, grp in seen.items():
        p = grp[0]
        rows = table.get(key)
        verdict, wit = sbcheck.classify(n, list(p["lam"]))
        ft = len(p["traces"]) == 1 and p["traces"][0] == Hmask
        print(f"  [{len(grp)}] {catalogue.pretty(n, p['lam'])} = {p['r_const']}*1_N")
        print(f"      traces {[nm(R) for R in p['traces']]} lift {[nm(S) for S in p['lift']]}"
              f"  b={p['b']} delta={p['delta']}  {'FULL-TRACE' if ft else 'SPLIT'}")
        print(f"      catalogue rows: {rows if rows else 'NOT CATALOGUED'};  {verdict}"
              + (f"  (decomposed by E={nm(wit)})" if isinstance(wit, int) else ""))


if __name__ == "__main__":
    main()

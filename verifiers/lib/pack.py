"""Enumerate the one-packet systems (P) at a slack boundary and match them
against the Studeny-Kratochvil catalogue.

Independent of the project's source: games are rebuilt from the manuscript's
displayed generator rows, Lmin is recomputed with exact staged z3 optimization
(audit.lmin), and the packets are enumerated from the statement of
Theorem 3 rather than from any project code.
"""
from __future__ import annotations

import itertools
import sys
from fractions import Fraction as F

import audit
import catalogue
import sbcheck


# ---------------------------------------------------------------- games

def family1(m):
    """Proposition 6 (unique-richest).  Players 0..m-1 poorer, m richer."""
    n = m + 1
    r = m
    def e(i, c=1):
        v = [F(0)] * n
        v[i] = F(c)
        return v
    def add(*vs):
        return [sum(col) for col in zip(*vs)]
    g1 = add(e(3, m - 1), e(r, m - 1))
    g2 = add(e(2, m - 1), e(3, m - 1))
    g3 = add(e(0), e(1), e(2), e(4, m - 4) if m >= 5 else e(0, 0), e(r, m - 1))
    g4 = add(*[e(i) for i in range(m)], e(r, m - 2))
    return n, [tuple(g) for g in (g1, g2, g3, g4)], tuple(g4), (1 << r)


def family2(m, h):
    """Proposition 7 (two-poorer internal sacrifice).
    Layout: 0..m-1 poorer with p1=0, p2=1, Q=2..m-1;
            H = m..m+h-1 with a=m, b=m+1, K=m+2..m+h-1."""
    D = (h - 2) * (h - 3)
    r = h - 2
    n = m + h
    p1, p2 = 0, 1
    Q = list(range(2, m))
    a, b = m, m + 1
    K = list(range(m + 2, n))
    assert len(K) == r
    H = list(range(m, n))

    def vec(**_):
        return [F(0)] * n

    rows = []
    u = vec(); u[p2] = D
    for j in Q: u[j] = D
    u[a] = u[b] = 3 * D
    for k in K: u[k] = (2 * r - 1) * (r - 1)
    rows.append(u)

    z = vec(); z[p1] = 4 * D
    for j in Q: z[j] = D
    for k in K: z[k] = 2 * (r * r - 1)
    rows.append(z)

    for k in K:
        w = vec(); w[p1] = D
        for j in Q: w[j] = D
        w[a] = w[b] = 3 * D
        for kk in K:
            if kk != k:
                w[kk] = r * (2 * r - 1)
        rows.append(w)

    phi = vec()
    for i in range(m): phi[i] = D
    for i in H: phi[i] = 2 * D
    rows.append(phi)

    for j in Q:
        q = list(phi); q[p1] += D; q[j] -= D
        rows.append(q)

    Hmask = sum(1 << i for i in H)
    return n, [tuple(g) for g in rows], tuple(phi), Hmask


def family3(m, h):
    """Proposition 8 (three-poorer escape).
    Layout: p1=0, p2=1, p3=2, Q=3..m-1; H = m..m+h-1, r1=m, rh=n-1."""
    n = m + h
    p1, p2, p3 = 0, 1, 2
    Q = list(range(3, m))
    H = list(range(m, n))
    r1, rh = H[0], H[-1]

    def vec():
        return [F(0)] * n

    a = vec(); a[p1] = 2; a[p3] = 3
    for j in Q: a[j] = 1
    a[r1] = 5
    for i in H:
        if i not in (r1, rh): a[i] = 3

    b = vec(); b[p2] = 2; b[p3] = 1
    for j in Q: b[j] = 1
    b[r1] = 4
    for i in H:
        if i != r1: b[i] = 3

    c = vec()
    for j in Q: c[j] = 1
    c[rh] = 3 * h + 4

    phi = vec(); phi[p1] = 1; phi[p2] = 1; phi[p3] = 2
    for j in Q: phi[j] = 1
    for i in H: phi[i] = 3

    rows = [a, b, c, phi]
    for j in Q:
        q = list(phi); q[p1] += 1; q[j] -= 1
        rows.append(q)

    Hmask = sum(1 << i for i in H)
    return n, [tuple(g) for g in rows], tuple(phi), Hmask


# ------------------------------------------------- minimal balanced collections

def min_balanced(elems):
    """All minimal balanced collections on the set `elems` (list of players),
    as [(collection, {R: weight})] with R a bitmask."""
    subs = [sum(1 << i for i in c)
            for k in range(1, len(elems) + 1)
            for c in itertools.combinations(elems, k)]
    target = sum(1 << i for i in elems)
    out = []
    for size in range(1, len(elems) + 1):
        for coll in itertools.combinations(subs, size):
            A = [[F(1) if R >> i & 1 else F(0) for R in coll] for i in elems]
            sol = _solve_unique(A, [F(1)] * len(elems))
            if sol is None or any(x <= 0 for x in sol):
                continue
            # minimality: uniqueness of the solution is exactly independence of
            # the incidence columns, which characterises the vertices of P_H.
            out.append((coll, dict(zip(coll, sol))))
    return out


def _solve_unique(A, b):
    """Least-squares-free exact solve of A x = b; None unless a unique solution
    exists (columns independent and system consistent)."""
    rows = [list(r) + [v] for r, v in zip(A, b)]
    nr, nc = len(rows), len(A[0])
    piv = []
    rr = 0
    for c in range(nc):
        p = next((i for i in range(rr, nr) if rows[i][c] != 0), None)
        if p is None:
            continue
        rows[rr], rows[p] = rows[p], rows[rr]
        pv = rows[rr][c]
        rows[rr] = [q / pv for q in rows[rr]]
        for i in range(nr):
            if i != rr and rows[i][c] != 0:
                f = rows[i][c]
                rows[i] = [rows[i][j] - f * rows[rr][j] for j in range(nc + 1)]
        piv.append(c)
        rr += 1
    if len(piv) != nc:
        return None                      # free variable -> not a vertex
    for i in range(rr, nr):
        if rows[i][nc] != 0:
            return None                  # inconsistent
    x = [F(0)] * nc
    for i, c in enumerate(piv):
        x[c] = rows[i][nc]
    return x


# ------------------------------------------------------------------ packets

def packets(n, v, phi, Hmask):
    """Every lifted packet of Theorem 3 with delta>0, as dicts."""
    full = (1 << n) - 1
    L = [i for i in range(n) if not Hmask >> i & 1]
    Hset = [i for i in range(n) if Hmask >> i & 1]
    tight = [S for S in range(1, full)
             if sum(phi[i] for i in range(n) if S >> i & 1) == v[S]]
    out = []
    for coll, beta in min_balanced(Hset):
        # choices of a tight preimage for each trace
        options = []
        for R in coll:
            opts = [S for S in tight if S & Hmask == R]
            if not opts:
                options = None
                break
            options.append(opts)
        if options is None:
            continue
        for lift in itertools.product(*options):
            r = {i: sum(beta[R] for R, S in zip(coll, lift) if S >> i & 1)
                 for i in L}
            bmax = max(r.values())
            u = {i: bmax - r[i] for i in L}
            delta = 1 + sum(u.values()) - bmax
            if delta <= 0:
                continue
            lam = {}
            for R, S in zip(coll, lift):
                lam[S] = lam.get(S, F(0)) + beta[R]
            for i in L:
                if u[i]:
                    S = Hmask | (1 << i)
                    lam[S] = lam.get(S, F(0)) + u[i]
            lam[Hmask] = lam.get(Hmask, F(0)) - delta
            lam = {S: c for S, c in lam.items() if c != 0}
            # integer-normalize
            den = 1
            for c in lam.values():
                den = den * c.denominator // _g(den, c.denominator)
            lam = {S: int(c * den) for S, c in lam.items()}
            load = [sum(c for S, c in lam.items() if S >> i & 1) for i in range(n)]
            assert len(set(load)) == 1, (lam, load)
            out.append({
                "traces": coll, "lift": lift, "beta": beta,
                "r": r, "b": bmax, "u": u, "delta": delta,
                "lam": lam, "r_const": load[0],
            })
    return out, tight


def _g(a, b):
    while b:
        a, b = b, a % b
    return a


# ------------------------------------------------------------------- driver

def nm(n, mask):
    return "".join("abcdefgh"[i] for i in range(n) if mask >> i & 1) or "0"


def report(label, n, gens, phi_claim, Hmask, table):
    v = audit.envelope(n, gens)
    for i in range(n):
        assert v[1 << i] == 0, f"{label}: not singleton-normalized at {i}"
    phi = audit.lmin(n, v)
    assert phi is not None, f"{label}: Lmin infeasible"
    assert tuple(phi) == tuple(map(F, phi_claim)), (
        f"{label}: Lmin mismatch\n  claimed {list(map(str,phi_claim))}\n"
        f"  computed {list(map(str,phi))}")
    slack = sum(phi[i] for i in range(n) if Hmask >> i & 1) - v[Hmask]
    print(f"\n=== {label} ===")
    print(f"  n={n}  H={nm(n,Hmask)}  Lmin={[str(q) for q in phi]}  "
          f"v(H)={v[Hmask]}  s(H)={slack}")
    assert slack > 0, f"{label}: boundary is not slack"
    pks, tight = packets(n, v, phi, Hmask)
    print(f"  tight proper coalitions: {', '.join(sorted(nm(n,S) for S in tight))}")
    print(f"  packets with delta>0: {len(pks)}")
    seen = {}
    for p in pks:
        key = catalogue.canon(n, p["lam"])
        seen.setdefault(key, []).append(p)
    facets = 0
    for key, group in sorted(seen.items(), key=lambda kv: -len(kv[1])):
        p = group[0]
        found = table is not None and key in table
        verdict, wit = sbcheck.classify(n, list(p["lam"]))
        if verdict.startswith("indecomposable"):
            facets += 1
        if table is not None:
            assert found == verdict.startswith("indecomposable"), (
                "catalogue lookup and independent classifier disagree")
        print(f"   [{len(group):2d} packet(s)] {catalogue.pretty(n, p['lam'])}"
              f"  = {p['r_const']}*1_N")
        print(f"        traces {[nm(n,R) for R in p['traces']]}"
              f"  lift {[nm(n,S) for S in p['lift']]}"
              f"  delta={p['delta']}  b={p['b']}")
        extra = ""
        if isinstance(wit, int):
            extra = f"; decomposed by E={nm(n,wit)}"
        elif wit:
            extra = f"; semi-balanced subsystem {[nm(n,S) for S in wit]}"
        tag = "in catalogue" if found else (
            "n/a (n>6)" if table is None else "NOT in catalogue")
        print(f"        {verdict}{extra}  [{tag}]")
    return {"types": len(seen), "facets": facets}


CASES = {
    "41": ("family1", lambda: family1(4), 5),
    "51": ("family1", lambda: family1(5), 6),
    "61": ("family1", lambda: family1(6), 7),
    "32": ("family3", lambda: family3(3, 2), 5),
    "33": ("family3", lambda: family3(3, 3), 6),
    "42": ("family3", lambda: family3(4, 2), 6),
    "43": ("family3", lambda: family3(4, 3), 7),
    "24": ("family2", lambda: family2(2, 4), 6),
    "34": ("family2", lambda: family2(3, 4), 7),
    "25": ("family2", lambda: family2(2, 5), 7),
}


def main():
    which = sys.argv[1:] or list(CASES)
    tabs = {5: catalogue.index(5)[0], 6: catalogue.index(6)[0]}
    summary = []
    for key in which:
        fam, build, n = CASES[key]
        m, h = int(key[0]), int(key[1])
        ng, gens, phi, H = build()
        res = report(f"{fam}  (m,h)=({m},{h})   n={ng}", ng, gens, phi, H,
                     tabs.get(ng))
        summary.append((fam, m, h, ng, res["types"], res["facets"]))
    print("\n  family    m  h  n   packet types  facet-defining")
    for fam, m, h, ng, t, f in summary:
        print(f"  {fam:9s} {m:2d} {h:2d} {ng:2d}   {t:6d}        {f:6d}"
              + ("" if t == f else "   <-- non-facet certificate"))


if __name__ == "__main__":
    main()

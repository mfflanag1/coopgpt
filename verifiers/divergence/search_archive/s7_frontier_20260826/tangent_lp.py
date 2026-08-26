"""Tangent LP polisher: maximize rho over generator entries with the combinatorial cell frozen.
Cell data from the seed: argmin generator a(S), x/z tight rows, weak orders of x and z, zero pattern.
Selectors stay certified (staged Farkas identities depend only on incidence), verified exactly afterwards."""
import sys, json
from fractions import Fraction as F
from math import lcm
from exactsel import analyze, envelope, exact_lp

def cell_lp(G, margin=F(0)):
    G = [[F(a) for a in g] for g in G]; m = len(G); n = len(G[0]); T = sum(G[0])
    r = analyze(G, verbose=False); x, z = r['x'], r['z']
    gens = [x, z] + [g for g in G if g != x and g != z]; m = len(gens)
    v = envelope(gens); full = (1 << n) - 1
    def csum(g, S): return sum(g[i] for i in range(n) if S >> i & 1)
    amin = {S: min(range(m), key=lambda r_: csum(gens[r_], S)) for S in range(1, full)}
    Tx = [S for S in range(1, full) if csum(x, S) == v[S]]; Tz = [S for S in range(1, full) if csum(z, S) == v[S]]
    P = [i for i in range(n) if x[i] > z[i]]; M = [i for i in range(n) if z[i] > x[i]]
    nv = m * n
    def var(r_, i): return r_ * n + i
    def rowvec(r_, S, coef=F(1)):
        row = [F(0)] * nv
        for i in range(n):
            if S >> i & 1: row[var(r_, i)] += coef
        return row
    A = []; b = []; always = []
    def le(row, rhs, keep=False):
        A.append(row); b.append(F(rhs))
        if keep: always.append(len(A) - 1)
    def eq(row, rhs, keep=False):
        le(row, rhs, keep); le([-c for c in row], -rhs, keep)
    for r_ in range(m):
        eq([F(1) if var(r_, i) // n == r_ else F(0) for i in range(nv)] if False else [F(1) if (k // n) == r_ else F(0) for k in range(nv)], T, True)
        for i in range(n):
            if gens[r_][i] == 0:
                row = [F(0)] * nv; row[var(r_, i)] = F(1); eq(row, 0, True)
    for S in range(1, full):
        a = amin[S]
        for r_ in range(m):
            if r_ == a: continue
            row = rowvec(a, S); row2 = rowvec(r_, S)
            le([p - q for p, q in zip(row, row2)], 0)
    for S in Tx:
        a = amin[S]
        if a != 0: eq([p - q for p, q in zip(rowvec(0, S), rowvec(a, S))], 0, True)
    for S in Tz:
        a = amin[S]
        if a != 1: eq([p - q for p, q in zip(rowvec(1, S), rowvec(a, S))], 0, True)
    def order_constraints(r_, point, ascending):
        levels = sorted(set(point), reverse=not ascending)
        blocks = [[i for i in range(n) if point[i] == L] for L in levels]
        for bl in blocks:
            for i, j in zip(bl, bl[1:]):
                row = [F(0)] * nv; row[var(r_, i)] = F(1); row[var(r_, j)] = F(-1); eq(row, 0, True)
        for b1, b2 in zip(blocks, blocks[1:]):
            i, j = b1[0], b2[0]
            row = [F(0)] * nv
            if ascending: row[var(r_, i)] = F(1); row[var(r_, j)] = F(-1)   # x_i <= x_j - margin
            else: row[var(r_, i)] = F(-1); row[var(r_, j)] = F(1)          # z_i >= z_j + margin
            le(row, -margin * T, True)
    order_constraints(0, x, True); order_constraints(1, z, False)
    for i in P:
        row = [F(0)] * nv; row[var(0, i)] = F(-1); row[var(1, i)] = F(1); le(row, 0, True)
    for i in M:
        row = [F(0)] * nv; row[var(0, i)] = F(1); row[var(1, i)] = F(-1); le(row, 0, True)
    c = [F(0)] * nv
    for i in P: c[var(0, i)] += 2; c[var(1, i)] -= 2
    st, val, sol = exact_lp(A, b, c, always)
    assert st == 'optimal', st
    newgens = [[sol[var(r_, i)] for i in range(n)] for r_ in range(m)]
    return newgens, val / T, r['rho']

def integerize(gens):
    den = 1
    for g in gens:
        for a in g: den = lcm(den, a.denominator)
    return [[int(a * den) for a in g] for g in gens]

if __name__ == '__main__':
    src = sys.argv[1]; out = sys.argv[2]; margin = F(sys.argv[3]) if len(sys.argv) > 3 else F(0)
    d = json.load(open(src)); G = d['gens']
    newgens, lp_rho, old_rho = cell_lp(G, margin)
    Gi = integerize(newgens)
    print('old rho', old_rho, float(old_rho), ' LP rho', lp_rho, float(lp_rho))
    r = analyze(Gi, verbose=False)
    print('verified rho of LP point', r['rho'], float(r['rho']), ' T =', r['T'], ' match LP:', r['rho'] == lp_rho)
    json.dump({'n': r['n'], 'T': int(r['T']), 'gens': Gi, 'rho': float(r['rho']), 'rho_exact': str(r['rho'])}, open(out, 'w'))

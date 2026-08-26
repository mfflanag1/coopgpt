"""Independent exact-rational leximin / leximax selectors for lower-envelope games.
Written from scratch this session; does not import the repository's exactlp.
Exact cutting-plane: float LP (scipy/HiGHS) proposes active rows, an exact Fraction simplex
solves the relaxation, all rows are re-checked exactly; repeat until no violation.
"""
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog

def simplex_max(A, b, c):
    """maximize c.x  s.t. A x <= b, x >= 0 (exact Fractions). Returns (status, value, x)."""
    m = len(A); n = len(c)
    art = [i for i in range(m) if b[i] < 0]
    na = len(art); N = n + m + na
    T = []; basis = []
    for i in range(m):
        row = [F(v) for v in A[i]] + [F(0)]*m + [F(0)]*na + [F(b[i])]
        row[n+i] = F(1)
        if i in art:
            row = [-v for v in row]
            row[n+m+art.index(i)] = F(1)
            basis.append(n+m+art.index(i))
        else:
            basis.append(n+i)
        T.append(row)
    def pivot(pr, pc):
        pv = T[pr][pc]
        T[pr] = [v/pv for v in T[pr]]
        prow = T[pr]
        for i in range(m):
            if i != pr and T[i][pc] != 0:
                f = T[i][pc]
                T[i] = [vi - f*vp for vi, vp in zip(T[i], prow)]
        basis[pr] = pc
    def run(obj):
        inb = set(basis)
        while True:
            cb = [obj[bj] for bj in basis]
            enter = None
            for j in range(N):
                if j in inb: continue
                rc = obj[j] - sum(cb[i]*T[i][j] for i in range(m) if T[i][j] != 0)
                if rc > 0: enter = j; break
            if enter is None: return True
            pr = None; br = None
            for i in range(m):
                if T[i][enter] > 0:
                    r = T[i][-1]/T[i][enter]
                    if br is None or r < br or (r == br and basis[i] < basis[pr]):
                        br = r; pr = i
            if pr is None: return False
            inb.discard(basis[pr]); inb.add(enter)
            pivot(pr, enter)
    if na:
        obj1 = [F(0)]*N
        for a in range(na): obj1[n+m+a] = F(-1)
        run(obj1)
        if sum(obj1[bj]*T[i][-1] for i, bj in enumerate(basis)) != 0:
            return ('infeasible', None, None)
        for i in range(m):
            if basis[i] >= n+m:
                for j in range(n+m):
                    if T[i][j] != 0: pivot(i, j); break
    obj = [F(v) for v in c] + [F(0)]*m + [F(-10**12)]*na
    if not run(obj): return ('unbounded', None, None)
    x = [F(0)]*n
    for i, bj in enumerate(basis):
        if bj < n: x[bj] = T[i][-1]
    return ('optimal', sum(F(c[j])*x[j] for j in range(n)), x)

def exact_lp(A, b, c, always):
    """maximize c.x s.t. A x <= b, x>=0, exact. `always` = row indices always kept."""
    Af = np.array([[float(v) for v in r] for r in A]); bf = np.array([float(v) for v in b]); cf = np.array([float(v) for v in c])
    res = linprog(-cf, A_ub=Af, b_ub=bf, bounds=[(0, None)]*len(c), method='highs')
    R = set(always)
    if res.status == 0:
        slack = bf - Af @ res.x
        R |= set(np.where(slack < 1e-7)[0].tolist())
    while True:
        rows = sorted(R)
        st, val, x = simplex_max([A[i] for i in rows], [b[i] for i in rows], c)
        if st != 'optimal':
            if st == 'infeasible': return st, None, None
            # unbounded relaxation: add all rows (fallback)
            if len(R) == len(A): return st, None, None
            R = set(range(len(A))); continue
        viol = [i for i in range(len(A)) if i not in R and sum(A[i][j]*x[j] for j in range(len(c))) > b[i]]
        if not viol: return 'optimal', val, x
        R |= set(viol)

def coalitions(n): return range(1, 1 << n)

def envelope(gens):
    n = len(gens[0]); v = {}
    for S in coalitions(n):
        v[S] = min(sum(g[i] for i in range(n) if S >> i & 1) for g in gens)
    return v

def core_rows(v, n, T):
    A = []; b = []; full = (1 << n) - 1
    for S in coalitions(n):
        if S == full: continue
        A.append([F(-1) if S >> i & 1 else F(0) for i in range(n)]); b.append(-F(v[S]))
    A.append([F(1)]*n); b.append(F(T)); A.append([F(-1)]*n); b.append(-F(T))
    return A, b

def staged(v, n, T, mode):
    A0, b0 = core_rows(v, n, T)
    fixed = {}; blocks = []
    while len(fixed) < n:
        U = [i for i in range(n) if i not in fixed]
        A = [row + [F(0)] for row in A0]; b = list(b0); always = [len(A0)-2, len(A0)-1]
        for i, val in fixed.items():
            r = [F(0)]*(n+1); r[i] = F(1); A.append(r); b.append(val); always.append(len(A)-1)
            r = [F(0)]*(n+1); r[i] = F(-1); A.append(r); b.append(-val); always.append(len(A)-1)
        for i in U:
            r = [F(0)]*(n+1)
            if mode == 'min': r[i] = F(-1); r[n] = F(1)
            else: r[i] = F(1); r[n] = F(-1)
            A.append(r); b.append(F(0)); always.append(len(A)-1)
        c = [F(0)]*n + [F(1) if mode == 'min' else F(-1)]
        st, val, sol = exact_lp(A, b, c, always); assert st == 'optimal', st
        tstar = sol[n]
        forced = []
        for i in U:
            A2 = A + [[F(0)]*n + [F(-1) if mode == 'min' else F(1)]]
            b2 = b + [(-tstar) if mode == 'min' else tstar]
            c2 = [F(0)]*(n+1); c2[i] = F(1) if mode == 'min' else F(-1)
            st2, val2, sol2 = exact_lp(A2, b2, c2, always + [len(A2)-1]); assert st2 == 'optimal', st2
            if sol2[i] == tstar: forced.append(i)
        assert forced
        for i in forced: fixed[i] = tstar
        blocks.append((sorted(forced), tstar))
    return [fixed[i] for i in range(n)], blocks

def analyze(gens, verbose=True):
    n = len(gens[0]); gens = [[F(a) for a in g] for g in gens]; T = sum(gens[0])
    assert all(sum(g) == T for g in gens), "unequal totals"
    assert all(a >= 0 for g in gens for a in g)
    v = envelope(gens)
    for i in range(n): assert v[1 << i] == 0, f"not singleton-normalized at {i}"
    x, bx = staged(v, n, T, 'min'); z, bz = staged(v, n, T, 'max')
    O = sum(min(a, c) for a, c in zip(x, z)); dist = sum(abs(a - c) for a, c in zip(x, z)); rho = dist / T
    if verbose:
        print("n=", n, "T=", T)
        print("Lmin =", [str(a) for a in x], "blocks", [(bl, str(t)) for bl, t in bx])
        print("Lmax =", [str(a) for a in z], "blocks", [(bl, str(t)) for bl, t in bz])
        print("overlap O =", O, " O/T =", O / T, " ||x-z||_1 =", dist, " rho =", rho, "~", float(rho))
    return dict(n=n, T=T, x=x, z=z, O=O, dist=dist, rho=rho, xblocks=bx, zblocks=bz)

def target(n): return F(2) - F(8 * n, n * n - (n % 2))

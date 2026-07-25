"""Thorough multi-strategy search for an imputation in BS \\ core of a given game.
Candidate generators (all fed to the exact bargaining_set oracle):
  (K) transfer-scheme kernel points from many starts (incl. extreme imputations)
  (P) prekernel-ish points (transfer without the IR floor, then clipped)
  (M) per-coalition core-face minimizers pushed just outside across each facet
  (F) facet-crossing: from core vertices, step outward along many efficient directions
Returns a certified witness (x, viol) or None.  Exact oracle is the certificate.
"""
import random, numpy as np
from fractions import Fraction as F
from tugame import Game, exact_lp_min
from bargaining_set import in_bargaining_set, float_has_justified_objection


def _masks(n):
    N = (1 << n) - 1
    M = np.zeros((N + 1, n))
    for S in range(1, N + 1):
        for i in range(n):
            if S >> i & 1:
                M[S, i] = 1.0
    return M


def sij(vf, M, x, n):
    N = (1 << n) - 1
    e = vf - M @ np.asarray(x); e[0] = -1e18; e[N] = -1e18
    s = np.full((n, n), -1e18)
    for i in range(n):
        inc = M[:, i] > 0.5
        for j in range(n):
            if i != j:
                s[i, j] = e[inc & (M[:, j] < 0.5)].max()
    return s


def transfer(vf, M, ivals, x0, n, iters=4000, tol=1e-12, ir=True):
    x = np.array(x0, float)
    for _ in range(iters):
        s = sij(vf, M, x, n)
        best = None; bd = tol
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                d = s[i, j] - s[j, i]
                floor = ivals[j] if ir else -1e18
                if d > bd and x[j] - floor > tol:
                    bd = d; best = (i, j, d)
        if best is None:
            break
        i, j, d = best
        cap = (x[j] - ivals[j]) if ir else 1e18
        delta = min(d / 2.0, cap)
        x[i] += delta; x[j] -= delta
    return x.tolist()


def rat(game, xf, md=10 ** 7):
    n = game.n
    xr = [F(xf[i]).limit_denominator(md) for i in range(n)]
    xr[-1] += game.v[game.N] - sum(xr)
    return xr


def core_vertices(game, cap=40):
    """Enumerate core vertices by optimizing random linear objectives (exact)."""
    n, N = game.n, game.N
    A_ub = [[-1 if S >> i & 1 else 0 for i in range(n)] for S in range(1, N)]
    b_ub = [-game.v[S] for S in range(1, N)]
    A_eq = [[1] * n]; b_eq = [game.v[N]]
    verts = set()
    rng = random.Random(0)
    for _ in range(cap):
        c = [rng.randint(-9, 9) for _ in range(n)]
        opt, x = exact_lp_min(c, A_ub, b_ub, A_eq, b_eq)
        if x is not None and opt not in (None, 'unbounded'):
            verts.add(tuple(x))
    return [list(v) for v in verts]


def check(game, xr, cand_seen):
    key = tuple(xr)
    if key in cand_seen:
        return None
    cand_seen.add(key)
    n = game.n
    if sum(xr) != game.v[game.N]:
        return None
    if any(xr[i] < game.v[1 << i] for i in range(n)):
        return None
    viol = game.core_violations(xr)
    if not viol:
        return None
    if float_has_justified_objection(game, xr):    # fast screen: clearly not in BS
        return None
    inbs, _ = in_bargaining_set(game, xr)          # exact confirmation
    if inbs:
        return (xr, viol)
    return None


def probe(game, seed=0, starts=30):
    n, N = game.n, game.N
    vf = np.array([float(t) for t in game.v])
    ivals = np.array([float(game.v[1 << i]) for i in range(n)])
    M = _masks(n)
    base = ivals.tolist(); rem = float(game.v[N]) - sum(base)
    rng = random.Random(seed)
    seen = set()

    # (K)/(P) transfer points, IR and non-IR
    starts_w = [[1.0 if i == q else 0.0 for i in range(n)] for q in range(n)]
    starts_w += [[rng.random() for _ in range(n)] for _ in range(starts)]
    for ir in (True, False):
        for w in starts_w:
            sw = sum(w) or 1.0
            x0 = [base[i] + rem * w[i] / sw for i in range(n)]
            xr = rat(game, transfer(vf, M, ivals, x0, n, ir=ir))
            r = check(game, xr, seen)
            if r:
                return r

    verts = core_vertices(game)
    # (F) facet crossing: from each core vertex step outward along efficient directions
    dirs = []
    for i in range(n):
        for j in range(n):
            if i != j:
                d = [0] * n; d[i] = 1; d[j] = -1; dirs.append(d)   # move j->i
    # group directions (move a whole coalition's worth outward)
    for S in range(1, N):
        mem = [i for i in range(n) if S >> i & 1]
        comp = [i for i in range(n) if not (S >> i & 1)]
        if not mem or not comp:
            continue
        d = [0] * n
        for i in mem:
            d[i] = F(-1, len(mem))
        for i in comp:
            d[i] = F(1, len(comp))
        dirs.append(d)
    steps = [F(1, 6), F(1, 3), F(1, 2), F(1), F(3, 2), F(2), F(3)]
    for v in verts:
        vv = [F(a).limit_denominator(10 ** 7) for a in v]
        for d in dirs:
            for s in steps:
                xr = [vv[i] + s * d[i] for i in range(n)]
                xr[-1] += game.v[N] - sum(xr)
                r = check(game, xr, seen)
                if r:
                    return r
    return None

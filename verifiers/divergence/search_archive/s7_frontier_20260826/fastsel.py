"""Fast float staged selectors (HiGHS) for lower-envelope games; search use only."""
import numpy as np
from scipy.optimize import linprog

def envelope_np(G):
    """G: (m,n) array. returns v over masks 1..2^n-1 as array indexed by mask."""
    m, n = G.shape
    masks = np.arange(1 << n)
    inc = ((masks[:, None] >> np.arange(n)[None, :]) & 1).astype(float)  # (2^n, n)
    vals = inc @ G.T  # (2^n, m)
    return inc, vals.min(axis=1)

def staged_float(inc, v, n, T, mode, tol=1e-7):
    full = (1 << n) - 1
    A_core = -inc[1:full]           # -y(S) <= -v(S)
    b_core = -v[1:full]
    fixed = {}
    blocks = []
    while len(fixed) < n:
        U = [i for i in range(n) if i not in fixed]
        rows = [np.append(A_core, np.zeros((A_core.shape[0], 1)), axis=1)]
        rhs = [b_core]
        extra = []
        for i in U:
            r = np.zeros(n + 1)
            if mode == 'min': r[i] = -1; r[n] = 1
            else: r[i] = 1; r[n] = -1
            extra.append(r)
        A = np.vstack(rows + [np.array(extra)]); b = np.concatenate(rhs + [np.zeros(len(U))])
        Aeq = [np.append(np.ones(n), 0.0)]; beq = [T]
        for i, val in fixed.items():
            r = np.zeros(n + 1); r[i] = 1; Aeq.append(r); beq.append(val)
        Aeq = np.array(Aeq); beq = np.array(beq)
        c = np.zeros(n + 1); c[n] = -1 if mode == 'min' else 1
        res = linprog(c, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq, bounds=[(0, None)] * (n + 1), method='highs')
        if res.status != 0: return None, None
        t = res.x[n]
        # bulk unforced detection
        A2 = np.vstack([A, np.array([[0.0]*n + [-1.0 if mode == 'min' else 1.0]])])
        b2 = np.append(b, -t if mode == 'min' else t)
        c2 = np.zeros(n + 1)
        for i in U: c2[i] = -1 if mode == 'min' else 1
        r2 = linprog(c2, A_ub=A2, b_ub=b2, A_eq=Aeq, b_eq=beq, bounds=[(0, None)] * (n + 1), method='highs')
        cand = [i for i in U if r2.status != 0 or abs(r2.x[i] - t) <= tol * max(1.0, abs(t))]
        forced = []
        for i in cand:
            c3 = np.zeros(n + 1); c3[i] = -1 if mode == 'min' else 1
            r3 = linprog(c3, A_ub=A2, b_ub=b2, A_eq=Aeq, b_eq=beq, bounds=[(0, None)] * (n + 1), method='highs')
            if r3.status != 0 or abs(r3.x[i] - t) <= tol * max(1.0, abs(t)):
                forced.append(i)
        if not forced:
            forced = [min(cand or U)]  # numerical fallback
        for i in forced: fixed[i] = t
        blocks.append((forced, t))
    return np.array([fixed[i] for i in range(n)]), blocks

def rho_float(G):
    G = np.asarray(G, dtype=float); m, n = G.shape; T = G[0].sum()
    inc, v = envelope_np(G)
    x, bx = staged_float(inc, v, n, T, 'min')
    if x is None: return None
    z, bz = staged_float(inc, v, n, T, 'max')
    if z is None: return None
    return np.abs(x - z).sum() / T, x, z, bx, bz

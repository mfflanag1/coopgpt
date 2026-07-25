"""Fast FLOAT SD-prenucleolus for screening only (scipy HiGHS).
Mirrors sd_prenucleolus.py exactly but in floating point; any candidate
coalitional-monotonicity violation it flags is re-derived with the exact
rational sd_prenucleolus before it is believed."""
import numpy as np
from scipy.optimize import linprog

TOL = 1e-7

def _sigma_and_f(S, H, level, n):
    sigma = 0
    for T in H:
        if T & S == T:
            sigma |= T
    fvals = {}
    for i in range(n):
        if sigma >> i & 1:
            best = None
            for U in H:
                if (U >> i & 1) and (U & S == U) and (best is None or level[U] < best):
                    best = level[U]
            fvals[i] = best
    return sigma, fvals

def _affine(S, H, level, vfun, n):
    sigma, fvals = _sigma_and_f(S, H, level, n)
    popS, popsig = bin(S).count("1"), bin(sigma).count("1")
    a = np.zeros(n)
    if sigma == S:
        sumf = sum(fvals.values())
        for i in range(n):
            if S >> i & 1:
                a[i] = 1.0
        b = -(vfun[S] + sumf - max(fvals.values()))
    else:
        d = popS - popsig
        sumf = sum(fvals.values())
        for i in range(n):
            if S >> i & 1:
                a[i] = 1.0 / d
        b = -(vfun[S] + sumf) / d
    return a, b

def sd_prenucleolus_float(vfun, n):
    """vfun: list length 2^n of floats, vfun[0]=0. Returns np.array length n or None."""
    N = (1 << n) - 1
    settled = set(); s_a = {}; s_b = {}; s_lvl = {}
    unsettled = set(range(1, N))

    def eqmat():
        A = [np.append(np.ones(n), 0.0)]; b = [vfun[N]]
        for S in settled:
            A.append(np.append(s_a[S], 0.0)); b.append(s_lvl[S] - s_b[S])
        return np.array(A), np.array(b)

    bounds = [(None, None)] * (n + 1)
    guard = 0
    while unsettled:
        guard += 1
        if guard > 2 * (1 << n):
            return None
        expr = {S: _affine(S, settled, s_lvl, vfun, n) for S in unsettled}
        A_eq, b_eq = eqmat()
        Aub, bub = [], []
        for S in unsettled:
            a, b = expr[S]
            Aub.append(np.append(-a, 1.0)); bub.append(b)          # -a.x+alpha<=b
        c = np.append(np.zeros(n), -1.0)
        r = linprog(c, A_ub=np.array(Aub), b_ub=np.array(bub),
                    A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
        if not r.success:
            return None
        alpha = -r.fun
        xv = r.x[:n]
        # a forced coalition is tight at EVERY optimum, hence at this vertex:
        # only forced-test the vertex-tight coalitions (exact, and far fewer LPs).
        tight = [S for S in unsettled if abs(expr[S][0] @ xv + expr[S][1] - alpha) < TOL]
        Aub2, bub2 = [], []
        for S in unsettled:
            a, b = expr[S]
            Aub2.append(-a); bub2.append(b - alpha)                # a.x>=alpha-b
        Aub2 = np.array(Aub2); bub2 = np.array(bub2)
        Aeq2 = A_eq[:, :n]; beq2 = b_eq
        newly = []
        for S in tight:
            a, b = expr[S]
            r2 = linprog(-a, A_ub=Aub2, b_ub=bub2, A_eq=Aeq2, b_eq=beq2,
                         bounds=[(None, None)] * n, method="highs")
            if r2.success and abs((-r2.fun) + b - alpha) < TOL:
                newly.append(S)
        if not newly:            # float degeneracy fallback: fix vertex-tight set
            newly = tight
            if not newly:
                return None
        for S in newly:
            s_a[S], s_b[S] = expr[S]; s_lvl[S] = alpha
            settled.add(S); unsettled.discard(S)
    A_eq, b_eq = eqmat()
    r = linprog(np.zeros(n + 1), A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    return None if not r.success else r.x[:n]

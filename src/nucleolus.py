"""Nucleolus computation.

Two tiers:
  1. prenucleolus_float: fast successive-LP scheme with scipy (screening).
  2. certified_prenucleolus: float solve -> rational reconstruction ->
     exact Kohlberg certification. Only certified outputs are trusted.
"""
from fractions import Fraction
import numpy as np
from scipy.optimize import linprog as flinprog
from tugame import Game, kohlberg_certify_prenucleolus

TOL = 1e-9

def prenucleolus_float(game, weights=None):
    """Maschler scheme for the (weighted) prenucleolus: lexicographically
    minimize sorted excesses (v(S)-x(S))/w_S. weights: dict S->w_S (default 1).
    A coalition is fixed at level t_k iff its excess equals t_k in EVERY optimal
    solution (tested per-coalition by a secondary LP)."""
    n, N, v = game.n, game.N, [float(val) for val in game.v]
    w = {S: float(weights[S]) for S in range(1, N)} if weights else {S: 1.0 for S in range(1, N)}
    proper = list(range(1, N))
    rowS = {S: np.array([1.0 if S >> i & 1 else 0.0 for i in range(n)]) for S in proper}
    fixed = {}          # S -> excess level pinned
    unfixed = set(proper)
    eq_rows = [np.append(np.ones(n), 0.0)]
    eq_rhs = [v[N]]
    for _round in range(2 * n + 2):
        if not unfixed:
            break
        A_ub, b_ub = [], []
        for S in unfixed:
            A_ub.append(np.append(-rowS[S], -w[S])); b_ub.append(-v[S])
        A_eq = list(eq_rows); b_eq = list(eq_rhs)
        for S, lev in fixed.items():
            A_eq.append(np.append(-rowS[S], 0.0)); b_eq.append(w[S] * lev - v[S])
        c = np.zeros(n + 1); c[n] = 1.0
        res = flinprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                       A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                       bounds=[(None, None)] * (n + 1), method="highs")
        if not res.success:
            return None
        t_k = res.x[n]
        # which unfixed S are forced to excess t_k in every optimum?
        newly = []
        for S in unfixed:
            ex = (v[S] - rowS[S] @ res.x[:n]) / w[S]
            if ex < t_k - 1e-7:
                continue
            # try to push excess of S below t_k: fix t = t_k, maximize x(S)
            A_eq2 = A_eq + [np.append(np.zeros(n), 1.0)]
            b_eq2 = b_eq + [t_k]
            res2 = flinprog(-np.append(rowS[S], 0.0), A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                            A_eq=np.array(A_eq2), b_eq=np.array(b_eq2),
                            bounds=[(None, None)] * (n + 1), method="highs")
            if res2 is None or not res2.success:
                newly.append(S)
                continue
            ex_min = (v[S] - (-res2.fun)) / w[S]
            if ex_min > t_k - 1e-7:
                newly.append(S)
        if not newly:
            # numerical corner: fall back to fixing all at-level coalitions
            newly = [S for S in unfixed if (v[S] - rowS[S] @ res.x[:n]) / w[S] > t_k - 1e-7]
        for S in newly:
            fixed[S] = t_k
            unfixed.discard(S)
    # final solve for x with all fixed
    A_eq = list(eq_rows); b_eq = list(eq_rhs)
    for S, lev in fixed.items():
        A_eq.append(np.append(-rowS[S], 0.0)); b_eq.append(w[S] * lev - v[S])
    res = flinprog(np.zeros(n + 1), A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                   bounds=[(None, None)] * (n + 1), method="highs")
    if not res.success:
        return None
    return res.x[:n]

def rationalize(xf, game, max_den=10 ** 8):
    """Turn float vector into exact Fractions summing to v(N)."""
    n = game.n
    for D in (10, 60, 360, 2520, 10 ** 4, 10 ** 6, max_den):
        x = [Fraction(float(xi)).limit_denominator(D) for xi in xf]
        resid = game.v[game.N] - sum(x)
        if resid == 0:
            return x
        # distribute residual on the largest-denominator coordinate
        x[-1] += resid
        if abs(float(resid)) < 1e-6:
            return x
    return None

def certified_prenucleolus(game, weights=None):
    """Returns exact Fraction vector certified by Kohlberg, or None."""
    xf = prenucleolus_float(game, weights)
    if xf is None:
        return None
    x = rationalize(xf, game)
    if x is None:
        return None
    ok, why = kohlberg_certify_prenucleolus(game, x, weights)
    if ok:
        return x
    return None

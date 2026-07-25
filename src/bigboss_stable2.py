"""Reliable big-boss core-stability check: broad FLOAT escape search + EXACT
certification via the box-domination test. Returns an exact escaping imputation
(=> NOT stable) or None (no escape found; likely stable, esp. convex => provably stable).
"""
from fractions import Fraction as F
from tugame import Game
from bigboss import marginals
from bigboss_stability import is_dominated_bigboss, in_box
from stability_float import find_escape_float, is_dominated_float, in_core_float, _core_rows


def _fix_eff(g, y, boss):
    y = list(y)
    y[boss] += g.v[g.N] - sum(y)
    return y


def certify_escape_exact(g, M, boss, yf, denoms=(1, 2, 3, 4, 5, 6, 12, 20, 60)):
    """Try to turn a float escape yf into an exact undominated imputation."""
    n = g.n
    for D in denoms:
        y = [F(round(a * D), D) for a in yf]
        y = _fix_eff(g, y, boss)
        if any(a < 0 for a in y):
            continue
        if in_box(g, M, boss, y):
            continue
        dom, _ = is_dominated_bigboss(g, M, boss, y)
        if not dom:
            return y
    return None


def reliable_escape(g, boss=None, tries=60000, seeds=(1, 2, 3)):
    """Return exact escaping imputation (non-stable) or None."""
    n, N = g.n, g.N
    if boss is None:
        boss = n - 1
    M = marginals(g)
    vf = [float(x) for x in g.v]
    base = _core_rows(vf, n, N)
    for seed in seeds:
        yf = find_escape_float(vf, n, N, tries=tries, seed=seed)
        if yf is None:
            continue
        ex = certify_escape_exact(g, M, boss, yf)
        if ex is not None:
            return ex
        # float said escape but exact rounding failed; try the float point's exact LP snap:
        # round to a fine grid and re-verify undomination in float as a fallback signal
    return None


def is_stable_reliable(g, boss=None, tries=60000):
    """(stable_guess, escape_or_None). stable_guess True iff no escape found."""
    esc = reliable_escape(g, boss, tries=tries)
    return (esc is None), esc

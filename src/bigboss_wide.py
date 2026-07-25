"""Big boss games with NON-degenerate (wide) core boxes: all non-boss M_i>0.
Two families, both satisfying B1/B2/B3:

union_tight(M, c): boss floor c>=0, v(S)= c + sum_{i in S, non-boss} M_i for boss in S,
   else 0. Here v(N)=c+sum M_i, and B3 holds with equality (union-tight). Additive-
   given-boss. Core box {0<=x_i<=M_i}.

submodular(w, h): v(S)= h(sum_{i in S non-boss} w_i) for boss in S (h concave increasing,
   h(0)=0), else 0. Submodular => union property B3. M_i = h(W)-h(W-w_i) > 0.
"""
from fractions import Fraction as F
from tugame import Game
from bigboss import is_big_boss, marginals


def union_tight(M, c, boss=None):
    n = len(M) + 1
    if boss is None:
        boss = n - 1
    others = [i for i in range(n) if i != boss]
    v = [F(0)] * (1 << n)
    for S in range(1, 1 << n):
        if S >> boss & 1:
            v[S] = F(c) + sum(F(M[k]) for k, pl in enumerate(others) if S >> pl & 1)
    return Game(n, v), boss


def submodular(w, hvals, boss=None):
    """w: weights for non-boss players (len n-1). hvals: dict wsum->h value (concave,
    h[0]=0, increasing). v(S)=h(sum w_i over non-boss in S) for boss in S."""
    n = len(w) + 1
    if boss is None:
        boss = n - 1
    others = [i for i in range(n) if i != boss]
    v = [F(0)] * (1 << n)
    for S in range(1, 1 << n):
        if S >> boss & 1:
            ws = sum(w[k] for k, pl in enumerate(others) if S >> pl & 1)
            v[S] = F(hvals[ws])
    return Game(n, v), boss


def gen_submodular_bigboss(rng, n=6, wmax=4, boss=None):
    """Random submodular big boss game with all M_i>0. Weights w_i in [1,wmax];
    concave h on 0..W via random positive decreasing increments."""
    if boss is None:
        boss = n - 1
    w = [rng.randint(1, wmax) for _ in range(n - 1)]
    W = sum(w)
    # concave increasing h: increments delta_1>=delta_2>=...>=delta_W>0
    incs = sorted((rng.randint(1, 6) for _ in range(W)), reverse=True)
    hvals = {0: 0}
    acc = 0
    for k in range(1, W + 1):
        acc += incs[k - 1]; hvals[k] = acc
    g, b = submodular(w, hvals, boss)
    ok, why = is_big_boss(g, b)
    if not ok:
        return None
    M = marginals(g)
    if any(M[i] == 0 for i in range(n) if i != b):
        return None
    return g

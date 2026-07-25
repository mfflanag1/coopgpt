"""SD-prekernel (Arin-Katsev 2018): for i != j,
  s_ij(x) = min over coalitions S with i in S, j not in S of F(S;x)
where F(S;x) is the exact SD-satisfaction (sd.sd_satisfactions).
SD-prekernel = {efficient x : s_ij(x) == s_ji(x) for all i != j}.

Hunt goal: a balanced game with an SD-prekernel point != SD-prenucleolus.
"""
from fractions import Fraction as F
from sd import sd_satisfactions
from tugame import Game

def s_matrix(game, x):
    """Return dict (i,j)->Fraction s_ij(x) for all ordered pairs i!=j."""
    n, N = game.n, game.N
    Fx = sd_satisfactions(game, x)   # dict S(1..N-1) -> Fraction; proper coalitions
    s = {}
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            best = None
            for S in range(1, N):            # proper coalitions
                if (S >> i & 1) and not (S >> j & 1):
                    v = Fx[S]
                    if best is None or v < best:
                        best = v
            s[(i, j)] = best
    return s

def imbalances(game, x):
    """dict (i,j)->s_ij - s_ji for i<j (the equalization residuals)."""
    s = s_matrix(game, x)
    out = {}
    for i in range(game.n):
        for j in range(i + 1, game.n):
            out[(i, j)] = s[(i, j)] - s[(j, i)]
    return out

def is_equalized(game, x):
    return all(d == 0 for d in imbalances(game, x).values())

def is_efficient(game, x):
    return sum(x) == game.v[game.N]

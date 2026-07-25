"""Big boss games (Muto-Nakayama-Potters-Tijs 1988). Boss = player b (default n-1).
B1 monotone; B2 veto: v(S)=0 if b not in S; B3 union: for b in S,
   v(N)-v(S) >= sum_{i in N\\S} M_i,  M_i = v(N)-v(N\\{i}).
Core = { x : sum x = v(N), 0 <= x_i <= M_i for non-boss i } (parallelotope);
MNPT: this core is a vNM-STABLE set. We verify computationally and test ES.
"""
import random
from fractions import Fraction as F
from tugame import Game


def is_big_boss(g, b=None):
    n, N, v = g.n, g.N, g.v
    if b is None:
        b = n - 1
    # B2 veto
    for S in range(1, N + 1):
        if not (S >> b & 1) and v[S] != 0:
            return False, "veto"
    # B1 monotone
    for S in range(N + 1):
        for i in range(n):
            if not (S >> i & 1) and v[S | (1 << i)] < v[S]:
                return False, "monotone"
    # B3 union
    M = [v[N] - v[N ^ (1 << i)] for i in range(n)]
    for S in range(1, N + 1):
        if S >> b & 1:
            out = [i for i in range(n) if not (S >> i & 1)]
            if v[N] - v[S] < sum(M[i] for i in out):
                return False, "union"
    return True, "ok"


def marginals(g):
    n, N, v = g.n, g.N, g.v
    return [v[N] - v[N ^ (1 << i)] for i in range(n)]


def gen_big_boss(rng, n, vmax=6, b=None):
    """Random big boss game: boss=b (default n-1). Draw monotone nonneg values on
    coalitions containing the boss (v=0 otherwise), REJECT-sampling the union
    property. Returns Game or None."""
    if b is None:
        b = n - 1
    N = (1 << n) - 1
    others = [i for i in range(n) if i != b]
    # value depends only on T = S\{b} (subset of others). Build monotone g(T)>=0.
    # assign a random nonneg weight to each other-player 'block' then make monotone
    v = [F(0)] * (1 << n)
    # random values on subsets containing boss, enforce monotonicity by construction:
    # g(T) = sum of a base plus supermodular-ish random increments; simplest: random
    # then monotone-close. We draw random ints and take cumulative max over subsets.
    raw = {}
    for T in range(1 << len(others)):
        raw[T] = rng.randint(0, vmax)
    # monotone closure over the subset lattice of 'others'
    gval = {}
    for T in range(1 << len(others)):
        best = raw[T]
        sub = T
        while sub:
            best = max(best, gval.get(sub, 0))
            sub = (sub - 1) & T
        gval[T] = best
    gval[0] = raw[0] if 0 not in gval else gval[0]
    # map T (bitmask over 'others' index) -> coalition S = {b} U corresponding players
    def Tmask_to_S(T):
        S = 1 << b
        for idx, pl in enumerate(others):
            if T >> idx & 1:
                S |= 1 << pl
        return S
    for T in range(1 << len(others)):
        v[Tmask_to_S(T)] = F(gval[T])
    g = Game(n, v)
    ok, why = is_big_boss(g, b)
    if not ok:
        return None
    return g

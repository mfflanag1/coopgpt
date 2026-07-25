"""Hunt: coalitional monotonicity of the SD-prenucleolus.

phi is coalitionally monotonic if  w(S) > v(S), w(T)=v(T) for all T != S
implies phi_i(w) >= phi_i(v) for every i in S.  Arin-Katsev PROVED this on
convex games and on (monotonic) veto games.  Young(1985)/Housman-Clark: no core
selector is coalitionally monotonic for n>=4, so violations on general balanced
games are guaranteed (rediscovery).  The value is (a) calibration -- ZERO
violations on convex & veto games -- and (b) the tightest class in which the
violation already occurs (totally balanced / exact / large core -- all >convex).
"""
from fractions import Fraction as F
from tugame import Game, is_balanced_game, exact_lp_min
from sd_prenucleolus import sd_prenucleolus

def is_totally_balanced(g):
    for T in range(1, g.N + 1):
        sub, _ = g.subgame(T)
        if not is_balanced_game(sub):
            return False
    return True

def is_exact(g):
    """v(S) = min_{x in core} x(S) for every S (LP: min x(S) s.t. core)."""
    n, N = g.n, g.N
    for S in range(1, N):
        A_ub = [[-1 if T >> i & 1 else 0 for i in range(n)] for T in range(1, N)]
        b_ub = [-g.v[T] for T in range(1, N)]
        A_eq, b_eq = [[1] * n], [g.v[N]]
        c = [1 if S >> i & 1 else 0 for i in range(n)]
        opt, _ = exact_lp_min(c, A_ub, b_ub, A_eq, b_eq)
        if opt is None or opt == 'unbounded' or opt != g.v[S]:
            return False
    return True

def classes(g):
    tags = []
    if g.is_convex(): tags.append("convex")
    if is_balanced_game(g): tags.append("balanced")
    if g.is_superadditive(): tags.append("superadd")
    if is_totally_balanced(g): tags.append("totbal")
    if is_exact(g): tags.append("exact")
    return tags

def check_game(g, deltas=(F(1),), need_balanced=True):
    """Return list of violation dicts for game g under single-coalition raises."""
    n, N = g.n, g.N
    base = sd_prenucleolus(g)
    if base is None:
        return []
    viols = []
    for S in range(1, N):                     # proper coalition to raise (S != N)
        for d in deltas:
            w = list(g.v); w[S] = w[S] + d
            gw = Game(n, w)
            if need_balanced and not is_balanced_game(gw):
                continue
            after = sd_prenucleolus(gw)
            if after is None:
                continue
            losers = [i for i in range(n) if (S >> i & 1) and after[i] < base[i]]
            if losers:
                viols.append(dict(S=S, delta=d, losers=losers,
                                  before=base, after=after, w=w))
    return viols

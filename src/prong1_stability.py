"""Prong 1: do the exact non-ES witnesses (and their n=6 padded versions) have
vNM-STABLE cores?  A stable-core non-ES game resolves the 2nd half of
Dietzenbacher's question negatively.

Chain of reasoning to test:
 - non-ES => non-large (contrapositive of large-core => ES, Dietzenbacher 2021).
 - n<=5: stable core <=> large core (Estevez-Fernandez, GEB 76, 2012).
   => the n=5 bases have NON-stable cores. We CONFIRM with an explicit
      undominated imputation outside the core (certified negative).
 - padding by a null/constant player lifts that escaping imputation, so the
   n=6 padded games also have non-stable cores. We CONFIRM directly.
"""
import random, sys, json
from fractions import Fraction as F
from tugame import Game
from eshunt import is_ES
from hunt_sd import is_exact_game
from large_core import non_large_witness
from core_stability import (is_dominated_by_core, in_core, is_imputation,
                            certify_undominated, dominated_via)

WIT_VN4 = [0,0,0,0,0,1,1,1,1,1,1,1,2,2,2,2,0,1,1,2,0,1,1,2,2,3,3,3,2,3,3,4]
BASE_VN6 = [0,0,0,0,3,3,3,3,0,0,0,0,4,4,4,4,0,0,0,0,4,5,5,5,0,0,0,0,4,5,5,6]


def pad(v, n, c):
    w = [F(0)] * (1 << (n + 1))
    for S in range(1 << n):
        w[S] = F(v[S]); w[S | (1 << n)] = F(v[S]) + F(c)
    return w, n + 1


def search_escape(game, tries=20000, seed=0):
    """Random search for an imputation outside the core, undominated by the core.
    Zero-normalized games: y_i >= 0, sum y = v(N). Returns y (Fractions) or None."""
    n, N, v = game.n, game.N, game.v
    vN = v[N]
    lo = [v[1 << i] for i in range(n)]           # singleton lower bounds
    slack = vN - sum(lo)
    rng = random.Random(seed)
    D = 12                                        # rational granularity
    for _ in range(tries):
        # random composition of slack into n nonneg rationals with denom D
        cuts = sorted(rng.randint(0, int(slack) * D) for _ in range(n - 1))
        parts = []
        prev = 0
        for cpt in cuts + [int(slack) * D]:
            parts.append(F(cpt - prev, D)); prev = cpt
        y = [lo[i] + parts[i] for i in range(n)]
        if in_core(game, y):
            continue
        dom, _ = is_dominated_by_core(game, y)
        if not dom:
            return y
    return None


def analyze(tag, v, n):
    g = Game(n, [F(x) for x in v])
    es, gamma = is_ES(g)
    exact = is_exact_game(g)
    nlw = non_large_witness([float(x) for x in g.v], n, g.N, samples=6000, seed=0)
    print(f"\n=== {tag} (n={n}) ===", flush=True)
    print(f"  exact={exact}  ES={es}  claims={[str(x) for x in gamma]}  v(N)={g.v[g.N]}", flush=True)
    print(f"  non-large (LP witness found)={nlw is not None}", flush=True)
    esc = search_escape(g, tries=30000, seed=1)
    if esc is None:
        print("  NO escaping imputation found in search (inconclusive here).", flush=True)
        return g, None
    cert = certify_undominated(g, esc)
    print(f"  ESCAPING IMPUTATION (outside core, undominated) y={[str(x) for x in esc]}", flush=True)
    print(f"  => CORE NOT vNM-STABLE. blocking coalitions={cert['blocking_coalitions']}", flush=True)
    return g, esc


def lift_and_verify(g5, esc5, c, tag):
    """Pad g5 by a player with constant c; lift esc5 -> (esc5, c); verify it is
    an imputation outside the padded core and undominated => padded core unstable."""
    v6, n6 = pad([F(x) for x in g5.v], g5.n, c)
    g6 = Game(n6, v6)
    es6, gamma6 = is_ES(g6)
    exact6 = is_exact_game(g6)
    y6 = list(esc5) + [F(c)]
    cert = certify_undominated(g6, y6)
    print(f"\n--- {tag}: n=6 pad(c={c}) ---", flush=True)
    print(f"  exact={exact6}  ES={es6}  v(N)={g6.v[g6.N]}", flush=True)
    if cert is None:
        # escaping point didn't lift; search fresh
        esc6 = search_escape(g6, tries=40000, seed=3)
        cert = certify_undominated(g6, esc6) if esc6 else None
    if cert is None:
        print("  lifted point NOT certified; SEARCH also failed -> INCONCLUSIVE", flush=True)
        return g6, None
    print(f"  lifted y={cert['y']} is imputation, outside core, UNDOMINATED", flush=True)
    print(f"  => padded core NOT vNM-stable. blocking={cert['blocking_coalitions']}", flush=True)
    return g6, cert


if __name__ == "__main__":
    out = {}
    for tag, v, n in [("witness_vN4", WIT_VN4, 5), ("base_vN6", BASE_VN6, 5)]:
        g5, esc5 = analyze(tag, v, n)
        if esc5 is not None:
            for c in (0, 1):
                lift_and_verify(g5, esc5, c, tag)
    print("\nDONE prong1", flush=True)

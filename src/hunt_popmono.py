"""Population monotonicity hunter: does the nucleolus satisfy
phi_i(v|S) <= phi_i(v|T) for all i in S, S subset T?

Adjacent pairs (|T \\ S| = 1) suffice. We check T = any subset with |T| >= 3,
S = T minus one player, on a given class of games.
"""
import random, sys, json
from fractions import Fraction as F
from tugame import Game, is_balanced_game, members
from nucleolus import prenucleolus_float, certified_prenucleolus
from hunt_monotonic import rand_game, popcount

def pm_violation_float(g):
    """Scan adjacent subgame pairs; return worst float violation or None."""
    n, Nm = g.n, g.N
    nuc = {}
    for T in range(1, Nm + 1):
        k = popcount(T)
        if k < 2:
            continue
        sub, mem = g.subgame(T)
        x = prenucleolus_float(sub)
        if x is None:
            return None
        nuc[T] = dict(zip(mem, x))
    worst = None
    for T in nuc:
        for j in members(T, n):
            S = T ^ (1 << j)
            if S not in nuc:
                continue
            for i in members(S, n):
                gap = nuc[S][i] - nuc[T][i]
                if gap > 1e-6 and (worst is None or gap > worst[0]):
                    worst = (gap, S, T, i)
    return worst

def certify_pm(g, S, T, i):
    subS, memS = g.subgame(S)
    subT, memT = g.subgame(T)
    xS = certified_prenucleolus(subS)
    xT = certified_prenucleolus(subT)
    if xS is None or xT is None:
        return None
    vi_S = xS[memS.index(i)]
    vi_T = xT[memT.index(i)]
    if vi_S <= vi_T:
        return None
    return {
        "n": g.n, "v": [str(t) for t in g.v],
        "S": S, "T": T, "player": i,
        "phi_i_S": str(vi_S), "phi_i_T": str(vi_T), "gap": str(vi_S - vi_T),
        "convex": g.is_convex(), "superadditive": g.is_superadditive(),
        "balanced_S": is_balanced_game(g.subgame(S)[0]),
        "balanced_T": is_balanced_game(g.subgame(T)[0]),
    }

if __name__ == "__main__":
    n = int(sys.argv[1]); kind = sys.argv[2]
    trials = int(sys.argv[3]); seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    rng = random.Random(seed)
    for t in range(trials):
        g = rand_game(n, rng, kind)
        w = pm_violation_float(g)
        if w:
            gap, S, T, i = w
            print(f"[cand] trial={t} gap~{gap:.4f} S={S:b} T={T:b} i={i}")
            rep = certify_pm(g, S, T, i)
            if rep:
                print("CERTIFIED PM VIOLATION:")
                print(json.dumps(rep, indent=1))
                break
    else:
        print("no certified violation in", trials, "trials")

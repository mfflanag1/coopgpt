"""Permutation games: n players, value matrix K (n x n, K[i][j] = value if i's
item assigned to j). v(S) = max over permutations pi of S of sum_{i in S} K[i][pi(i)].
Assignment games embed as special cases; permutation games are totally balanced.

Hunt: pairwise entry monotonicity of the nucleolus — raise K[i][j] (i != j) or
K[i][i], watch players i and j for a certified strict drop.
"""
import random, sys, json
from fractions import Fraction as F
from itertools import permutations
from tugame import Game
from nucleolus import prenucleolus_float, certified_prenucleolus

def permutation_game(K):
    n = len(K)
    v = [F(0)] * (1 << n)
    for S in range(1, 1 << n):
        mem = [i for i in range(n) if S >> i & 1]
        best = None
        for perm in permutations(mem):
            w = sum(F(K[i][p]) for i, p in zip(mem, perm))
            if best is None or w > best:
                best = w
        v[S] = best
    return Game(n, v)

def hunt(n, trials, seed, vmax=12):
    rng = random.Random(seed)
    for t in range(trials):
        K = [[rng.randint(0, vmax) for _ in range(n)] for _ in range(n)]
        g = permutation_game(K)
        x = prenucleolus_float(g)
        if x is None:
            continue
        i, j = rng.randrange(n), rng.randrange(n)
        d = rng.choice([1, 2])
        K2 = [r[:] for r in K]; K2[i][j] += d
        g2 = permutation_game(K2)
        y = prenucleolus_float(g2)
        if y is None:
            continue
        watch = {i, j}
        drops = [(p, x[p] - y[p]) for p in watch if x[p] - y[p] > 1e-6]
        if drops:
            print(f"[cand] t={t} K={K} bump=({i},{j})+{d} drops={[(p, round(dd,4)) for p,dd in drops]}", flush=True)
            gx = certified_prenucleolus(g); gy = certified_prenucleolus(g2)
            if gx and gy:
                ed = [(p, gx[p] - gy[p]) for p in watch if gx[p] > gy[p]]
                if ed:
                    print("CERTIFIED permutation-game pairwise-monotonicity violation:", flush=True)
                    print(json.dumps({"K": K, "bump": [i, j, d],
                                      "x": [str(u) for u in gx], "y": [str(u) for u in gy],
                                      "drops": [(p, str(dd)) for p, dd in ed]}, indent=1), flush=True)
                    return True
            print("  certification failed", flush=True)
    print(f"no certified violation in {trials} trials", flush=True)
    return False

if __name__ == "__main__":
    n, trials = int(sys.argv[1]), int(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    hunt(n, trials, seed)

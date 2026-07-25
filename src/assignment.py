"""Assignment games (Shapley-Shubik): rows = sellers 0..m-1, cols = buyers m..m+m'-1.
v(S) = max-weight matching between sellers and buyers inside S.

Hunts: does increasing one matrix entry a_ij ever strictly DECREASE the
nucleolus payoff of i or j (the two players whose joint opportunity improved)?
"""
import random, sys, json
from fractions import Fraction as F
from itertools import permutations
from tugame import Game, is_balanced_game
from nucleolus import prenucleolus_float, certified_prenucleolus

def assignment_game(A):
    m = len(A); mp = len(A[0]); n = m + mp
    v = [F(0)] * (1 << n)
    for S in range(1, 1 << n):
        rows = [i for i in range(m) if S >> i & 1]
        cols = [j for j in range(mp) if S >> (m + j) & 1]
        best = F(0)
        k = min(len(rows), len(cols))
        # brute-force matching (sizes <= 4)
        if k:
            if len(rows) <= len(cols):
                for perm in permutations(cols, len(rows)):
                    w = sum(F(A[r][c]) for r, c in zip(rows, perm))
                    best = max(best, w)
            else:
                for perm in permutations(rows, len(cols)):
                    w = sum(F(A[r][c]) for r, c in zip(perm, cols))
                    best = max(best, w)
        v[S] = best
    return Game(n, v)

def hunt(m, mp, trials, seed, vmax=12):
    rng = random.Random(seed)
    n = m + mp
    for t in range(trials):
        A = [[rng.randint(0, vmax) for _ in range(mp)] for _ in range(m)]
        g = assignment_game(A)
        x = prenucleolus_float(g)
        if x is None:
            continue
        i = rng.randrange(m); j = rng.randrange(mp)
        d = rng.choice([1, 2, 3])
        A2 = [row[:] for row in A]; A2[i][j] += d
        g2 = assignment_game(A2)
        y = prenucleolus_float(g2)
        if y is None:
            continue
        # watch the two players whose entry improved
        drops = [(p, x[p] - y[p]) for p in (i, m + j) if x[p] - y[p] > 1e-6]
        if drops:
            print(f"[cand] t={t} A={A} bump=({i},{j})+{d} drops={[(p, round(dd,4)) for p,dd in drops]}")
            gx = certified_prenucleolus(g); gy = certified_prenucleolus(g2)
            if gx is None or gy is None:
                print("  certification failed, skipping")
                continue
            ed = [(p, gx[p] - gy[p]) for p in (i, m + j) if gx[p] > gy[p]]
            if ed:
                print("CERTIFIED entry-monotonicity violation (own-payoff):")
                print(json.dumps({"A": A, "bump": [i, j, d],
                                  "x": [str(u) for u in gx], "y": [str(u) for u in gy],
                                  "drops": [(p, str(dd)) for p, dd in ed]}, indent=1))
                return True
    print("no certified violation", trials, "trials")
    return False

if __name__ == "__main__":
    m, mp, trials = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    hunt(m, mp, trials, seed)

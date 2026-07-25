"""Minimum cost spanning tree games. Players 1..n, source 0.
Cost c(S) = weight of MST on S + source (complete graph, integer costs).
We hunt COST monotonicity of the nucleolus of the cost game:
  raise one edge cost c_e by d; does some player's nucleolus COST SHARE
  strictly DECREASE ... or for edge (i,j), does a player incident to e
  see its share move perversely? Classic notion (cost monotonicity):
  if an edge incident to player i gets cheaper, i's share should not rise.
  We hunt the contrapositive form: bump c(e) up by d for e=(i,j) (i,j players
  or j=source) and flag if share of i strictly drops... i.e. i benefits
  from its own edge getting MORE expensive.

Cost game -> value game via savings: v(S) = sum_i c({i}) - c(S), nucleolus of
savings game maps back: share_i = c({i}) - x_i. We work directly on the cost
game's prenucleolus defined by excesses e(S,x) = x(S) - c(S) (mirror).
Equivalent: run value-game machinery on v(S) = -c(S) shifted? Simplest exact
mirror: prenucleolus of cost game = -(prenucleolus of value game w(S)=-c(S)).
w has w[0]=0 automatically since c(empty)=0.
"""
import random, sys, json
from fractions import Fraction as F
from tugame import Game
from nucleolus import prenucleolus_float, certified_prenucleolus

def mst_cost(nodes, C):
    """Prim on node set nodes (incl 0). C symmetric dict/matrix."""
    nodes = list(nodes)
    intree = {nodes[0]}
    total = 0
    rest = set(nodes[1:])
    while rest:
        best, bn = None, None
        for u in intree:
            for w in rest:
                cw = C[u][w]
                if best is None or cw < best:
                    best, bn = cw, w
        total += best
        intree.add(bn); rest.discard(bn)
    return total

def mcst_cost_game(n, C):
    """players 1..n (bit i-1 = player i), source 0. Returns cost list k[S]."""
    k = [0] * (1 << n)
    for S in range(1, 1 << n):
        nodes = [0] + [i + 1 for i in range(n) if S >> i & 1]
        k[S] = mst_cost(nodes, C)
    return k

def cost_prenuc_float(n, k):
    w = [F(0)] + [F(-k[S]) for S in range(1, 1 << n)]
    g = Game(n, w)
    x = prenucleolus_float(g)
    return None if x is None else [-xi for xi in x], g

def cost_prenuc_exact(n, k):
    w = [F(0)] + [F(-k[S]) for S in range(1, 1 << n)]
    g = Game(n, w)
    x = certified_prenucleolus(g)
    return None if x is None else [-xi for xi in x]

def hunt(n, trials, seed, cmax=12):
    rng = random.Random(seed)
    for t in range(trials):
        C = [[0] * (n + 1) for _ in range(n + 1)]
        for a in range(n + 1):
            for b in range(a + 1, n + 1):
                C[a][b] = C[b][a] = rng.randint(1, cmax)
        k = mcst_cost_game(n, C)
        r = cost_prenuc_float(n, k)
        if r is None:
            continue
        x, _ = r
        a = rng.randint(0, n); b = rng.randint(0, n)
        while b == a:
            b = rng.randint(0, n)
        d = rng.choice([1, 2, 3])
        C2 = [row[:] for row in C]; C2[a][b] += d; C2[b][a] += d
        k2 = mcst_cost_game(n, C2)
        r2 = cost_prenuc_float(n, k2)
        if r2 is None:
            continue
        y, _ = r2
        watch = [p - 1 for p in (a, b) if p >= 1]
        drops = [(p, x[p] - y[p]) for p in watch if x[p] - y[p] > 1e-6]
        if drops:
            print(f"[cand] t={t} edge=({a},{b})+{d} drops={[(p+1, round(dd,4)) for p,dd in drops]}")
            gx = cost_prenuc_exact(n, k); gy = cost_prenuc_exact(n, k2)
            if gx is None or gy is None:
                print("  certification failed"); continue
            ed = [(p, gx[p] - gy[p]) for p in watch if gx[p] > gy[p]]
            if ed:
                print("CERTIFIED: raising edge cost STRICTLY LOWERS incident player's share")
                print(json.dumps({"n": n, "C": C, "edge": [a, b], "d": d,
                                  "shares_before": [str(u) for u in gx],
                                  "shares_after": [str(u) for u in gy],
                                  "drops": [(p + 1, str(dd)) for p, dd in ed]}, indent=1))
                return True
    print("no certified violation in", trials, "trials")
    return False

if __name__ == "__main__":
    n, trials = int(sys.argv[1]), int(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    hunt(n, trials, seed)

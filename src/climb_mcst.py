"""Hill-climb hunt for cost-monotonicity violations of the nucleolus in MCST games.
Margin for cost matrix C and edge bump ((a,b),+d):
    f = max over incident PLAYERS p of  share_p(C) - share_p(C + d on (a,b))
(f > 0 means raising the edge's cost strictly LOWERED an incident player's share.)
"""
import random, sys, json
from mcst import mcst_cost_game, cost_prenuc_float, cost_prenuc_exact

def margin(n, C, a, b, d):
    k = mcst_cost_game(n, C)
    r = cost_prenuc_float(n, k)
    if r is None:
        return None
    x = r[0]
    C2 = [row[:] for row in C]; C2[a][b] += d; C2[b][a] += d
    k2 = mcst_cost_game(n, C2)
    r2 = cost_prenuc_float(n, k2)
    if r2 is None:
        return None
    y = r2[0]
    watch = [p - 1 for p in (a, b) if p >= 1]
    return max(x[p] - y[p] for p in watch)

def climb(n, restarts, steps, seed, cmax=15):
    rng = random.Random(seed)
    best_global = None
    for r in range(restarts):
        C = [[0] * (n + 1) for _ in range(n + 1)]
        for u in range(n + 1):
            for w in range(u + 1, n + 1):
                C[u][w] = C[w][u] = rng.randint(1, cmax)
        a = rng.randint(0, n); b = rng.randint(0, n)
        while b == a:
            b = rng.randint(0, n)
        d = rng.choice([1, 2])
        f = margin(n, C, a, b, d)
        if f is None:
            continue
        for s in range(steps):
            u = rng.randint(0, n); w = rng.randint(0, n)
            while w == u:
                w = rng.randint(0, n)
            delta = rng.choice([-2, -1, 1, 2])
            C2 = [row[:] for row in C]
            nv = max(1, C2[u][w] + delta)
            C2[u][w] = C2[w][u] = nv
            f2 = margin(n, C2, a, b, d)
            if f2 is not None and f2 > f:
                C, f = C2, f2
            if f > 1e-6:
                break
        if best_global is None or f > best_global[0]:
            best_global = (f, [row[:] for row in C], a, b, d)
            print(f"[restart {r}] best margin {f:.5f} edge=({a},{b})+{d}", flush=True)
        if f > 1e-6:
            print("FLOAT VIOLATION, certifying...", flush=True)
            k = mcst_cost_game(n, C)
            C2 = [row[:] for row in C]; C2[a][b] += d; C2[b][a] += d
            k2 = mcst_cost_game(n, C2)
            gx = cost_prenuc_exact(n, k); gy = cost_prenuc_exact(n, k2)
            if gx and gy:
                watch = [p - 1 for p in (a, b) if p >= 1]
                ed = [(p + 1, gx[p] - gy[p]) for p in watch if gx[p] > gy[p]]
                if ed:
                    print("CERTIFIED cost-monotonicity violation:")
                    print(json.dumps({"n": n, "C": C, "edge": [a, b], "d": d,
                                      "before": [str(u) for u in gx], "after": [str(u) for u in gy],
                                      "drops": [(p, str(dd)) for p, dd in ed]}, indent=1), flush=True)
                    return
            print("certification failed — false positive recorded", flush=True)
    print("best margin overall:", best_global[0] if best_global else None)
    if best_global:
        print("C =", best_global[1], "edge", best_global[2:])

if __name__ == "__main__":
    n, restarts, steps = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    climb(n, restarts, steps, seed)

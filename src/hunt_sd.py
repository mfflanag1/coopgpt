"""Hunt: coalitional monotonicity of the SD-prenucleolus on classes between
convex/veto (proven monotonic) and balanced (Housman-Clark forces failure).

Class-restricted claim: v, v' in class C, v'(S) = v(S)+d for ONE proper S,
equal elsewhere => SD_i(v') >= SD_i(v) for all i in S.
A certified violation on class C: both games verified in C (exact arithmetic),
both SD points certified (pointwise recursion + SD-Kohlberg balancedness),
some i in S drops (exact).
"""
import random, sys, json
from fractions import Fraction as F
from tugame import Game, is_balanced_game, exact_lp_min, popcount
from sd import sd_prenucleolus_float, certified_sd_prenucleolus
from hunt_monotonic import rand_game

def core_min_xS(game, S):
    """Exact min of x(S) over the core; None if core empty."""
    n, N = game.n, game.N
    A_ub, b_ub = [], []
    for T in range(1, N):
        A_ub.append([-1 if T >> i & 1 else 0 for i in range(n)])
        b_ub.append(-game.v[T])
    A_eq = [[1] * n]; b_eq = [game.v[N]]
    c = [1 if S >> i & 1 else 0 for i in range(n)]
    opt, _ = exact_lp_min(c, A_ub, b_ub, A_eq, b_eq)
    if opt is None or opt == 'unbounded':
        return None
    return opt

def is_exact_game(game):
    for S in range(1, game.N):
        m = core_min_xS(game, S)
        if m is None or m != game.v[S]:
            return False
    return True

def is_totally_balanced(game):
    for T in range(1, game.N + 1):
        if popcount(T) < 2:
            continue
        sub, _ = game.subgame(T)
        if not is_balanced_game(sub):
            return False
    return True

def exactify(game):
    """Exact cover: v_e(S) = min core x(S). Returns exact Game or None."""
    v2 = [F(0)] * (1 << game.n)
    v2[game.N] = game.v[game.N]
    for S in range(1, game.N):
        m = core_min_xS(game, S)
        if m is None:
            return None
        v2[S] = m
    return Game(game.n, v2)

def in_class(game, cls):
    if cls == "balanced":
        return is_balanced_game(game)
    if cls == "supbal":
        return game.is_superadditive() and is_balanced_game(game)
    if cls == "totbal":
        return is_totally_balanced(game)
    if cls == "exact":
        return is_exact_game(game)
    raise ValueError(cls)

def gen(cls, n, rng):
    g = rand_game(n, rng, "general")
    if cls == "exact":
        return exactify(g) if is_balanced_game(g) else None
    if cls in ("balanced", "supbal", "totbal"):
        return g if in_class(g, cls) else None
    return None

def hunt(cls, n, trials, seed, dmax=3):
    rng = random.Random(seed)
    tried = 0
    for t in range(trials):
        g = gen(cls, n, rng)
        if g is None:
            continue
        tried += 1
        x = sd_prenucleolus_float(g)
        if x is None:
            continue
        # try several bumps per game
        Ss = rng.sample(range(1, g.N), min(6, g.N - 1))
        for S in Ss:
            d = rng.randint(1, dmax)
            v2 = list(g.v); v2[S] += d
            g2 = Game(n, v2)
            y = sd_prenucleolus_float(g2)
            if y is None:
                continue
            drops = [(i, x[i] - y[i]) for i in range(n) if S >> i & 1 and x[i] - y[i] > 1e-6]
            if not drops:
                continue
            if not in_class(g2, cls):
                continue    # class exited; not a class-restricted witness
            print(f"[cand] t={t} cls={cls} S={S:b} d={d} drops={[(i, round(dd,4)) for i,dd in drops]}", flush=True)
            gx = certified_sd_prenucleolus(g)
            gy = certified_sd_prenucleolus(g2)
            if gx is None or gy is None:
                print("  certification failed", flush=True)
                continue
            ed = [(i, gx[i] - gy[i]) for i in range(n) if S >> i & 1 and gx[i] > gy[i]]
            if ed:
                print(f"CERTIFIED SD COALITIONAL-MONOTONICITY VIOLATION on class {cls}:", flush=True)
                print(json.dumps({"cls": cls, "n": n, "v": [str(u) for u in g.v], "S": S, "d": d,
                                  "x": [str(u) for u in gx], "y": [str(u) for u in gy],
                                  "drops": [(i, str(dd)) for i, dd in ed],
                                  "class_before": True, "class_after": True,
                                  "convex_before": g.is_convex(), "convex_after": g2.is_convex()},
                                 indent=1), flush=True)
                return True
    print(f"no certified violation: class={cls} n={n}, {tried} in-class games tried", flush=True)
    return False

if __name__ == "__main__":
    cls, n, trials = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    hunt(cls, n, trials, seed)

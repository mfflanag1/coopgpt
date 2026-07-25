"""Calibrate + hunt SD-prenucleolus coalitional monotonicity (FLOAT screen,
EXACT verify).

CALIBRATION (must be ZERO): convex & monotonic-veto games -- the classes where
Arin-Katsev proved coalitional monotonicity. A confirmed hit there refutes their
theorem (or my code); investigate before trusting anything else.

SEARCH: random balanced n=4 games (minimal size a core selector can fail,
Housman-Clark). Report the tightest class the failure already lives in.
"""
import sys, json, random
import numpy as np
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from sd_prenucleolus import sd_prenucleolus, sd_kohlberg
from sd_float import sd_prenucleolus_float
from hunt_sd_coalmono import classes
from validate_sd import random_monotonic_veto

def log(*a): print(*a, flush=True)
SCREEN = 1e-6

def balanced_float(vf, n):
    from scipy.optimize import linprog
    N = (1 << n) - 1
    Aub = [[-1.0 if S >> i & 1 else 0.0 for i in range(n)] for S in range(1, N)]
    bub = [-vf[S] for S in range(1, N)]
    r = linprog([1.0] * n, A_ub=np.array(Aub), b_ub=np.array(bub),
                bounds=[(None, None)] * n, method="highs")
    return r.success and r.fun <= vf[N] + 1e-9

def screen_game(vf, n, deltas, need_balanced):
    """Yield (S, delta) whose float SD shows a member of S losing payoff."""
    base = sd_prenucleolus_float(vf, n)
    if base is None:
        return
    N = (1 << n) - 1
    for S in range(1, N):
        for d in deltas:
            w = list(vf); w[S] += d
            if need_balanced and not balanced_float(w, n):
                continue
            aft = sd_prenucleolus_float(w, n)
            if aft is None:
                continue
            if any((S >> i & 1) and aft[i] < base[i] - SCREEN for i in range(n)):
                yield S, d

def exact_confirm(vint, n, S, d):
    """Return witness dict if exact SD confirms a violation, else None."""
    g = Game(n, [F(x) for x in vint])
    w = list(vint); w[S] += d
    gw = Game(n, [F(x) for x in w])
    b = sd_prenucleolus(g); a = sd_prenucleolus(gw)
    if b is None or a is None:
        return None
    losers = [i for i in range(n) if (S >> i & 1) and a[i] < b[i]]
    if not losers:
        return None
    okb, _ = sd_kohlberg(g, b); oka, _ = sd_kohlberg(gw, a)
    return dict(S=S, delta=d, losers=losers, before=b, after=a, g=g, gw=gw,
                kohl_before=okb, kohl_after=oka)

def random_convex(n, hi=6, rng=random):
    a = [rng.randint(0, hi) for _ in range(n)]
    bb = {(i, j): rng.randint(0, hi) for i in range(n) for j in range(i + 1, n)}
    v = [F(0)] * (1 << n)
    for S in range(1, 1 << n):
        mem = [i for i in range(n) if S >> i & 1]
        v[S] = F(sum(a[i] for i in mem)
                 + sum(bb[(i, j)] for x, i in enumerate(mem) for j in mem[x + 1:]))
    return Game(n, v)

def random_balanced_int(n, hi=9, rng=random, tries=40):
    for _ in range(tries):
        v = [0] * (1 << n)
        for S in range(1, 1 << n):
            v[S] = rng.randint(0, hi)
        v[(1 << n) - 1] = rng.randint(n, 3 * n)
        if balanced_float([float(x) for x in v], n):
            return v
    return None

RANK = {"convex": 0, "exact": 1, "totbal": 2, "balanced": 3, "none": 4}
def tightness(tags):
    for t in ("convex", "exact", "totbal", "balanced"):
        if t in tags:
            return t
    return "none"

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    random.seed(seed)

    # ---------- calibration: convex ----------
    hits = 0
    for k in range(100):
        g = random_convex(4)
        assert g.is_convex()
        vf = [float(x) for x in g.v]
        for S, d in screen_game(vf, 4, (F(1), F(2)), False):
            w = exact_confirm([int(x) for x in g.v], 4, S, d)
            if w:
                hits += 1
                log(f"!!! CALIB-CONVEX CONFIRMED seed{seed} k{k} S={S} d={d} "
                    f"losers={w['losers']} v={[int(x) for x in g.v]}")
    log(f"CALIB convex: 100 games -> confirmed violations={hits} (expect 0)")

    # ---------- calibration: veto ----------
    vhits = 0
    for k in range(100):
        nn = random.choice([3, 4])
        g = random_monotonic_veto(nn)
        vf = [float(x) for x in g.v]
        for S, d in screen_game(vf, nn, (F(1), F(2)), False):
            w = exact_confirm([int(x) for x in g.v], nn, S, d)
            if w:
                vhits += 1
                log(f"!!! CALIB-VETO CONFIRMED n{nn} k{k} S={S} d={d} "
                    f"losers={w['losers']} v={[int(x) for x in g.v]}")
    log(f"CALIB veto: 100 games -> confirmed violations={vhits} (expect 0)")

    # ---------- search: balanced n=4 ----------
    best = None; nconf = 0; games = 0
    for k in range(800):
        vint = random_balanced_int(4)
        if vint is None:
            continue
        games += 1
        vf = [float(x) for x in vint]
        for S, d in screen_game(vf, 4, (F(1), F(2), F(3)), True):
            w = exact_confirm(vint, 4, S, d)
            if not w:
                continue
            nconf += 1
            tv, tw = classes(w["g"]), classes(w["gw"])
            tight = max(tightness(tv), tightness(tw), key=lambda t: RANK[t])
            if best is None or RANK[tight] < best[0]:
                best = (RANK[tight], dict(
                    n=4, S=S, delta=str(d), losers=w["losers"],
                    before=[str(u) for u in w["before"]],
                    after=[str(u) for u in w["after"]],
                    v={s: int(vint[s]) for s in range(1, 16)},
                    w={s: int(w["gw"].v[s]) for s in range(1, 16)},
                    class_v=tv, class_w=tw, tight=tight,
                    kohl_before=w["kohl_before"], kohl_after=w["kohl_after"]))
                log(f"VIOLATION seed{seed} tight={tight} S={S} d={d} losers={w['losers']}")
                log(f"   class_v={tv} class_w={tw}")
                log(f"   before={best[1]['before']} after={best[1]['after']}")
                log(f"   v={best[1]['v']}")
        if k % 200 == 0:
            log(f"...progress k={k} games={games} confirmed={nconf}")
    log(f"SEARCH done: games={games} confirmed_violations={nconf}")
    if best:
        path = f"../results/SD_coalmono_witness_seed{seed}.json"
        json.dump(best[1], open(path, "w"), indent=1)
        log(f"BEST tight={best[1]['tight']} kohl_before={best[1]['kohl_before']} "
            f"kohl_after={best[1]['kohl_after']} -> {path}")

if __name__ == "__main__":
    main()

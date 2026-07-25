"""Hunt for SD-prekernel multi-valuedness on balanced games.

For each random balanced game g:
  1. x0 = float SD-prenucleolus (reference zero of the equalization objective).
  2. Float local search on the efficient hyperplane for OTHER low-residual points
     far from x0 (minimize sum (s_ij - s_ji)^2). Several restarts.
  3. Any far low-residual point: polish to exact rationals, verify EXACTLY with
     sdpk.is_equalized; then compute the EXACT SD-prenucleolus and confirm the
     found point differs from it.
"""
import random, sys, json
from fractions import Fraction as F
import numpy as np
from scipy.optimize import minimize
from tugame import Game, is_balanced_game
from sd import sd_prenucleolus_float, certified_sd_prenucleolus
from sdpk import is_equalized, is_efficient
from sdpk_float import s_pairs_float
from hunt_monotonic import rand_game

def obj_factory(n, N, vf, vN):
    def obj(t):
        xf = np.empty(n)
        xf[:n-1] = t
        xf[n-1] = vN - t.sum()
        res, _ = s_pairs_float(n, N, vf, xf)
        return sum(r*r for r in res)
    return obj

def to_x(n, t, vN):
    xf = np.empty(n)
    xf[:n-1] = t
    xf[n-1] = vN - t.sum()
    return xf

def polish(n, g, xf):
    vN = g.v[g.N]
    cands = []
    for md in (6, 12, 24, 48):
        x = [F(xf[i]).limit_denominator(md) for i in range(n-1)]
        x.append(vN - sum(x)); cands.append(x)
    for k in (1,2,3,4,6,8,12,24):
        x = [F(round(xf[i]*k), k) for i in range(n-1)]
        x.append(vN - sum(x)); cands.append(x)
    seen = set()
    for x in cands:
        key = tuple(x)
        if key in seen or sum(x) != vN:
            continue
        seen.add(key)
        if is_equalized(g, x):
            return x
    return None

def hunt(n, trials, seed, log, nstart=14):
    rng = random.Random(seed)
    tried = 0
    closest = None
    for t in range(trials):
        g = rand_game(n, rng, "general")
        if not is_balanced_game(g):
            continue
        x0f = sd_prenucleolus_float(g)
        if x0f is None:
            continue
        tried += 1
        vf = np.array([float(x) for x in g.v]); vN = float(g.v[g.N])
        obj = obj_factory(n, g.N, vf, vN)
        for s in range(nstart):
            if s < nstart//2:
                t0 = x0f[:n-1] + np.array([rng.uniform(-4,4) for _ in range(n-1)])
            else:
                base = vN/n
                t0 = np.array([base + rng.uniform(-vN, vN) for _ in range(n-1)])
            r = minimize(obj, t0, method="Nelder-Mead",
                         options={"xatol":1e-10,"fatol":1e-18,"maxiter":2000,"maxfev":2000})
            xf = to_x(n, r.x, vN)
            dist = float(np.max(np.abs(xf - x0f)))
            if r.fun < 1e-9 and dist > 1e-2:
                x = polish(n, g, xf)
                if x is not None:
                    xstar = certified_sd_prenucleolus(g)
                    if xstar is not None and list(x) != list(xstar) and is_equalized(g, xstar):
                        log_write(log, f"*** CANDIDATE trial {t}: exact 2nd equalized point\n"
                                       f"    v={vlist(g)}\n    x={x}\n    x*={list(xstar)}\n")
                        return ("WITNESS", g, x, xstar)
            if r.fun < 1e-7 and dist > 1e-2:
                if closest is None or r.fun < closest[0]:
                    closest = (r.fun, vlist(g), [round(float(v),4) for v in xf],
                               [round(float(v),4) for v in x0f], dist)
        if tried % 10 == 0:
            log_write(log, f"[hunt n={n}] tried {tried} (trial {t}); "
                           f"best far-residual: {closest[0] if closest else 'none'}\n")
    return ("NONE", closest, tried)

def vlist(g):
    return [int(x) if x.denominator==1 else str(x) for x in g.v]

def log_write(log, msg):
    log.write(msg); log.flush(); print(msg, end="", flush=True)

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    with open(f"../results/agent_sdpk_hunt_n{n}.txt", "a") as log:
        log_write(log, f"\n=== SD-PK hunt n={n} trials={trials} seed={seed} ===\n")
        res = hunt(n, trials, seed, log)
        if res[0] == "WITNESS":
            _, g, x, xstar = res
            out = {"n": n, "v": [str(v) for v in g.v],
                   "x_second": [str(v) for v in x],
                   "x_sd_prenucleolus": [str(v) for v in xstar]}
            with open("../results/agent_sdpk_witness.json", "w") as f:
                json.dump(out, f, indent=2)
            log_write(log, "SAVED witness to results/agent_sdpk_witness.json\n")
        else:
            _, closest, tried = res
            log_write(log, f"NO WITNESS in {tried} balanced games. "
                           f"Best far-from-x0 residual: {closest[0] if closest else 'none'}\n")
            if closest:
                log_write(log, f"  at v={closest[1]}\n  xf~={closest[2]}\n  x0~={closest[3]} (dist {closest[4]})\n")

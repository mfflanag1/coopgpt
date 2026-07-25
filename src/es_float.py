"""Fast FLOAT screener for exact non-ES games. Candidates certified exactly
via eshunt.is_ES + hunt_sd.is_exact_game.

core_min_float(S): min x(S) over core (HiGHS). exactify_float builds v_e(S)=core-min.
ega_float: egalitarian procedure in float with tolerance. Screen sum(claims)-v(N)>tol.
"""
import sys, random, json
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F

TOL = 1e-7

def core_min_all(n, v):
    """Return list ve[S] = min_{core} x(S) for all S (float), or None if core empty.
    core: x(T)>=v(T) all proper T, x(N)=v(N). Vars x free -> bounds (None,None)."""
    N = (1 << n) - 1
    # constraints: -x(T) <= -v(T) for proper T; equality x(N)=v(N)
    A_ub = []; b_ub = []
    for T in range(1, N):
        A_ub.append([-1.0 if T >> i & 1 else 0.0 for i in range(n)])
        b_ub.append(-v[T])
    A_eq = [[1.0] * n]; b_eq = [v[N]]
    ve = [0.0] * (1 << n)
    ve[N] = v[N]
    bounds = [(None, None)] * n
    for S in range(1, N):
        c = [1.0 if S >> i & 1 else 0.0 for i in range(n)]
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
        if not res.success:
            return None
        ve[S] = res.fun
    return ve


def ega_float(n, v):
    """Egalitarian claims in float. Returns (gamma list, sum-inflation over v(N))."""
    N = (1 << n) - 1
    coals = list(range(1, N + 1))
    P = 0
    gamma = [0.0] * n
    for k in range(n + 2):
        chi = {}
        for S in coals:
            fixedsum = 0.0; free = 0
            for i in range(n):
                if S >> i & 1:
                    if P >> i & 1: fixedsum += gamma[i]
                    else: free += 1
            d = {}
            if free == 0:
                for i in range(n):
                    if S >> i & 1: d[i] = gamma[i]
            else:
                share = (v[S] - fixedsum) / free
                for i in range(n):
                    if S >> i & 1:
                        d[i] = gamma[i] if (P >> i & 1) else share
            chi[S] = d
        maxval = [-1e18] * n
        for S in coals:
            for i, val in chi[S].items():
                if val > maxval[i]: maxval[i] = val
        newP = 0
        for S in coals:
            if abs(sum(chi[S].values()) - v[S]) > TOL * max(1, abs(v[S])):
                continue
            if all(val >= maxval[i] - TOL for i, val in chi[S].items()):
                newP |= S
                for i, val in chi[S].items():
                    gamma[i] = val
        if newP | P == P and P != N:
            return gamma, None  # stuck -> undecided
        P |= newP
        if P == N:
            return gamma, sum(gamma) - v[N]
    return gamma, None


def rand_game_seeded(n, rng, amax=8, slackmax=6):
    a = [rng.randint(0, amax) for _ in range(n)]
    N = (1 << n) - 1
    v = [0.0] * (1 << n)
    for S in range(1, N):
        aS = sum(a[i] for i in range(n) if S >> i & 1)
        v[S] = max(0.0, aS - rng.randint(0, slackmax))
    v[N] = float(sum(a))
    return v, a


def certify(n, ve_float, orig_v):
    """Re-derive exact game by exactifying orig_v (exact) and check ES exactly."""
    from tugame import Game
    from hunt_sd import exactify, is_exact_game
    from eshunt import is_ES
    g = Game(n, [F(x).limit_denominator(10**6) for x in orig_v])
    ge = exactify(g)
    if ge is None:
        return None
    ok_exact = is_exact_game(ge)
    es, gamma = is_ES(ge)
    return {"exact": ok_exact, "ES": es, "claims": [str(x) for x in gamma],
            "v": [str(x) for x in ge.v], "infl": str(sum(gamma) - ge.v[ge.N])}


def search(n, trials, seed, report=2000):
    rng = random.Random(seed)
    tested = 0; worst = 0.0; cands = 0
    for t in range(trials):
        v, a = rand_game_seeded(n, rng)
        ve = core_min_all(n, v)
        if ve is None:
            continue
        gamma, infl = ega_float(n, ve)
        if infl is None:
            continue
        tested += 1
        if infl > worst: worst = infl
        if infl > 1e-5:
            cands += 1
            print(f"[float-cand] t={t} infl={infl:.6f} -> certifying...", flush=True)
            res = certify(n, ve, v)
            print("  CERT:", json.dumps(res), flush=True)
            if res and res["exact"] and not res["ES"]:
                print("CERTIFIED EXACT NON-ES COUNTEREXAMPLE", flush=True)
                with open(f"COUNTEREX_es_n{n}_s{seed}_t{t}.json", "w") as f:
                    json.dump(res, f, indent=1)
                return res
        if tested % report == 0:
            print(f"  n={n} s={seed}: {tested} tested, worst_float_infl={worst:.2e}, cands={cands}", flush=True)
    print(f"DONE n={n} s={seed}: {tested} exact games screened, worst_float_infl={worst:.3e}, {cands} candidates", flush=True)
    return None


if __name__ == "__main__":
    n = int(sys.argv[1]); trials = int(sys.argv[2]); seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    search(n, trials, seed)

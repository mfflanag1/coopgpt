"""Hunt EXACT games (thin core, min-of-points generator) whose Davis-Maschler
bargaining set strictly contains the core -> kills 'exactness => BS = core'.

Candidate generator: Stearns transfer scheme -> a kernel point (kernel subset BS).
A kernel point outside the core is a BS\\core point.  Certified by the exact
bargaining_set oracle (independent of how the point was found).
"""
import random, sys, json, time
import numpy as np
from fractions import Fraction as F
from tugame import Game
from bargaining_set import in_bargaining_set


def _masks(n):
    N = (1 << n) - 1
    M = np.zeros((N + 1, n), dtype=np.float64)     # membership incidence
    for S in range(1, N + 1):
        for i in range(n):
            if S >> i & 1:
                M[S, i] = 1.0
    return M


def transfer_kernel(vf, M, ivals, x0, iters=600, tol=1e-11):
    """Stearns transfer scheme (numpy) from imputation x0 -> a kernel-ish point.
    vf: float value array (2^n), M: incidence (2^n x n), ivals: singleton values."""
    n = M.shape[1]; N = (1 << n) - 1
    x = np.array(x0, dtype=np.float64)
    for _ in range(iters):
        xS = M @ x                                  # x(S) for all S
        e = vf - xS
        e[0] = -1e18; e[N] = -1e18                  # exclude empty & grand
        # s_ij = max over S with i in S, j notin S of e[S]
        s = np.full((n, n), -1e18)
        for i in range(n):
            inc = M[:, i] > 0.5
            for j in range(n):
                if i == j:
                    continue
                sel = inc & (M[:, j] < 0.5)
                s[i, j] = e[sel].max()
        best = None; bestd = tol
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                d = s[i, j] - s[j, i]
                if d > bestd and x[j] - ivals[j] > tol:
                    bestd = d; best = (i, j, d)
        if best is None:
            break
        i, j, d = best
        delta = min(d / 2.0, x[j] - ivals[j])
        x[i] += delta; x[j] -= delta
    return x.tolist()


def rand_point_sum(n, c, rng):
    if n == 1:
        return [c]
    cuts = sorted(rng.randint(0, c) for _ in range(n - 1))
    prev = 0; p = []
    for xx in cuts:
        p.append(xx - prev); prev = xx
    p.append(c - prev)
    return p


def game_from_points(n, pts):
    N = (1 << n) - 1
    c = sum(pts[0])
    v = [0] * (1 << n)
    for S in range(1, N):
        v[S] = min(sum(pts[j][i] for i in range(n) if S >> i & 1) for j in range(len(pts)))
    v[N] = c
    return Game(n, [F(x) for x in v])


def rationalize_check(game, xf, max_den=10 ** 6):
    """Snap floats to simple rationals summing to v(N); return list or None."""
    n = game.n
    xr = [F(xf[i]).limit_denominator(max_den) for i in range(n)]
    diff = game.v[game.N] - sum(xr)
    xr[-1] += diff
    return xr


def try_game(game, rng, M, starts=10):
    """Return a certified (x, viol_coalitions) BS\\core witness or None."""
    n, N = game.n, game.N
    vf = np.array([float(t) for t in game.v])
    ivals = np.array([float(game.v[1 << i]) for i in range(n)])
    vN = float(game.v[N])
    base = ivals.tolist()
    rem0 = vN - sum(base)
    if rem0 < 0:
        return None
    starts_w = []
    for i in range(n):                    # extreme imputations
        e = [0.0] * n; e[i] = 1.0; starts_w.append(e)
    for _ in range(starts):               # random Dirichlet
        starts_w.append([rng.random() for _ in range(n)])
    cand_seen = set()
    for w in starts_w:
        sw = sum(w) or 1.0
        x0 = [base[i] + rem0 * w[i] / sw for i in range(n)]
        xf = transfer_kernel(vf, M, ivals, x0)
        xr = rationalize_check(game, xf)
        if xr is None:
            continue
        key = tuple(xr)
        if key in cand_seen:
            continue
        cand_seen.add(key)
        if any(xr[i] < game.v[1 << i] for i in range(n)):
            continue
        if sum(xr) != game.v[N]:
            continue
        viol = game.core_violations(xr)
        if not viol:
            continue                      # inside core, not a witness
        inbs, w_ = in_bargaining_set(game, xr)
        if inbs:
            return xr, viol
    return None


def hunt(n, trials, seed, cmax=24, kmax=3):
    rng = random.Random(seed)
    LOG = f"/Users/maxf/projects/counterexample-hunt/coopgames/results/wildcard_bs_n{n}_s{seed}.txt"
    def log(m):
        print(m, flush=True)
        with open(LOG, "a") as f:
            f.write(m + "\n")
    M = _masks(n)
    t0 = time.time(); exact_seen = 0; nonconvex = 0
    for t in range(trials):
        k = rng.randint(2, kmax)
        c = rng.randint(n, cmax)
        pts = [rand_point_sum(n, c, rng) for _ in range(k)]
        g = game_from_points(n, pts)      # exact by construction (points in core)
        exact_seen += 1
        if g.is_convex():               # convex => BS=core, skip
            continue
        nonconvex += 1
        res = try_game(g, rng, M)
        if res is not None:
            xr, viol = res
            log("*** CERTIFIED: exact non-convex game with BS point outside core ***")
            rep = {"n": n, "seed": seed, "trial": t, "points": pts,
                   "v": [str(x) for x in g.v], "witness_x": [str(x) for x in xr],
                   "core_violations": [{"S": S, "members": [i for i in range(n) if S >> i & 1],
                                        "v(S)": str(g.v[S]),
                                        "x(S)": str(sum(xr[i] for i in range(n) if S >> i & 1))}
                                       for S in viol],
                   "is_exact": True, "is_convex": False}
            log(json.dumps(rep, indent=1))
            WIT = f"/Users/maxf/projects/counterexample-hunt/coopgames/results/WITNESS_bs_exact_n{n}.json"
            with open(WIT, "w") as f:
                json.dump(rep, f, indent=1)
            return rep
        if t % 200 == 0 and t:
            log(f"... t={t} exact_seen={exact_seen} nonconvex={nonconvex} "
                f"elapsed={time.time()-t0:.0f}s")
    log(f"DONE n={n} seed={seed}: trials={trials} exact_seen={exact_seen} "
        f"nonconvex={nonconvex} NO witness")
    return None


if __name__ == "__main__":
    n = int(sys.argv[1]); trials = int(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    hunt(n, trials, seed)

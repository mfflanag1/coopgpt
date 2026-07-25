"""Hunt non-ES exact games via the point-generator.

FACT: for any finite point set P in R^n with common sum c, the game
      v(S) = min_{x in P} x(S)  (proper S),   v(N) = c
is EXACT. Proof: core(v) contains P, and x(S) >= v(S) on the core forces
min_core x(S) = v(S). Few points => thin, often non-large core = the frontier where
a non-ES exact game (if any) must live. The egalitarian procedure is pure exact
arithmetic (no LP), so this sweep is fast and fully exact.
"""
import random, sys, json, time
from fractions import Fraction as F
from tugame import Game
from pes import egalitarian_procedure, pes
from hunt_sd import is_exact_game

LOG = "/Users/maxf/projects/counterexample-hunt/coopgames/results/agent_pes.txt"
WIT = "/Users/maxf/projects/counterexample-hunt/coopgames/results/WITNESS_exact_not_ES.json"


def log(msg):
    print(msg, flush=True)
    with open(LOG, "a") as f:
        f.write(msg + "\n"); f.flush()


def rand_point_sum(n, c, rng):
    """n nonneg integers summing to c (random composition)."""
    if n == 1:
        return [c]
    cuts = sorted(rng.randint(0, c) for _ in range(n - 1))
    prev = 0; p = []
    for x in cuts:
        p.append(x - prev); prev = x
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


def certify(g):
    exact = is_exact_game(g)
    claims, A_hat, is_ES = egalitarian_procedure(g)
    p, D = pes(g)
    viols = g.core_violations(p)
    return {
        "n": g.n, "v": [str(x) for x in g.v], "is_exact": exact, "is_ES": is_ES,
        "N_in_Ahat": g.N in A_hat, "claims": [str(x) for x in claims],
        "sum_claims_minus_vN": str(sum(claims) - g.v[g.N]),
        "A_hat": sorted(A_hat), "PES": [str(x) for x in p], "strong_D": D,
        "PES_core_violations": [{"S": S, "v(S)": str(g.v[S]), "x(S)": str(g.xS(p, S))}
                                for S in viols],
    }, (exact and not is_ES)


def greedy_minimize(g):
    from tugame import is_balanced_game
    v = [int(x) for x in g.v]; n, N = g.n, g.N
    improved = True
    while improved:
        improved = False
        for S in range(1, N):
            while v[S] > 0:
                trial = list(v); trial[S] -= 1
                gt = Game(n, [F(x) for x in trial])
                if not is_balanced_game(gt) or not is_exact_game(gt):
                    break
                _, _, est = egalitarian_procedure(gt)
                if est:
                    break
                v = trial; improved = True
    return Game(n, [F(x) for x in v])


def hunt(n, trials, seed, cmax=30, kmax=4):
    rng = random.Random(seed)
    t0 = time.time()
    seen = 0; nonES = 0; maxslack = F(0)
    for t in range(trials):
        k = rng.randint(2, kmax)
        c = rng.randint(n, cmax)
        pts = [rand_point_sum(n, c, rng) for _ in range(k)]
        g = game_from_points(n, pts)
        seen += 1
        claims, A_hat, is_ES = egalitarian_procedure(g)
        slack = sum(claims) - g.v[g.N]
        if slack > maxslack:
            maxslack = slack
        if not is_ES:
            nonES += 1
            log(f"[cand] t={t} seed={seed} slack={slack} NON-ES (exact by construction)")
            rep, ok = certify(g)
            if ok:
                log("*** CONFIRMED exact game NOT egalitarian stable ***")
                log(json.dumps(rep, indent=1))
                gm = greedy_minimize(g)
                repm, okm = certify(gm)
                out = {"witness": rep, "minimized": repm if okm else None,
                       "seed": seed, "trial": t, "points": pts}
                with open(WIT, "w") as f:
                    json.dump(out, f, indent=1)
                log(f"witness saved; minimized_ok={okm}")
                if okm:
                    log("MINIMIZED:\n" + json.dumps(repm, indent=1))
                return out
            else:
                log(f"[rejected] is_exact={rep['is_exact']} is_ES={rep['is_ES']}")
        if seen % 20000 == 0:
            log(f"... t={t} seed={seed} seen={seen} nonES={nonES} maxslack={maxslack} "
                f"elapsed={time.time()-t0:.0f}s")
    log(f"DONE points seed={seed}: seen={seen} nonES={nonES} maxslack={maxslack} trials={trials}")
    return None


if __name__ == "__main__":
    n = int(sys.argv[1]); trials = int(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    hunt(n, trials, seed)

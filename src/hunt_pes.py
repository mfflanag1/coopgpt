"""Hunt: an EXACT 5-player game that is NOT egalitarian stable.

Refutes Dietzenbacher (GEB 2021) open question. For n<=4, exact => large core => ES
(impossible), so n=5 is the frontier. Strategy: exactify random balanced 5-player
games (exactify = min-core cover, always exact) and test N in A-hat exactly.
Structural families biased toward THIN cores (non-large-core), since large core => ES.
"""
import random, sys, json, time
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from hunt_sd import exactify, is_exact_game
from hunt_monotonic import rand_game
from pes import egalitarian_procedure, pes

LOG = "/Users/maxf/projects/counterexample-hunt/coopgames/results/agent_pes.txt"
WIT = "/Users/maxf/projects/counterexample-hunt/coopgames/results/WITNESS_exact_not_ES.json"


def log(msg):
    print(msg, flush=True)
    with open(LOG, "a") as f:
        f.write(msg + "\n")
        f.flush()


def core_min_slack(game, claims):
    """sum(claims) - v(N): aspiration excess. 0 iff ES (at full-fix termination)."""
    return sum(claims) - game.v[game.N]


def rand_thin(n, rng, vmax=20):
    """Random game biased to a thin (non-large) core: high pairwise/mid worths that
    conflict. Zero-normalized, superadditive-ish via lower bounds."""
    from hunt_monotonic import popcount
    Nm = (1 << n) - 1
    v = [F(0)] * (1 << n)
    order = sorted(range(1, Nm + 1), key=popcount)
    for S in order:
        pc = popcount(S)
        if pc == 1:
            continue
        lo = 0
        T = (S - 1) & S
        while T:
            lo = max(lo, int(v[T] + v[S ^ T]))
            T = (T - 1) & S
        # push mid-size coalitions high (creates conflicting demands -> thin core)
        if pc in (2, 3):
            v[S] = F(lo + rng.randint(vmax // 2, vmax))
        else:
            v[S] = F(lo + rng.randint(0, vmax // 2))
    return Game(n, v)


def certify_witness(g):
    """Full exact certification of a non-ES exact game."""
    exact = is_exact_game(g)
    claims, A_hat, is_ES = egalitarian_procedure(g)
    p, D = pes(g)
    viols = g.core_violations(p)
    slack = core_min_slack(g, claims)
    rep = {
        "n": g.n,
        "v": [str(x) for x in g.v],
        "is_exact": exact,
        "is_ES": is_ES,
        "N_in_Ahat": g.N in A_hat,
        "claims": [str(x) for x in claims],
        "sum_claims_minus_vN": str(slack),
        "A_hat": sorted(A_hat),
        "PES": [str(x) for x in p],
        "strong_claimants_D": D,
        "PES_core_violations": [{"S": S, "v(S)": str(g.v[S]),
                                 "x(S)": str(g.xS(p, S))} for S in viols],
    }
    return rep, (exact and not is_ES)


def greedy_minimize(g):
    """Shrink integer worths while keeping exact + non-ES. Returns minimized Game."""
    v = [int(x) for x in g.v]
    n, N = g.n, g.N
    improved = True
    while improved:
        improved = False
        for S in range(1, N):          # never touch v(N)
            while v[S] > 0:
                trial = list(v)
                trial[S] -= 1
                gt = Game(n, [F(x) for x in trial])
                if not is_balanced_game(gt):
                    break
                if not is_exact_game(gt):
                    break
                _, _, est = egalitarian_procedure(gt)
                if est:
                    break
                v = trial
                improved = True
    return Game(n, [F(x) for x in v])


def hunt(n, trials, seed, family="mix"):
    rng = random.Random(seed)
    t0 = time.time()
    exact_seen = 0
    non_es = 0
    min_slack = None
    for t in range(trials):
        if family == "thin":
            g0 = rand_thin(n, rng)
        elif family == "general":
            g0 = rand_game(n, rng, "general")
        else:  # mix
            g0 = rand_thin(n, rng) if rng.random() < 0.5 else rand_game(n, rng, "general")
        if not is_balanced_game(g0):
            continue
        g = exactify(g0)
        if g is None:
            continue
        exact_seen += 1
        claims, A_hat, is_ES = egalitarian_procedure(g)
        slack = core_min_slack(g, claims)
        if not is_ES:
            non_es += 1
            log(f"[cand] t={t} NON-ES exact game found (slack={slack})")
            rep, confirmed = certify_witness(g)
            if confirmed:
                log("*** CONFIRMED: exact game that is NOT egalitarian stable ***")
                log(json.dumps(rep, indent=1))
                gm = greedy_minimize(g)
                repm, okm = certify_witness(gm)
                out = {"witness": rep, "minimized": repm if okm else None,
                       "seed": seed, "trial": t, "family": family}
                with open(WIT, "w") as f:
                    json.dump(out, f, indent=1)
                log(f"witness saved to {WIT}; minimized_ok={okm}")
                if okm:
                    log("MINIMIZED:\n" + json.dumps(repm, indent=1))
                return out
        else:
            if slack != 0:
                log(f"[warn] ES but slack={slack} (N in A-hat via unfixed route) t={t}")
        if min_slack is None or slack < min_slack:
            if slack > 0:
                min_slack = slack
        if exact_seen % 100 == 0:
            log(f"... t={t} exact_seen={exact_seen} non_es={non_es} "
                f"min_pos_slack={min_slack} elapsed={time.time()-t0:.0f}s")
    log(f"DONE family={family}: {exact_seen} exact games, {non_es} non-ES, "
        f"min positive slack seen={min_slack}, trials={trials}")
    return None


def calibrate_n4(trials, seed):
    """Every exact n<=4 game must be ES. If any is not, the impl is buggy."""
    rng = random.Random(seed)
    seen = 0
    for _ in range(trials):
        g0 = rand_thin(4, rng) if rng.random() < 0.5 else rand_game(4, rng, "general")
        if not is_balanced_game(g0):
            continue
        g = exactify(g0)
        if g is None:
            continue
        seen += 1
        _, _, is_ES = egalitarian_procedure(g)
        if not is_ES:
            log(f"[CALIBRATION FAILURE] exact n=4 game NOT ES: v={[str(x) for x in g.v]}")
            return False
    log(f"[calibrate n=4] {seen} exact games, all ES (as required)")
    return True


if __name__ == "__main__":
    if sys.argv[1] == "calibrate":
        calibrate_n4(int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 1)
    else:
        n = int(sys.argv[1]); trials = int(sys.argv[2])
        seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        family = sys.argv[4] if len(sys.argv) > 4 else "mix"
        hunt(n, trials, seed, family)

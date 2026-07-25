"""Population-monotonicity hunter for the SD-prenucleolus on CONVEX games.

PM: for all i in S subset T, phi_i(v|S) <= phi_i(v|T). Adjacent pairs |T\\S|=1
suffice. Float screen with sd_prenucleolus_float over all subgames >=2 players;
certify candidates with certified_sd_prenucleolus on BOTH subgames + exact
convexity of the full game.
"""
import random, sys, json
from fractions import Fraction as F
from tugame import Game, members
from sd import sd_prenucleolus_float, certified_sd_prenucleolus
from hunt_monotonic import rand_game, popcount

def pm_violation_float(g):
    """Scan adjacent subgame pairs; return worst float violation (gap,S,T,i) or None."""
    n, Nm = g.n, g.N
    sd = {}
    for T in range(1, Nm + 1):
        if popcount(T) < 2:
            continue
        sub, mem = g.subgame(T)
        x = sd_prenucleolus_float(sub)
        if x is None:
            return None
        sd[T] = dict(zip(mem, x))
    worst = None
    for T in sd:
        for j in members(T, n):
            S = T ^ (1 << j)
            if S not in sd:
                continue
            for i in members(S, n):
                gap = sd[S][i] - sd[T][i]
                if gap > 1e-6 and (worst is None or gap > worst[0]):
                    worst = (gap, S, T, i)
    return worst

def certify_pm(g, S, T, i):
    subS, memS = g.subgame(S)
    subT, memT = g.subgame(T)
    xS = certified_sd_prenucleolus(subS)
    xT = certified_sd_prenucleolus(subT)
    if xS is None or xT is None:
        return None
    vi_S = xS[memS.index(i)]
    vi_T = xT[memT.index(i)]
    if vi_S <= vi_T:
        return None
    return {
        "n": g.n, "v": [str(t) for t in g.v],
        "S": S, "T": T, "player": i,
        "phi_i_S": str(vi_S), "phi_i_T": str(vi_T), "gap": str(vi_S - vi_T),
        "phi_S": [str(t) for t in xS], "memS": memS,
        "phi_T": [str(t) for t in xT], "memT": memT,
        "convex_full": g.is_convex(),
    }

def run(n, trials, seed, log):
    rng = random.Random(seed)
    cert = None
    for t in range(trials):
        g = rand_game(n, rng, "convex")
        w = pm_violation_float(g)
        if w:
            gap, S, T, i = w
            msg = f"[cand] n={n} trial={t} gap~{gap:.5f} S={S:b} T={T:b} i={i}"
            print(msg); log.write(msg + "\n"); log.flush()
            rep = certify_pm(g, S, T, i)
            if rep and rep["convex_full"]:
                cert = rep
                log.write("CERTIFIED PM VIOLATION\n"); log.write(json.dumps(rep, indent=1) + "\n")
                log.flush()
                break
            else:
                log.write(f"  [not certified] rep={rep is not None} "
                          f"convex={rep['convex_full'] if rep else '-'}\n"); log.flush()
        if t % 25 == 0:
            log.write(f"..n={n} trial={t} clean\n"); log.flush()
    return cert

if __name__ == "__main__":
    n = int(sys.argv[1]); trials = int(sys.argv[2]); seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    logpath = sys.argv[4] if len(sys.argv) > 4 else "../results/agent_sd_pm.txt"
    with open(logpath, "a") as log:
        log.write(f"=== run n={n} trials={trials} seed={seed} ===\n"); log.flush()
        cert = run(n, trials, seed, log)
        if cert:
            with open("../results/agent_sd_pm_witness.json", "w") as f:
                json.dump(cert, f, indent=1)
            print("CERTIFIED PM VIOLATION -> results/agent_sd_pm_witness.json")
            print(json.dumps(cert, indent=1))
        else:
            print(f"no certified PM violation in {trials} trials (n={n}, seed={seed})")
            log.write(f"=== DONE: no violation n={n} trials={trials} seed={seed} ===\n"); log.flush()

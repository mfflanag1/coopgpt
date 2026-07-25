"""Tightest single-base shape at n=5: a MAXIMAL star -- base b plus EVERY
exact-preserving single bump as an arm (the largest set of monotonicity
constraints that can hang off one shared base point). If piling on arms ever
drives the family slack negative, this is where it shows. Float; negative-slack
hits are handed to hunt_frontier5.certify.
"""
import random, sys, time, json
from scipy.optimize import linprog
from fractions import Fraction as F
from floatscreen import is_exact_float, _core_min_xS_float, is_balanced_float
from tugame import Game, is_balanced_game
from hunt_sd import exactify, is_exact_game
from family_infeasible import is_family_feasible, certify_infeasible

n = 5
N = (1 << n) - 1

def float_exactify(vf):
    v2 = [0.0] * (1 << n); v2[N] = vf[N]
    for S in range(1, N):
        m = _core_min_xS_float(n, vf, S)
        if m is None:
            return None
        v2[S] = m
    return v2

def seed_gen(rng, kind):
    if kind == "neardegen":
        a = [rng.randint(0, 4) for _ in range(n)]
        vf = [float(sum(a[i] for i in range(n) if S >> i & 1)) for S in range(1 << n)]
        for _ in range(rng.randint(1, 4)):
            T = rng.randint(1, N); w = rng.randint(1, 3)
            for S in range(1, N + 1):
                if S & T == T:
                    vf[S] += w
        return vf
    c = rng.randint(6, 16); vf = [0.0] * (1 << n); vf[N] = float(c)
    for _ in range(rng.randint(2, 10)):
        vf[rng.randint(1, N - 1)] = float(rng.randint(0, c - 1))
    return vf

def slack(games_v, edges):
    m = len(games_v); nv = n * m + 1; ti = n * m
    A, b, Aeq, beq = [], [], [], []
    for k in range(m):
        row = [0.0] * nv
        for i in range(n):
            row[k * n + i] = 1.0
        Aeq.append(row); beq.append(games_v[k][N])
    for k in range(m):
        for T in range(1, N):
            row = [0.0] * nv
            for i in range(n):
                if T >> i & 1:
                    row[k * n + i] = -1.0
            A.append(row); b.append(-games_v[k][T])
    for (k, l, S) in edges:
        for i in range(n):
            if S >> i & 1:
                row = [0.0] * nv
                row[k * n + i] = 1.0; row[l * n + i] = -1.0; row[ti] = 1.0
                A.append(row); b.append(0.0)
    c = [0.0] * nv; c[ti] = -1.0
    r = linprog(c, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq, bounds=[(None, None)] * nv, method="highs")
    return None if not r.success else -r.fun

def run(trials, seed, dmax=3, logpath=None):
    rng = random.Random(seed)
    log = open(logpath, "a") if logpath else None
    def out(s):
        print(s, flush=True)
        if log:
            log.write(s + "\n"); log.flush()
    out(f"=== probe_maxstar5 trials={trials} seed={seed} dmax={dmax} @ {time.strftime('%H:%M:%S')} ===")
    bases = 0; min_slack = None; max_arms = 0; t0 = time.time()
    for t in range(trials):
        seed_int = seed_gen(rng, "neardegen" if t % 2 == 0 else "asym")
        if not is_balanced_float(n, seed_int):
            continue
        base = float_exactify(seed_int)
        if base is None or not is_exact_float(n, base):
            continue
        # maximal arm set: every coalition whose single bump keeps exactness,
        # at the largest exact-preserving depth
        arms = []
        for S in range(1, N):
            best = None
            for d in range(1, dmax + 1):
                v2 = list(base); v2[S] += d
                if is_exact_float(n, v2):
                    best = d
                else:
                    break
            if best:
                arms.append((S, best))
        if len(arms) < 3:
            continue
        bases += 1
        max_arms = max(max_arms, len(arms))
        games_v = [base]
        for S, d in arms:
            v2 = list(base); v2[S] += d; games_v.append(v2)
        edges = [(0, j + 1, S) for j, (S, d) in enumerate(arms)]
        s = slack(games_v, edges)
        if s is None:
            continue
        if min_slack is None or s < min_slack:
            min_slack = s
            out(f"[newmin] slack={s:.5f} arms={len(arms)} t={t}")
        if s < 1e-6:
            out(f"[CANDIDATE] t={t} maxstar arms={len(arms)} slack={s:.3e} -> certify")
            eb = exactify(Game(n, [F(x) for x in seed_int]))
            if eb is None or not is_exact_game(eb):
                out("  [reject] exact base failed"); continue
            games = [eb]
            for S, d in arms:
                v2 = list(eb.v); v2[S] += d; games.append(Game(n, v2))
            if not all(is_exact_game(g) for g in games):
                out("  [reject] member not exact"); continue
            feas, _ = is_family_feasible(games, edges)
            if feas:
                out("  [reject] exact FEASIBLE (float false pos)"); continue
            cert = certify_infeasible(games, edges)
            if not cert["infeasible"]:
                out(f"  [reject] recheck feasible: {cert.get('reason')}"); continue
            fk = cert.get("farkas")
            payload = {"claim": "INFEASIBLE exact n=5 maximal-star family", "arms": len(arms),
                       "edges": edges, "games": [[str(u) for u in g.v] for g in games],
                       "all_exact": [is_exact_game(g) for g in games],
                       "farkas": None if fk is None else {"rhs": str(fk["rhs"]),
                           "active_ineq": [(m, str(y)) for m, y in fk["active_ineq"]],
                           "active_eq": [(m, str(y)) for m, y in fk["active_eq"]]}}
            with open("../results/WITNESS_family_exact5.json", "w") as f:
                json.dump(payload, f, indent=1)
            out("!!! CERTIFIED INFEASIBLE EXACT n=5 MAXIMAL-STAR FAMILY !!!")
            out(json.dumps(payload, indent=1))
            return payload
        if bases % 40 == 0:
            out(f"[progress] t={t} bases={bases} min_slack={min_slack:.5f} max_arms={max_arms} elapsed={time.time()-t0:.0f}s")
    out(f"[DONE] bases={bases} min_slack={min_slack} max_arms={max_arms} elapsed={time.time()-t0:.0f}s")
    return None

if __name__ == "__main__":
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 303
    dmax = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    logpath = sys.argv[4] if len(sys.argv) > 4 else "../results/agent_maxstar5.txt"
    run(trials, seed, dmax=dmax, logpath=logpath)

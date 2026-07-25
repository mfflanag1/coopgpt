"""Aggressive slack-frontier search at n=5: drive the family monotonicity slack
toward 0 (or negative) using ASYMMETRIC and NEAR-DEGENERATE exact bases -- the
regime the lead flags as where infeasibility (if any) lives.

Base types:
  neardegen : additive a_i + small supermodular perturbation, exactified
              (thin/low-dimensional core).
  asym      : simplex v(N)=c with heavily asymmetric proper values, exactified.
All float; a negative-slack hit is handed to exact certification (hunt_family5.exact_certify).
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

def coord_widths(vf):
    """max-min of each x_i over core (float) -- small sum => near-degenerate."""
    A, b = [], []
    for T in range(1, N):
        A.append([-1.0 if T >> i & 1 else 0.0 for i in range(n)]); b.append(-vf[T])
    Aeq = [[1.0] * n]; beq = [vf[N]]
    w = []
    for i in range(n):
        c = [0.0] * n; c[i] = 1.0
        rlo = linprog(c, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq, bounds=[(None, None)] * n, method="highs")
        c[i] = -1.0
        rhi = linprog(c, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq, bounds=[(None, None)] * n, method="highs")
        if not (rlo.success and rhi.success):
            return None
        w.append(-rhi.fun - rlo.fun)
    return w

def neardegen_seed(rng):
    a = [rng.randint(0, 4) for _ in range(n)]
    vf = [0.0] * (1 << n)
    for S in range(1, N + 1):
        vf[S] = float(sum(a[i] for i in range(n) if S >> i & 1))
    # small supermodular perturbation: add w * unanimity_T for a few T
    for _ in range(rng.randint(1, 4)):
        T = rng.randint(1, N)
        w = rng.randint(1, 3)
        for S in range(1, N + 1):
            if S & T == T:
                vf[S] += w
    return vf

def asym_seed(rng):
    c = rng.randint(6, 16)
    vf = [0.0] * (1 << n); vf[N] = float(c)
    for _ in range(rng.randint(2, 10)):
        S = rng.randint(1, N - 1)
        vf[S] = float(rng.randint(0, c - 1))
    return vf

def family_slack(games_v, edges):
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

def arm_pool(base, dmax):
    pool = {}
    for S in range(1, N):
        best = None
        for d in range(1, dmax + 1):
            v2 = list(base); v2[S] += d
            if is_exact_float(n, v2):
                best = d
            else:
                break
        if best:
            pool[S] = best
    return pool

def shapes(base, pool, rng):
    out = []
    cos = [(N ^ (1 << k), pool[N ^ (1 << k)]) for k in range(n) if (N ^ (1 << k)) in pool]
    if len(cos) >= 2:
        gv = [base] + [_bump(base, S, d) for S, d in cos]
        out.append((gv, [(0, j + 1, S) for j, (S, d) in enumerate(cos)], f"cosingleton{len(cos)}"))
    keys = list(pool)
    for r in (2, 3, 4, 5):
        if len(keys) >= r:
            arms = [(S, pool[S]) for S in rng.sample(keys, r)]
            gv = [base] + [_bump(base, S, d) for S, d in arms]
            out.append((gv, [(0, j + 1, S) for j, (S, d) in enumerate(arms)], f"star{r}"))
    return out

def _bump(vf, S, d):
    v2 = list(vf); v2[S] += d
    return v2

def certify(base_seed_int, base, games_v, edges, tag, out, resultpath):
    exact_base = exactify(Game(n, [F(x) for x in base_seed_int]))
    if exact_base is None or not is_exact_game(exact_base):
        out("  [reject] exact base re-derivation failed"); return None
    games = [exact_base]
    for gv in games_v[1:]:
        v2 = list(exact_base.v)
        for S in range(len(gv)):
            v2[S] += round(gv[S] - base[S])
        games.append(Game(n, v2))
    if not all(is_exact_game(gm) for gm in games):
        out("  [reject] member not exact under exact arithmetic"); return None
    feas, _ = is_family_feasible(games, edges)
    if feas:
        out("  [reject] exact LP FEASIBLE (float false positive)"); return None
    cert = certify_infeasible(games, edges)
    if not cert["infeasible"]:
        out(f"  [reject] recheck feasible: {cert.get('reason')}"); return None
    fk = cert.get("farkas")
    payload = {"claim": "INFEASIBLE exact n=5 family (frontier search)", "shape": tag,
               "edges": edges, "games": [[str(u) for u in gm.v] for gm in games],
               "all_exact": [is_exact_game(gm) for gm in games],
               "all_balanced": [is_balanced_game(gm) for gm in games],
               "farkas": None if fk is None else {"rhs": str(fk["rhs"]),
                   "active_ineq": [(m, str(y)) for m, y in fk["active_ineq"]],
                   "active_eq": [(m, str(y)) for m, y in fk["active_eq"]]}}
    with open(resultpath, "w") as f:
        json.dump(payload, f, indent=1)
    out("!!! CERTIFIED INFEASIBLE EXACT n=5 FAMILY (frontier) !!!")
    out(json.dumps(payload, indent=1))
    return payload

def run(trials, seed, dmax=3, logpath=None):
    rng = random.Random(seed)
    log = open(logpath, "a") if logpath else None
    def out(s):
        print(s, flush=True)
        if log:
            log.write(s + "\n"); log.flush()
    resultpath = "../results/WITNESS_family_exact5.json"
    out(f"=== hunt_frontier5 trials={trials} seed={seed} dmax={dmax} @ {time.strftime('%H:%M:%S')} ===")
    bases = 0; fams = 0; min_slack = None; min_by_shape = {}
    degen_min = None
    t0 = time.time()
    for t in range(trials):
        seed_int = neardegen_seed(rng) if t % 2 == 0 else asym_seed(rng)
        if not is_balanced_float(n, seed_int):
            continue
        base = float_exactify(seed_int)
        if base is None or not is_exact_float(n, base):
            continue
        bases += 1
        pool = arm_pool(base, dmax)
        if len(pool) < 2:
            continue
        w = coord_widths(base)
        degen = sum(w) if w else None
        for games_v, edges, tag in shapes(base, pool, rng):
            if not all(is_exact_float(n, gv) for gv in games_v):
                continue
            fams += 1
            s = family_slack(games_v, edges)
            if s is None:
                continue
            if min_slack is None or s < min_slack:
                min_slack = s
                out(f"[newmin] slack={s:.5f} shape={tag} degen={degen} t={t}")
            if tag not in min_by_shape or s < min_by_shape[tag]:
                min_by_shape[tag] = s
            if s < 1e-6:
                out(f"[CANDIDATE] t={t} shape={tag} slack={s:.3e} -> certify")
                hit = certify(seed_int, base, games_v, edges, tag, out, resultpath)
                if hit is not None:
                    return hit
        if bases % 50 == 0:
            out(f"[progress] t={t} bases={bases} fams={fams} min_slack={min_slack:.5f} "
                f"by_shape={ {k: round(v,4) for k,v in min_by_shape.items()} } elapsed={time.time()-t0:.0f}s")
    out(f"[DONE] bases={bases} fams={fams} min_slack={min_slack} by_shape="
        f"{ {k: round(v,4) for k,v in min_by_shape.items()} } elapsed={time.time()-t0:.0f}s")
    return None

if __name__ == "__main__":
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 202
    dmax = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    logpath = sys.argv[4] if len(sys.argv) > 4 else "../results/agent_frontier5.txt"
    run(trials, seed, dmax=dmax, logpath=logpath)

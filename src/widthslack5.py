"""Width-slack data collection at n=5 (proof-lead for the existence conjecture).

For each exact base and family shape, record:
  t*            : family monotonicity slack (max-min gap; >=0 iff feasible)
  w_i           : per-player core coordinate width  max_core x_i - min_core x_i
  dw_S          : directional core width in coalition S = max_core x(S)-min_core x(S)
                  (= v(N)-v(N\\S)-v(S) exactly, on exact games)
  min_w         : min_i w_i over all players
  min_armw      : min over arms of the bumped coalition's directional width
Emits CSV rows to results/widthslack5.csv and tracks the worst-case ratios
t*/min_w and t*/min_armw (a positive infimum = uniform feasibility bound =
skeleton of an existence proof). Any t* <= 0 is a REFUTATION -> exact-certify.
"""
import random, sys, time, csv
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

def core_minmax_xS(vf, S):
    A, b = [], []
    for T in range(1, N):
        A.append([-1.0 if T >> i & 1 else 0.0 for i in range(n)]); b.append(-vf[T])
    Aeq = [[1.0] * n]; beq = [vf[N]]
    c = [1.0 if S >> i & 1 else 0.0 for i in range(n)]
    lo = linprog(c, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq, bounds=[(None, None)] * n, method="highs")
    hi = linprog([-x for x in c], A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq, bounds=[(None, None)] * n, method="highs")
    if not (lo.success and hi.success):
        return None
    return lo.fun, -hi.fun

def coord_widths(vf):
    w = []
    for i in range(n):
        mm = core_minmax_xS(vf, 1 << i)
        if mm is None:
            return None
        w.append(mm[1] - mm[0])
    return w

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

def seed_gen(rng, kind):
    if kind == "simplex":
        c = rng.randint(5, 14); vf = [0.0] * (1 << n); vf[N] = float(c)
        for _ in range(rng.randint(0, 6)):
            vf[rng.randint(1, N - 1)] = float(rng.randint(0, max(1, c // 3)))
        return vf
    if kind == "neardegen":
        a = [rng.randint(0, 4) for _ in range(n)]
        vf = [float(sum(a[i] for i in range(n) if S >> i & 1)) for S in range(1 << n)]
        for _ in range(rng.randint(1, 4)):
            T = rng.randint(1, N); w = rng.randint(1, 3)
            for S in range(1, N + 1):
                if S & T == T:
                    vf[S] += w
        return vf
    # asym / random
    c = rng.randint(6, 18); vf = [0.0] * (1 << n); vf[N] = float(c)
    for _ in range(rng.randint(2, 12)):
        vf[rng.randint(1, N - 1)] = float(rng.randint(0, c - 1))
    return vf

def dirwidth(vf, S):
    mm = core_minmax_xS(vf, S)
    return None if mm is None else mm[1] - mm[0]

def families(base, pool, rng):
    out = []
    cos = [(N ^ (1 << k), pool[N ^ (1 << k)]) for k in range(n) if (N ^ (1 << k)) in pool]
    if len(cos) >= 2:
        out.append(("cosingleton", cos))
    keys = list(pool)
    for r in (2, 3, 4, 5, min(8, len(keys))):
        if 2 <= r <= len(keys):
            out.append((f"star{r}", [(S, pool[S]) for S in rng.sample(keys, r)]))
    return out

def run(trials, seed, dmax=3, logpath=None, csvpath=None):
    rng = random.Random(seed)
    log = open(logpath, "a") if logpath else None
    csvf = open(csvpath, "a", newline="")
    cw = csv.writer(csvf)
    if csvf.tell() == 0:
        cw.writerow(["shape", "arms", "tstar", "min_w", "min_armw", "sum_w", "kind"])
    def out(s):
        print(s, flush=True)
        if log:
            log.write(s + "\n"); log.flush()
    out(f"=== widthslack5 trials={trials} seed={seed} dmax={dmax} @ {time.strftime('%H:%M:%S')} ===")
    bases = 0; rows = 0
    min_ratio_w = None; min_ratio_armw = None; t0 = time.time()
    kinds = ["simplex", "neardegen", "asym"]
    for t in range(trials):
        kind = kinds[t % 3]
        seed_int = seed_gen(rng, kind)
        if not is_balanced_float(n, seed_int):
            continue
        base = float_exactify(seed_int)
        if base is None or not is_exact_float(n, base):
            continue
        pool = arm_pool(base, dmax)
        if len(pool) < 2:
            continue
        w = coord_widths(base)
        if w is None:
            continue
        bases += 1
        min_w = min(w)
        # precompute directional widths for pooled coalitions
        dw = {S: dirwidth(base, S) for S in pool}
        for shape, arms in families(base, pool, rng):
            gv = [base]
            for S, d in arms:
                v2 = list(base); v2[S] += d; gv.append(v2)
            edges = [(0, j + 1, S) for j, (S, d) in enumerate(arms)]
            ts = family_slack(gv, edges)
            if ts is None:
                continue
            min_armw = min(dw[S] for S, d in arms if dw[S] is not None)
            cw.writerow([shape, len(arms), f"{ts:.6f}", f"{min_w:.6f}", f"{min_armw:.6f}", f"{sum(w):.6f}", kind])
            rows += 1
            if min_w > 1e-9:
                rw = ts / min_w
                if min_ratio_w is None or rw < min_ratio_w:
                    min_ratio_w = rw
                    out(f"[minratio_w] t*/min_w={rw:.5f} t*={ts:.4f} min_w={min_w:.4f} shape={shape} kind={kind}")
            if min_armw > 1e-9:
                ra = ts / min_armw
                if min_ratio_armw is None or ra < min_ratio_armw:
                    min_ratio_armw = ra
                    out(f"[minratio_armw] t*/min_armw={ra:.5f} t*={ts:.4f} min_armw={min_armw:.4f} shape={shape} kind={kind}")
            if ts < 1e-7:
                out(f"[CANDIDATE] REFUTATION? t*={ts:.3e} shape={shape} kind={kind} -> exact certify")
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
                if cert["infeasible"]:
                    import json
                    fk = cert.get("farkas")
                    payload = {"claim": "INFEASIBLE exact n=5 family (widthslack)", "shape": shape,
                               "edges": edges, "games": [[str(u) for u in g.v] for g in games],
                               "farkas": None if fk is None else {"rhs": str(fk["rhs"])}}
                    with open("../results/WITNESS_family_exact5.json", "w") as f:
                        json.dump(payload, f, indent=1)
                    out("!!! CERTIFIED INFEASIBLE EXACT n=5 FAMILY !!!")
                    out(json.dumps(payload, indent=1))
                    csvf.flush()
                    return payload
        csvf.flush()
        if bases % 40 == 0:
            out(f"[progress] t={t} bases={bases} rows={rows} min_ratio_w={min_ratio_w} "
                f"min_ratio_armw={min_ratio_armw} elapsed={time.time()-t0:.0f}s")
    out(f"[DONE] bases={bases} rows={rows} min_ratio_w={min_ratio_w} min_ratio_armw={min_ratio_armw} "
        f"elapsed={time.time()-t0:.0f}s")
    csvf.close()
    return None

if __name__ == "__main__":
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 404
    dmax = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    logpath = sys.argv[4] if len(sys.argv) > 4 else "../results/agent_widthslack5.txt"
    csvpath = sys.argv[5] if len(sys.argv) > 5 else "../results/widthslack5.csv"
    run(trials, seed, dmax=dmax, logpath=logpath, csvpath=csvpath)

"""n=5 exact-game family-feasibility hunt (coalitional-monotonicity crown jewel).

TARGET: refute (or gather evidence for) the conjecture that a coalitionally
monotonic single-valued core selection exists on exact n=5 games. By the
compactness reduction this is EVERY finite bump family of exact games being
feasible. A refutation = one INFEASIBLE family of exact 5-player games (all
members exact, family LP over core+monotonicity infeasible, exact Farkas cert).

DISCIPLINE: exactify is ~20s per game at n=5 (exact simplex), so the census runs
in FLOAT (scipy HiGHS): float-exactify bases, precompute the pool of single
bumps that keep exactness, float-screen family feasibility. Every float-
infeasible family is CERTIFIED with the exact stack (exactify / is_exact_game /
is_family_feasible / Farkas), re-solved under row shuffling. Feasible families
contribute slack t* = max over the family polytope of the minimum monotonicity
gap (t* >= 0 iff feasible; small t* = near-infeasible).

Shapes:
  cosingleton : base + bump each N\\{k}  (m=n=5 arms; the shape whose core
                intersection the reviewer broke at n=4 -- prime suspect).
  star_r      : base + r proper-coalition bumps (r=2,3,4).
  diamond     : base -> two arms -> joint top (depth-2).

Bases: random-exactified (superadditive seeds) AND structured simplex-type /
near-degenerate bases, on which co-singleton bumps preserve exactness.
"""
import random, sys, json, time
from scipy.optimize import linprog
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from hunt_monotonic import rand_game
from floatscreen import is_balanced_float, is_exact_float, _core_min_xS_float
from hunt_sd import exactify, is_exact_game
from family_infeasible import is_family_feasible, certify_infeasible

n = 5
N5 = (1 << n) - 1

# ---------- bases ----------
def float_exactify(vf):
    """Float exact-cover v_e(S)=min core x(S). Returns list[float] or None."""
    v2 = [0.0] * (1 << n)
    v2[N5] = vf[N5]
    for S in range(1, N5):
        m = _core_min_xS_float(n, vf, S)
        if m is None:
            return None
        v2[S] = m
    return v2

def random_exact_base(rng):
    g = rand_game(n, rng, "general")
    vf = [float(x) for x in g.v]
    if not is_balanced_float(n, vf):
        return None, None
    b = float_exactify(vf)
    if b is None or not is_exact_float(n, b):
        return None, None
    return b, g.v  # float base, exact-integer seed

def simplex_base(rng):
    """Structured near-simplex exact base: v(N)=c, a few proper coalitions given
    small slack values, then exact-covered. Co-singleton bumps tend to survive."""
    c = rng.randint(5, 12)
    vf = [0.0] * (1 << n)
    vf[N5] = float(c)
    # raise a handful of proper coalitions to small values below their simplex cap
    ncoal = rng.randint(0, 6)
    for _ in range(ncoal):
        S = rng.randint(1, N5 - 1)
        vf[S] = float(rng.randint(0, max(1, c // 3)))
    b = float_exactify(vf)
    if b is None or not is_exact_float(n, b):
        return None, None
    # seed for exact re-derivation = the integer pre-exactify game
    seed = [F(round(x)) for x in vf]
    return b, seed

# ---------- arm pool ----------
def bump_vf(vf, S, d):
    v2 = list(vf); v2[S] += d
    return v2

def exact_arm_pool(base_vf, dmax):
    """S -> largest d in 1..dmax keeping the single-bumped base float-exact."""
    pool = {}
    for S in range(1, N5):
        best = None
        for d in range(1, dmax + 1):
            if is_exact_float(n, bump_vf(base_vf, S, d)):
                best = d
            else:
                break  # exactness fails monotonically in d for a single coalition
        if best:
            pool[S] = best
    return pool

# ---------- families (built from a precomputed pool) ----------
def cosingleton_family(base_vf, pool):
    arms = [(N5 ^ (1 << k), pool[N5 ^ (1 << k)]) for k in range(n)
            if (N5 ^ (1 << k)) in pool]
    if len(arms) < 2:
        return None
    games_v = [base_vf] + [bump_vf(base_vf, S, d) for S, d in arms]
    edges = [(0, j + 1, S) for j, (S, d) in enumerate(arms)]
    return games_v, edges, {"shape": "cosingleton", "arms": [(f"{S:05b}", d) for S, d in arms]}

def star_family(base_vf, r, pool, rng):
    keys = [S for S in pool]
    if len(keys) < r:
        return None
    arms = [(S, pool[S]) for S in rng.sample(keys, r)]
    games_v = [base_vf] + [bump_vf(base_vf, S, d) for S, d in arms]
    edges = [(0, j + 1, S) for j, (S, d) in enumerate(arms)]
    return games_v, edges, {"shape": f"star{r}", "arms": [(f"{S:05b}", d) for S, d in arms]}

def diamond_family(base_vf, pool, rng):
    keys = [S for S in pool]
    if len(keys) < 2:
        return None
    (S1, S2) = rng.sample(keys, 2)
    d1, d2 = pool[S1], pool[S2]
    t1 = bump_vf(base_vf, S1, d1)
    t2 = bump_vf(base_vf, S2, d2)
    top = bump_vf(bump_vf(base_vf, S1, d1), S2, d2)
    if not is_exact_float(n, top):
        return None
    games_v = [base_vf, t1, t2, top]
    edges = [(0, 1, S1), (0, 2, S2), (1, 3, S2), (2, 3, S1)]
    return games_v, edges, {"shape": "diamond", "arms": [(f"{S1:05b}", d1), (f"{S2:05b}", d2)]}

# ---------- feasibility / slack ----------
def family_slack_float(games_v, edges):
    """t* = max over family polytope of the min monotonicity gap. t*>=0 iff feasible."""
    m = len(games_v); nv = n * m + 1; ti = n * m
    A, b, Aeq, beq = [], [], [], []
    for k in range(m):
        row = [0.0] * nv
        for i in range(n):
            row[k * n + i] = 1.0
        Aeq.append(row); beq.append(games_v[k][N5])
    for k in range(m):
        for T in range(1, N5):
            row = [0.0] * nv
            for i in range(n):
                if T >> i & 1:
                    row[k * n + i] = -1.0
            A.append(row); b.append(-games_v[k][T])
    for (k, l, S) in edges:
        for i in range(n):
            if S >> i & 1:
                row = [0.0] * nv
                row[k * n + i] = 1.0
                row[l * n + i] = -1.0
                row[ti] = 1.0
                A.append(row); b.append(0.0)
    c = [0.0] * nv; c[ti] = -1.0
    r = linprog(c, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq,
                bounds=[(None, None)] * nv, method="highs")
    if not r.success:
        return None
    return -r.fun

# ---------- exact certification of a hit ----------
def exact_certify(base_seed, base_vf, games_v, edges, desc, out, resultpath):
    exact_base = exactify(Game(n, [F(x) for x in base_seed]))
    if exact_base is None or not is_exact_game(exact_base):
        out("  [reject] exact re-exactify of base failed"); return None
    games = [exact_base]
    for gv in games_v[1:]:
        v2 = list(exact_base.v)
        for S in range(len(gv)):
            v2[S] += round(gv[S] - base_vf[S])
        games.append(Game(n, v2))
    if not all(is_exact_game(gm) for gm in games):
        out("  [reject] a member not exact under exact arithmetic"); return None
    feas, _ = is_family_feasible(games, edges)
    if feas:
        out("  [reject] exact LP FEASIBLE (float false positive)"); return None
    cert = certify_infeasible(games, edges)
    if not cert["infeasible"]:
        out(f"  [reject] recheck feasible: {cert.get('reason')}"); return None
    fk = cert.get("farkas")
    payload = {
        "claim": "INFEASIBLE family of EXACT n=5 games -> NO coalitionally monotonic core selection on exact 5-player games.",
        "n": n, "shape": desc, "edges": edges,
        "games": [[str(u) for u in gm.v] for gm in games],
        "all_exact": [is_exact_game(gm) for gm in games],
        "all_balanced": [is_balanced_game(gm) for gm in games],
        "farkas": None if fk is None else {
            "rhs": str(fk["rhs"]),
            "active_ineq": [(mt, str(y)) for mt, y in fk["active_ineq"]],
            "active_eq": [(mt, str(y)) for mt, y in fk["active_eq"]],
        },
    }
    with open(resultpath, "w") as f:
        json.dump(payload, f, indent=1)
    out("!!! CERTIFIED INFEASIBLE EXACT n=5 FAMILY !!!")
    out(json.dumps(payload, indent=1))
    return payload

# ---------- driver ----------
def run(trials, seed, dmax=3, mix="both", logpath=None, resultpath=None):
    rng = random.Random(seed)
    log = open(logpath, "a") if logpath else None
    def out(s):
        print(s, flush=True)
        if log:
            log.write(s + "\n"); log.flush()
    resultpath = resultpath or "../results/WITNESS_family_exact5.json"
    out(f"=== hunt_family5 trials={trials} seed={seed} dmax={dmax} mix={mix} @ {time.strftime('%H:%M:%S')} ===")
    bases = 0; fams = 0; near = 0
    min_slack = None; cosingleton_bases = 0
    slack_hist = {}  # rounded slack -> count
    t_start = time.time()
    for t in range(trials):
        if mix == "simplex" or (mix == "both" and t % 2 == 0):
            base_vf, base_seed = simplex_base(rng)
        else:
            base_vf, base_seed = random_exact_base(rng)
        if base_vf is None:
            continue
        bases += 1
        pool = exact_arm_pool(base_vf, dmax)
        if len(pool) < 2:
            continue
        cosingleton_arms = sum(1 for k in range(n) if (N5 ^ (1 << k)) in pool)
        if cosingleton_arms >= 2:
            cosingleton_bases += 1
        builders = [cosingleton_family(base_vf, pool),
                    star_family(base_vf, 2, pool, rng),
                    star_family(base_vf, 3, pool, rng),
                    star_family(base_vf, 4, pool, rng),
                    diamond_family(base_vf, pool, rng)]
        for fam in builders:
            if fam is None:
                continue
            games_v, edges, desc = fam
            if not all(is_exact_float(n, gv) for gv in games_v):
                continue
            fams += 1
            slack = family_slack_float(games_v, edges)
            if slack is None:
                continue
            key = round(slack, 1)
            slack_hist[key] = slack_hist.get(key, 0) + 1
            if min_slack is None or slack < min_slack:
                min_slack = slack
            if slack < 1e-6:
                near += 1
                out(f"[CANDIDATE] trial={t} shape={desc['shape']} slack={slack:.3e} arms={desc['arms']}")
                hit = exact_certify(base_seed, base_vf, games_v, edges, desc, out, resultpath)
                if hit is not None:
                    return hit
        if bases % 25 == 0:
            out(f"[progress] t={t} bases={bases} (cosing>=2:{cosingleton_bases}) fams={fams} "
                f"min_slack={min_slack:.4f} near0={near} elapsed={time.time()-t_start:.0f}s")
    out(f"[DONE] trials={trials} bases={bases} (cosing>=2:{cosingleton_bases}) fams={fams} "
        f"min_slack={min_slack} near0={near} elapsed={time.time()-t_start:.0f}s")
    out(f"[SLACK HIST] {dict(sorted(slack_hist.items()))}")
    out("NO infeasible exact family found." if near == 0 else f"{near} near-zero candidates (see above).")
    return None

if __name__ == "__main__":
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    dmax = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    mix = sys.argv[4] if len(sys.argv) > 4 else "both"
    logpath = sys.argv[5] if len(sys.argv) > 5 else "../results/agent_fam5.txt"
    run(trials, seed, dmax=dmax, mix=mix, logpath=logpath)

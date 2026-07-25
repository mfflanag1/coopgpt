"""Search for INFEASIBLE families (=> no coalitionally monotonic core selection).

Structure exploited: a single bump v'(S)=v(S)+d shrinks the core
(core(v') = core(v) cap {x(S)>=v'(S)} subset core(v)). Hence any family with a
single maximal ("top") game is feasible (use a top core point everywhere). So we
search STAR / multi-top DAG families: a base game b plus several one-coalition
bumps t_1..t_r (distinct coalitions), edges (b,t_j,A_j). More tension: also
"double stars" (two bases sharing tops) and general small DAGs.

cls in {balanced, supbal, totbal, exact}: EVERY member game must lie in cls,
verified exactly, or the family is discarded.
"""
import random, sys, json
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from hunt_monotonic import rand_game
from hunt_sd import exactify, is_exact_game, is_totally_balanced, in_class
from family_infeasible import is_family_feasible, certify_infeasible, verify_witness

def member_ok(g, cls):
    return in_class(g, cls)

def bump(g, S, d):
    v2 = list(g.v); v2[S] += d
    return Game(g.n, v2)

def star_families(base, cls, rng, dmax=3, max_arms=4):
    """Yield (games, edges, desc) for star families rooted at exact/base game."""
    n, N = base.n, base.N
    coals = list(range(1, N))
    rng.shuffle(coals)
    # arms: coalition S with a bump depth d that keeps membership in cls
    arms = []
    for S in coals:
        for d in range(1, dmax+1):
            t = bump(base, S, d)
            if member_ok(t, cls):
                arms.append((S, d, t))
                break
    if len(arms) < 2:
        return
    # try subsets of arms of size 2..max_arms as tops of a star
    from itertools import combinations
    for r in range(2, min(max_arms, len(arms)) + 1):
        for combo in combinations(range(len(arms)), r):
            games = [base]
            edges = []
            desc_arms = []
            for j, ai in enumerate(combo):
                S, d, t = arms[ai]
                games.append(t)
                edges.append((0, j+1, S))
                desc_arms.append((S, d))
            yield games, edges, {"shape": "star", "arms": desc_arms}

def hunt(cls, n, trials, seed, dmax=3, logpath=None):
    rng = random.Random(seed)
    log = open(logpath, "a") if logpath else None
    def out(s):
        print(s, flush=True)
        if log: log.write(s+"\n"); log.flush()
    out(f"=== hunt cls={cls} n={n} trials={trials} seed={seed} dmax={dmax} ===")
    checked = 0
    bases = 0
    for t in range(trials):
        g = rand_game(n, rng, "general")
        if not is_balanced_game(g):
            continue
        if cls == "exact":
            base = exactify(g)
            if base is None or not is_exact_game(base):
                continue
        else:
            base = g
            if not member_ok(base, cls):
                continue
        bases += 1
        for games, edges, desc in star_families(base, cls, rng, dmax):
            checked += 1
            feas, x = is_family_feasible(games, edges)
            if feas:
                continue
            # INFEASIBLE candidate — re-verify every member in class, then certify
            if not all(member_ok(gm, cls) for gm in games):
                out(f"[skip] infeasible but a member left class {cls}")
                continue
            out(f"[INFEASIBLE] trial={t} cls={cls} shape={desc}")
            cert = certify_infeasible(games, edges)
            if not cert["infeasible"]:
                out(f"  RECHECK SAYS FEASIBLE: {cert}")
                continue
            payload = {
                "cls": cls, "n": n, "shape": desc,
                "games": [[str(u) for u in gm.v] for gm in games],
                "edges": edges,
                "farkas": None if cert.get("farkas") is None else {
                    "rhs": str(cert["farkas"]["rhs"]),
                    "active_ineq": [(m, str(y)) for m, y in cert["farkas"]["active_ineq"]],
                    "active_eq": [(m, str(y)) for m, y in cert["farkas"]["active_eq"]],
                },
                "exact_members": [is_exact_game(gm) for gm in games],
            }
            out("CERTIFIED INFEASIBLE FAMILY:")
            out(json.dumps(payload, indent=1))
            return payload
    out(f"no infeasible family: cls={cls} n={n}, bases={bases}, families_checked={checked}")
    return None

if __name__ == "__main__":
    cls = sys.argv[1]; n = int(sys.argv[2]); trials = int(sys.argv[3])
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    logpath = sys.argv[5] if len(sys.argv) > 5 else None
    hunt(cls, n, trials, seed, logpath=logpath)

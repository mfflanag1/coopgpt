"""TEST THE SELECTION: is the leximin-above-floors core selection phi coalitionally
monotonic on EXACT games?

For each exact game v and each proper coalition S, bump v(S)->v(S)+d keeping the
game exact; compute phi(v), phi(v'); coalitional monotonicity requires
phi_i(v') >= phi_i(v) for every i in S. A single i in S that strictly DROPS is a
violation (kills the candidate). Float screen -> exact certification of any
violation.

Base games: point-generator (thin cores, the frontier), plus near-degenerate /
asym / random-exactified.
"""
import random, sys, json, time
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from floatscreen import is_exact_float, is_balanced_float, _core_min_xS_float
from hunt_sd import is_exact_game, exactify
from hunt_exact_points import rand_point_sum, game_from_points
from hunt_monotonic import rand_game
from leximin import leximin_core_float, leximin_core_exact

def float_exactify(n, vf):
    N = (1 << n) - 1
    v2 = [0.0] * (1 << n); v2[N] = vf[N]
    for S in range(1, N):
        m = _core_min_xS_float(n, vf, S)
        if m is None:
            return None
        v2[S] = m
    return v2

def gen_base(n, rng, kind):
    """Return an exact game's float v-list (and an exact-integer seed for re-derivation)."""
    N = (1 << n) - 1
    if kind == "points":
        k = rng.randint(2, 4); c = rng.randint(n, 6 * n)
        pts = [rand_point_sum(n, c, rng) for _ in range(k)]
        g = game_from_points(n, pts)          # exact by construction, integer
        vf = [float(x) for x in g.v]
        return vf, [int(x) for x in g.v]
    if kind == "neardegen":
        a = [rng.randint(0, 4) for _ in range(n)]
        vf = [float(sum(a[i] for i in range(n) if S >> i & 1)) for S in range(1 << n)]
        for _ in range(rng.randint(1, 4)):
            T = rng.randint(1, N); w = rng.randint(1, 3)
            for S in range(1, N + 1):
                if S & T == T:
                    vf[S] += w
        if not is_balanced_float(n, vf):
            return None, None
        b = float_exactify(n, vf)
        return (b, [round(x) for x in vf]) if b and is_exact_float(n, b) else (None, None)
    # asym / random-exactify
    g = rand_game(n, rng, "general"); vf = [float(x) for x in g.v]
    if not is_balanced_float(n, vf):
        return None, None
    b = float_exactify(n, vf)
    return (b, [int(x) for x in g.v]) if b and is_exact_float(n, b) else (None, None)

def certify_violation(n, base_seed, base_vf, S, d, drops, out, resultpath, kind):
    """Re-derive exactly and confirm the phi coalitional-monotonicity violation."""
    if kind == "points":
        gv = base_seed                      # already exact integers = the game itself
    else:
        eb = exactify(Game(n, [F(x) for x in base_seed]))
        if eb is None or not is_exact_game(eb):
            out("  [reject] exact base re-derivation failed"); return None
        gv = [int(x) for x in eb.v] if False else list(eb.v)
    g = Game(n, [F(x) for x in gv])
    if not is_exact_game(g):
        out("  [reject] base not exact (exact check)"); return None
    v2 = list(g.v); v2[S] += d
    g2 = Game(n, v2)
    if not is_exact_game(g2):
        out("  [reject] bumped game not exact (exact check)"); return None
    x = leximin_core_exact(g); y = leximin_core_exact(g2)
    if x is None or y is None:
        out("  [reject] exact phi failed"); return None
    ed = [(i, x[i] - y[i]) for i in range(n) if S >> i & 1 and x[i] > y[i]]
    if not ed:
        out("  [reject] exact phi shows no drop (float false positive)"); return None
    if not (g.in_core(x) and g2.in_core(y)):
        out("  [reject] phi not in core (bug)"); return None
    payload = {
        "claim": "leximin-above-floors core selection phi is NOT coalitionally monotonic on EXACT games",
        "n": n, "kind": kind, "v": [str(u) for u in g.v], "bumped_S": S, "delta": d,
        "S_members": [i for i in range(n) if S >> i & 1],
        "phi_v": [str(u) for u in x], "phi_vbump": [str(u) for u in y],
        "drops": [(i, str(dd)) for i, dd in ed],
        "both_exact": True, "both_balanced": [is_balanced_game(g), is_balanced_game(g2)],
        "phi_v_in_core": True, "phi_vbump_in_core": True,
    }
    with open(resultpath, "w") as f:
        json.dump(payload, f, indent=1)
    out("*** CERTIFIED: phi NOT coalitionally monotonic on exact games ***")
    out(json.dumps(payload, indent=1))
    return payload

def run(n, target_bumps, seed, logpath=None, resultpath=None):
    rng = random.Random(seed)
    log = open(logpath, "a") if logpath else None
    def out(s):
        print(s, flush=True)
        if log:
            log.write(s + "\n"); log.flush()
    resultpath = resultpath or f"../results/WITNESS_leximin_notmono_n{n}.json"
    out(f"=== hunt_leximin n={n} target_bumps={target_bumps} seed={seed} @ {time.strftime('%H:%M:%S')} ===")
    N = (1 << n) - 1
    kinds = ["points", "points", "neardegen", "asym"]   # weight point-generated
    bumps_tested = 0; bases = 0; viols = 0; t0 = time.time()
    ki = 0
    while bumps_tested < target_bumps:
        kind = kinds[ki % len(kinds)]; ki += 1
        base_vf, base_seed = gen_base(n, rng, kind)
        if base_vf is None:
            continue
        xv = leximin_core_float(n, base_vf)
        if xv is None:
            continue
        bases += 1
        # try several coalitions with an exact-preserving bump
        coals = rng.sample(range(1, N), min(8, N - 1))
        for S in coals:
            # largest exact-preserving d up to 4
            d = None
            for dd in range(1, 5):
                v2 = list(base_vf); v2[S] += dd
                if is_exact_float(n, v2):
                    d = dd
                else:
                    break
            if d is None:
                continue
            v2 = list(base_vf); v2[S] += d
            yv = leximin_core_float(n, v2)
            if yv is None:
                continue
            bumps_tested += 1
            drops = [(i, xv[i] - yv[i]) for i in range(n) if S >> i & 1 and xv[i] - yv[i] > 1e-6]
            if drops:
                viols += 1
                out(f"[cand] kind={kind} S={S:0{n}b} d={d} float-drops={[(i,round(dd,4)) for i,dd in drops]}")
                hit = certify_violation(n, base_seed, base_vf, S, d, drops, out, resultpath, kind)
                if hit is not None:
                    out(f"[STOP] certified violation after {bumps_tested} bumps")
                    return hit
        if bases % 50 == 0:
            out(f"[progress] bases={bases} bumps={bumps_tested} float_viol={viols} elapsed={time.time()-t0:.0f}s")
    out(f"[DONE] n={n} bases={bases} bumps_tested={bumps_tested} float_violations={viols} "
        f"elapsed={time.time()-t0:.0f}s")
    out("CLEAN: no coalitional-monotonicity violation of phi found." if viols == 0
        else f"{viols} float candidates (all certified-rejected as false positives, else stopped above).")
    return None

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    target = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    logpath = sys.argv[4] if len(sys.argv) > 4 else f"../results/agent_leximin_n{n}.txt"
    run(n, target, seed, logpath=logpath)

"""ADVERSARIAL stress of the leximin-above-floors selection phi on exact games.
Thinnest cores (k=2 point-generated games), EXHAUSTIVE over all proper
coalitions per base, larger bump depths, singleton bumps included. n in {5,6}.
Any float drop of an S-member is exact-certified (kills the candidate theorem).
"""
import random, sys, json, time
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from floatscreen import is_exact_float
from hunt_sd import is_exact_game
from hunt_exact_points import rand_point_sum, game_from_points
from leximin import leximin_core_float, leximin_core_exact

def run(n, target_bumps, seed, kpts=2, dmax=6, logpath=None):
    rng = random.Random(seed)
    N = (1 << n) - 1
    log = open(logpath, "a") if logpath else None
    def out(s):
        print(s, flush=True)
        if log:
            log.write(s + "\n"); log.flush()
    resultpath = f"../results/WITNESS_leximin_notmono_n{n}.json"
    out(f"=== hunt_leximin_adv n={n} target={target_bumps} seed={seed} kpts={kpts} dmax={dmax} @ {time.strftime('%H:%M:%S')} ===")
    bases = 0; bumps = 0; viols = 0; t0 = time.time()
    while bumps < target_bumps:
        c = rng.randint(n, 8 * n)
        pts = [rand_point_sum(n, c, rng) for _ in range(kpts)]
        g = game_from_points(n, pts)               # exact, thin core
        base_vf = [float(x) for x in g.v]
        xv = leximin_core_float(n, base_vf)
        if xv is None:
            continue
        bases += 1
        for S in range(1, N):                       # EXHAUSTIVE over proper coalitions
            d = None
            for dd in range(1, dmax + 1):
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
            bumps += 1
            drops = [(i, xv[i] - yv[i]) for i in range(n) if S >> i & 1 and xv[i] - yv[i] > 1e-6]
            if drops:
                viols += 1
                out(f"[cand] S={S:0{n}b} d={d} drops={[(i,round(dd,4)) for i,dd in drops]}")
                # exact certify
                gv = [int(x) for x in g.v]
                ge = Game(n, [F(x) for x in gv])
                if not is_exact_game(ge):
                    out("  [reject] base not exact"); continue
                v2e = list(ge.v); v2e[S] += d
                g2 = Game(n, v2e)
                if not is_exact_game(g2):
                    out("  [reject] bump not exact"); continue
                xe = leximin_core_exact(ge); ye = leximin_core_exact(g2)
                if xe is None or ye is None:
                    out("  [reject] exact phi failed"); continue
                ed = [(i, xe[i] - ye[i]) for i in range(n) if S >> i & 1 and xe[i] > ye[i]]
                if not ed:
                    out("  [reject] exact shows no drop (float false positive)"); continue
                payload = {"claim": "leximin NOT coalitionally monotonic on exact games (adversarial)",
                           "n": n, "v": [str(u) for u in ge.v], "bumped_S": S, "delta": d,
                           "S_members": [i for i in range(n) if S >> i & 1],
                           "phi_v": [str(u) for u in xe], "phi_vbump": [str(u) for u in ye],
                           "drops": [(i, str(dd)) for i, dd in ed],
                           "in_core": [ge.in_core(xe), g2.in_core(ye)]}
                with open(resultpath, "w") as f:
                    json.dump(payload, f, indent=1)
                out("*** CERTIFIED: leximin NOT coalitionally monotonic on exact games ***")
                out(json.dumps(payload, indent=1))
                return payload
        if bases % 40 == 0:
            out(f"[progress] bases={bases} bumps={bumps} viol={viols} elapsed={time.time()-t0:.0f}s")
    out(f"[DONE] n={n} kpts={kpts} bases={bases} bumps={bumps} float_viol={viols} elapsed={time.time()-t0:.0f}s")
    out("CLEAN (adversarial): phi coalitionally monotonic." if viols == 0 else f"{viols} candidates (see above).")
    return None

if __name__ == "__main__":
    n = int(sys.argv[1]); target = int(sys.argv[2]); seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    kpts = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    logpath = sys.argv[5] if len(sys.argv) > 5 else f"../results/agent_leximin_adv_n{n}.txt"
    run(n, target, seed, kpts=kpts, logpath=logpath)

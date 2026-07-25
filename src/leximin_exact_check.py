"""Fully EXACT leximin coalitional-monotonicity check (no float screening).
Point-generated exact games (thin cores), exact phi on both sides, exact-rational
comparison. Confirms the candidate theorem without any float tolerance.
"""
import random, sys, time
from fractions import Fraction as F
from tugame import Game
from hunt_sd import is_exact_game
from hunt_exact_points import rand_point_sum, game_from_points
from leximin import leximin_core_exact

def run(n, target_bumps, seed, kpts=2, dmax=4):
    rng = random.Random(seed)
    N = (1 << n) - 1
    bumps = 0; bases = 0; viol = 0; t0 = time.time()
    while bumps < target_bumps:
        c = rng.randint(n, 6 * n)
        pts = [rand_point_sum(n, c, rng) for _ in range(kpts)]
        g = game_from_points(n, pts)
        if not is_exact_game(g):
            continue
        x = leximin_core_exact(g)
        if x is None or not g.in_core(x):
            continue
        bases += 1
        for S in range(1, N):
            # largest exact-preserving d (EXACT check)
            d = None
            for dd in range(1, dmax + 1):
                v2 = list(g.v); v2[S] += dd
                if is_exact_game(Game(n, v2)):
                    d = dd
                else:
                    break
            if d is None:
                continue
            g2 = Game(n, [F(u) for u in g.v]); v2 = list(g2.v); v2[S] += d; g2 = Game(n, v2)
            y = leximin_core_exact(g2)
            if y is None or not g2.in_core(y):
                continue
            bumps += 1
            drops = [(i, x[i] - y[i]) for i in range(n) if S >> i & 1 and x[i] > y[i]]
            if drops:
                viol += 1
                print(f"*** EXACT VIOLATION n={n} S={S:0{n}b} d={d} drops={[(i,str(dd)) for i,dd in drops]}", flush=True)
                print(f"    v={[str(u) for u in g.v]}", flush=True)
                print(f"    phi_v={[str(u) for u in x]} phi_v'={[str(u) for u in y]}", flush=True)
                return
        if bumps and bases % 30 == 0:
            print(f"[progress] bases={bases} exact_bumps={bumps} viol={viol} elapsed={time.time()-t0:.0f}s", flush=True)
    print(f"[DONE-EXACT] n={n} kpts={kpts} bases={bases} exact_bumps={bumps} EXACT_violations={viol} elapsed={time.time()-t0:.0f}s", flush=True)
    print("CLEAN (fully exact): phi coalitionally monotonic." if viol == 0 else f"{viol} EXACT violations!", flush=True)

if __name__ == "__main__":
    n = int(sys.argv[1]); target = int(sys.argv[2]); seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    kpts = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    run(n, target, seed, kpts=kpts)

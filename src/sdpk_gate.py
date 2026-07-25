"""Validation gate: the Arin-Katsev theorem says the SD-prenucleolus is ALWAYS
in the SD-prekernel. So at x* = certified_sd_prenucleolus(g), every pair must
equalize exactly. Run on random balanced games BEFORE hunting."""
import random, sys
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from sd import certified_sd_prenucleolus
from hunt_monotonic import rand_game
from sdpk import imbalances, is_efficient

def run(n=4, want=10, seed=0):
    rng = random.Random(seed)
    passed = 0
    tried = 0
    t = 0
    while passed < want and t < 5000:
        t += 1
        g = rand_game(n, rng, "general")
        if not is_balanced_game(g):
            continue
        x = certified_sd_prenucleolus(g)
        if x is None:
            continue
        tried += 1
        if not is_efficient(g, x):
            print(f"[gate] game#{t}: SD point NOT efficient", flush=True)
            return False
        imb = imbalances(g, x)
        maxres = max(abs(d) for d in imb.values())
        if maxres != 0:
            print(f"[gate] FAIL game#{t}: max|s_ij-s_ji| = {maxres} at SD point", flush=True)
            print(f"  v = {[int(x) if x.denominator==1 else x for x in g.v]}", flush=True)
            print(f"  x = {x}", flush=True)
            bad = {k:v for k,v in imb.items() if v!=0}
            print(f"  nonzero residuals: {bad}", flush=True)
            return False
        passed += 1
        print(f"[gate] game#{t} n={n}: SD point equalizes all pairs  (passed {passed}/{want})", flush=True)
    print(f"[gate] {'PASS' if passed>=want else 'INCONCLUSIVE'}: {passed}/{want} balanced games, all equalize at SD point", flush=True)
    return passed >= want

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    ok = run(n=n, want=10, seed=1)
    sys.exit(0 if ok else 1)

import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import (tight_coalitions, core_max_xS, binding_bumpable, star_holds,
                  residual_cover, xS)

def members(S,n): return [i for i in range(n) if S>>i&1]
n=int(sys.argv[1]); seed=int(sys.argv[2]); trials=int(sys.argv[3])
rng=random.Random(seed); N=(1<<n)-1
cases=0; starfail=0; t0=time.time()
for t in range(trials):
    k=rng.randint(2,3); c=rng.randint(n,5*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(k)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        if not binding_bumpable(g,phi,S): continue
        cases+=1
        h,val,y=star_holds(g,phi,S)
        if not h:
            starfail+=1
            print("*** STAR FAILS on exact game! ***", [str(u) for u in g.v], "S",members(S,n))
    if time.time()-t0>90: 
        print(f"[timecap] t={t}"); break
print(f"n={n} seed={seed}: cases={cases} starfail={starfail} elapsed={time.time()-t0:.0f}s")

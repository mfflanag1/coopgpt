import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, exact_bumpable, core_max_xS, xS
def members(S,n): return [i for i in range(n) if S>>i&1]
n=int(sys.argv[1]); seed=int(sys.argv[2]); trials=int(sys.argv[3]); cap=int(sys.argv[4])
rng=random.Random(seed); N=(1<<n)-1
tab={}; mism=0; t0=time.time()
for t in range(trials):
    k=rng.randint(2,3); c=rng.randint(n,5*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(k)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        if core_max_xS(g,S)<=xS(phi,S,n): continue
        h,val,y=star_holds(g,phi,S)
        b=exact_bumpable(g,S)
        tab[(bool(h),b)]=tab.get((bool(h),b),0)+1
        if b and not h:
            mism+=1
            print("*** d>0 but star FAILS ***",[str(u) for u in g.v],members(S,n),flush=True)
    if time.time()-t0>cap: print("[timecap] t=",t,flush=True); break
print(f"n={n} seed={seed} (star,bumpable)->count:",tab,"| bumpable-but-starfail:",mism,flush=True)

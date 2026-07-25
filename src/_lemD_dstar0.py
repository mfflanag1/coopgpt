import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, max_exact_bump, core_max_xS, xS
def members(S,n): return [i for i in range(n) if S>>i&1]
n=int(sys.argv[1]); seed=int(sys.argv[2]); cap=int(sys.argv[3])
rng=random.Random(seed*104729); N=(1<<n)-1
t0=time.time(); sf=0; dstar0=0; dstar_le_slack=0; bad=[]
while time.time()-t0<cap:
    k=rng.randint(2,4); c=rng.randint(n,7*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(k)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        pS=xS(phi,S,n)
        if core_max_xS(g,S)<=pS: continue
        h,_,_=star_holds(g,phi,S)
        if h: continue
        sf+=1
        d=max_exact_bump(g,S); slack=pS-g.v[S]
        if d==0: dstar0+=1
        if d<=slack: dstar_le_slack+=1
        else:
            bad.append(([str(u) for u in g.v],members(S,n),str(d),str(slack)))
            print("*** star-fail but d*>slack (Lemma D counterex) ***",[str(u) for u in g.v],members(S,n),"d*",str(d),"slack",str(slack),flush=True)
print(f"n={n} seed={seed}: starfails={sf} d*==0:{dstar0} d*<=slack:{dstar_le_slack} VIOL:{len(bad)} t={time.time()-t0:.0f}s",flush=True)

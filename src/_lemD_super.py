import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, core_max_xS, xS, residual_cover, tight_coalitions
def members(S,n): return [i for i in range(n) if S>>i&1]
n=int(sys.argv[1]); seed=int(sys.argv[2]); cap=int(sys.argv[3])
rng=random.Random(seed*6113); N=(1<<n)-1; t0=time.time()
sf=0; superOK=0; superEQ=0; Wtight=0; NmSinW=0; bad=[]
while time.time()-t0<cap:
    kk=rng.randint(2,3); c=rng.randint(n,5*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(kk)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        pS=xS(phi,S,n)
        if core_max_xS(g,S)<=pS: continue
        h,_,_=star_holds(g,phi,S)
        if h: continue
        sf+=1
        rc=residual_cover(g,phi,S)
        W=0
        for U in rc['lambda']: W|=U
        Tstar=W&S
        # checks
        offSinW = (N ^ S) & (~W) == 0    # N\S subset W ?
        SW=S|W; SiW=S&W
        delta = g.v[S]+g.v[W]-g.v[SW]-g.v[SiW]   # supermodular gap (>=0 means supermod)
        if offSinW: NmSinW+=1
        if delta>=0: superOK+=1
        if delta==0: superEQ+=1
        # also need S|W==N and S&W==Tstar
        ok_union = (SW==N)
        if not(delta>=0 and offSinW and ok_union):
            bad.append((delta, offSinW, ok_union))
            if len(bad)<=6:
                print("BAD:",[str(u) for u in g.v],"S",members(S,n),"W",members(W,n),
                      "delta",str(delta),"offSinW",offSinW,"S|W==N",ok_union,flush=True)
print(f"n={n} seed={seed}: sf={sf} superOK(delta>=0):{superOK} superEQ(delta==0):{superEQ} "
      f"NmS_subset_W:{NmSinW} BADcount:{len(bad)} t={time.time()-t0:.0f}s",flush=True)

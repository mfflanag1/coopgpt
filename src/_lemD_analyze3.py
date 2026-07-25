import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from lemD import (star_holds, core_max_xS, xS, residual_cover, tight_coalitions,
                  max_exact_bump, exact_lp_min, core_min_xT)
from hunt_exact_points import rand_point_sum, game_from_points
def members(S,n): return [i for i in range(n) if S>>i&1]
n=int(sys.argv[1]); seed=int(sys.argv[2])
rng=random.Random(seed); N=(1<<n)-1; t0=time.time(); nfound=0
while time.time()-t0<600 and nfound<8:
    kk=rng.randint(2,4); c=rng.randint(n,7*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(kk)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    for S in range(1,N):
        if bin(S).count("1")<3: continue
        if core_max_xS(g,S)<=xS(phi,S,n): continue
        h,_,_=star_holds(g,phi,S)
        if h: continue
        rc=residual_cover(g,phi,S)
        if not rc['lambda']: continue
        sig=rc['mu']; r=rc['r']
        Tstar=[k for k in members(S,n) if r[k]<sig]
        rT=set(r[k] for k in Tstar)
        if len(rT)<2: continue     # only care about NON-constant-on-T* (r>=3 valued on S)
        nfound+=1
        Wm=0
        for U in rc['lambda']: Wm|=U
        Tmask=Wm & S; P=N & ~S
        vW=g.v[Wm]; rhs=xS(phi,P,n)+g.v[Tmask]
        d=max_exact_bump(g,S); slack=xS(phi,S,n)-g.v[S]
        print(f"[{nfound}] n={n} S={members(S,n)} r={ {k:str(v) for k,v in r.items()} } sig={sig}")
        print(f"    r on T*={Tstar} = {sorted(str(x) for x in rT)} (NON-constant)")
        print(f"    v(W)={vW} phi(P)+v(T*)={rhs}  CERT v(W)>=phi(P)+v(T*)? {vW>=rhs}")
        print(f"    d*={d} slack={slack}  LEMMA D? {d<=slack}", flush=True)
print(f"done n={n} seed={seed} found={nfound}")

import random, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, core_max_xS, xS, residual_cover, max_exact_bump
def members(S,n): return [i for i in range(n) if S>>i&1]
n=6; N=(1<<n)-1; found=0
for seed in range(1,60):
    if found>=3: break
    rng=random.Random(seed*777)
    t0=time.time()
    while time.time()-t0<9 and found<3:
        kk=rng.randint(2,3); c=rng.randint(n,5*n)
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
            if len(set(r[k] for k in Tstar))<2: continue
            found+=1
            Wm=0
            for U in rc['lambda']: Wm|=U
            Tmask=Wm&S; P=N&~S
            cert=g.v[Wm]>=xS(phi,P,n)+g.v[Tmask]
            slackT=xS(phi,Tmask,n)-g.v[Tmask]
            vals=sorted(set(r[k] for k in Tstar),reverse=True); rhos=vals+[F(0)]; lhs=F(0)
            for l in range(len(vals)):
                Dl=0
                for k in Tstar:
                    if r[k]>=vals[l]: Dl|=1<<k
                lhs+=(rhos[l]-rhos[l+1])*(xS(phi,Dl,n)-g.v[Dl])
            d=max_exact_bump(g,S); slack=xS(phi,S,n)-g.v[S]
            print(f"NC case: S={members(S,n)} r={ {k:str(v) for k,v in r.items()} } sig={sig}")
            print(f"  T*={members(Tmask,n)} rOnT*={sorted(str(r[k]) for k in Tstar)}")
            print(f"  CERT v(W)={g.v[Wm]}>=phi(P)+v(T*)={xS(phi,P,n)+g.v[Tmask]}? {cert}")
            print(f"  GOAL3 lhs={lhs} <= sig*slackT={sig*slackT}? {lhs<=sig*slackT}")
            print(f"  d*={d} slack={slack} LEMMA_D={d<=slack}",flush=True)
print("found",found)

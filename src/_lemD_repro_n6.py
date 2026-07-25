import random, time, sys
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from lemD import (star_holds, core_max_xS, xS, residual_cover, tight_coalitions,
                  max_exact_bump, exact_lp_min)
from hunt_exact_points import rand_point_sum, game_from_points
def members(S,n): return [i for i in range(n) if S>>i&1]
n=6; rng=random.Random(3*211); N=(1<<n)-1; t0=time.time(); found=0
while time.time()-t0<115 and found<4:
    kk=rng.randint(2,3); c=rng.randint(n,6*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(kk)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        if core_max_xS(g,S)<=xS(phi,S,n): continue
        h,_,_=star_holds(g,phi,S)
        if h: continue
        rc=residual_cover(g,phi,S)
        if not rc['lambda']: continue
        sig=rc['mu']; r=rc['r']
        Tstar=[k for k in members(S,n) if r[k]<sig]
        if len(set(r[k] for k in Tstar))<2: continue   # constant on T* -> skip
        found+=1
        Wm=0
        for U in rc['lambda']: Wm|=U
        Tmask=Wm&S; P=N&~S
        vW=g.v[Wm]; rhs=xS(phi,P,n)+g.v[Tmask]
        d=max_exact_bump(g,S); slack=xS(phi,S,n)-g.v[S]
        print("=== NON-CONSTANT-T* CASE ===")
        print("v",[str(u) for u in g.v]); print("S",members(S,n),"phi",[str(p) for p in phi])
        print("r",{k:str(v) for k,v in r.items()},"sig",str(sig),"| r on T*",members(0 if False else Tmask,n),"=",sorted(str(r[k]) for k in Tstar))
        print("W",members(Wm,n),"T*",members(Tmask,n),"P",members(P,n))
        print("CERT v(W)=%s >= phi(P)+v(T*)=%s ? %s"%(str(vW),str(rhs),vW>=rhs))
        print("d*=%s slack=%s LEMMA D? %s"%(str(d),str(slack),d<=slack))
        # also: does ANY 2-valued-on-S cover exist? try objectives
        Sm=members(S,n); tights=tight_coalitions(g,phi); r2=0; seen=set()
        m=len(tights)
        def cov(obj):
            nv=m+1+len(Sm); ri={k:m+1+t for t,k in enumerate(Sm)}
            A_eq,b_eq=[],[]
            for i in range(n):
                row=[0]*nv
                for t,T in enumerate(tights):
                    if T>>i&1: row[t]=-1
                row[m]=1
                if S>>i&1: row[ri[i]]=-1
                A_eq.append(row); b_eq.append(0)
            A_ub,b_ub=[],[]
            for t in range(m):
                row=[0]*nv; row[t]=-1; A_ub.append(row); b_ub.append(0)
            for k in Sm:
                row=[0]*nv; row[ri[k]]=-1; A_ub.append(row); b_ub.append(-1)
            c2=[0]*nv
            for k in Sm: c2[ri[k]]=-obj.get(k,0)
            opt,sol=exact_lp_min(c2,A_ub,b_ub,A_eq,b_eq)
            return None if opt is None or opt=='unbounded' else {k:sol[ri[k]] for k in Sm}
        rng2=random.Random(7)
        for _ in range(150):
            rr=cov({k:rng2.randint(-6,6) for k in Sm})
            if rr is None: continue
            key=tuple(sorted(rr.items()))
            if key in seen: continue
            seen.add(key)
            # 2-valued means r constant on {r<sig}
            TT=[k for k in Sm if rr[k]<max(rr.values())]
            if len(set(rr[k] for k in TT))<=1: r2+=1
        print("distinct covers:%d  covers-with-constant-T*:%d"%(len(seen),r2), flush=True)
print("found",found)

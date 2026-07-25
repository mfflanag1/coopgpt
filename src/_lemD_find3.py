import random, time, itertools
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from lemD import (star_holds, core_max_xS, xS, residual_cover, tight_coalitions,
                  max_exact_bump, exact_lp_min)
from hunt_exact_points import rand_point_sum, game_from_points
def members(S,n): return [i for i in range(n) if S>>i&1]
def cover(g,phi,S,tights,Sm,obj):
    n=g.n; m=len(tights); nv=m+1+len(Sm); ri={k:m+1+t for t,k in enumerate(Sm)}
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
    c=[0]*nv
    for k in Sm: c[ri[k]]=-obj.get(k,0)
    opt,sol=exact_lp_min(c,A_ub,b_ub,A_eq,b_eq)
    if opt is None or opt=='unbounded': return None
    return {k:sol[ri[k]] for k in Sm}
rng=random.Random(12345); n=5; N=31; t0=time.time(); found=0
while time.time()-t0<110 and found<3:
    kk=rng.randint(2,3); c=rng.randint(n,6*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(kk)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    for S in range(1,N):
        if bin(S).count("1")<3: continue
        if core_max_xS(g,S)<=xS(phi,S,n): continue
        h,_,_=star_holds(g,phi,S)
        if h: continue
        rc=residual_cover(g,phi,S)
        if not rc['lambda'] or len(set(rc['r'].values()))<3: continue
        # FOUND a 3-valued residual
        found+=1
        Sm=members(S,n); tights=tight_coalitions(g,phi)
        print("=== 3-VALUED CASE ===")
        print("v",[str(u) for u in g.v]); print("S",Sm,"phi",[str(p) for p in phi])
        print("residual r:",{k:str(v) for k,v in rc['r'].items()},"sig",str(rc['mu']))
        d=max_exact_bump(g,S); slack=xS(phi,S,n)-g.v[S]
        print("d*",str(d),"slack",str(slack),"LEMMA D holds (d<=slack)?",d<=slack)
        # search for a 2-valued cover
        r2=[]; rng2=random.Random(7); seen=set()
        for _ in range(300):
            obj={k:rng2.randint(-8,8) for k in Sm}
            r=cover(g,phi,S,tights,Sm,obj)
            if r is None: continue
            key=tuple(sorted(r.items()))
            if key in seen: continue
            seen.add(key)
            if len(set(r.values()))<=2: r2.append(r)
        print(f"distinct covers:{len(seen)} 2-valued covers found:{len(r2)}")
        for r in r2[:4]: print("   2val:",{k:str(v) for k,v in r.items()})
        if found>=3: break
    if found>=3: break
print("done, found",found)

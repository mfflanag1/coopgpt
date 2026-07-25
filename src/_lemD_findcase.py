import random, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from lemD import (star_holds, core_max_xS, xS, residual_cover, tight_coalitions,
                  max_exact_bump, exact_lp_min)
def members(S,n): return [i for i in range(n) if S>>i&1]
from hunt_exact_points import rand_point_sum, game_from_points
# reproduce n5 seed5 case with S={0,2,3,4}, r 3-valued
rng=random.Random(5*211); N=31; n=5
target=None; t0=time.time()
while time.time()-t0<95 and not target:
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
        if len(set(rc['r'].values()))>=3:
            target=(g,phi,S,rc); break
    if target: break
if not target:
    print("not found"); exit()
g,phi,S,rc=target
print("v",[str(u) for u in g.v]); print("phi",[str(p) for p in phi],"S",members(S,n))
print("v(S)",str(g.v[S]),"phi(S)",str(xS(phi,S,n)),"max_core x(S)",str(core_max_xS(g,S)))
print("residual r (3-valued):",{k:str(v) for k,v in rc['r'].items()},"sigma",str(rc['mu']))
print("d*(S)",str(max_exact_bump(g,S)),"slack",str(xS(phi,S,n)-g.v[S]))
# Search for a 2-VALUED cover: minimize number of distinct values is nonlinear;
# instead try many objectives and record all distinct r, check if any 2-valued.
tights=tight_coalitions(g,phi); Sm=members(S,n)
def cover(obj):
    m=len(tights); nv=m+1+len(Sm); ri={k:m+1+t for t,k in enumerate(Sm)}
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
rng2=random.Random(1); seen=set(); twoval=[]
for _ in range(200):
    obj={k:rng2.randint(-6,6) for k in Sm}
    r=cover(obj)
    if r is None: continue
    key=tuple(sorted(r.items()))
    if key in seen: continue
    seen.add(key)
    if len(set(r.values()))<=2: twoval.append(r)
print(f"distinct covers found: {len(seen)}; 2-valued among them: {len(twoval)}")
for r in twoval[:5]: print("  2-valued cover:",{k:str(v) for k,v in r.items()})

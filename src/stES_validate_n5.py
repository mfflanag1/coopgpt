"""ACID TEST of the segment-core completeness theorem: run the reenum4 arrangement
(coalition + floor + endpoint-coordinate + pairwise segment-support planes) + the
conservative-margin screen on the CANONICAL n=5 witness, which has a 1-D (segment)
core and is KNOWN NON-STABLE (escape (0,1,1,2,0)). If the theorem/architecture are
correct, this MUST find an undominated escape. If it finds NONE, the completeness is
FALSE and cand1/cand2's surv=0 does NOT certify stability."""
import sys, itertools
import numpy as np
from fractions import Fraction as F
from scipy.optimize import linprog
sys.path.insert(0,'/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members, exact_lp_min
from core_stability import certify_undominated
from largeness_exact import exact_solve

MARG=1e-4
V=[0,0,0,0,0,1,1,1,1,1,1,1,2,2,2,2,0,1,1,2,0,1,1,2,2,3,3,3,2,3,3,4]  # canonical n=5
n=5; g=Game(n,[F(x) for x in V]); N=g.N; vf=[float(x) for x in g.v]; lo=[vf[1<<i] for i in range(n)]

# segment endpoints
def core_opt(c,s):
    A=[[-1 if T>>i&1 else 0 for i in range(n)] for T in range(1,N)]; b=[-g.v[T] for T in range(1,N)]
    _,x=exact_lp_min([s*ci for ci in c],A,b,[[1]*n],[g.v[N]]); return x
A=core_opt([1,3,7,13,23],1); B=core_opt([1,3,7,13,23],-1)
print("segment endpoints A=",[str(x) for x in A]," B=",[str(x) for x in B])

planes=[]
for S in range(1,N): planes.append(([F(1) if S>>i&1 else F(0) for i in range(n)], F(g.v[S]), ('S',S)))
for i in range(n):
    r=[F(0)]*n; r[i]=F(1); planes.append((r, F(g.v[1<<i]), ('x',i)))
seen=set((i,g.v[1<<i]) for i in range(n))
for v in (A,B):
    for i in range(n):
        if (i,v[i]) in seen: continue
        seen.add((i,v[i])); r=[F(0)]*n; r[i]=F(1); planes.append((r,v[i],('v',i)))
for i in range(n):
    for j in range(i+1,n):
        di=B[i]-A[i]; dj=B[j]-A[j]
        if di==0 and dj==0: continue
        r=[F(0)]*n; r[i]=dj; r[j]=-di; planes.append((r, dj*A[i]-di*A[j], ('p',i,j)))
m=len(planes); print("arrangement m=",m,"pairs=",sum(1 for p in planes if p[2][0]=='p'))
frows=[[float(a) for a in p[0]] for p in planes]; frhs=[float(p[1]) for p in planes]
eff=[1.0]*n; effr=vf[N]
core_A=[[-1.0 if T>>i&1 else 0.0 for i in range(n)] for T in range(1,N)]; core_b=[-vf[T] for T in range(1,N)]
def dom_margin(yf,S):
    Aa=[r+[0.0] for r in core_A]; bb=list(core_b)
    Aa.append([1.0 if S>>i&1 else 0.0 for i in range(n)]+[0.0]); bb.append(vf[S])
    for i in range(n):
        if S>>i&1:
            rr=[0.0]*(n+1); rr[i]=-1.0; rr[n]=1.0; Aa.append(rr); bb.append(-yf[i])
    r=linprog([0.0]*n+[-1.0],A_ub=Aa,b_ub=bb,A_eq=[[1.0]*n+[0.0]],b_eq=[vf[N]],bounds=[(None,None)]*(n+1),method="highs")
    return (-r.fun, r.x[:n]) if r.success else (None,None)
def exact_dom_ok(yx,S,xf):
    for D in (1,2,3,4,6,12,24,60,120,360):
        xr=[F(a).limit_denominator(D) for a in xf]
        if sum(xr)!=g.v[N]: continue
        if any(sum(xr[i] for i in range(n) if T>>i&1)<g.v[T] for T in range(1,N)): continue
        if sum(xr[i] for i in range(n) if S>>i&1)!=g.v[S]: continue
        if all(xr[i]>yx[i] for i in range(n) if S>>i&1): return True
    return False
escapes=0; surv=0; outside=0
for combo in itertools.combinations(range(m),n-1):
    Mx=np.array([frows[j] for j in combo]+[eff]); bb=np.array([frhs[j] for j in combo]+[effr])
    try:
        if abs(np.linalg.det(Mx))<1e-9: continue
        yf=np.linalg.solve(Mx,bb)
    except np.linalg.LinAlgError: continue
    ok=abs(sum(yf)-vf[N])<1e-6 and all(yf[i]>=lo[i]-1e-7 for i in range(n))
    blk=[S for S in range(1,N) if sum(yf[i] for i in range(n) if S>>i&1)<vf[S]-1e-7] if ok else []
    if ok and blk:
        outside+=1
        Me=[list(planes[j][0]) for j in combo]+[[F(1)]*n]; be=[planes[j][1] for j in combo]+[g.v[N]]
        yx=exact_solve([r[:] for r in Me],be,n)
        if yx is None: continue
        dominated=False
        for S in blk:
            t,xs=dom_margin(list(yf),S)
            if t is not None and t>MARG and exact_dom_ok(yx,S,xs): dominated=True; break
        if not dominated:
            surv+=1
            if certify_undominated(g,yx):
                escapes+=1
                print("ESCAPE FOUND:",[str(a) for a in yx],"tags=",[planes[j][2] for j in combo])
                if escapes>=3: break
print(f"RESULT: outside={outside} survivors={surv} escapes={escapes}")
print("VALIDATION", "PASSED (found escape on segment-core non-stable game)" if escapes>0 else "*** FAILED *** completeness THEOREM IS WRONG")

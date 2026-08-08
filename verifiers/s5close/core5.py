"""Task #27 (a): UNSAT CORES for the five impossible two-stratum configurations.

Each is impossible, so the hypothesis set is contradictory with NO failure
hypothesis.  Tracking every assertion and asking z3 for an unsat core names the
handful of facts that actually collide -- the skeleton of a hand proof.

Encoding: the A3 anchors + core memberships + exactness (Theorem A) + the
Farkas leximin/leximax identities, as in closecfg3, but with each assertion
tracked so a minimal core can be extracted and then minimized greedily.
"""
import json, sys, itertools
from fractions import Fraction as F
import z3
sys.path.insert(0,'.'); sys.path.insert(0,'lib')
from closecfg import q, layout, reps

N, FULL = 5, 31
PROPER=list(range(1,FULL)); SZ=[bin(S).count("1") for S in range(32)]
NM=lambda S:"".join("abcde"[i] for i in range(N) if S>>i&1) or "0"

CASES=[((3,2),(1,1,1,2),[[1,1,1,0],[0,0,0,2]]),
       ((3,2),(1,1,3),  [[1,1,1],[0,0,2]]),
       ((4,1),(1,1,1,2),[[1,1,1,1],[0,0,0,1]]),
       ((4,1),(1,1,3),  [[1,1,2],[0,0,1]]),
       ((4,1),(1,2,2),  [[1,2,1],[0,0,1]])]

def prog(r,c,tbl):
    A,B=len(r),len(c); cell,P,D1=layout(r,c,tbl)
    m=[z3.Real(f"m{k}") for k in range(A)]; Mv=[z3.Real(f"M{l}") for l in range(B)]
    v=[z3.Real(f"v{S}") for S in range(32)]
    x=[m[cell[i][0]] for i in range(N)]; z=[Mv[cell[i][1]] for i in range(N)]
    mu,Mx=m[0],Mv[B-1]
    s=z3.Solver(); s.set(unsat_core=True); T={}
    def add(name,e):
        p=z3.Bool(name); T[name]=e; s.assert_and_track(e,p)
    add("levels", z3.And(m[0]>=0, Mv[0]>=0,
        z3.Sum([q(r[k])*m[k] for k in range(A)])==1,
        z3.Sum([q(c[l])*Mv[l] for l in range(B)])==1,
        *[m[k]<m[k+1] for k in range(A-1)], *[Mv[l]<Mv[l+1] for l in range(B-1)]))
    add("norm", z3.And(v[0]==0, v[FULL]==1, *[v[1<<i]==0 for i in range(N)]))
    xS=lambda S: z3.Sum([x[i] for i in range(N) if S>>i&1])
    zS=lambda S: z3.Sum([z[i] for i in range(N) if S>>i&1])
    for S in PROPER:
        add(f"xcore_{NM(S)}", v[S]<=xS(S))
        add(f"zcore_{NM(S)}", v[S]<=zS(S))
        add(f"vpos_{NM(S)}", v[S]>=0)
    add("anchor_ceiling", z3.Or([v[S0]==q(SZ[S0])*Mx
        for S0 in reps(D1,cell,lambda cl:cl[0],lo=2)]))
    add("anchor_floor", z3.Or([1-v[FULL^Ss]==q(SZ[Ss])*mu
        for Ss in reps(P,cell,lambda cl:cl[1],lo=1)]))
    add("A3_nu", z3.And(*[v[S]<=q(SZ[S])*Mx for S in PROPER]))
    add("A3_lambda", z3.And(*[1-v[FULL^S]>=q(SZ[S])*mu for S in PROPER]))
    # protectors, level form
    for i in range(N):
        for j in range(N):
            subs=[S for S in PROPER if (S>>j&1) and not (S>>i&1)]
            if cell[i][0]<cell[j][0]:
                add(f"protF_{i}{j}", z3.Or([z3.And(xS(S)==v[S], xS(S)<=zS(S)) for S in subs]))
            if cell[i][1]<cell[j][1]:
                add(f"protC_{i}{j}", z3.Or([z3.And(zS(S)==v[S], zS(S)<=xS(S)) for S in subs]))
    return s,T

for r,c,tbl in CASES:
    s,T=prog(r,c,tbl)
    res=s.check()
    if res!=z3.unsat:
        print(f"lmin={r} lmax={c} tbl={tbl}: {res} (NOT excluded by this set)"); continue
    core=[str(x) for x in s.unsat_core()]
    # greedy minimization
    changed=True
    while changed:
        changed=False
        for nm in list(core):
            trial=[n for n in core if n!=nm]
            s2=z3.Solver(); [s2.add(T[n]) for n in trial]
            if s2.check()==z3.unsat:
                core=trial; changed=True; break
    print(f"lmin={r} lmax={c} tbl={tbl}: UNSAT, minimal core {len(core)}: {sorted(core)}")

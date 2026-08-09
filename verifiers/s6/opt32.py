"""Task #32 Phase 1: can the n=6 encoding be made to terminate?

The 120s 'unknown's come from the Boolean structure.  In the n=5 encoding the
support condition "y_A = 0 or phi(A) = v(A)" is re-decided inside EVERY Farkas
bundle -- 62 disjunctions per (stage,player), 6 players x 2 sides = 744
independent Boolean choices, all of them really asking the same question: which
coalitions are tight?

Fix: hoist tightness into ONE Boolean per coalition per side (62 x 2 = 124),
shared by every bundle:
      tx[A]  <->  x(A) = v(A)        (and the same for z)
      y_A > 0  =>  tx[A]
This is logically equivalent -- tightness is a property of (v, phi), not of the
bundle -- but it collapses the search space enormously.
"""
import sys, time
from fractions import Fraction as F
import z3
sys.path.insert(0,'.')
import nsix
N=6; FULL=(1<<N)-1; PROPER=list(range(1,FULL)); R=F(2,3)

def pipeline2_shared(n,r,c,tbl,Rt,fail=True):
    cell=nsix.layout(n,r,c,tbl); A,B=len(r),len(c)
    s=z3.Solver(); m,Mv=nsix.levels(n,r,c,s)
    x=[m[cell[i][0]] for i in range(n)]; z=[Mv[cell[i][1]] for i in range(n)]
    v=[z3.Real(f"v{S}") for S in range(1<<n)]
    s.add(v[0]==0, v[FULL]==1)
    for i in range(n): s.add(v[1<<i]==0)
    xS=lambda S: z3.Sum([x[i] for i in range(n) if S>>i&1])
    zS=lambda S: z3.Sum([z[i] for i in range(n) if S>>i&1])
    for S in PROPER: s.add(v[S]<=xS(S)); s.add(v[S]<=zS(S))
    for S in PROPER:
        w=[z3.Real(f"w{S}_{i}") for i in range(n)]
        s.add(z3.Sum(w)==1)
        for Aa in PROPER: s.add(z3.Sum([w[i] for i in range(n) if Aa>>i&1])>=v[Aa])
        s.add(z3.Sum([w[i] for i in range(n) if S>>i&1])==v[S])
    # SHARED tightness markers
    tx={S:z3.Bool(f"tx{S}") for S in PROPER}; tz={S:z3.Bool(f"tz{S}") for S in PROPER}
    for S in PROPER:
        s.add(tx[S]==(xS(S)==v[S])); s.add(tz[S]==(zS(S)==v[S]))
    rowmask=[[i for i in range(n) if cell[i][0]==k] for k in range(A)]
    colmask=[[i for i in range(n) if cell[i][1]==l] for l in range(B)]
    def farkas(phi,blocks,ceiling,tag,tt):
        sgn=1 if ceiling else -1; rhs=-1 if ceiling else 1; pinned=[]
        for t,Bt in enumerate(blocks):
            for i in Bt:
                y={Aa:z3.Real(f"{tag}y{t}_{i}_{Aa}") for Aa in PROPER}
                eta=z3.Real(f"{tag}e{t}_{i}")
                rho={l:z3.Real(f"{tag}r{t}_{i}_{l}") for l in pinned}
                sig={cc:z3.Real(f"{tag}s{t}_{i}_{cc}") for cc in Bt}
                for Aa in PROPER:
                    s.add(y[Aa]>=0); s.add(z3.Implies(y[Aa]>0, tt[Aa]))
                for cc in Bt: s.add(sig[cc]>=0)
                for j in range(n):
                    e=-z3.Sum([y[Aa] for Aa in PROPER if Aa>>j&1])+eta
                    if j in pinned: e=e+rho[j]
                    if j in Bt: e=e+sgn*sig[j]
                    s.add(e==z3.RealVal(rhs if j==i else 0))
            pinned=pinned+list(Bt)
    farkas(x,rowmask,False,"F",tx); farkas(z,colmask[::-1],True,"C",tz)
    ratio=z3.Sum([nsix.q(tbl[k][l])*z3.Abs(m[k]-Mv[l])
                  for k in range(A) for l in range(B) if tbl[k][l]])
    s.add(ratio>nsix.q(Rt) if fail else ratio<=nsix.q(Rt))
    return s

CASES=[((1,3,1,1),(1,1,1,1,2)),((1,4,1),(1,1,1,1,2)),
       ((1,2,1,1,1),(1,1,1,3)),((2,1,3),(1,1,2,2))]
print("re-timing the hard cases with SHARED tightness markers (600s cap):")
for r,c in CASES:
    tbl=nsix.tables(r,c)[0]
    for name,fn in (("orig", lambda: nsix.pipeline2(N,r,c,tbl,R)[0]),
                    ("shared", lambda: pipeline2_shared(N,r,c,tbl,R))):
        s=fn(); s.set("timeout",600000)
        t0=time.time(); out=s.check(); dt=time.time()-t0
        print(f"   lmin={r} lmax={c} [{name:6s}] -> {out} in {dt:.1f}s", flush=True)

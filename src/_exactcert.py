"""Exact end-to-end certification of a d*>0 star-fail case. Prints incrementally.
Usage: python3 -u _exactcert.py '<json {"v":[...],"S":[...]}>'
Certifies: game exact; phi=leximin; star_S fails; a single-stratum subset-of-S cert C
with M^(C)<=phi(S) (=> d*<=slack exactly); and d*(S) via max_exact_bump (sharpness)."""
import sys, json, time
from fractions import Fraction as F
from tugame import Game, exact_lp_min
from leximin import leximin_core_exact
from lemD import (core_min_xT, star_holds, core_max_xS, xS, residual_cover,
                  tight_coalitions, max_exact_bump)
def members(S,n): return [i for i in range(n) if S>>i&1]
def P(*a): print(*a,flush=True);
d=json.loads(sys.argv[1]); vg=[F(x) for x in d['v']]; Sl=d['S']
import math; n=int(round(math.log2(len(vg)))); N=(1<<n)-1
S=0
for i in Sl: S|=1<<i
g=Game(n,vg); t0=time.time()
P(f"# n={n} S={Sl}")
# exactness (spot: all coalitions)
bad=[T for T in range(1,N) if core_min_xT(g,T)!=g.v[T]]
P(f"exact: {len(bad)==0} (nonexact={len(bad)})  [{time.time()-t0:.0f}s]")
phi=leximin_core_exact(g)
P(f"phi={[str(x) for x in phi]} in_core={g.in_core(phi)}  [{time.time()-t0:.0f}s]")
pS=xS(phi,S,n); slack=pS-g.v[S]
P(f"phi(S)={pS} v(S)={g.v[S]} slack={slack} maxcore x(S)={core_max_xS(g,S)}")
h,val,_=star_holds(g,phi,S); P(f"star_S holds={h} (fail={not h})")
gains=[phi[i]-g.v[1<<i] for i in range(n)]; lv=sorted(set(gains)); strat={i:lv.index(gains[i]) for i in range(n)}
P(f"gains={[str(x) for x in gains]} strata={strat}")
rc=residual_cover(g,phi,S); sig=rc['mu']; r=rc['r']
cdep={k:sig-r[k] for k in members(S,n)}
P(f"cover sigma={sig} r={ {k:str(r[k]) for k in r} } coverage c_k={ {k:str(cdep[k]) for k in cdep} }")
def Mc(C):
    A=[[-1 if U>>i&1 else 0 for i in range(n)] for U in range(1,N)]; b=[-g.v[U] for U in range(1,N)]
    Aeq=[[1]*n,[1 if C>>i&1 else 0 for i in range(n)]]; beq=[g.v[N],g.v[C]]
    opt,_=exact_lp_min([-1 if S>>i&1 else 0 for i in range(n)],A,b,Aeq,beq)
    return None if opt is None or opt=='unbounded' else -opt
# min-residual (=max coverage) members
cmax=max(cdep.values()); maxc=[k for k in members(S,n) if cdep[k]==cmax]
P(f"max-coverage members (selector) = {maxc}")
cert=None
for k in maxc:
    M=Mc(1<<k)
    P(f"  M^({{{k}}})={M}  <=phi(S)? {M<=pS}  (stratum {strat[k]})")
    if M is not None and M<=pS and cert is None: cert=(1<<k,M)
if cert is None:  # try same-stratum pairs within S
    Sm=members(S,n)
    for a in range(len(Sm)):
        for b2 in range(a+1,len(Sm)):
            if strat[Sm[a]]!=strat[Sm[b2]]: continue
            C=(1<<Sm[a])|(1<<Sm[b2]); M=Mc(C)
            if M is not None and M<=pS: cert=(C,M); P(f"  PAIR cert C={members(C,n)} M={M}<=phi(S)"); break
        if cert: break
if cert:
    P(f"==> CERT C={members(cert[0],n)} M^(C)={cert[1]} <= phi(S)={pS}  => d*<=slack EXACT (d*<= {cert[1]-g.v[S]})")
P(f"computing exact d* (max_exact_bump)...  [{time.time()-t0:.0f}s]")
dstar=max_exact_bump(g,S)
P(f"*** EXACT d*(S)={dstar}  slack={slack}  d*<=slack={dstar<=slack}  d*>0={dstar>0} ***  [{time.time()-t0:.0f}s]")

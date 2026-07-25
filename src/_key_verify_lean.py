import sys
from fractions import Fraction as F
from tugame import Game, exact_lp_min
from leximin import leximin_core_exact
from lemD import (star_holds, core_max_xS, xS, residual_cover, tight_coalitions,
                  max_exact_bump)
def members(S,n): return [i for i in range(n) if S>>i&1]
def P(*a): print(*a,flush=True)

VS=["0","5","1","9","3","8","9","14","3","11","4","12","12","19","13","21","3","8","6","14","6","11","12","17","8","16","9","17","17","22","18","26","1","6","4","12","4","9","10","15","6","14","7","15","15","20","16","24","4","9","9","15","7","12","13","18","11","19","12","20","18","23","21","29"]
n=6; N=(1<<n)-1
g=Game(n,[F(x) for x in VS])
phi=leximin_core_exact(g)
P("phi=",[str(x) for x in phi],"in_core=",g.in_core(phi))

def Mc(S,C):
    A_ub=[[-1 if U>>i&1 else 0 for i in range(n)] for U in range(1,N)]
    b_ub=[-g.v[U] for U in range(1,N)]
    A_eq=[[1]*n,[1 if C>>i&1 else 0 for i in range(n)]]; b_eq=[g.v[N],g.v[C]]
    c=[-1 if S>>i&1 else 0 for i in range(n)]
    opt,_=exact_lp_min(c,A_ub,b_ub,A_eq,b_eq)
    return None if opt is None or opt=='unbounded' else -opt

for S in [0b011101, 0b101101]:
    P(f"\n===== S={members(S,n)} =====")
    pS=xS(phi,S,n); slack=pS-g.v[S]
    P("  phi(S)=",str(pS)," v(S)=",str(g.v[S])," slack=",str(slack)," maxcore x(S)=",str(core_max_xS(g,S)))
    h,val,_=star_holds(g,phi,S); P("  star holds?",h)
    rc=residual_cover(g,phi,S); sig=rc['mu']; r=rc['r']; lam=rc['lambda']
    tights=set(tight_coalitions(g,phi))
    P("  cover valid: tights",all(U in tights for U in lam),"lam>=0",all(l>=0 for l in lam.values()),
      "r>=1",all(r[k]>=1 for k in members(S,n)))
    W=0
    for U in lam: W|=U
    Tstar=W&S; Pset=N&~S
    P("  cover=",{tuple(members(U,n)):str(lam[U]) for U in lam}," sig=",str(sig)," r=",{k:str(r[k]) for k in r})
    P("  W=",members(W,n)," T*=",members(Tstar,n)," P=",members(Pset,n))
    P(f"  KEY margin = v(W)-phi(P)-v(T*) = {g.v[W]}-{xS(phi,Pset,n)}-{g.v[Tstar]} = {g.v[W]-xS(phi,Pset,n)-g.v[Tstar]}")
    P("  M^(T*)=",str(Mc(S,Tstar))," phi(S)=",str(pS)," M<=phi(S)?",Mc(S,Tstar)<=pS)
    d=max_exact_bump(g,S)
    P(f"  *** DECISIVE d*(S)={d}  slack={slack}  d*>slack (LEMMA D REFUTED)? {d>slack} ***")

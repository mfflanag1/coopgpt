import sys
from fractions import Fraction as F
from tugame import Game, exact_lp_min
from leximin import leximin_core_exact
from lemD import core_min_xT, star_holds, core_max_xS, xS, residual_cover, max_exact_bump
def members(S,n): return [i for i in range(n) if S>>i&1]
def P(*a): print(*a,flush=True)
VS=["0","5","1","9","3","8","9","14","3","11","4","12","12","19","13","21","3","8","6","14","6","11","12","17","8","16","9","17","17","22","18","26","1","6","4","12","4","9","10","15","6","14","7","15","15","20","16","24","4","9","9","15","7","12","13","18","11","19","12","20","18","23","21","29"]
n=6; N=(1<<n)-1
g=Game(n,[F(x) for x in VS])
# EXACTNESS: min_core x(T)==v(T) for all proper T
bad=[T for T in range(1,N) if core_min_xT(g,T)!=g.v[T]]
P("EXACT (min_core x(T)=v(T) all T):", len(bad)==0, "num_nonexact=",len(bad))
phi=leximin_core_exact(g)
P("phi=",[str(x) for x in phi])
# independent M-witness: core point x with x(T*)=v(T*) and x(S)>phi(S)?
def maxS_given(S,C):
    A_ub=[[-1 if U>>i&1 else 0 for i in range(n)] for U in range(1,N)]
    b_ub=[-g.v[U] for U in range(1,N)]
    A_eq=[[1]*n,[1 if C>>i&1 else 0 for i in range(n)]]; b_eq=[g.v[N],g.v[C]]
    c=[-1 if S>>i&1 else 0 for i in range(n)]
    opt,x=exact_lp_min(c,A_ub,b_ub,A_eq,b_eq)
    return (None,None) if opt is None or opt=='unbounded' else (-opt,x)
for S in [0b011101, 0b101101]:
    P(f"\n== S={members(S,n)} ==")
    rc=residual_cover(g,phi,S); lam=rc['lambda']
    W=0
    for U in lam: W|=U
    Tstar=W&S; Pset=N&~S
    pS=xS(phi,S,n); slack=pS-g.v[S]
    P("  W=",members(W,n),"T*=",members(Tstar,n),"P=",members(Pset,n))
    P("  KEY margin=",str(g.v[W]-xS(phi,Pset,n)-g.v[Tstar]))
    MT,xw=maxS_given(S,Tstar)
    P("  M^(T*)=",str(MT),"phi(S)=",str(pS),"witness x(S)>phi(S):",MT>pS,"x=",[str(z) for z in xw] if xw else None)
    if xw: P("    x in core:",g.in_core(xw)," x(T*)=",str(xS(xw,Tstar,n))," v(T*)=",str(g.v[Tstar]))
    d=max_exact_bump(g,S)
    P("  d*(S)=",str(d)," slack=",str(slack)," LEMMA D REFUTED (d*>slack)?",d>slack)

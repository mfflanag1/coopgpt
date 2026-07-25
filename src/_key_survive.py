import sys
from fractions import Fraction as F
from tugame import Game, exact_lp_min
from leximin import leximin_core_exact
from lemD import xS, residual_cover, core_max_xS
def members(S,n): return [i for i in range(n) if S>>i&1]
def P(*a): print(*a,flush=True)
VS=["0","5","1","9","3","8","9","14","3","11","4","12","12","19","13","21","3","8","6","14","6","11","12","17","8","16","9","17","17","22","18","26","1","6","4","12","4","9","10","15","6","14","7","15","15","20","16","24","4","9","9","15","7","12","13","18","11","19","12","20","18","23","21","29"]
n=6; N=(1<<n)-1
g=Game(n,[F(x) for x in VS]); phi=leximin_core_exact(g)

def maxS_given(S,C):
    A_ub=[[-1 if U>>i&1 else 0 for i in range(n)] for U in range(1,N)]
    b_ub=[-g.v[U] for U in range(1,N)]
    A_eq=[[1]*n,[1 if C>>i&1 else 0 for i in range(n)]]; b_eq=[g.v[N],g.v[C]]
    c=[-1 if S>>i&1 else 0 for i in range(n)]
    opt,x=exact_lp_min(c,A_ub,b_ub,A_eq,b_eq)
    return None if opt is None or opt=='unbounded' else -opt

for S in [0b011101, 0b101101]:
    pS=xS(phi,S,n); slack=pS-g.v[S]
    P(f"\n== S={members(S,n)}  phi(S)={pS} v(S)={g.v[S]} slack={slack} ==")
    # certificate coalitions: C!=S with M^(C)<=phi(S); find the tight one (M^(C)=v(S))
    certs=[]; dstar=None
    for C in range(1,N):
        if C==S: continue
        m=maxS_given(S,C)
        if m is None: continue
        dT=m-g.v[S]
        if dstar is None or dT<dstar: dstar=dT
        if m<=pS: certs.append((C,m))
    P(f"  d*(S)={dstar}  (LEMMA D holds iff d*<=slack: {dstar<=slack})")
    P(f"  #cert coalitions C!=S with M^(C)<=phi(S): {len(certs)}")
    # the T* from residual_cover (KEY route) and whether it's among certs
    rc=residual_cover(g,phi,S); W=0
    for U in rc['lambda']: W|=U
    Tstar=W&S
    P(f"  KEY-route T*=W∩S={members(Tstar,n)}  M^(T*)={maxS_given(S,Tstar)}  in certs: {any(c==Tstar for c,_ in certs)}")
    # smallest / tightest cert
    tight=[(C,m) for C,m in certs if m==g.v[S]]
    P(f"  #certs achieving M^(C)=v(S) (force S to floor): {len(tight)}")
    if tight:
        C,m=min(tight,key=lambda cm:bin(cm[0]).count('1'))
        P(f"     smallest such: C={members(C,n)} (|C|={bin(C).count('1')}) M^(C)=v(S)={m}")

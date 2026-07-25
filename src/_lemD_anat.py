from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from lemD import (tight_coalitions, residual_cover, star_holds, core_max_xS, xS,
                  core_min_xT, max_exact_bump, exact_lp_min)
def members(S,n): return [i for i in range(n) if S>>i&1]
def maxxS_with_Ttight(g,S,T):
    n,N,v=g.n,g.N,g.v
    A_ub,b_ub=[],[]
    for U in range(1,N):
        A_ub.append([-1 if U>>i&1 else 0 for i in range(n)]); b_ub.append(-v[U])
    A_eq=[[1]*n,[1 if T>>i&1 else 0 for i in range(n)]]; b_eq=[v[N],v[T]]
    c=[-1 if S>>i&1 else 0 for i in range(n)]
    opt,_=exact_lp_min(c,A_ub,b_ub,A_eq,b_eq)
    return None if opt is None or opt=='unbounded' else -opt

g1=Game(5,[F(x) for x in ['0','0','2','3','0','1','2','3','1','1','4','5','2','2','4','5','0','0','4','5','1','1','4','5','1','1','6','6','2','2','6','7']])
S=0b1101  # {0,2,3}
phi=leximin_core_exact(g1); n=5
print("phi",[str(p) for p in phi],"S",members(S,n),"v(S)",str(g1.v[S]),"phi(S)",str(xS(phi,S,n)))
print("min_core x(S)",str(core_min_xT(g1,S)),"max_core x(S)",str(core_max_xS(g1,S)))
tights=tight_coalitions(g1,phi)
print("TIGHT at phi:",[members(T,n) for T in tights])
rc=residual_cover(g1,phi,S)
print("cover lambda:",{tuple(members(T,n)):str(v) for T,v in rc['lambda'].items()},"mu",str(rc['mu']),"r",{k:str(v) for k,v in rc['r'].items()})
# find T!=S achieving d*_T=0 (maxxS with T tight == v(S))
print("--- d*_T per proper T (only those <= slack shown) ---")
slack=xS(phi,S,n)-g1.v[S]
for T in range(1,g1.N):
    if T==S: continue
    mx=maxxS_with_Ttight(g1,S,T)
    if mx is not None and mx-g1.v[S] <= slack:
        print(f"  T={members(T,n)} maxxS|T tight={str(mx)} (v(S)={str(g1.v[S])}) => d*_T={str(mx-g1.v[S])}")

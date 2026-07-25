from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from lemD import (tight_coalitions, residual_cover, star_holds, core_max_xS, xS,
                  core_min_xT, max_exact_bump, exact_lp_min, round1_dual)
def members(S,n): return [i for i in range(n) if S>>i&1]
def maxxS_Ttight(g,S,T):
    n,N,v=g.n,g.N,g.v
    A_ub,b_ub=[],[]
    for U in range(1,N):
        A_ub.append([-1 if U>>i&1 else 0 for i in range(n)]); b_ub.append(-v[U])
    A_eq=[[1]*n,[1 if T>>i&1 else 0 for i in range(n)]]; b_eq=[v[N],v[T]]
    c=[-1 if S>>i&1 else 0 for i in range(n)]
    opt,_=exact_lp_min(c,A_ub,b_ub,A_eq,b_eq)
    return None if opt is None or opt=='unbounded' else -opt
gv=['0','0','5','5','1','2','9','9','2','2','7','7','4','5','11','11','2','3','10','10','3','4','12','13','5','6','12','12','6','7','15','16']
g=Game(5,[F(x) for x in gv]); n=5; S=0b11101  # {0,2,3,4}
phi=leximin_core_exact(g)
print("phi",[str(p) for p in phi])
m=[g.v[1<<i] for i in range(n)]; print("m",[str(x) for x in m],"gains",[str(phi[i]-m[i]) for i in range(n)])
print("S",members(S,n),"v(S)",str(g.v[S]),"phi(S)",str(xS(phi,S,n)),"min_core x(S)",str(core_min_xT(g,S)),"max_core x(S)",str(core_max_xS(g,S)))
h,val,y=star_holds(g,phi,S); print("star_holds",h,"maxval",str(val))
rc=residual_cover(g,phi,S); print("cover r",{k:str(v) for k,v in rc['r'].items()} if rc else None,"lambda",{tuple(members(T,n)):str(v) for T,v in rc['lambda'].items()} if rc else None)
print("tight",[members(T,n) for T in tight_coalitions(g,phi)])
d=max_exact_bump(g,S); slack=xS(phi,S,n)-g.v[S]
print("d*(S)=",str(d),"slack=",str(slack),"  d*>slack (binding-bumpable & star-fail = LEMMA D COUNTEREX)?",d>slack)
# which T (any) achieves M^(T) <= phi(S)?
pS=xS(phi,S,n); cert=[]
for T in range(1,g.N):
    if T==S: continue
    mx=maxxS_Ttight(g,S,T)
    if mx is not None and mx<=pS: cert.append((members(T,n),str(mx)))
print("T with M^(T)<=phi(S):",cert[:20])

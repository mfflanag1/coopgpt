from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from lemD import (tight_coalitions, residual_cover, star_holds, core_max_xS, xS,
                  core_min_xT, max_exact_bump, exact_lp_min)
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
gv=['0','1','0','2','1','2','2','3','1','2','2','3','2','3','3','4','3','5','3','5','5','7','5','7','5','7','5','7','7','8','7','9']
g=Game(5,[F(x) for x in gv]); n=5; N=g.N
phi=leximin_core_exact(g); print("phi",[str(p) for p in phi])
m=[g.v[1<<i] for i in range(n)]; print("gains",[str(phi[i]-m[i]) for i in range(n)])
for S in [0b10001,0b10100,0b11000]:  # {0,4},{2,4},{3,4}
    print("==== S",members(S,n),"====")
    pS=xS(phi,S,n); print("v(S)",str(g.v[S]),"phi(S)",str(pS),"min_core",str(core_min_xT(g,S)),"max_core",str(core_max_xS(g,S)))
    h,val,y=star_holds(g,phi,S); print("star_holds",h,"val",str(val))
    rc=residual_cover(g,phi,S); 
    if rc: print("cover",[members(U,n) for U in rc['lambda']],"r",{k:str(v) for k,v in rc['r'].items()},"mu",str(rc['mu']))
    d=max_exact_bump(g,S); print("d*(S)=",str(d),"slack=",str(pS-g.v[S]),"binding-bumpable?",d>pS-g.v[S])
    # all T!=S with M^(T)<=phi(S), and which give =v(S)
    cert=[]
    for T in range(1,N):
        if T==S: continue
        mx=maxxS_Ttight(g,S,T)
        if mx is not None and mx<=pS: cert.append((members(T,n),str(mx)))
    print("T with M^(T)<=phi(S):",cert)
    print("tight:",[members(T,n) for T in tight_coalitions(g,phi)])

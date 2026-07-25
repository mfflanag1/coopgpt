import numpy as np
from fractions import Fraction as F
from scipy.optimize import linprog
from tugame import Game
from leximin import leximin_core_exact
from lemD import residual_cover, xS, tight_coalitions
def members(S,n): return [i for i in range(n) if S>>i&1]
# empty-certk example
gv=['0','0','5','5','1','2','9','9','2','2','7','7','4','5','11','11','2','3','10','10','3','4','12','13','5','6','12','12','6','7','15','16']
g=Game(5,[F(x) for x in gv]); n=5; S=0b11101; N=g.N
phi=leximin_core_exact(g)
rc=residual_cover(g,phi,S)
Tstar=0
for U in rc['lambda']: Tstar |= (U&S)
print("S",members(S,n),"cover",[members(U,n) for U in rc['lambda']],"r",{k:str(v) for k,v in rc['r'].items()})
print("Tstar",members(Tstar,n),"v(Tstar)",str(g.v[Tstar]),"v(S)",str(g.v[S]))
# LP: max x(S) s.t. x(U)>=v(U) all proper U, x(N)=v(N), x(Tstar)=v(Tstar). Get duals via scipy.
props=list(range(1,N))
A_ub=[[-1.0 if U>>i&1 else 0.0 for i in range(n)] for U in props]
b_ub=[-float(g.v[U]) for U in props]
A_eq=[[1.0]*n,[1.0 if Tstar>>i&1 else 0.0 for i in range(n)]]
b_eq=[float(g.v[N]),float(g.v[Tstar])]
c=[-1.0 if S>>i&1 else 0.0 for i in range(n)]
res=linprog(c,A_ub=A_ub,b_ub=b_ub,A_eq=A_eq,b_eq=b_eq,bounds=[(None,None)]*n,method="highs")
print("max x(S)=",-res.fun)
yU=-res.ineqlin.marginals  # dual for <= constraints
al=-res.eqlin.marginals
print("active tight U with dual y_U>0:")
for U,y in zip(props,yU):
    if y>1e-7: print("  U",members(U,n),"y_U=",round(y,4),"tight?",xS([F(str(round(x,6))) for x in res.x],U,n))
print("alpha(eff)=",round(al[0],4),"beta(Tstar)=",round(al[1],4))
print("x*=",[round(x,4) for x in res.x])

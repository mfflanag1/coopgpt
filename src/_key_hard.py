"""Dissect the hard non-constant, no-2-valued-cover case S=[0,1,2,4,5].
Goal: understand why (KEY) v(W)>=phi(P)+v(T*) holds. Examine:
 - the W-minimizer x* (min core x(W)); is x*<=phi on T*?
 - the (W,T*)-flooring point y; leximin direction phi-y.
 - the full cover polytope: all vertices of valid residuals r on S.
"""
from fractions import Fraction as F
from tugame import Game, exact_lp_min
from leximin import leximin_core_exact
from lemD import star_holds, core_max_xS, xS, residual_cover, tight_coalitions

def members(S,n): return [i for i in range(n) if S>>i&1]

VS=['0','1','8','9','5','8','15','18','1','2','9','10','7','10','17','20','2','3','10','11','10','13','20','21','3','4','11','12','12','14','21','22','0','3','10','12','5','8','15','18','2','5','12','13','7','10','17','20','5','6','13','14','10','13','20','23','6','7','14','15','12','15','22','25']
n=6; N=(1<<n)-1
g=Game(n,[F(x) for x in VS]); phi=leximin_core_exact(g)
print("phi=",[str(x) for x in phi],"gains=",[str(phi[i]-g.v[1<<i]) for i in range(n)])

S=0b110111  # {0,1,2,4,5}
rc=residual_cover(g,phi,S); sig=rc['mu']; r=rc['r']
W=0
for U in rc['lambda']: W|=U
Tstar=W&S; P=N&~S; R=S&~W
print(f"S={members(S,n)} W={members(W,n)} T*={members(Tstar,n)} P={members(P,n)} R={members(R,n)} sigma={sig}")
print("cover:", {tuple(members(U,n)):str(rc['lambda'][U]) for U in rc['lambda']})
print("r:", {k:str(r[k]) for k in r})
print(f"v(W)={g.v[W]} phi(P)={xS(phi,P,n)} v(T*)={g.v[Tstar]} rhs={xS(phi,P,n)+g.v[Tstar]} margin={g.v[W]-xS(phi,P,n)-g.v[Tstar]}")

def min_xA(g,A,extra_eq=None):
    n,N,v=g.n,g.N,g.v
    A_ub=[[-1 if U>>i&1 else 0 for i in range(n)] for U in range(1,N)]
    b_ub=[-v[U] for U in range(1,N)]
    A_eq=[[1]*n]; b_eq=[v[N]]
    if extra_eq:
        for (C,val) in extra_eq: A_eq.append([1 if C>>i&1 else 0 for i in range(n)]); b_eq.append(val)
    c=[1 if A>>i&1 else 0 for i in range(n)]
    opt,x=exact_lp_min(c,A_ub,b_ub,A_eq,b_eq)
    return opt,x

# W-minimizer
opt,xstar=min_xA(g,W)
print(f"\nmin core x(W)={opt} (=v(W)? {opt==g.v[W]})")
print("x* =",[str(z) for z in xstar])
print("x* on T*:",[str(xstar[k]) for k in members(Tstar,n)]," phi on T*:",[str(phi[k]) for k in members(Tstar,n)])
print("x*<=phi on T*?", all(xstar[k]<=phi[k] for k in members(Tstar,n)))
print("x* on P:",[str(xstar[k]) for k in members(P,n)]," phi on P:",[str(phi[k]) for k in members(P,n)])

# flooring point y: y(W)=v(W), y(T*)=v(T*)
opt2,y=min_xA(g,0,extra_eq=[(W,g.v[W]),(Tstar,g.v[Tstar])])
print("\nfloor y=",[str(z) for z in y] if y else None)
if y:
    print("y(P)=",xS(y,P,n)," phi(P)=",xS(phi,P,n)," phi(P)<=y(P)?",xS(phi,P,n)<=xS(y,P,n))
    print("d=phi-y:",[str(phi[i]-y[i]) for i in range(n)])

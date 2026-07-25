"""RIGOROUS independent verification of the candidate (KEY) violation (n=6).
Exact rational throughout. Checks, from scratch:
 1. game exact
 2. phi = leximin core point (recompute; verify in core & leximin-optimal enough)
 3. star_S fails
 4. the found cover is VALID (lambda>=0 on tight U, r>=1 on S, r=0 off S, phi max r.x)
 5. v(W), phi(P), v(T*): KEY margin
 6. DECISIVE: d*(S) vs slack  -> is Lemma D itself refuted?
 7. certificate M^(T*)=max{x(S):core,x(T*)=v(T*)} vs phi(S) (KEY-sufficient-not-necessary)
 8. does ANY cover / ANY coalition C!=S give M^(C)<=phi(S)? (is the reduction rescuable?)
"""
from fractions import Fraction as F
from itertools import combinations
from tugame import Game, exact_lp_min
from leximin import leximin_core_exact
from lemD import (star_holds, core_max_xS, xS, residual_cover, tight_coalitions,
                  max_exact_bump, core_min_xT)

def members(S,n): return [i for i in range(n) if S>>i&1]

VS=["0","5","1","9","3","8","9","14","3","11","4","12","12","19","13","21","3","8","6","14","6","11","12","17","8","16","9","17","17","22","18","26","1","6","4","12","4","9","10","15","6","14","7","15","15","20","16","24","4","9","9","15","7","12","13","18","11","19","12","20","18","23","21","29"]
n=6; N=(1<<n)-1
g=Game(n,[F(x) for x in VS])

# 1. exact?
exact=all(core_min_xT(g,T)==g.v[T] for T in range(1,N))
print("1. game exact:",exact)
# balanced?
from tugame import is_balanced_game
print("   balanced (core nonempty):",is_balanced_game(g))

# 2. phi
phi=leximin_core_exact(g)
print("2. phi=",[str(x) for x in phi],"in core:",g.in_core(phi),"gains=",[str(phi[i]-g.v[1<<i]) for i in range(n)])

def M_Ctight(g,S,C):
    n,N,v=g.n,g.N,g.v
    A_ub=[[-1 if U>>i&1 else 0 for i in range(n)] for U in range(1,N)]
    b_ub=[-v[U] for U in range(1,N)]
    A_eq=[[1]*n,[1 if C>>i&1 else 0 for i in range(n)]]; b_eq=[v[N],v[C]]
    c=[-1 if S>>i&1 else 0 for i in range(n)]
    opt,_=exact_lp_min(c,A_ub,b_ub,A_eq,b_eq)
    return None if opt is None or opt=='unbounded' else -opt

for S in [0b011101, 0b101101]:  # {0,2,3,4}, {0,2,3,5}
    print(f"\n===== S={members(S,n)} =====")
    pS=xS(phi,S,n); slack=pS-g.v[S]
    print("  phi(S)=",pS," v(S)=",g.v[S]," slack=",slack," max_core x(S)=",core_max_xS(g,S))
    h,val,y=star_holds(g,phi,S)
    print("  3. star holds?",h," (star-fail if False); max y(S) with y>=phi on S =",val)
    rc=residual_cover(g,phi,S)
    sig=rc['mu']; r=rc['r']; lam=rc['lambda']
    # 4. validate cover
    tights=set(tight_coalitions(g,phi))
    cover_ok = all(U in tights for U in lam) and all(l>=0 for l in lam.values())
    rok = all(r[k]>=1 for k in members(S,n)) and all((k in members(S,n)) for k in r)
    # r_j=0 off S is implicit (r only defined on S); check phi maximizes r.x:
    rvec=[F(0)]*n
    for k in r: rvec[k]=r[k]
    # max r.x over core
    A_ub=[[-1 if U>>i&1 else 0 for i in range(n)] for U in range(1,N)]
    b_ub=[-g.v[U] for U in range(1,N)]
    A_eq=[[1]*n]; b_eq=[g.v[N]]
    cc=[-rvec[i] for i in range(n)]
    opt,xx=exact_lp_min(cc,A_ub,b_ub,A_eq,b_eq)
    rmax=-opt; rphi=sum(rvec[i]*phi[i] for i in range(n))
    print("  4. cover: lambda>=0 on tights:",cover_ok," r>=1 on S:",rok,
          " phi maximizes r.x:",rmax==rphi," (rmax=",str(rmax)," r.phi=",str(rphi),")")
    W=0
    for U in lam: W|=U
    Tstar=W&S; P=N&~S; R=S&~W
    print("     cover=",{tuple(members(U,n)):str(lam[U]) for U in lam}," sigma=",str(sig))
    print("     r=",{k:str(r[k]) for k in r})
    print("     W=",members(W,n)," T*=",members(Tstar,n)," P=",members(P,n)," R=",members(R,n))
    # 5. KEY
    vW=g.v[W]; phiP=xS(phi,P,n); vT=g.v[Tstar]
    print(f"  5. v(W)={vW} phi(P)={phiP} v(T*)={vT}  KEY margin=v(W)-phi(P)-v(T*)={vW-phiP-vT}")
    # 6. DECISIVE d* vs slack
    d=max_exact_bump(g,S)
    print(f"  6. DECISIVE: d*(S)={d}  slack={slack}  ->  d*>slack (Lemma D REFUTED)? {d>slack}")
    # 7. certificate for THIS T*
    MT=M_Ctight(g,S,Tstar)
    print(f"  7. M^(T*)=max{{x(S):x(T*)=v(T*)}}={MT}  <= phi(S)={pS}? {MT<=pS}  (KEY-route cert)")
    # 8. does ANY coalition C!=S give M^(C)<=phi(S)? (reduction rescuable)
    good=[]
    for C in range(1,N):
        if C==S: continue
        m=M_Ctight(g,S,C)
        if m is not None and m<=pS:
            good.append((C,m))
    print(f"  8. #coalitions C!=S with M^(C)<=phi(S): {len(good)}  (any => Lemma D cert survives)")
    if good:
        C,m=min(good,key=lambda cm: bin(cm[0]).count('1'))
        print(f"     e.g. C={members(C,n)} M^(C)={m}<=phi(S)={pS}")

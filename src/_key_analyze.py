"""Deep-analyze the rich n=6 game with non-constant covers. For each non-constant
star-fail: dump cover, W/T*/P/R, (KEY) margin, and the simultaneous-flooring point y
(y in core, y(W)=v(W), y(T*)=v(T*)); test phi(P)<=y(P) and inspect leximin direction."""
from fractions import Fraction as F
from tugame import Game, exact_lp_min
from leximin import leximin_core_exact
from lemD import star_holds, core_max_xS, xS, residual_cover, tight_coalitions, max_exact_bump

def members(S,n): return [i for i in range(n) if S>>i&1]

VS=['0','0','1','4','1','1','3','6','0','0','2','5','1','1','4','6','2','2','5','7','3','3','7','8','2','2','6','7','3','3','8','8','7','10','8','11','9','11','10','13','8','10','9','12','10','11','11','14','11','12','12','15','13','13','14','17','12','12','13','16','13','13','15','18']
n=6; N=(1<<n)-1
g=Game(n,[F(x) for x in VS])
phi=leximin_core_exact(g)
print("phi =",[str(x) for x in phi])
print("phi sorted gains:",sorted(str(phi[i]-g.v[1<<i]) for i in range(n)))

def floor_two(g,A,B):
    """core y with y(A)=v(A) and y(B)=v(B), minimize y(A) then feasibility."""
    n,N,v=g.n,g.N,g.v
    A_ub,b_ub=[],[]
    for U in range(1,N):
        A_ub.append([-1 if U>>i&1 else 0 for i in range(n)]); b_ub.append(-v[U])
    A_eq=[[1]*n,[1 if A>>i&1 else 0 for i in range(n)],[1 if B>>i&1 else 0 for i in range(n)]]
    b_eq=[v[N],v[A],v[B]]
    c=[0]*n
    opt,y=exact_lp_min(c,A_ub,b_ub,A_eq,b_eq)
    return y

nccount=0
for S in range(1,N):
    if bin(S).count("1")<2: continue
    if core_max_xS(g,S)<=xS(phi,S,n): continue
    h,_,_=star_holds(g,phi,S)
    if h: continue
    rc=residual_cover(g,phi,S)
    if rc is None or not rc['lambda']: continue
    sig=rc['mu']; r=rc['r']
    W=0
    for U in rc['lambda']: W|=U
    Tstar=W&S; P=N&~S; R=S&~W
    rT=[r[k] for k in members(Tstar,n)]
    if len(set(rT))<2: continue
    nccount+=1
    sW=xS(phi,W,n)-g.v[W]; sT=xS(phi,Tstar,n)-g.v[Tstar]
    print(f"\n=== NON-CONST cover #{nccount} S={members(S,n)} ===")
    lam=rc['lambda']
    print("  cover: "+"; ".join(f"{members(U,n)}:{lam[U]}" for U in lam)+f"  sigma={sig}")
    print("  r: "+", ".join(f"{k}:{r[k]}" for k in r))
    print(f"  W={members(W,n)} T*={members(Tstar,n)} P={members(P,n)} R={members(R,n)}")
    print(f"  v(W)={g.v[W]} phi(P)={xS(phi,P,n)} v(T*)={g.v[Tstar]} rhs={xS(phi,P,n)+g.v[Tstar]}  (KEY margin={g.v[W]-(xS(phi,P,n)+g.v[Tstar])})")
    print(f"  slack(W)={sW} slack(T*)={sT}  (KEY<=> sW<=sT: {sW<=sT})")
    # simultaneous floor point
    y=floor_two(g,W,Tstar)
    if y is not None:
        print(f"  floor y: y(P)={xS(y,P,n)} phi(P)={xS(phi,P,n)} (phi(P)<=y(P): {xS(phi,P,n)<=xS(y,P,n)})")
        d=[phi[i]-y[i] for i in range(n)]
        print(f"  leximin dir d=phi-y on P={[str(d[i]) for i in members(P,n)]} on T*={[str(d[i]) for i in members(Tstar,n)]} on R={[str(d[i]) for i in members(R,n)]}")
print(f"\ntotal non-const covers: {nccount}")

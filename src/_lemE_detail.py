import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, core_max_xS, xS, max_exact_bump, tight_coalitions
def members(S,n): return [i for i in range(n) if S>>i&1]
def vtau(g,S,tau):
    v=list(g.v); v[S]=F(tau); return Game(g.n,v)
n=5; rng=random.Random(int(sys.argv[1])); N=31; t0=time.time(); found=0
while time.time()-t0<110 and found<2:
    kk=2; c=rng.randint(n,5*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(kk)])
    phi0=leximin_core_exact(g)
    if phi0 is None: continue
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        d=max_exact_bump(g,S)
        slack=xS(phi0,S,n)-g.v[S]
        if d<=slack: continue    # binding-bumpable only
        found+=1
        print(f"=== BINDING PATH: S={members(S,n)} v(S)={g.v[S]} d*={d} slack={slack} ===")
        print("v",[str(u) for u in g.v])
        vS=g.v[S]
        # fine grid to locate breakpoints & derivative signs
        prev=None
        for t in range(0,25):
            tau=vS+F(t,24)*d
            gt=vtau(g,S,tau); pt=leximin_core_exact(gt)
            if pt is None: continue
            h,_,_=star_holds(gt,pt,S)
            binds = xS(pt,S,n)==tau
            tag=""
            if prev is not None:
                dsign=[('+' if pt[i]>prev[1][i] else '-' if pt[i]<prev[1][i] else '0') for i in range(n)]
                tag="d="+''.join(dsign)+" (S:"+''.join(dsign[i] for i in range(n) if S>>i&1)+")"
            print(f"  tau={str(tau):>8} phiS={str(xS(pt,S,n)):>6} binds={binds} star={h} phi={[str(x) for x in pt]} {tag}")
            prev=(tau,pt)
        if found>=2: break
print("found",found)

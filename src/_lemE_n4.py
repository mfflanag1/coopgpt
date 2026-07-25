import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, xS, max_exact_bump
def members(S,n): return [i for i in range(n) if S>>i&1]
def vtau(g,S,tau):
    v=list(g.v); v[S]=F(tau); return Game(g.n,v)
n=4; rng=random.Random(int(sys.argv[1])); N=15; t0=time.time(); found=0
while time.time()-t0<100 and found<3:
    kk=rng.randint(2,3); c=rng.randint(n,6*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(kk)])
    phi0=leximin_core_exact(g)
    if phi0 is None: continue
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        d=max_exact_bump(g,S)
        slack=xS(phi0,S,n)-g.v[S]
        if d<=slack: continue
        found+=1
        print(f"=== BINDING PATH S={members(S,n)} v(S)={g.v[S]} d*={d} slack={slack} v={[str(u) for u in g.v]} ===")
        vS=g.v[S]; prev=None
        for t in range(0,19):
            tau=vS+F(t,18)*d
            gt=vtau(g,S,tau); pt=leximin_core_exact(gt)
            if pt is None: continue
            h,_,_=star_holds(gt,pt,S)
            binds=xS(pt,S,n)==tau
            tag=""
            if prev is not None:
                ds=['+' if pt[i]>prev[i] else '-' if pt[i]<prev[i] else '0' for i in range(n)]
                tag="d="+''.join(ds)
            print(f"  tau={str(tau):>7} binds={binds} star={h} phi={[str(x) for x in pt]} {tag}")
            prev=pt
        if found>=3: break
print("found",found)

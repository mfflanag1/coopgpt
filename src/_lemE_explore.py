"""Explore the exact path phi(v_tau): monotonicity, piecewise-affine breakpoints,
derivative sign on S, and star_S along the path. Exact rational."""
import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, core_max_xS, xS, is_exact_game, core_min_xT
def members(S,n): return [i for i in range(n) if S>>i&1]
def vtau(g,S,tau):
    v=list(g.v); v[S]=F(tau); return Game(g.n,v)
def max_exact_bump(g,S):
    from lemD import max_exact_bump as meb
    return meb(g,S)
n=int(sys.argv[1]); seed=int(sys.argv[2]); cap=int(sys.argv[3])
rng=random.Random(seed*7); N=(1<<n)-1; t0=time.time()
paths=0; monoOK=0; starallOK=0; viol=0
while time.time()-t0<cap:
    kk=rng.randint(2,3); c=rng.randint(n,6*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(kk)])
    phi0=leximin_core_exact(g)
    if phi0 is None: continue
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        d=max_exact_bump(g,S)
        if d<=0: continue
        slack=xS(phi0,S,n)-g.v[S]
        if d<=slack: continue    # need binding (path actually moves phi)
        paths+=1
        # sample tau over [v(S), v(S)+d] incl endpoints and midpoints
        vS=g.v[S]; taus=[vS+F(t,6)*d for t in range(7)]
        phis=[]
        starall=True
        for tau in taus:
            gt=vtau(g,S,tau); pt=leximin_core_exact(gt)
            if pt is None: starall=False; break
            phis.append((tau,pt))
            h,_,_=star_holds(gt,pt,S)
            if not h: starall=False
        if len(phis)<len(taus): continue
        if starall: starallOK+=1
        # monotonicity check on S (phi_i nondecreasing as tau grows) and outside
        mono=True
        for i in range(n):
            seq=[pt[i] for _,pt in phis]
            if S>>i&1:
                if any(seq[a]>seq[a+1] for a in range(len(seq)-1)): mono=False
            else:
                if any(seq[a]<seq[a+1] for a in range(len(seq)-1)): mono=False
        if mono: monoOK+=1
        else:
            viol+=1
            print("*** E' MONOTONICITY VIOLATION ***","S",members(S,n),"v",[str(u) for u in g.v],flush=True)
            for tau,pt in phis: print("   tau",str(tau),"phi",[str(x) for x in pt],flush=True)
    if paths and paths%20==0:
        print(f"[prog] paths={paths} mono_ok={monoOK} star_all_ok={starallOK} viol={viol} t={time.time()-t0:.0f}s",flush=True)
print(f"n={n} seed={seed}: binding_paths={paths} mono_ok={monoOK} star_all_along={starallOK} VIOL={viol} t={time.time()-t0:.0f}s",flush=True)

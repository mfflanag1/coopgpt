"""(Q1) DECISIVE PROOF TEST. For each star-fail at phi (exact game), does there exist a
Farkas cover whose residual r is CONSTANT on T* = {k in S: r_k<sigma}?
Such a cover => (KEY) via the elementary convexity Steps 4-5 => Lemma D. If universal,
the theorem is PROVEN.

A constant-on-T* cover with intended split S = T0 (level rho) ⊍ R0 (level sigma) exists iff
the LP is feasible:
  vars: lambda_U>=0 on tight U, alpha(=sigma) free, rho free
  alpha - sum_{U∋j} lambda_U = 0      (j off S)          [P covered at level alpha]
  alpha - sum_{U∋k} lambda_U = rho     (k in T0)          [T* at common level rho]
        sum_{U∋k} lambda_U = 0         (k in R0)          [R uncovered -> r=alpha]
  rho >= 1,  alpha - rho >= tiny(>0)   (R0 strictly above -> proper room)
We test feasibility over ALL partitions (T0 nonempty, R0 nonempty).
"""
import random, sys, time
from fractions import Fraction as F
from tugame import Game, exact_lp_min
from leximin import leximin_core_exact
from lemD import star_holds, core_max_xS, xS, residual_cover, tight_coalitions
from hunt_exact_points import rand_point_sum, game_from_points

def members(S,n): return [i for i in range(n) if S>>i&1]

def const_cover_exists(g, phi, S):
    """Return (found, partition) : exists constant-on-T0 cover for some split."""
    n,N=g.n,g.N
    tights=tight_coalitions(g,phi)
    m=len(tights)
    Sm=members(S,n)
    # precompute membership
    inU=[[1 if U>>i&1 else 0 for i in range(n)] for U in tights]
    # enumerate splits of S into R0 (nonempty) / T0 (nonempty)
    kS=len(Sm)
    for rmask in range(1, (1<<kS)-0):   # subset of Sm = R0 (as index-subset); need R0,T0 nonempty
        R0=[Sm[j] for j in range(kS) if rmask>>j&1]
        T0=[Sm[j] for j in range(kS) if not (rmask>>j&1)]
        if not R0 or not T0: continue
        # vars: lambda(m) >=0, alpha, rho ; ordering [lambda..][alpha][rho]
        nv=m+2; ai=m; ri=m+1
        A_eq,b_eq=[],[]
        # off-S players j: alpha - sum lambda = 0
        for j in range(n):
            if S>>j&1: continue
            row=[0]*nv
            for t,U in enumerate(tights):
                if U>>j&1: row[t]=-1
            row[ai]=1
            A_eq.append(row); b_eq.append(0)
        # T0: alpha - sum lambda - rho = 0
        for k in T0:
            row=[0]*nv
            for t,U in enumerate(tights):
                if U>>k&1: row[t]=-1
            row[ai]=1; row[ri]=-1
            A_eq.append(row); b_eq.append(0)
        # R0: sum lambda = 0
        for k in R0:
            row=[0]*nv
            for t,U in enumerate(tights):
                if U>>k&1: row[t]=1
            A_eq.append(row); b_eq.append(0)
        A_ub,b_ub=[],[]
        for t in range(m):            # lambda>=0
            row=[0]*nv; row[t]=-1; A_ub.append(row); b_ub.append(0)
        # rho>=1
        row=[0]*nv; row[ri]=-1; A_ub.append(row); b_ub.append(-1)
        # alpha - rho >= 1  (strict room; scale-free: sigma-rho>=1 achievable by scaling)
        row=[0]*nv; row[ai]=-1; row[ri]=1; A_ub.append(row); b_ub.append(-1)
        c=[0]*nv
        opt,sol=exact_lp_min(c,A_ub,b_ub,A_eq,b_eq)
        if opt is not None and opt!='unbounded':
            return True,(T0,R0)
    return False,None

def _main():
  n=int(sys.argv[1]); seed0=int(sys.argv[2]); trials=int(sys.argv[3])
  log=sys.argv[4] if len(sys.argv)>4 else None
  def out(s):
    print(s,flush=True)
    if log:
        with open(log,'a') as f: f.write(s+'\n')

  rng=random.Random(seed0*99991+3); N=(1<<n)-1; t0=time.time()
  games=0; sf=0; found=0; notfound=0
  out(f"=== Q1 const-cover-exists n={n} seed0={seed0} trials={trials} @ {time.strftime('%H:%M:%S')} ===")
  for t in range(trials):
    kk=rng.randint(2,3); c=rng.randint(n,6*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(kk)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    games+=1
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        if core_max_xS(g,S)<=xS(phi,S,n): continue
        h,_,_=star_holds(g,phi,S)
        if h: continue
        sf+=1
        ok,part=const_cover_exists(g,phi,S)
        if ok: found+=1
        else:
            notfound+=1
            out("*** NO CONSTANT-ON-T* COVER *** "+f"v={[str(u) for u in g.v]} S={members(S,n)}")
    if games%50==0:
        out(f"[prog] games={games} sf={sf} constcover found={found} NOTfound={notfound} t={time.time()-t0:.0f}s")
  out(f"DONE n={n} s={seed0}: games={games} sf={sf} constcover_found={found} NOTfound={notfound}")

if __name__=="__main__":
    _main()

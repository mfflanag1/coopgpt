import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, core_max_xS, xS, residual_cover
def members(S,n): return [i for i in range(n) if S>>i&1]
n=int(sys.argv[1]); seed=int(sys.argv[2]); cap=int(sys.argv[3])
rng=random.Random(seed*211); N=(1<<n)-1; t0=time.time()
sf=0; cov01=0; other=0
while time.time()-t0<cap:
    kk=rng.randint(2,3); c=rng.randint(n,6*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(kk)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        if core_max_xS(g,S)<=xS(phi,S,n): continue
        h,_,_=star_holds(g,phi,S)
        if h: continue
        sf+=1
        rc=residual_cover(g,phi,S)
        if not rc['lambda']: continue
        sig=rc['mu']
        # coverage depth of each k in S: sum_{T ni k} lambda_T = sig - r_k
        depths={k: sig-rc['r'][k] for k in rc['r']}
        # is each depth in {0, sig-1}?  (0 => r=sig uncovered; sig-1 => r=1 floor)
        ok=all(d==0 or d==sig-1 for d in depths.values())
        if ok: cov01+=1
        else:
            other+=1
            print("NON-{0,sig-1} depth:",members(S,n),"depths",{k:str(v) for k,v in depths.items()},"sig",str(sig),"r",{k:str(v) for k,v in rc['r'].items()},flush=True)
print(f"n={n} seed={seed}: sf={sf} depths_in_{{0,sig-1}}:{cov01} other:{other} t={time.time()-t0:.0f}s",flush=True)

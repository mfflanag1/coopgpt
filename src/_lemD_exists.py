import random, sys, time
from itertools import combinations
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, core_max_xS, xS
def members(S,n): return [i for i in range(n) if S>>i&1]
n=int(sys.argv[1]); seed=int(sys.argv[2]); cap=int(sys.argv[3])
rng=random.Random(seed*4093); N=(1<<n)-1; t0=time.time()
sf=0; existR=0; bad=0
while time.time()-t0<cap:
    kk=rng.randint(2,3); c=rng.randint(n,5*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(kk)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        pS=xS(phi,S,n)
        if core_max_xS(g,S)<=pS: continue
        h,_,_=star_holds(g,phi,S)
        if h: continue
        sf+=1
        Sm=members(S,n)
        found=None
        for rsz in range(1,len(Sm)+1):
            for Rt in combinations(Sm,rsz):
                Rmask=0
                for i in Rt: Rmask|=1<<i
                if xS(phi,Rmask,n)==core_max_xS(g,Rmask):
                    found=Rt; break
            if found: break
        if found: existR+=1
        else:
            bad+=1
            print("*** NO nonempty R subset S with phi(R)=max_core x(R) ***",
                  [str(u) for u in g.v],"S",Sm,"phi",[str(p) for p in phi],flush=True)
print(f"n={n} seed={seed}: sf={sf} existR:{existR} BAD(no R):{bad} t={time.time()-t0:.0f}s",flush=True)

import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import xS
def members(S,n): return [i for i in range(n) if S>>i&1]
n=int(sys.argv[1]); seed=int(sys.argv[2]); cap=int(sys.argv[3])
rng=random.Random(seed*40499); N=(1<<n)-1; t0=time.time()
games=0; pairs=0; mono=0; viol=[]
while time.time()-t0<cap:
    kk=rng.randint(2,3); c=rng.randint(n,6*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(kk)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    games+=1
    slack=lambda A: xS(phi,A,n)-g.v[A]
    # test all nested A subset B (both proper nonempty)
    for B in range(1,N):
        sB=slack(B)
        sub=(B-1)&B
        while sub:
            if sub!=0:
                if slack(sub)<=sB: mono+=1
                else:
                    viol.append((members(sub,n),members(B,n),str(slack(sub)),str(sB)))
                pairs+=1
            sub=(sub-1)&B
    if viol:
        print("*** SLACK-MONO VIOLATION ***",[str(u) for u in g.v],"A,B,slackA,slackB:",viol[0],flush=True)
        break
print(f"n={n} seed={seed}: games={games} nested_pairs={pairs} mono_ok={mono} viols={len(viol)} t={time.time()-t0:.0f}s",flush=True)

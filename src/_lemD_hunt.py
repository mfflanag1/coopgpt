import random, sys, time, json
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, max_exact_bump, core_max_xS, xS
def members(S,n): return [i for i in range(n) if S>>i&1]
n=int(sys.argv[1]); seed=int(sys.argv[2]); trials=int(sys.argv[3]); cap=int(sys.argv[4])
rng=random.Random(seed); N=(1<<n)-1
t0=time.time(); games=0; roomS=0; starfail=0; bumpable_binding=0; sf_notbump=0
for t in range(trials):
    k=rng.randint(2,3); c=rng.randint(n,6*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(k)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    games+=1
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        pS=xS(phi,S,n)
        if core_max_xS(g,S)<=pS: continue
        roomS+=1
        h,val,y=star_holds(g,phi,S)
        if h: continue
        starfail+=1
        d=max_exact_bump(g,S)          # only when star fails
        slack=pS-g.v[S]
        if d>slack:                    # binding-bumpable AND star fails => COUNTEREXAMPLE
            bumpable_binding+=1
            pay=dict(claim="Lemma D COUNTEREXAMPLE: exact, binding-bumpable, star FAILS",
                     n=n,v=[str(u) for u in g.v],S=S,members=members(S,n),
                     phi=[str(u) for u in phi],dstar=str(d),slack=str(slack),
                     max_core_xS=str(core_max_xS(g,S)))
            print("*** LEMMA D COUNTEREXAMPLE ***",json.dumps(pay),flush=True)
            json.dump(pay,open(f"../results/WITNESS_lemD_counterex_n{n}.json","w"),indent=1)
        else:
            sf_notbump+=1
    if time.time()-t0>cap: print("[timecap] t=",t,flush=True); break
print(f"n={n} seed={seed}: games={games} roomS={roomS} starfail={starfail} "
      f"starfail_not_bindingbumpable={sf_notbump} COUNTEREX={bumpable_binding} "
      f"t={time.time()-t0:.0f}s",flush=True)

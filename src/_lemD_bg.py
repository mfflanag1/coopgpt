import random, sys, time, json
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, max_exact_bump, core_max_xS, xS
def members(S,n): return [i for i in range(n) if S>>i&1]
n=int(sys.argv[1]); seed0=int(sys.argv[2]); log=sys.argv[3]
def out(s):
    print(s,flush=True)
    with open(log,'a') as f: f.write(s+'\n')
rng=random.Random(seed0*7919); N=(1<<n)-1
t0=time.time(); games=0; roomS=0; starfail=0; sf_notbump=0; cx=0
out(f"=== lemD bg hunt n={n} seed0={seed0} @ {time.strftime('%H:%M:%S')} ===")
while True:
    k=rng.randint(2,4); c=rng.randint(n,7*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(k)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    games+=1
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        pS=xS(phi,S,n)
        if core_max_xS(g,S)<=pS: continue
        roomS+=1
        h,_,_=star_holds(g,phi,S)
        if h: continue
        starfail+=1
        d=max_exact_bump(g,S); slack=pS-g.v[S]
        if d>slack:
            cx+=1
            pay=dict(n=n,v=[str(u) for u in g.v],S=S,members=members(S,n),
                     phi=[str(u) for u in phi],dstar=str(d),slack=str(slack))
            out("*** LEMMA D COUNTEREXAMPLE *** "+json.dumps(pay))
            json.dump(pay,open(f"../results/WITNESS_lemD_counterex_n{n}_s{seed0}.json","w"),indent=1)
        else:
            sf_notbump+=1
    if games%25==0:
        out(f"[prog] games={games} roomS={roomS} starfail={starfail} sf_notbump={sf_notbump} CX={cx} t={time.time()-t0:.0f}s")

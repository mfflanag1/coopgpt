import random, sys, time, json
from fractions import Fraction as F
from tugame import Game
import bs_probe
from hunt_exact_points import rand_point_sum, game_from_points

def run(n, trials, seed):
    rng=random.Random(seed)
    seen=0; nonconvex=0; t0=time.time(); witness=None
    for t in range(trials):
        k=rng.randint(2,3); c=rng.randint(n,22)
        pts=[rand_point_sum(n,c,rng) for _ in range(k)]
        g=game_from_points(n,pts)   # exact by construction
        seen+=1
        if g.is_convex(): continue
        nonconvex+=1
        r=bs_probe.probe(g, seed=seed+t, starts=18)
        if r is not None:
            xr,viol=r
            witness={'v':[str(a) for a in g.v],'x':[str(a) for a in xr],
                     'viol':[{'S':S,'members':[i for i in range(n) if S>>i&1],'vS':str(g.v[S]),
                              'xS':str(sum(xr[i] for i in range(n) if S>>i&1))} for S in viol]}
            print('*** WITNESS ***', json.dumps(witness)); 
            json.dump(witness, open(f'/Users/maxf/projects/counterexample-hunt/coopgames/results/WITNESS_bs_exact_nonlarge.json','w'),indent=1)
            return witness
        if t and t%25==0:
            print(f'... t={t} nonconvex={nonconvex} elapsed={time.time()-t0:.0f}s rate={(time.time()-t0)/(t+1):.1f}s/game',flush=True)
    print(f'DONE n={n} seed={seed}: seen={seen} nonconvex={nonconvex} NO witness ({time.time()-t0:.0f}s)')
    return None

if __name__=='__main__':
    run(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))

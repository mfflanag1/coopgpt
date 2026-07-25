"""ADVERSARIAL binding-regime hunt: test ONLY exact-preserving bumps where the
constraint actually binds (d > slack of S at phi(v)) -- the rare regime where a
counterexample could hide. Every binding bump exact-certified.
"""
import random, sys, json, time
from fractions import Fraction as F
from tugame import Game
from hunt_sd import is_exact_game
from hunt_exact_points import rand_point_sum, game_from_points
from leximin import leximin_core_float, leximin_core_exact
from floatscreen import is_exact_float
def xS(x,S,n): return sum(x[i] for i in range(n) if S>>i&1)
def run(n,target,seed,logpath):
    rng=random.Random(seed); log=open(logpath,'a')
    def out(s): print(s,flush=True); log.write(s+'\n'); log.flush()
    out(f"=== binding hunt n={n} target={target} seed={seed} @ {time.strftime('%H:%M:%S')} ===")
    N=(1<<n)-1; binding=0; certified=0; t0=time.time()
    while binding<target:
        k=rng.randint(2,4); c=rng.randint(n,8*n)
        g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(k)]); vf=[float(u) for u in g.v]
        x=leximin_core_float(n,vf)
        if x is None: continue
        for S in range(1,N):
            if bin(S).count('1')<2: continue
            sl=xS(x,S,n)-g.v[S]
            for dd in range(1,12):
                v2=list(vf); v2[S]+=dd
                if not is_exact_float(n,v2): break
                if dd<=sl+1e-9: continue           # not binding yet
                y=leximin_core_float(n,v2)
                if y is None: continue
                binding+=1
                drop=[i for i in range(n) if S>>i&1 and y[i]<x[i]-1e-6]
                # ALWAYS exact-certify binding bumps (both directions of interest)
                ge=Game(n,[F(u) for u in g.v])
                if not is_exact_game(ge): continue
                v2e=list(ge.v); v2e[S]+=dd; g2=Game(n,v2e)
                if not is_exact_game(g2): continue
                xe=leximin_core_exact(ge); ye=leximin_core_exact(g2)
                if xe is None or ye is None: continue
                certified+=1
                ed=[(i,str(xe[i]-ye[i])) for i in range(n) if S>>i&1 and xe[i]>ye[i]]
                if ed:
                    pay=dict(claim="phi NOT coal-monotone on EXACT games (binding)",n=n,
                        v=[str(u) for u in ge.v],S=S,d=dd,members=[i for i in range(n) if S>>i&1],
                        phi_v=[str(u) for u in xe],phi_vp=[str(u) for u in ye],drops=ed)
                    json.dump(pay,open(f"../results/WITNESS_leximin_binding_n{n}.json","w"),indent=1)
                    out("*** CERTIFIED EXACT VIOLATION (binding) ***"); out(json.dumps(pay)); return pay
                break   # one binding bump per (game,S)
        if binding and binding%200==0:
            out(f"[progress] binding_tested={binding} exact_certified={certified} clean, t={time.time()-t0:.0f}s")
    out(f"[DONE] binding_tested={binding} exact_certified={certified} ALL CLEAN (no exact violation)")
    return None
if __name__=="__main__":
    n=int(sys.argv[1]); target=int(sys.argv[2]); seed=int(sys.argv[3])
    run(n,target,seed,f"../results/agent_leximin_binding_n{n}_s{seed}.txt")

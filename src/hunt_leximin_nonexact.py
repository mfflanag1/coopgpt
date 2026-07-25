"""Is leximin-above-floors phi coalitionally monotonic on BALANCED but NON-EXACT
games? Hunt a counterexample: raising one v(S) makes some i in S drop.
Non-exact games made by lowering some worths (esp. singleton floors) below their
core-min, keeping the core nonempty. Float screen -> exact certify.
"""
import random, sys, json, time
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from hunt_sd import is_exact_game, core_min_xS
from hunt_exact_points import rand_point_sum, game_from_points
from leximin import leximin_core_float, leximin_core_exact
from floatscreen import is_balanced_float

def xS(x,S,n): return sum(x[i] for i in range(n) if S>>i&1)

def gen_nonexact(n, rng):
    N=(1<<n)-1
    k=rng.randint(2,3); c=rng.randint(n,7*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(k)])  # exact seed
    v=[F(u) for u in g.v]
    # lower some worths below core-min (make non-exact); bias to singletons
    targets=[]
    for _ in range(rng.randint(1,4)):
        if rng.random()<0.6:
            i=rng.randrange(n); targets.append(1<<i)
        else:
            targets.append(rng.randint(1,N-1))
    for T in targets:
        v[T]=v[T]-F(rng.randint(1,4))       # relax -> core grows or same, stays balanced
    g2=Game(n,v)
    if is_exact_game(g2): return None       # want NON-exact
    return g2

def run(n, trials, seed, logpath):
    rng=random.Random(seed); log=open(logpath,'a')
    def out(s):
        print(s,flush=True); log.write(s+'\n'); log.flush()
    out(f"=== hunt_leximin NONEXACT n={n} trials={trials} seed={seed} @ {time.strftime('%H:%M:%S')} ===")
    N=(1<<n)-1; bases=0; bumps=0; viols=0; t0=time.time()
    for t in range(trials):
        g=gen_nonexact(n,rng)
        if g is None: continue
        vf=[float(u) for u in g.v]
        if not is_balanced_float(n,vf): continue
        x=leximin_core_float(n,vf)
        if x is None: continue
        bases+=1
        for S in range(1,N):
            for d in range(1,5):
                v2=list(vf); v2[S]+=d
                if not is_balanced_float(n,v2): break
                y=leximin_core_float(n,v2)
                if y is None: continue
                bumps+=1
                drops=[i for i in range(n) if S>>i&1 and y[i]<x[i]-1e-6]
                if drops:
                    viols+=1
                    out(f"[cand] S={S:0{n}b} d={d} drops={drops} nonexact")
                    # exact certify
                    ge=g; v2e=list(ge.v); v2e[S]+=d; g2=Game(n,v2e)
                    if not is_balanced_game(g2): out("  reject: v2 not balanced"); continue
                    xe=leximin_core_exact(ge); ye=leximin_core_exact(g2)
                    if xe is None or ye is None: out("  reject: exact phi failed"); continue
                    ed=[(i,str(xe[i]-ye[i])) for i in range(n) if S>>i&1 and xe[i]>ye[i]]
                    if not ed: out("  reject: exact shows no drop"); continue
                    if not (ge.in_core(xe) and g2.in_core(ye)): out("  reject: not in core"); continue
                    payload=dict(claim="phi NOT coalitionally monotonic on BALANCED NON-EXACT games",
                        n=n,v=[str(u) for u in ge.v],S=S,d=d,members=[i for i in range(n) if S>>i&1],
                        phi_v=[str(u) for u in xe],phi_vp=[str(u) for u in ye],drops=ed,
                        base_exact=is_exact_game(ge),v2_exact=is_exact_game(g2))
                    json.dump(payload,open(f"../results/WITNESS_leximin_nonexact_n{n}.json","w"),indent=1)
                    out("*** CERTIFIED: phi NOT monotone on balanced non-exact ***")
                    out(json.dumps(payload,indent=1)); return payload
        if bases%100==0: out(f"[progress] bases={bases} bumps={bumps} viols={viols} t={time.time()-t0:.0f}s")
    out(f"[DONE] bases={bases} bumps={bumps} float_viols={viols}")
    return None

if __name__=="__main__":
    n=int(sys.argv[1]); trials=int(sys.argv[2]); seed=int(sys.argv[3])
    run(n,trials,seed,f"../results/agent_leximin_nonexact_n{n}_s{seed}.txt")

import random, sys
from itertools import combinations
from hunt_monotonic import rand_game
from floatscreen import is_balanced_float, is_exact_float, _core_min_xS_float
def vbump(v,bumps):
    v2=list(v)
    for S,d in bumps: v2[S]+=d
    return v2
def run(trials, seed, dmax=2):
    rng=random.Random(seed); n=4
    bases=0; pairs=0; pairM_unbal=0; tris=0; triM_unbal=0
    for t in range(trials):
        g=rand_game(4,rng,"general"); v=[float(x) for x in g.v]
        if not is_balanced_float(4,v): continue
        # float exactify
        N=15; ve=[0.0]*16; ve[15]=v[15]
        ok=True
        for S in range(1,15):
            m=_core_min_xS_float(4,v,S)
            if m is None: ok=False; break
            ve[S]=m
        if not ok: continue
        base=ve
        arms=[]
        for S in range(1,15):
            for d in range(1,dmax+1):
                if is_exact_float(4, vbump(base,[(S,d)])): arms.append((S,d)); break
        if len(arms)<2: continue
        bases+=1
        for a,b in combinations(arms,2):
            pairs+=1
            if not is_balanced_float(4, vbump(base,[a,b])): pairM_unbal+=1
        for a,b,c in combinations(arms,3):
            tris+=1
            if not is_balanced_float(4, vbump(base,[a,b,c])): triM_unbal+=1
        if bases%200==0:
            print(f"[t={t}] bases={bases} pairs={pairs} pairM_unbal={pairM_unbal} tris={tris} triM_unbal={triM_unbal}",flush=True)
        if bases>=2000: break
    print(f"FINAL bases={bases} pairs={pairs} pairM_unbal={pairM_unbal} tris={tris} triM_unbal={triM_unbal}",flush=True)
if __name__=="__main__":
    run(int(sys.argv[1]), int(sys.argv[2]) if len(sys.argv)>2 else 1)

"""n>=6 DECISIVE test of stable => ES.

For n<=5 stable<=>large=>ES (Estevez-Fernandez), so the open frontier is n>=6.
This hunts non-ES n=6 games and tries hard to exhibit an undominated escape
(=> core NOT stable, consistent with the theorem). Any non-ES game where NO
escape is found by heavy search is a CANDIDATE stable-core counterexample and is
dumped for deep investigation.

Escape candidates tried (all exact-certified):
  (A) single strips y = gh - delta*e_p for every absorbing p;
  (B) hub-boost vertices: push a set F of satellites to their floor, then choose
      the boosted coordinates by solving efficiency on tight admissible coalitions;
  (C) broad float search (find_escape_float) as a catch-all, exact-certified.
"""
import sys, itertools, random, json
from fractions import Fraction as F
sys.path.insert(0,'/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members
from es_check_main import egalitarian_procedure
from core_stability import in_core, is_imputation, is_dominated_by_core, certify_undominated
from largeness_exact import exact_solve
from stability_float import find_escape_float
from stES_test_construction import rand_point_sum, game_from_points, rand_balanced_superadd

def undom(g, y):
    if not is_imputation(g, y) or in_core(g, y): return False
    dom,_ = is_dominated_by_core(g, y)
    return not dom

def try_single_strips(g, gh, delta):
    n=g.n
    for p in range(n):
        if gh[p]-g.v[1<<p] < delta: continue
        y=list(gh); y[p]=gh[p]-delta
        if undom(g,y): return y, ("single",p)
    return None, None

def try_floor_vertices(g, gh, delta, maxF=3):
    """Push subsets F of players to their floor; fill remaining coords to a vertex
    by adding tight-coalition / floor planes; test undomination."""
    n,N=g.n,g.N
    planes=[]
    for S in range(1,N): planes.append(([1 if S>>i&1 else 0 for i in range(n)],g.v[S]))
    floorplane={i:([1 if j==i else 0 for j in range(n)], g.v[1<<i]) for i in range(n)}
    eff=([1]*n,g.v[N])
    seen=set()
    # choose a set F (|F|<=maxF) of players forced to floor + (n-1-|F|) coalition planes
    for kF in range(1, maxF+1):
        for Fset in itertools.combinations(range(n), kF):
            need = n-1-kF
            if need < 0: continue
            base=[floorplane[i] for i in Fset]
            # pick 'need' coalition planes from proper coalitions
            for combo in itertools.combinations(range(len(planes)), need):
                M=[base[j][0] for j in range(kF)]+[planes[c][0] for c in combo]+[eff[0]]
                b=[base[j][1] for j in range(kF)]+[planes[c][1] for c in combo]+[eff[1]]
                y=exact_solve([r[:] for r in M], b[:], n)
                if y is None: continue
                key=tuple(y)
                if key in seen: continue
                seen.add(key)
                if undom(g,y): return y, ("floor",Fset,combo)
    return None, None

def hunt(seed=1, n=6, ntrials=200, maxF=2):
    rng=random.Random(seed)
    st={"nonES":0,"escape_single":0,"escape_floor":0,"escape_float":0,"NO_ESCAPE":0}
    candidates=[]
    for t in range(ntrials):
        # ALL point-generated exact n=6 games (exact by construction) + occasional random balanced
        if rng.random()<0.85:
            k=rng.randint(2,5); c=rng.randint(n,26)
            g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(k)])
        else:
            g=rand_balanced_superadd(n,rng)
        fixed,A,esN=egalitarian_procedure(n,list(g.v))
        if esN: continue
        gh=[fixed[i] for i in range(n)]; delta=sum(gh)-g.v[g.N]
        st["nonES"]+=1
        y,tag=try_single_strips(g,gh,delta)
        if y is not None: st["escape_single"]+=1
        else:
            y,tag=try_floor_vertices(g,gh,delta,maxF=maxF)
            if y is not None: st["escape_floor"]+=1
            else:
                vf=[float(x) for x in g.v]
                yf=find_escape_float(vf,n,g.N,tries=120000,seed=seed*7+t)
                if yf is not None:
                    yq=[F(a).limit_denominator(720) for a in yf]
                    if undom(g,yq): y=yq; st["escape_float"]+=1
                if y is None:
                    st["NO_ESCAPE"]+=1
                    candidates.append({"v":[str(x) for x in g.v],"gh":[str(x) for x in gh],
                                       "delta":str(delta)})
                    print("!!! NO ESCAPE FOUND (candidate stable non-ES)", flush=True)
                    print(json.dumps(candidates[-1]), flush=True)
        if st["nonES"]%10==0:
            print(f"  ...nonES={st['nonES']} single={st['escape_single']} floor={st['escape_floor']} "
                  f"float={st['escape_float']} NOESC={st['NO_ESCAPE']}", flush=True)
    return st, candidates

if __name__=="__main__":
    n=int(sys.argv[1]) if len(sys.argv)>1 else 6
    ntr=int(sys.argv[2]) if len(sys.argv)>2 else 150
    seed=int(sys.argv[3]) if len(sys.argv)>3 else 1
    st,cands=hunt(seed,n,ntr)
    print(json.dumps(st,indent=1))
    if cands:
        print(f"=== {len(cands)} CANDIDATE stable non-ES games (NO escape found) ===")
        for c in cands: print(json.dumps(c))
    else:
        print("Every non-ES n=%d game had an undominated escape (core not stable) -- theorem holds on sample."%n)

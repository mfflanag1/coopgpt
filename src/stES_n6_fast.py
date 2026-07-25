"""FAST n=6 hunt for a stable non-ES game (Dietzenbacher 2nd half).

Per non-ES point-generated game: screen escape candidates with FLOAT domination
(HiGHS, fast); exact-certify any undominated escape found. If NO candidate escape
survives float screening, escalate: broad float random search; if still none,
flag as CANDIDATE stable non-ES and exact-certify-attempt (full arrangement is too
big at n=6, so candidates are dumped for manual/expensive follow-up).

Candidates screened (float):
  (A) single strips gh - delta*e_p, all absorbing p
  (B) floor-vertex escapes: force small subsets to floor + coalition planes
  (C) broad random float imputations (find_escape_float)
"""
import sys, itertools, random, json
from fractions import Fraction as F
sys.path.insert(0,'/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members
from es_check_main import egalitarian_procedure
from core_stability import certify_undominated  # exact final certificate
from stability_float import (in_core_float, is_dominated_float, _core_rows,
                             find_escape_float)
from largeness_exact import exact_solve
from stES_test_construction import rand_point_sum, game_from_points

def undom_float(vf, n, N, y, base):
    if in_core_float(vf, n, N, y): return False
    return not is_dominated_float(vf, n, N, y, base)

def exact_ok(g, y):
    return certify_undominated(g, y) is not None

def screen(g, gh, delta, maxF=2):
    n, N = g.n, g.N
    vf = [float(x) for x in g.v]
    base = _core_rows(vf, n, N)
    lo = [g.v[1<<i] for i in range(n)]
    # (A) single strips
    for p in range(n):
        if gh[p]-lo[p] < delta: continue
        y = list(gh); y[p] = gh[p]-delta
        yf = [float(x) for x in y]
        if undom_float(vf, n, N, yf, base) and exact_ok(g, y):
            return y, ("single", p)
    # (B) HUB-BOOST: strip a satellite s fully to floor (freeing gh_s-lo_s >= delta),
    #     put the surplus (freed-delta) on ONE other player t. Deterministic + exact.
    for s in range(n):
        freed = gh[s]-lo[s]
        if freed < delta: continue
        boost = freed - delta
        for t in range(n):
            if t==s: continue
            y=list(gh); y[s]=lo[s]; y[t]=gh[t]+boost
            yf=[float(x) for x in y]
            if undom_float(vf, n, N, yf, base) and exact_ok(g, y):
                return y, ("boost", s, t)
    # (B2) two satellites to floor, surplus on one target
    for s1,s2 in itertools.combinations(range(n),2):
        freed = (gh[s1]-lo[s1])+(gh[s2]-lo[s2])
        if freed < delta: continue
        boost = freed - delta
        for t in range(n):
            if t in (s1,s2): continue
            y=list(gh); y[s1]=lo[s1]; y[s2]=lo[s2]; y[t]=gh[t]+boost
            yf=[float(x) for x in y]
            if undom_float(vf, n, N, yf, base) and exact_ok(g, y):
                return y, ("boost2", (s1,s2), t)
    # (C) broad random float last resort (catches remaining full-dim regions)
    yf = find_escape_float(vf, n, N, tries=40000, seed=hash(tuple(g.v))&0xffff)
    if yf is not None:
        for den in (12,24,60,120,360,720):
            yq=[F(a).limit_denominator(den) for a in yf]
            if exact_ok(g, yq):
                return yq, ("float",)
    return None, None

def hunt(seed=1, n=6, ntrials=3000, maxF=2):
    rng=random.Random(seed)
    st={"seen":0,"nonES":0,"single":0,"boost":0,"boost2":0,"float":0,"CAND":0}
    cands=[]
    for t in range(ntrials):
        k=rng.randint(2,5); c=rng.randint(n,26)
        g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(k)])
        st["seen"]+=1
        fixed,A,esN=egalitarian_procedure(n,list(g.v))
        if esN: continue
        gh=[fixed[i] for i in range(n)]; delta=sum(gh)-g.v[g.N]
        st["nonES"]+=1
        y,tag=screen(g,gh,delta,maxF=maxF)
        if y is None:
            st["CAND"]+=1
            rec={"v":[str(x) for x in g.v],"gh":[str(x) for x in gh],"delta":str(delta)}
            cands.append(rec)
            print("!!! CANDIDATE stable non-ES (no escape via float screen)", flush=True)
            print(json.dumps(rec), flush=True)
        else:
            st[tag[0]]+=1
        if st["nonES"]>0 and st["nonES"]%25==0:
            print(f"  ...seen={st['seen']} nonES={st['nonES']} single={st['single']} "
                  f"boost={st['boost']} boost2={st['boost2']} float={st['float']} CAND={st['CAND']}", flush=True)
    return st, cands

if __name__=="__main__":
    n=int(sys.argv[1]) if len(sys.argv)>1 else 6
    ntr=int(sys.argv[2]) if len(sys.argv)>2 else 3000
    seed=int(sys.argv[3]) if len(sys.argv)>3 else 1
    st,cands=hunt(seed,n,ntr)
    print(json.dumps(st,indent=1))
    if cands:
        print(f"=== {len(cands)} CANDIDATES (need exact follow-up) ===")
        for c in cands: print(json.dumps(c))
    else:
        print(f"n={n}: every non-ES game had an exact-certified undominated escape (core NOT stable).")

"""Condition 2 (coalition-marginal ceiling), LP-free sufficient undomination.

Single strip y = gh - delta*e_p. Domination via Q (p in Q) needs core x tight on Q
with x_i > gh_i on R:=Q\{p}, so x(R) > gh(R). But every core x has
x(R) <= M(R) := v(N) - v(N\R). Hence if gh(R) >= M(R) for R = Q\{p}, i.e.
g(N\R) := gh(N\R)-v(N\R) <= delta, domination via Q is impossible.

COND2(p): for every proper Q with p in Q and g(Q) < delta (the blockers),
          gh(Q\{p}) >= v(N) - v(N \ (Q\{p})).
If COND2(p) holds and p is absorbing (gh_p - v(p) >= delta), single strip is undominated.

Tests: (a) COND2 => LP-undominated (soundness, no false positives);
       (b) does an absorbing COND2 player always exist? coverage vs LP-undominated.
"""
import sys, itertools, random, json
from fractions import Fraction as F
sys.path.insert(0, '/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members
from es_check_main import egalitarian_procedure
from core_stability import in_core, is_imputation, is_dominated_by_core
from stES_test_construction import rand_point_sum, game_from_points, rand_balanced_superadd

def cond2_players(g, gh, delta):
    n, N = g.n, g.N
    good=[]
    for p in range(n):
        if gh[p]-g.v[1<<p] < delta: continue
        ok=True
        for Q in range(1,N):
            if not (Q>>p&1): continue
            if g.xS(gh,Q)-g.v[Q] < delta:      # Q blocks
                R = Q ^ (1<<p)                  # Q\{p}
                notR = N ^ R
                MR = g.v[N]-g.v[notR] if notR!=N else g.v[N]  # v(N)-v(N\R); if R empty, notR=N
                if R==0:
                    # R empty: domination via {p} alone needs x_p>y_p and x({p})=v(p); x_p=v(p)<=y_p? y_p=gh_p-delta>=v(p). ok blocked
                    continue
                if g.xS(gh,R) < MR:
                    ok=False; break
        if ok: good.append(p)
    return good

def lp_undom(g, gh, delta, p):
    y=list(gh); y[p]=gh[p]-delta
    if not is_imputation(g,y) or in_core(g,y): return None
    dom,_=is_dominated_by_core(g,y); return not dom

def run(seed=1,n=5,ntrials=500):
    rng=random.Random(seed)
    st={"nonES":0,"cond2_exists":0,"lp_exists":0,"cond2_false_pos":0,
        "cond2_missing_lp_has":0}
    misses=[]
    for t in range(ntrials):
        if rng.random()<0.6:
            k=rng.randint(2,4); c=rng.randint(n,20)
            g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(k)])
        else:
            g=rand_balanced_superadd(n,rng)
        fixed,A,esN=egalitarian_procedure(n,list(g.v))
        if esN: continue
        gh=[fixed[i] for i in range(n)]; delta=sum(gh)-g.v[g.N]
        st["nonES"]+=1
        # absorbing players
        absb=[p for p in range(n) if gh[p]-g.v[1<<p]>=delta]
        c2=cond2_players(g,gh,delta)
        lp=[p for p in absb if lp_undom(g,gh,delta,p)]
        if c2: st["cond2_exists"]+=1
        if lp: st["lp_exists"]+=1
        # soundness: every cond2 player must be LP-undominated
        for p in c2:
            if not lp_undom(g,gh,delta,p):
                st["cond2_false_pos"]+=1
                print("FALSE POS", [str(x) for x in g.v],"p",p,flush=True)
        if not c2 and lp:
            st["cond2_missing_lp_has"]+=1
            misses.append({"v":[str(x) for x in g.v],"gh":[str(x) for x in gh],
                           "delta":str(delta),"lp_players":lp})
        if st["nonES"]%50==0:
            print(f"  ...nonES={st['nonES']} cond2={st['cond2_exists']} lp={st['lp_exists']} "
                  f"fp={st['cond2_false_pos']} c2miss={st['cond2_missing_lp_has']}",flush=True)
    return st, misses

if __name__=="__main__":
    n=int(sys.argv[1]) if len(sys.argv)>1 else 5
    ntr=int(sys.argv[2]) if len(sys.argv)>2 else 400
    seed=int(sys.argv[3]) if len(sys.argv)>3 else 1
    st,misses=run(seed,n,ntr)
    print(json.dumps(st,indent=1))
    print(f"cond2-missing-but-LP-has cases: {len(misses)}")
    for m in misses[:12]: print(json.dumps(m))

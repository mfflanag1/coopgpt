"""For each non-ES game, for each absorbing-feasible player p, record features and
whether single-strip y=gh-delta*e_p is LP-undominated. Find the selection rule."""
import sys, itertools, random, json
from fractions import Fraction as F
sys.path.insert(0, '/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members
from es_check_main import egalitarian_procedure
from core_stability import in_core, is_imputation, is_dominated_by_core
from stES_test_construction import rand_point_sum, game_from_points, rand_balanced_superadd

def analyze_game(g):
    n, N = g.n, g.N
    fixed, A, esN = egalitarian_procedure(n, list(g.v))
    if esN: return None
    gh = [fixed[i] for i in range(n)]
    delta = sum(gh) - g.v[N]
    M = [g.v[N] - g.v[N ^ (1<<i)] for i in range(n)]
    Ahat = [S for S in range(1, N) if g.xS(gh, S) == g.v[S]]  # proper tight
    maximal = [S for S in Ahat if not any((S & T)==S and S!=T for T in Ahat)]
    Dset = set()  # strong claimants: in some tight S not strictly contained in another tight
    for S in maximal:
        for i in members(S, n): Dset.add(i)
    # actually D = union of maximal admissible (per union reading) -- keep both
    ntight = [sum(1 for S in Ahat if S>>i&1) for i in range(n)]
    hub = [i for i in range(n) if all(S>>i&1 for S in Ahat)] if Ahat else []
    rows = []
    for p in range(n):
        if gh[p] - g.v[1<<p] < delta: continue  # not absorbing-feasible
        y = list(gh); y[p] = gh[p] - delta
        if not is_imputation(g, y): continue
        dom, domS = is_dominated_by_core(g, y)
        rows.append({
            "p": p, "gh_p": str(gh[p]), "floor": str(g.v[1<<p]),
            "ceil_slack": str(M[p]-gh[p]), "in_maximal_tight": p in Dset,
            "ntight": ntight[p], "is_hub": p in hub,
            "undom": (not dom),
        })
    return {"delta": str(delta), "gh": [str(x) for x in gh],
            "hub": hub, "nrows": len(rows), "rows": rows,
            "any_undom": any(r["undom"] for r in rows)}

def run(seed=1, n=5, ntrials=500):
    rng = random.Random(seed)
    tot=0; any_undom=0
    # aggregate: among undominated vs dominated single-strips, feature distributions
    feat_undom = {"ceil_slack_pos":0,"ceil_slack_zero":0,"in_max":0,"not_in_max":0,"is_hub":0}
    feat_dom   = {"ceil_slack_pos":0,"ceil_slack_zero":0,"in_max":0,"not_in_max":0,"is_hub":0}
    no_undom_games=[]
    for t in range(ntrials):
        if rng.random()<0.6:
            k=rng.randint(2,4); c=rng.randint(n,20)
            g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(k)])
        else:
            g=rand_balanced_superadd(n,rng)
        a=analyze_game(g)
        if a is None: continue
        tot+=1
        if a["any_undom"]: any_undom+=1
        else: no_undom_games.append({"v":[str(x) for x in g.v], **a})
        for r in a["rows"]:
            d = feat_undom if r["undom"] else feat_dom
            if F(r["ceil_slack"])>0: d["ceil_slack_pos"]+=1
            else: d["ceil_slack_zero"]+=1
            if r["in_maximal_tight"]: d["in_max"]+=1
            else: d["not_in_max"]+=1
            if r["is_hub"]: d["is_hub"]+=1
        if tot%50==0:
            print(f"  ...games={tot} any_undom={any_undom}", flush=True)
    return {"games":tot,"any_undom":any_undom,
            "feat_undom":feat_undom,"feat_dom":feat_dom}, no_undom_games

if __name__=="__main__":
    n=int(sys.argv[1]) if len(sys.argv)>1 else 5
    ntr=int(sys.argv[2]) if len(sys.argv)>2 else 400
    seed=int(sys.argv[3]) if len(sys.argv)>3 else 1
    st, nog = run(seed, n, ntr)
    print(json.dumps(st, indent=1))
    print(f"games with NO absorbing single-strip undominated: {len(nog)}")
    for gg in nog[:15]: print(json.dumps(gg))

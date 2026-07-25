"""Test the pure-strip escape construction on many non-ES balanced games.

Construction under test (candidate universal witness that stable => ES fails
whenever ES fails):
  Let gamma-hat be the egalitarian claims, delta = sum(gamma-hat) - v(N) > 0.
  Build an efficient y <= gamma-hat by REMOVING total delta from coordinates,
  never below v({i}).  y is automatically outside the core (lemma: any efficient
  z <= gamma-hat, z != gamma-hat, is outside the core).  We then ask: is y
  UNDOMINATED by the core?  If yes for some strip pattern, the core is non-stable.

Strip strategies tested, in order:
  (A) single-strip: put all delta on ONE player p (needs gamma-hat_p - v({p}) >= delta)
  (B) greedy multi-strip: strip players by their headroom until delta exhausted
Also: full arrangement-vertex enumeration to confirm SOME undominated escape
exists (direct test of contrapositive: non-ES => core not stable).
"""
import sys, itertools, random, json
from fractions import Fraction as F
sys.path.insert(0, '/Users/maxf/projects/counterexample-hunt/coopgames/src')
from tugame import Game, members, is_balanced_game
from es_check_main import egalitarian_procedure
from core_stability import in_core, is_imputation, is_dominated_by_core, certify_undominated
from largeness_exact import exact_solve

def claims(n, v):
    fixed, A, esN = egalitarian_procedure(n, [F(x) for x in v])
    gh = [fixed[i] for i in range(n)]
    return gh, esN

def single_strips(g, gh, delta):
    """All feasible single-player strip candidates y."""
    n = g.n; out = []
    for p in range(n):
        floor = g.v[1 << p]
        if gh[p] - delta >= floor:
            y = list(gh); y[p] = gh[p] - delta
            out.append((p, y))
    return out

def greedy_strip(g, gh, delta):
    """Strip delta greedily from players with most headroom (gh_i - v({i}))."""
    n = g.n
    head = [(gh[i] - g.v[1 << i], i) for i in range(n)]
    head.sort(reverse=True)
    y = list(gh); rem = delta
    for h, i in head:
        if rem == 0: break
        take = min(h, rem)
        y[i] -= take; rem -= take
    if rem != 0:
        return None
    return y

def undominated(g, y):
    if not is_imputation(g, y): return False
    if in_core(g, y): return False
    dom, _ = is_dominated_by_core(g, y)
    return not dom

def enum_any_escape(g):
    """Full arrangement-vertex enumeration: does ANY undominated escape exist?"""
    n, N = g.n, g.N
    planes = []
    for S in range(1, N):
        planes.append(([1 if S>>i&1 else 0 for i in range(n)], g.v[S]))
    for i in range(n):
        row=[0]*n; row[i]=1; planes.append((row, g.v[1<<i]))
    eff=([1]*n, g.v[N]); seen=set()
    for combo in itertools.combinations(range(len(planes)), n-1):
        M=[planes[j][0] for j in combo]+[eff[0]]; b=[planes[j][1] for j in combo]+[eff[1]]
        y=exact_solve([r[:] for r in M], b[:], n)
        if y is None: continue
        key=tuple(y)
        if key in seen: continue
        seen.add(key)
        if undominated(g, y):
            return y
    return None

def test_game(g, run_full=True):
    n, N = g.n, g.N
    gh, esN = claims(n, [str(x) for x in g.v])
    if esN:
        return None  # ES, skip
    delta = sum(gh) - g.v[N]
    res = {"n": n, "vN": str(g.v[N]), "claims": [str(x) for x in gh], "delta": str(delta)}
    # (A) single strip
    A_hits = []
    for p, y in single_strips(g, gh, delta):
        if undominated(g, y):
            A_hits.append((p, [str(x) for x in y]))
    res["single_strip_undominated"] = A_hits
    # (B) greedy multi strip
    yg = greedy_strip(g, gh, delta)
    res["greedy_undominated"] = (yg is not None and undominated(g, yg))
    res["greedy_y"] = [str(x) for x in yg] if yg else None
    # any escape at all (direct contrapositive test) -- only if cheap strips failed
    if A_hits or res["greedy_undominated"]:
        res["any_escape_exists"] = True
        res["any_escape_y"] = None
    elif run_full:
        ya = enum_any_escape(g)
        res["any_escape_exists"] = ya is not None
        res["any_escape_y"] = [str(x) for x in ya] if ya else None
    else:
        res["any_escape_exists"] = None
        res["any_escape_y"] = None
    return res

# ---- generators ----
def rand_point_sum(n, c, rng):
    if n == 1: return [c]
    cuts = sorted(rng.randint(0, c) for _ in range(n-1))
    prev=0; p=[]
    for x in cuts: p.append(x-prev); prev=x
    p.append(c-prev); return p

def game_from_points(n, pts):
    N=(1<<n)-1; c=sum(pts[0]); v=[0]*(1<<n)
    for S in range(1,N):
        v[S]=min(sum(pts[j][i] for i in range(n) if S>>i&1) for j in range(len(pts)))
    v[N]=c
    return Game(n, [F(x) for x in v])

def rand_balanced_superadd(n, rng, cmax=12):
    """Random superadditive game, then lift v(N) to make balanced. Not nec. exact."""
    N=(1<<n)-1
    v=[0]*(1<<n)
    # assign singletons then build up superadditively with random increments
    for S in range(1, N+1):
        mx = 0
        # superadditive floor: max over partitions into two parts
        sub = (S-1) & S
        while sub:
            comp = S ^ sub
            if sub < comp:
                mx = max(mx, v[sub]+v[comp])
            sub = (sub-1) & S
        v[S] = mx + rng.randint(0, 3)
    g = Game(n, [F(x) for x in v])
    # lift v(N) until balanced
    while not is_balanced_game(g):
        v[N]+=1; g=Game(n,[F(x) for x in v])
    return g

def run(seed=1, n=5, ntrials=400):
    rng = random.Random(seed)
    stats = {"nonES": 0, "single_ok":0, "greedy_ok":0, "any_ok":0,
             "no_single_but_greedy":0, "no_escape":0}
    fails = []
    for t in range(ntrials):
        mode = rng.random()
        if mode < 0.6:
            k=rng.randint(2,4); c=rng.randint(n, 20)
            pts=[rand_point_sum(n,c,rng) for _ in range(k)]
            g=game_from_points(n,pts)
        else:
            g=rand_balanced_superadd(n,rng)
        r = test_game(g)
        if r is None: continue
        stats["nonES"]+=1
        if r["single_strip_undominated"]: stats["single_ok"]+=1
        if r["greedy_undominated"]: stats["greedy_ok"]+=1
        if r["any_escape_exists"]: stats["any_ok"]+=1
        if not r["single_strip_undominated"] and r["greedy_undominated"]:
            stats["no_single_but_greedy"]+=1
        if r["any_escape_exists"] is False:
            stats["no_escape"]+=1
            fails.append({"kind":"NO_ESCAPE","v":[str(x) for x in g.v], **r})
        elif not r["single_strip_undominated"]:
            # single strip failed but an escape exists: record for construction refinement
            fails.append({"kind":"NO_SINGLE","v":[str(x) for x in g.v], **r})
        if stats["nonES"] % 10 == 0:
            print(f"  ...nonES={stats['nonES']} single_ok={stats['single_ok']} "
                  f"greedy_ok={stats['greedy_ok']} any_ok={stats['any_ok']} "
                  f"no_escape={stats['no_escape']}", flush=True)
    return stats, fails

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv)>1 else 5
    ntr = int(sys.argv[2]) if len(sys.argv)>2 else 300
    seed = int(sys.argv[3]) if len(sys.argv)>3 else 1
    stats, fails = run(seed, n, ntr)
    print(json.dumps(stats, indent=1))
    for f in fails[:30]:
        print(json.dumps(f))
    if not any(f["kind"]=="NO_ESCAPE" for f in fails):
        print("No non-ES game lacked an undominated escape (consistent with theorem).")

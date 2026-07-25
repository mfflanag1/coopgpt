"""SD-prenucleolus (Arin-Katsev) monotonicity on market game classes.

Q1 permutation games: pairwise entry monotonicity (bump K[i][j], watch i,j).
Q2 assignment games : entry monotonicity (bump A[i][j], watch seller i, buyer j).
Q3 MCST cost games  : cost monotonicity via the value mirror
                      cost-share = -(SD-prenucleolus of w(S) = -c(S)),
                      bump edge (a,b), watch incident players for a share DROP.

Discipline: float screen (sd_prenucleolus_float) -> every candidate certified
EXACT with certified_sd_prenucleolus on BOTH games, drop verified in Fractions.
Certification failure => false positive, logged and skipped.
"""
import random, sys, json, time
from fractions import Fraction as F
from tugame import Game
from sd import sd_prenucleolus_float, certified_sd_prenucleolus
from assignment import assignment_game
from permutation import permutation_game
from mcst import mcst_cost_game

OUT = "../results/agent_sd_markets.txt"
_fh = open(OUT, "a")
def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    _fh.write(s + "\n"); _fh.flush()

# --------------------------------------------------------------- SD cost mirror
def sd_cost_shares_float(n, k):
    """Float SD cost-shares via the value mirror w(S) = -c(S)."""
    w = [F(0)] + [F(-k[S]) for S in range(1, 1 << n)]
    xf = sd_prenucleolus_float(Game(n, w))
    return None if xf is None else [-xi for xi in xf]

def sd_cost_shares_exact(n, k):
    w = [F(0)] + [F(-k[S]) for S in range(1, 1 << n)]
    xe = certified_sd_prenucleolus(Game(n, w))
    return None if xe is None else [-xi for xi in xe]

# --------------------------------------------------------------- generic certify
def certify_pair(g1, g2, watch, kind):
    """Both games certified exact; return list of (player, drop>0) exact, or None on cert-fail."""
    x = certified_sd_prenucleolus(g1)
    y = certified_sd_prenucleolus(g2)
    if x is None or y is None:
        return None
    return [(p, x[p] - y[p]) for p in watch if x[p] > y[p]], x, y

# =============================================================== Q0: known witness
def q0_permutation_witness():
    log("=== Q0: SD on the known nucleolus permutation witness ===")
    K  = [[0,7,0,0],[1,0,0,1],[1,0,0,0],[0,9,1,0]]
    K2 = [r[:] for r in K]; K2[3][2] += 1   # 1 -> 2
    g, g2 = permutation_game(K), permutation_game(K2)
    x = certified_sd_prenucleolus(g); y = certified_sd_prenucleolus(g2)
    log("  bump K[3][2] 1->2; watch players 2 and 3 (both in improved coalitions)")
    log("  SD before =", [str(u) for u in x])
    log("  SD after  =", [str(u) for u in y])
    for p in (2, 3):
        d = x[p] - y[p]
        tag = "DROP" if d > 0 else ("rise" if d < 0 else "flat")
        log(f"    player {p}: {x[p]} -> {y[p]}  ({tag} {d})")
    log("  (nucleolus dropped player 2: 1/2 -> 1/3)")
    drops = [(p, x[p]-y[p]) for p in (2,3) if x[p] > y[p]]
    if drops:
        log("  *** SD ALSO VIOLATES on this instance:", [(p, str(d)) for p,d in drops])
        save_witness("q1_witness", {"class":"permutation","K":K,"bump":[3,2,1],
            "x":[str(u) for u in x],"y":[str(u) for u in y],
            "drops":[(p,str(d)) for p,d in drops],"note":"SD fails on the known nucleolus witness"})
        return True
    log("  => SD FIXES the known nucleolus witness (neither watched player drops)")
    return False

# =============================================================== helpers
def save_witness(tag, data):
    fn = f"../results/agent_sd_markets_witness_{tag}.json"
    with open(fn, "w") as f:
        json.dump(data, f, indent=1)
    log("  witness saved:", fn)

# =============================================================== Q1: permutation
def q1_permutation(trials, seed, vmax=12):
    log(f"=== Q1: permutation n=4 pairwise monotonicity, {trials} trials seed={seed} ===")
    rng = random.Random(seed)
    cands = certfails = 0
    for t in range(trials):
        K = [[rng.randint(0,vmax) for _ in range(4)] for _ in range(4)]
        g = permutation_game(K)
        xf = sd_prenucleolus_float(g)
        if xf is None: continue
        i, j = rng.randrange(4), rng.randrange(4)
        d = rng.choice([1,2])
        K2 = [r[:] for r in K]; K2[i][j] += d
        g2 = permutation_game(K2)
        yf = sd_prenucleolus_float(g2)
        if yf is None: continue
        watch = {i, j}
        fdrops = [p for p in watch if xf[p] - yf[p] > 1e-6]
        if fdrops:
            cands += 1
            log(f"[cand] t={t} K={K} bump=({i},{j})+{d} float-drops={[(p,round(xf[p]-yf[p],4)) for p in fdrops]}")
            res = certify_pair(g, g2, watch, "perm")
            if res is None:
                certfails += 1; log("  cert-failed (false positive)"); continue
            ed, x, y = res
            if ed:
                log("  *** CERTIFIED permutation SD pairwise-monotonicity violation ***")
                save_witness("q1", {"class":"permutation","K":K,"bump":[i,j,d],
                    "x":[str(u) for u in x],"y":[str(u) for u in y],
                    "drops":[(p,str(dd)) for p,dd in ed]})
                log(f"[Q1 SUMMARY] CERTIFIED violation at t={t}")
                return True
            log("  exact: no drop (float artifact)")
    log(f"[Q1 SUMMARY] no certified violation / {trials} trials; float-cands={cands} cert-fails={certfails}")
    return False

# =============================================================== Q2: assignment
def _neartie_3x3(rng, vmax=12):
    """random 3x3 then force diagonal to tie an off-diagonal permutation."""
    A = [[rng.randint(0,vmax) for _ in range(3)] for _ in range(3)]
    # make a11+a22 == a12+a21  => diag {0,1,2} ties perm swapping 1,2
    A[2][2] = A[1][2] + A[2][1] - A[1][1]
    if A[2][2] < 0: A[2][2] = 0
    return A

def q2_assignment(trials, seed, vmax=12):
    log(f"=== Q2: assignment 3x3 entry monotonicity, ~{trials} trials seed={seed} ===")
    rng = random.Random(seed)
    m = mp = 3
    cands = certfails = 0
    # mix: random 0-12, low-entry 0-5 (dense ties), explicit near-tie construction
    def gen(t):
        if t % 5 == 4:   return _neartie_3x3(rng, vmax)
        if t % 5 == 3:   return [[rng.randint(0,5) for _ in range(mp)] for _ in range(m)]
        return [[rng.randint(0,vmax) for _ in range(mp)] for _ in range(m)]
    for t in range(trials):
        A = gen(t)
        g = assignment_game(A)
        xf = sd_prenucleolus_float(g)
        if xf is None: continue
        i, j = rng.randrange(m), rng.randrange(mp)
        d = rng.choice([1,2,3])
        A2 = [r[:] for r in A]; A2[i][j] += d
        g2 = assignment_game(A2)
        yf = sd_prenucleolus_float(g2)
        if yf is None: continue
        watch = {i, m + j}   # seller i, buyer j
        fdrops = [p for p in watch if xf[p] - yf[p] > 1e-6]
        if fdrops:
            cands += 1
            log(f"[cand] t={t} A={A} bump=({i},{j})+{d} float-drops={[(p,round(xf[p]-yf[p],4)) for p in fdrops]}")
            res = certify_pair(g, g2, watch, "assign")
            if res is None:
                certfails += 1; log("  cert-failed (false positive)"); continue
            ed, x, y = res
            if ed:
                log("  *** CERTIFIED assignment SD entry-monotonicity violation ***")
                save_witness("q2", {"class":"assignment","A":A,"bump":[i,j,d],
                    "x":[str(u) for u in x],"y":[str(u) for u in y],
                    "drops":[(p,str(dd)) for p,dd in ed]})
                log(f"[Q2 SUMMARY] CERTIFIED violation at t={t}")
                return True
            log("  exact: no drop (float artifact)")
    log(f"[Q2 SUMMARY] no certified violation / {trials} trials; float-cands={cands} cert-fails={certfails}")
    return False

# =============================================================== Q3: MCST
def q3_mcst(n, trials, seed, cmax=12):
    log(f"=== Q3: MCST cost monotonicity n={n}, {trials} trials seed={seed} ===")
    rng = random.Random(seed)
    cands = certfails = 0
    for t in range(trials):
        C = [[0]*(n+1) for _ in range(n+1)]
        for a in range(n+1):
            for b in range(a+1, n+1):
                C[a][b] = C[b][a] = rng.randint(1, cmax)
        k = mcst_cost_game(n, C)
        xf = sd_cost_shares_float(n, k)
        if xf is None: continue
        a = rng.randint(0, n); b = rng.randint(0, n)
        while b == a: b = rng.randint(0, n)
        d = rng.choice([1,2,3])
        C2 = [row[:] for row in C]; C2[a][b] += d; C2[b][a] += d
        k2 = mcst_cost_game(n, C2)
        yf = sd_cost_shares_float(n, k2)
        if yf is None: continue
        watch = [p-1 for p in (a, b) if p >= 1]   # incident players (source excluded)
        # cost monotonicity: raising an incident edge should NOT lower a player's cost share
        fdrops = [p for p in watch if xf[p] - yf[p] > 1e-6]
        if fdrops:
            cands += 1
            log(f"[cand] t={t} edge=({a},{b})+{d} float share-drops={[(p+1,round(xf[p]-yf[p],4)) for p in fdrops]}")
            x = sd_cost_shares_exact(n, k); y = sd_cost_shares_exact(n, k2)
            if x is None or y is None:
                certfails += 1; log("  cert-failed (false positive)"); continue
            ed = [(p, x[p]-y[p]) for p in watch if x[p] > y[p]]
            if ed:
                log("  *** CERTIFIED MCST SD cost-monotonicity violation (share drops when edge cost rises) ***")
                save_witness(f"q3_n{n}", {"class":"mcst","n":n,"C":C,"edge":[a,b],"d":d,
                    "shares_before":[str(u) for u in x],"shares_after":[str(u) for u in y],
                    "drops":[(p+1,str(dd)) for p,dd in ed]})
                log(f"[Q3 SUMMARY n={n}] CERTIFIED violation at t={t}")
                return True
            log("  exact: no drop (float artifact)")
    log(f"[Q3 SUMMARY n={n}] no certified violation / {trials} trials; float-cands={cands} cert-fails={certfails}")
    return False

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    log(f"\n########## SD-markets hunt start {time.strftime('%H:%M:%S')} which={which} ##########")
    if which in ("q0","q1","all"):
        q0_permutation_witness()
    if which in ("q1","all"):
        q1_permutation(500, seed=101)
    if which in ("q2","all"):
        q2_assignment(300, seed=202)
    if which in ("q3","all"):
        q3_mcst(4, 200, seed=303)
        q3_mcst(5, 200, seed=304)
    log(f"########## done {time.strftime('%H:%M:%S')} ##########")

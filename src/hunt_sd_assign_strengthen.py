"""Strengthen Q2: SD entry-monotonicity on assignment games.
(a) exhaustive 2x2 float sweep on the 0..4 grid, all single-entry +1..+(4-entry) bumps,
    every float-flagged candidate certified exact;
(b) 400 extra 3x3 trials (near-tie heavy), same certify discipline.
"""
import itertools, random, json
from fractions import Fraction as F
from tugame import Game
from sd import sd_prenucleolus_float, certified_sd_prenucleolus
from assignment import assignment_game

_fh = open("../results/agent_sd_markets.txt", "a")
def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); _fh.write(s+"\n"); _fh.flush()

def certify(A, i, j, d, m, mp):
    g = assignment_game(A)
    A2 = [r[:] for r in A]; A2[i][j] += d
    g2 = assignment_game(A2)
    x = certified_sd_prenucleolus(g); y = certified_sd_prenucleolus(g2)
    if x is None or y is None:
        return "certfail"
    ed = [(p, x[p]-y[p]) for p in (i, m+j) if x[p] > y[p]]
    if ed:
        return ("VIOLATION", [str(u) for u in x], [str(u) for u in y], [(p,str(dd)) for p,dd in ed])
    return None

def sweep_2x2():
    log("=== Q2 strengthen (a): exhaustive 2x2 assignment float sweep, entries 0..4 ===")
    m = mp = 2; cands = certfails = tested = 0
    for vals in itertools.product(range(5), repeat=4):
        A = [[vals[0], vals[1]], [vals[2], vals[3]]]
        g = assignment_game(A)
        xf = sd_prenucleolus_float(g)
        if xf is None: continue
        for i in range(m):
            for j in range(mp):
                for d in range(1, 5 - A[i][j] if A[i][j] < 4 else 0):
                    A2 = [r[:] for r in A]; A2[i][j] += d
                    yf = sd_prenucleolus_float(assignment_game(A2))
                    if yf is None: continue
                    tested += 1
                    if any(xf[p]-yf[p] > 1e-6 for p in (i, m+j)):
                        cands += 1
                        log(f"[cand] A={A} bump=({i},{j})+{d}")
                        r = certify(A, i, j, d, m, mp)
                        if r == "certfail": certfails += 1; log("  cert-failed"); continue
                        if r: log("  *** CERTIFIED 2x2 VIOLATION ***", r)
    log(f"[2x2 sweep] tested={tested} float-cands={cands} cert-fails={certfails} -> 2x2 grid 0..4 finite-checked")

def extra_3x3(trials, seed):
    log(f"=== Q2 strengthen (b): {trials} extra 3x3 trials seed={seed} (near-tie heavy) ===")
    rng = random.Random(seed); m = mp = 3; cands = certfails = 0
    for t in range(trials):
        if t % 2 == 0:  # near-tie construction
            A = [[rng.randint(0,12) for _ in range(3)] for _ in range(3)]
            A[2][2] = max(0, A[1][2] + A[2][1] - A[1][1])
        else:
            A = [[rng.randint(0,8) for _ in range(3)] for _ in range(3)]
        g = assignment_game(A); xf = sd_prenucleolus_float(g)
        if xf is None: continue
        i, j = rng.randrange(m), rng.randrange(mp); d = rng.choice([1,2,3])
        A2 = [r[:] for r in A]; A2[i][j] += d
        yf = sd_prenucleolus_float(assignment_game(A2))
        if yf is None: continue
        if any(xf[p]-yf[p] > 1e-6 for p in (i, m+j)):
            cands += 1; log(f"[cand] t={t} A={A} bump=({i},{j})+{d}")
            r = certify(A, i, j, d, m, mp)
            if r == "certfail": certfails += 1; log("  cert-failed"); continue
            if r: log("  *** CERTIFIED 3x3 VIOLATION ***", r)
    log(f"[extra 3x3] {trials} trials float-cands={cands} cert-fails={certfails}")

if __name__ == "__main__":
    sweep_2x2()
    extra_3x3(400, seed=555)

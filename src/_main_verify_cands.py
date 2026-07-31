"""Main-session independent verification of cand1/cand2 foundations:
non-ES (own egalitarian procedure), exactness (62 exact LPs), segment core."""
import sys, time
from fractions import Fraction as F
from itertools import combinations
sys.path.insert(0, "src")
from tugame import Game
from lemD import is_exact_game, xS
from es_check_main import egalitarian_procedure  # main-session ES impl

CANDS = {
 "cand1": ([0,1,0,2,0,1,1,2,0,2,0,2,1,2,1,3,1,3,1,3,2,4,2,4,1,3,1,3,2,4,2,4,0,1,1,2,0,1,1,2,1,2,2,3,1,2,2,3,3,4,3,5,3,4,4,5,3,5,3,5,4,5,4,6],
           [F(1),F(1),F(0),F(1),F(3),F(0)], [F(2),F(0),F(1),F(0),F(1),F(2)]),
 "cand2": ([0,1,0,2,1,2,2,3,1,2,2,3,2,3,3,4,1,3,1,4,3,4,3,5,3,4,3,5,4,5,5,6,0,3,0,3,2,4,2,5,2,4,2,5,4,5,4,6,1,4,1,4,3,6,3,6,3,6,3,6,5,7,5,8],
           [F(3),F(0),F(2),F(2),F(1),F(0)], [F(1),F(1),F(1),F(1),F(2),F(2)]),
}
n = 6; N = 63
ok = True
def chk(lab, c):
    global ok
    print(("ok   " if c else "FAIL "), lab, flush=True)
    ok = ok and c

for name, (VV, A, B) in CANDS.items():
    print(f"== {name}")
    v = [F(x) for x in VV]; g = Game(n, v)
    # endpoints are core points
    for lbl, x in (("A", A), ("B", B)):
        chk(f"{lbl} in core", sum(x) == v[N] and all(xS(x, S, n) >= v[S] for S in range(1, N)))
    # fully-tight coalitions: tight at BOTH endpoints -> tight on whole segment
    ft = [S for S in range(1, N) if xS(A, S, n) == v[S] and xS(B, S, n) == v[S]]
    chk(f"12 fully-tight coalitions (got {len(ft)})", len(ft) == 12)
    # affine dim of {x: x(N)=v(N), x(S)=v(S) for S in ft} is 1, i.e. rank of eq system = n-1
    rows = [[F(1)]*n] + [[F(1) if S >> i & 1 else F(0) for i in range(n)] for S in ft]
    # rank via fraction Gaussian elimination
    M = [r[:] for r in rows]; rank = 0; col = 0
    for col in range(n):
        piv = next((r for r in range(rank, len(M)) if M[r][col] != 0), None)
        if piv is None: continue
        M[rank], M[piv] = M[piv], M[rank]
        pr = M[rank]
        for r in range(len(M)):
            if r != rank and M[r][col] != 0:
                f = M[r][col] / pr[col]
                M[r] = [a - f*b for a, b in zip(M[r], pr)]
        rank += 1
    chk(f"tight system rank = 5 (core affine dim 1); rank={rank}", rank == 5)
    # non-ES via main-session independent egalitarian procedure
    fixed, Ahat, es = egalitarian_procedure(n, v)
    claims = [fixed[i] for i in range(n)]
    chk(f"NOT egalitarian stable (claims={[str(c) for c in claims]}, sum={sum(claims)} > v(N)={v[N]})",
        (not es) and sum(claims) > v[N])
    # exactness — slow part
    t0 = time.time()
    chk(f"EXACT (62 coalitions attained)", is_exact_game(g))
    print(f"   (exactness took {time.time()-t0:.0f}s)")
print("\n" + ("ALL FOUNDATION CHECKS PASSED" if ok else "*** FAILURES ***"))
sys.exit(0 if ok else 1)

"""Lift the n=5 escaping imputations to the n=6 padded games and verify the
padded cores are NOT vNM-stable. Fast float undomination screen + exact certify.
"""
from fractions import Fraction as F
from tugame import Game
from eshunt import is_ES
from es_float import core_min_all
from stability_float import is_dominated_float, in_core_float, _core_rows
from core_stability import certify_undominated, is_imputation, in_core

WIT_VN4 = [0,0,0,0,0,1,1,1,1,1,1,1,2,2,2,2,0,1,1,2,0,1,1,2,2,3,3,3,2,3,3,4]
BASE_VN6 = [0,0,0,0,3,3,3,3,0,0,0,0,4,4,4,4,0,0,0,0,4,5,5,5,0,0,0,0,4,5,5,6]
ESC = {"vN4": (WIT_VN4, [F(0),F(1),F(1),F(2),F(0)]),
       "vN6": (BASE_VN6, [F(1),F(1),F(3),F(1),F(0)])}


def pad(v, n, c):
    w = [F(0)] * (1 << (n + 1))
    for S in range(1 << n):
        w[S] = F(v[S]); w[S | (1 << n)] = F(v[S]) + F(c)
    return w, n + 1


def exact_float(g):
    vf = [float(x) for x in g.v]
    ve = core_min_all(g.n, vf)
    return ve is not None and all(abs(ve[S] - vf[S]) < 1e-7 for S in range(1, (1 << g.n) - 1))


def undominated_float(g, y):
    vf = [float(x) for x in g.v]; n, N = g.n, g.N
    if in_core_float(vf, n, N, [float(a) for a in y]):
        return False, "in core"
    dom = is_dominated_float(vf, n, N, [float(a) for a in y], _core_rows(vf, n, N))
    return (not dom), ("undominated" if not dom else "dominated")


for tag, (v, esc) in ESC.items():
    g5 = Game(5, [F(x) for x in v])
    okf, why = undominated_float(g5, esc)
    print(f"{tag} BASE n=5: escape {[str(x) for x in esc]} float:{why}", flush=True)
    for c in (0, 1):
        v6, n6 = pad([F(x) for x in v], 5, c)
        g6 = Game(n6, v6)
        es6, _ = is_ES(g6)
        ex6 = exact_float(g6)
        y6 = list(esc) + [F(c)]
        okf, why = undominated_float(g6, y6)
        print(f"  pad c={c} n=6: exact={ex6} ES={es6} v(N)={g6.v[g6.N]} | "
              f"lifted y={[str(x) for x in y6]} float:{why}", flush=True)
        if okf:
            cert = certify_undominated(g6, y6)   # exact certification
            print(f"    EXACT CERT: imputation={is_imputation(g6,y6)} in_core={in_core(g6,y6)} "
                  f"undominated={cert is not None} "
                  f"blocking={cert['blocking_coalitions'] if cert else None} "
                  f"=> padded core NOT vNM-stable", flush=True)
print("DONE", flush=True)

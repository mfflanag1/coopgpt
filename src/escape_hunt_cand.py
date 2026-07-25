"""Hunt an undominated escape for prove-stES's two surviving non-ES candidates
(potential stable-core counterexamples). Exact certification throughout.

Strategies, in order:
 1. single-strip y^j = gamma - e*e_j for every j with gamma_j>=e.
 2. multi-strip: lower any SUBSET of players (greedy to floor 0) to absorb e -> all
    such vertices (like theorem_test.candidates but over ALL players, all orders).
 3. general efficient vertex below gamma: choose players to drop to 0, rest at claim,
    one partial -> enumerate all.
Each candidate y: exact-check imputation, outside core, undominated (is_dominated_by_core).
"""
import itertools, sys
from fractions import Fraction as F
from tugame import Game
from eshunt import egalitarian_procedure, is_ES
from pes import pes
from core_stability import is_dominated_by_core, in_core, is_imputation

CAND1 = [0,1,0,2,0,1,1,2,0,2,0,2,1,2,1,3,1,3,1,3,2,4,2,4,1,3,1,3,2,4,2,4,0,1,1,2,0,1,1,2,1,2,2,3,1,2,2,3,3,4,3,5,3,4,4,5,3,5,3,5,4,5,4,6]
CAND2 = [0,1,0,2,1,2,2,3,1,2,2,3,2,3,3,4,1,3,1,4,3,4,3,5,3,4,3,5,4,5,5,6,0,3,0,3,2,4,2,5,2,4,2,5,4,5,4,6,1,4,1,4,3,6,3,6,3,6,3,6,5,7,5,8]


def test_escape(g, y):
    if not is_imputation(g, y) or in_core(g, y):
        return False
    dom, _ = is_dominated_by_core(g, y)
    return not dom


def hunt(g, label):
    n, N = g.n, g.N
    gamma, A, k, Nadm = egalitarian_procedure(g)
    es, _ = is_ES(g)
    p, D = pes(g)
    e = sum(gamma) - g.v[N]
    M = [g.v[N] - g.v[N ^ (1 << i)] for i in range(n)]
    print(f"\n### {label}: ES={es} v(N)={g.v[N]} claims={[str(x) for x in gamma]} e={e} "
          f"D={[i for i in range(n) if D>>i&1]} M={[str(x) for x in M]}", flush=True)
    if e <= 0:
        print("  e<=0, ES game, skip", flush=True); return None
    # 1. single strips
    for j in range(n):
        if gamma[j] >= e:
            y = list(gamma); y[j] = gamma[j] - e
            if test_escape(g, y):
                print(f"  SINGLE-STRIP ESCAPE j={j}: y={[str(x) for x in y]}", flush=True)
                return y
    print("  no single-strip escape", flush=True)
    # 2/3. subset drops to vertex (all subsets, all orders) absorbing e
    players = list(range(n))
    found = []
    for r in range(1, n):
        for combo in itertools.permutations(players, r):
            y = list(gamma); rem = e
            for jj in combo:
                take = min(y[jj], rem); y[jj] -= take; rem -= take
            if rem != 0:
                continue
            if test_escape(g, y):
                found.append(y)
        if found:
            print(f"  SUBSET-VERTEX ESCAPE (|drop|={r}) e.g. y={[str(x) for x in found[0]]}", flush=True)
            return found[0]
    print("  no subset-vertex escape (strategies 1-3 exhausted)", flush=True)
    return None


if __name__ == "__main__":
    for label, v in [("cand1", CAND1), ("cand2", CAND2)]:
        g = Game(6, [F(x) for x in v])
        y = hunt(g, label)
        if y is None:
            print(f"{label}: NO ESCAPE from constructions 1-3 -> HIGH-VALUE failure case", flush=True)
        else:
            print(f"{label}: ESCAPE FOUND -> candidate DIES", flush=True)

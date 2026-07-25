"""Find non-ES n=6 games where the claims-zeroing construction FAILS to produce an
undominated escape but a broad float search DOES, and dump the escape structure
(claims, strong set D, core-max M, which players are reduced / at ceiling / over claim)
so we can generalize the construction.
"""
import random
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from eshunt import is_ES, egalitarian_procedure
from pes import pes
from core_stability import is_dominated_by_core, in_core, is_imputation
from theorem_test import candidates, rand_nonES_game
from stability_float import find_escape_float, is_dominated_float, in_core_float, _core_rows


def construction_escape(g):
    vf = [float(x) for x in g.v]; n, N = g.n, g.N
    base = _core_rows(vf, n, N)
    for y in candidates(g):
        if in_core_float(vf, n, N, [float(a) for a in y]):
            continue
        if not is_dominated_float(vf, n, N, [float(a) for a in y], base):
            dom, _ = is_dominated_by_core(g, y)
            if not dom:
                return y
    return None


def float_escape_exact(g):
    vf = [float(x) for x in g.v]; n, N = g.n, g.N
    yf = find_escape_float(vf, n, N, tries=60000, seed=3)
    if yf is None:
        return None
    for D in (1, 2, 3, 4, 6, 12, 24):
        yq = [F(round(a * D), D) for a in yf]
        yq[n - 1] += g.v[N] - sum(yq)
        if any(a < 0 for a in yq):
            continue
        if is_imputation(g, yq) and not in_core(g, yq):
            dom, _ = is_dominated_by_core(g, yq)
            if not dom:
                return yq
    return None


if __name__ == "__main__":
    rng = random.Random(101)
    found = 0
    for t in range(2000):
        g = rand_nonES_game(rng, 6)
        if not is_balanced_game(g):
            continue
        es, _ = is_ES(g)
        if es:
            continue
        if construction_escape(g) is not None:
            continue
        # construction failed; get a float escape
        y = float_escape_exact(g)
        if y is None:
            print(f"!!! NEITHER construction NOR float found escape: v={[str(x) for x in g.v]}", flush=True)
            continue
        gamma, A, k, Nadm = egalitarian_procedure(g)
        p, D = pes(g)
        n, N = g.n, g.N
        M = [g.v[N] - g.v[N ^ (1 << i)] for i in range(n)]
        strong = [i for i in range(n) if D >> i & 1]
        print(f"\n--- construction FAIL case #{found} ---", flush=True)
        print(f" v={[str(x) for x in g.v]}", flush=True)
        print(f" claims gamma={[str(x) for x in gamma]}  strong D={strong}  M(core-max)={[str(x) for x in M]}", flush=True)
        print(f" float escape y={[str(x) for x in y]}", flush=True)
        rel = []
        for i in range(n):
            tags = []
            if y[i] == 0: tags.append("zero")
            if y[i] == M[i]: tags.append("ceiling(=M)")
            if y[i] > gamma[i]: tags.append("ABOVE claim")
            if y[i] == gamma[i]: tags.append("=claim")
            if 0 < y[i] < gamma[i]: tags.append("reduced")
            rel.append(f"p{i}:{'/'.join(tags) or '?'}")
        print(f" per-player: {rel}", flush=True)
        found += 1
        if found >= 5:
            break
    print(f"\ndone, construction-fail cases examined: {found}", flush=True)

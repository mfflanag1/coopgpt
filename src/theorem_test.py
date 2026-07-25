"""Adversarial test of the conjecture  STABLE core => ES  (equivalently
non-ES => core not vNM-stable) at n=6, where it is NOT automatic (stable<=>large
only holds for n<=5).

For each non-ES game we build the CANDIDATE ESCAPE via the construction extracted
from the n=5 witnesses:
  take egalitarian claims gamma; keep the strong claimants D at full claim; absorb
  the excess e = sum(gamma)-v(N) by reducing NON-strong players to a simplex vertex
  (greedily to 0). Test whether the resulting imputation is UNDOMINATED by the core.
If undominated (exact-certified) => core not stable => theorem holds for this game.
If the construction fails, fall back to a broad float escape search. If NOTHING is
found => FLAG as a potential stable + non-ES counterexample and dump it.
"""
import random, itertools, sys, json
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from eshunt import is_ES, egalitarian_procedure
from pes import pes
from core_stability import is_dominated_by_core, in_core, is_imputation
from stability_float import find_escape_float, is_dominated_float, in_core_float, _core_rows


def candidates(g):
    """Yield candidate escape imputations (exact) from the claims-vertex construction."""
    n, N = g.n, g.N
    gamma, A, k, Nadm = egalitarian_procedure(g)
    p, D = pes(g)
    nonstrong = [i for i in range(n) if not (D >> i & 1)]
    e = sum(gamma) - g.v[N]
    if e <= 0:
        return
    seen = set()
    # reduce non-strong players (in every order) to 0 to absorb the excess e
    for r in range(1, len(nonstrong) + 1):
        for combo in itertools.permutations(nonstrong, r):
            y = list(gamma); rem = e
            for j in combo:
                take = min(y[j], rem); y[j] -= take; rem -= take
            if rem != 0:
                continue
            ty = tuple(y)
            if ty in seen:
                continue
            seen.add(ty)
            if is_imputation(g, y) and not in_core(g, y):
                yield y


def stability_via_construction(g):
    """Return (escape or None, method). Float-screen candidates, exact-certify a hit."""
    vf = [float(x) for x in g.v]; n, N = g.n, g.N
    base = _core_rows(vf, n, N)
    for y in candidates(g):
        yf = [float(a) for a in y]
        if in_core_float(vf, n, N, yf):
            continue
        if not is_dominated_float(vf, n, N, yf, base):     # float says undominated
            dom, _ = is_dominated_by_core(g, y)            # exact confirm
            if not dom:
                return y, "construction"
    # fallback: broad random float escape search + exact certify
    yf = find_escape_float(vf, n, N, tries=40000, seed=1)
    if yf is not None:
        from fractions import Fraction as FF
        for D in (1, 2, 3, 4, 6, 12):
            yq = [FF(round(a * D), D) for a in yf]
            yq[n - 1] += g.v[N] - sum(yq)
            if any(a < 0 for a in yq):
                continue
            if is_imputation(g, yq) and not in_core(g, yq):
                dom, _ = is_dominated_by_core(g, yq)
                if not dom:
                    return yq, "float"
    return None, "none"


def rand_nonES_game(rng, n=6, hi=3):
    v = [F(0)] * (1 << n)
    for S in range(1, 1 << n):
        mem = [i for i in range(n) if S >> i & 1]
        if len(mem) == 1:
            v[S] = F(0)
        else:
            base = max((v[S ^ (1 << i)] for i in mem), default=F(0))
            v[S] = base + F(rng.randint(0, hi))
    return Game(n, v)


if __name__ == "__main__":
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    rng = random.Random(seed)
    tested = nonES = nonstable = flagged = 0
    by_method = {"construction": 0, "float": 0}
    for t in range(trials):
        g = rand_nonES_game(rng, 6)
        if not is_balanced_game(g):
            continue
        es, _ = is_ES(g)
        if es:
            continue
        nonES += 1
        esc, method = stability_via_construction(g)
        if esc is not None:
            nonstable += 1
            by_method[method] = by_method.get(method, 0) + 1
        else:
            flagged += 1
            print(f"*** FLAG potential stable+nonES: v={[str(x) for x in g.v]}", flush=True)
            with open(f"/Users/maxf/projects/counterexample-hunt/coopgames/results/FLAG_stable_nonES_{seed}_{t}.json", "w") as f:
                json.dump({"v": [str(x) for x in g.v], "n": 6}, f)
    print(f"seed={seed} nonES={nonES} non_stable(theorem holds)={nonstable} "
          f"by_method={by_method} FLAGGED(potential counterex)={flagged}", flush=True)

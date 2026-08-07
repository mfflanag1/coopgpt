"""Decide PARTITION configurations exactly, using the facet description of the
cone of exact games.

The cone of exact games on n <= 6 players is cut out by the indecomposable
min-semi-balanced systems of the Studeny-Kratochvil catalogue: writing a
system as sum_{S proper} lambda_S chi_S = r chi_N with a single negative
coefficient, LP duality for min_{x in core} x(T) gives

        v is exact   <=>   sum_{S proper} lambda_S v(S)  <=  r * v(N)

for every system and every permutation of it.  (Validated below on random
exact and non-exact games.)

That turns "is there an exact game with this tight/slack/stratification
pattern?" into a rational LP.  Everything is homogeneous, so the slack is
normalized to 1.  NOTE the LP is a RELAXATION: it does not impose phi = Lmin,
only phi in the core with the required strict stratification.  Hence
INFEASIBLE is a proof of impossibility, while feasible is inconclusive.

Usage: python3 exactcone.py validate
       python3 exactcone.py part N p q      (decide PART(p,q) on n players)
"""
from __future__ import annotations

import itertools
import json
import random
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad")

import audit
import catalogue
import z3

BASE = "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/census7/zp"


def nm(n, mask):
    return "".join("abcdefg"[i] for i in range(n) if mask >> i & 1) or "0"


def systems(n):
    """All permuted catalogue systems as (lam dict, r), deduplicated."""
    rows = catalogue.load(n)[1]
    out = {}
    for row in rows:
        for perm in itertools.permutations(range(n)):
            lam = {}
            for S, c in row["lam"].items():
                S2 = sum(1 << perm[i] for i in range(n) if S >> i & 1)
                lam[S2] = c
            key = tuple(sorted(lam.items()))
            out[key] = row["r"]
    return [(dict(k), r) for k, r in out.items()]


def validate(n=5, trials=300, seed=0, converse_trials=20):
    sysd = systems(n)
    print(f"n={n}: {len(sysd)} permuted facet inequalities")
    rng = random.Random(seed)
    FULL = (1 << n) - 1
    bad_exact = bad_nonexact = 0
    n_ex = n_non = 0
    for _ in range(trials):
        total = rng.randint(n, 20)
        gens = audit.rand_gens(n, rng, rng.randint(2, 4), total, total)
        v = audit.envelope(n, gens)
        w, _ = audit.normalize(n, v)
        if w[FULL] <= 0:
            continue
        n_ex += 1
        for lam, r in sysd:
            lhs = sum(c * w[S] for S, c in lam.items())
            if lhs > r * w[FULL]:
                bad_exact += 1
                break
        # a perturbed (generally non-exact) game: bump one coalition up.
        # The converse direction is checked at n=5 only: deciding exactness by
        # definition needs core-vertex enumeration, which is exponential and is
        # never run at n=6 in this campaign.
        if n > 5 or n_non >= converse_trials:
            continue
        w2 = list(w)
        S0 = rng.randrange(1, FULL)
        w2[S0] += F(1)
        if audit.is_exact(n, w2):
            continue
        n_non += 1
        viol = False
        for lam, r in sysd:
            lhs = sum(c * w2[S] for S, c in lam.items())
            if lhs > r * w2[FULL]:
                viol = True
                break
        if not viol:
            bad_nonexact += 1
    print(f"  exact games tested {n_ex}, violating a facet inequality: "
          f"{bad_exact}  (must be 0)")
    print(f"  non-exact games tested {n_non}, satisfying ALL of them: "
          f"{bad_nonexact}  (must be 0)")
    return bad_exact == 0 and bad_nonexact == 0


def decide_partition(n, p, q, timeout_s=600):
    """Is there an exact normalized game with a strict h=2 boundary H={f,g},
    slack there, and complementary tight sets A (p poorer + f), B (q poorer
    + g)?  Returns (status, model_or_None)."""
    assert p + q == n - 2, (p, q, n)
    FULL = (1 << n) - 1
    # layout: poorer 0..n-3 (first p in A, next q in B), f = n-2, g = n-1
    f, g = n - 2, n - 1
    P = list(range(p))
    Q = list(range(p, p + q))
    A = sum(1 << i for i in P) | (1 << f)
    B = sum(1 << i for i in Q) | (1 << g)
    H = (1 << f) | (1 << g)
    assert A | B == FULL and A & B == 0

    v = {S: z3.Real(f"v{S}") for S in range(1, FULL + 1)}
    phi = [z3.Real(f"p{i}") for i in range(n)]
    s = z3.Solver()
    s.set("timeout", int(timeout_s * 1000))
    for i in range(n):
        s.add(v[1 << i] == 0)                       # singleton-normalized
    for i in range(n):
        s.add(phi[i] >= 0)
    s.add(z3.Sum(phi) == v[FULL])
    for S in range(1, FULL):
        s.add(z3.Sum([phi[i] for i in range(n) if S >> i & 1]) >= v[S])
    # exact cone
    for lam, r in systems(n):
        s.add(z3.Sum([c * v[S] for S, c in lam.items()]) <= r * v[FULL])
    # tightness of the complementary pair
    s.add(z3.Sum([phi[i] for i in range(n) if A >> i & 1]) == v[A])
    s.add(z3.Sum([phi[i] for i in range(n) if B >> i & 1]) == v[B])
    # H is slack; scale is free, so normalize the slack to 1
    s.add(z3.Sum([phi[i] for i in range(n) if H >> i & 1]) == v[H] + 1)
    # H is a STRICT richer suffix: every poorer player is strictly below both
    for i in range(n - 2):
        s.add(phi[i] < phi[f])
        s.add(phi[i] < phi[g])
    t0 = time.time()
    res = s.check()
    el = round(time.time() - t0, 1)
    if res == z3.sat:
        mdl = s.model()
        out = {"phi": [str(audit.rat(mdl.eval(phi[i], model_completion=True)))
                       for i in range(n)],
               "v": {nm(n, S): str(audit.rat(mdl.eval(v[S],
                                                      model_completion=True)))
                     for S in range(1, FULL + 1)}}
        return "SAT", out, el
    if res == z3.unsat:
        return "UNSAT", None, el
    return "UNKNOWN", None, el


def main():
    if sys.argv[1] == "validate":
        ok5 = validate(5)
        ok6 = validate(6, trials=60)
        print("characterization validated:", ok5 and ok6)
        return
    if sys.argv[1] == "part":
        n, p, q = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        status, mdl, el = decide_partition(n, p, q)
        print(f"PART({p},{q}) on n={n}: {status}  ({el}s)")
        if mdl:
            print("  phi =", mdl["phi"])
        json.dump({"n": n, "p": p, "q": q, "status": status, "model": mdl,
                   "elapsed": el},
                  open(f"{BASE}/part_{n}_{p}_{q}.json", "w"), indent=1)


if __name__ == "__main__":
    main()

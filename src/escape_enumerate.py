"""Deterministic search for an undominated imputation outside the core
(=> core NOT vNM-stable). Candidate points: vertices of the arrangement inside
the imputation simplex cut by the coalition hyperplanes y(S)=v(S) and the
non-negativity hyperplanes y_i=v({i}). At an escaping vertex several such
constraints are tight. Enumerate combos, solve exactly, filter to
(imputation & outside core), then test undomination with the exact domination LP.
"""
import itertools, sys
from fractions import Fraction as F
from tugame import Game
from largeness_exact import exact_solve
from stability_float import find_escape_float
from core_stability import (in_core, is_imputation, is_dominated_by_core,
                            dominated_via, certify_undominated)


def enumerate_escape(v, n, verbose=True):
    N = (1 << n) - 1
    g = Game(n, [F(x) for x in v])
    vN = g.v[N]
    # hyperplanes: (incidence_row, rhs). coalition S -> (1_S, v(S)); player i -> (e_i, v({i}))
    planes = []
    for S in range(1, N):                       # proper coalitions
        planes.append(([1 if S >> i & 1 else 0 for i in range(n)], F(v[S]), ('S', S)))
    for i in range(n):                          # nonneg (singleton value)
        row = [0] * n; row[i] = 1
        planes.append((row, g.v[1 << i], ('x', i)))
    eff = ([1] * n, vN)                         # efficiency (always tight)
    seen = set()
    cand = 0
    # a vertex in the (n-1)-dim imputation plane needs n-1 more tight planes
    for combo in itertools.combinations(range(len(planes)), n - 1):
        M = [planes[j][0] for j in combo] + [eff[0]]
        b = [planes[j][1] for j in combo] + [eff[1]]
        y = exact_solve([r[:] for r in M], b[:], n)
        if y is None:
            continue
        key = tuple(y)
        if key in seen:
            continue
        seen.add(key)
        if not is_imputation(g, y):
            continue
        if in_core(g, y):
            continue
        cand += 1
        # exact undomination test
        dom, _ = is_dominated_by_core(g, y)
        if not dom:
            cert = certify_undominated(g, y)
            if cert:
                if verbose:
                    print(f"  ESCAPING IMPUTATION y={cert['y']} blocking={cert['blocking_coalitions']}", flush=True)
                return g, y
    if verbose:
        print(f"  no arrangement-vertex escape (candidates tested={cand}). Trying float fine search...", flush=True)
    # fallback: dense float search then exact certify
    yf = find_escape_float([float(x) for x in g.v], n, N, tries=400000, seed=7)
    if yf is not None:
        yq = [F(a).limit_denominator(360) for a in yf]
        if is_imputation(g, yq) and not in_core(g, yq):
            dom, _ = is_dominated_by_core(g, yq)
            if not dom:
                print(f"  ESCAPING (float->exact) y={[str(a) for a in yq]}", flush=True)
                return g, yq
        print("  float candidate failed exact certification", flush=True)
    return g, None


if __name__ == "__main__":
    WIT_VN4 = [0,0,0,0,0,1,1,1,1,1,1,1,2,2,2,2,0,1,1,2,0,1,1,2,2,3,3,3,2,3,3,4]
    BASE_VN6 = [0,0,0,0,3,3,3,3,0,0,0,0,4,4,4,4,0,0,0,0,4,5,5,5,0,0,0,0,4,5,5,6]
    for tag, v in [("vN4", WIT_VN4), ("vN6", BASE_VN6)]:
        print(f"=== {tag} escape enumeration ===", flush=True)
        g, y = enumerate_escape(v, 5)
        print(f"  {tag}: {'NON-STABLE core (escape found)' if y else 'no escape found (candidate STABLE?)'}", flush=True)

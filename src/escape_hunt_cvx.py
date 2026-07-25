"""Strategy 4 for the two surviving candidates: escapes on CORE-VERTEX-COORDINATE
planes (prove-stES caveat). Enumerate the candidate's core vertices exactly, collect
the multiset of coordinate values V that occur, then search efficient imputations whose
coordinates are drawn from V (plus 0 and gamma_j - partials) for an undominated one.
"""
import itertools, sys
from fractions import Fraction as F
from tugame import Game, exact_lp_min
from eshunt import egalitarian_procedure
from core_stability import is_dominated_by_core, in_core, is_imputation
from largeness_exact import exact_solve

CAND1 = [0,1,0,2,0,1,1,2,0,2,0,2,1,2,1,3,1,3,1,3,2,4,2,4,1,3,1,3,2,4,2,4,0,1,1,2,0,1,1,2,1,2,2,3,1,2,2,3,3,4,3,5,3,4,4,5,3,5,3,5,4,5,4,6]
CAND2 = [0,1,0,2,1,2,2,3,1,2,2,3,2,3,3,4,1,3,1,4,3,4,3,5,3,4,3,5,4,5,5,6,0,3,0,3,2,4,2,5,2,4,2,5,4,5,4,6,1,4,1,4,3,6,3,6,3,6,3,6,5,7,5,8]


def core_vertices(g):
    """Enumerate exact core vertices: bases of n tight constraints among {x(S)=v(S)} and
    efficiency, solved exactly, kept if in core."""
    n, N = g.n, g.N
    planes = [([1 if S >> i & 1 else 0 for i in range(n)], F(g.v[S])) for S in range(1, N)]
    eff = ([1] * n, g.v[N])
    verts = set()
    for combo in itertools.combinations(range(len(planes)), n - 1):
        M = [planes[j][0] for j in combo] + [eff[0]]
        b = [planes[j][1] for j in combo] + [eff[1]]
        x = exact_solve([r[:] for r in M], b[:], n)
        if x is None:
            continue
        if any(sum(x[i] for i in range(n) if S >> i & 1) < g.v[S] for S in range(1, N)):
            continue
        if sum(x) != g.v[N]:
            continue
        verts.add(tuple(x))
    return [list(v) for v in verts]


def hunt_cvx(g, label, maxcombo=200000):
    n, N = g.n, g.N
    gamma, A, k, Nadm = egalitarian_procedure(g)
    verts = core_vertices(g)
    coords = sorted(set(x[i] for x in verts for i in range(n)) | {F(0)} | set(gamma))
    print(f"### {label}: #core_vertices={len(verts)} #distinct_coord_values={len(coords)} vN={g.v[N]}", flush=True)
    # search efficient imputations with coords in `coords`: fix n-1 coords from `coords`,
    # last = residual; check imputation/outside-core/undominated.
    tried = 0
    import random
    rng = random.Random(0)
    vals = coords
    for _ in range(maxcombo):
        y = [rng.choice(vals) for _ in range(n - 1)]
        last = g.v[N] - sum(y)
        y = y + [last]
        if any(a < 0 for a in y):
            continue
        if not is_imputation(g, y) or in_core(g, y):
            continue
        tried += 1
        dom, _ = is_dominated_by_core(g, y)
        if not dom:
            print(f"  CORE-VERTEX-COORD ESCAPE: y={[str(a) for a in y]}", flush=True)
            return y
    print(f"  no core-vertex-coord escape ({tried} imputations tested)", flush=True)
    return None


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    data = {"cand1": CAND1, "cand2": CAND2}
    for label in (["cand1", "cand2"] if which == "both" else [which]):
        g = Game(6, [F(x) for x in data[label]])
        y = hunt_cvx(g, label)
        print(f"{label}: {'ESCAPE (candidate DIES)' if y else 'still NO escape'}", flush=True)

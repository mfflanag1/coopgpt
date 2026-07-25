"""Broad float escape search over the WHOLE imputation space for cand1/cand2,
with exact certification. Complements structured enumerations (which missed escapes
if any). If an exact undominated escape is found -> candidate DIES.
"""
import sys, random
from fractions import Fraction as F
from tugame import Game
from core_stability import is_dominated_by_core, in_core, is_imputation
from stability_float import find_escape_float, is_dominated_float, in_core_float, _core_rows

CAND1 = [0,1,0,2,0,1,1,2,0,2,0,2,1,2,1,3,1,3,1,3,2,4,2,4,1,3,1,3,2,4,2,4,0,1,1,2,0,1,1,2,1,2,2,3,1,2,2,3,3,4,3,5,3,4,4,5,3,5,3,5,4,5,4,6]
CAND2 = [0,1,0,2,1,2,2,3,1,2,2,3,2,3,3,4,1,3,1,4,3,4,3,5,3,4,3,5,4,5,5,6,0,3,0,3,2,4,2,5,2,4,2,5,4,5,4,6,1,4,1,4,3,6,3,6,3,6,3,6,5,7,5,8]


def certify(g, yf):
    n, N = g.n, g.N
    for D in (1, 2, 3, 4, 6, 8, 12, 24, 60, 120):
        yq = [F(round(a * D), D) for a in yf]
        yq[n - 1] += g.v[N] - sum(yq)
        if any(a < 0 for a in yq):
            continue
        if is_imputation(g, yq) and not in_core(g, yq):
            dom, _ = is_dominated_by_core(g, yq)
            if not dom:
                return yq
    return None


def hunt(label, v, budget=400000):
    g = Game(6, [F(x) for x in v])
    vf = [float(x) for x in g.v]; n, N = g.n, g.N
    for seed in range(6):
        yf = find_escape_float(vf, n, N, tries=budget, seed=seed)
        if yf is None:
            print(f"{label} seed={seed}: float found no escape", flush=True)
            continue
        yq = certify(g, yf)
        if yq is not None:
            print(f"{label}: EXACT ESCAPE FOUND -> candidate DIES: y={[str(a) for a in yq]}", flush=True)
            return yq
        print(f"{label} seed={seed}: float escape did not certify exactly (rounding); retrying", flush=True)
    print(f"{label}: NO certified escape from {6}x{budget} float search", flush=True)
    return None


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    data = {"cand1": CAND1, "cand2": CAND2}
    for label in (["cand1", "cand2"] if which == "both" else [which]):
        hunt(label, data[label])

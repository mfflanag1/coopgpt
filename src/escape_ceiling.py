"""Strategy 5: CEILING-PINNED vertex escapes for cand1/cand2.
Pin a subset B of players at their core-max M_i (undominatable: no core x exceeds M_i),
requires sum_{B} M_i <= v(N). Distribute the remainder r=v(N)-sum_B M_i over the other
players as a vertex (all subsets to receive it, rest at 0), and exact-test undomination.
A pinned set B blocks any dominating coalition meeting B, so escapes live here.
"""
import itertools, sys
from fractions import Fraction as F
from tugame import Game
from core_stability import is_dominated_by_core, in_core, is_imputation

CAND1 = [0,1,0,2,0,1,1,2,0,2,0,2,1,2,1,3,1,3,1,3,2,4,2,4,1,3,1,3,2,4,2,4,0,1,1,2,0,1,1,2,1,2,2,3,1,2,2,3,3,4,3,5,3,4,4,5,3,5,3,5,4,5,4,6]
CAND2 = [0,1,0,2,1,2,2,3,1,2,2,3,2,3,3,4,1,3,1,4,3,4,3,5,3,4,3,5,4,5,5,6,0,3,0,3,2,4,2,5,2,4,2,5,4,5,4,6,1,4,1,4,3,6,3,6,3,6,3,6,5,7,5,8]


def hunt(label, v):
    g = Game(6, [F(x) for x in v]); n, N = g.n, g.N
    M = [g.v[N] - g.v[N ^ (1 << i)] for i in range(n)]
    print(f"### {label}: M={[str(x) for x in M]} vN={g.v[N]}", flush=True)
    tested = 0
    for bsize in range(1, n):
        for B in itertools.combinations(range(n), bsize):
            sumB = sum(M[i] for i in B)
            if sumB > g.v[N]:
                continue
            rest = [i for i in range(n) if i not in B]
            r = g.v[N] - sumB
            # distribute r over `rest` as vertices: put r on subsets, others 0, one partial
            for rr in range(1, len(rest) + 1):
                for combo in itertools.permutations(rest, rr):
                    y = [F(0)] * n
                    for i in B:
                        y[i] = F(M[i])
                    rem = r
                    for j in combo:
                        take = min(F(M[j]), rem); y[j] = take; rem -= take
                    if rem != 0:
                        continue
                    if not is_imputation(g, y) or in_core(g, y):
                        continue
                    tested += 1
                    dom, _ = is_dominated_by_core(g, y)
                    if not dom:
                        print(f"  CEILING-PINNED ESCAPE: B={B} y={[str(a) for a in y]}", flush=True)
                        return y
    print(f"  no ceiling-pinned escape ({tested} imputations tested)", flush=True)
    return None


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    data = {"cand1": CAND1, "cand2": CAND2}
    for label in (["cand1", "cand2"] if which == "both" else [which]):
        y = hunt(label, data[label])
        print(f"{label}: {'ESCAPE (candidate DIES)' if y else 'NO ceiling-pinned escape'}", flush=True)

"""Generate per-coalition exactness witnesses (core point attaining each proper
coalition) for cand1/cand2, for the paper-2 supplement."""
import sys, json
from fractions import Fraction as F
sys.path.insert(0, "src")
from tugame import Game
from lemD import xS
from exactlp import exact_lp_min

CANDS = {
 "cand1": [0,1,0,2,0,1,1,2,0,2,0,2,1,2,1,3,1,3,1,3,2,4,2,4,1,3,1,3,2,4,2,4,0,1,1,2,0,1,1,2,1,2,2,3,1,2,2,3,3,4,3,5,3,4,4,5,3,5,3,5,4,5,4,6],
 "cand2": [0,1,0,2,1,2,2,3,1,2,2,3,2,3,3,4,1,3,1,4,3,4,3,5,3,4,3,5,4,5,5,6,0,3,0,3,2,4,2,5,2,4,2,5,4,5,4,6,1,4,1,4,3,6,3,6,3,6,3,6,5,7,5,8],
}
n = 6; N = 63

def coname(S):
    return "{" + ",".join(str(i+1) for i in range(n) if S >> i & 1) + "}"

out = {}
for name, VV in CANDS.items():
    v = [F(x) for x in VV]
    wit = {}
    for T in range(1, N):
        A_ub, b_ub = [], []
        for U in range(1, N):
            A_ub.append([-1 if U >> i & 1 else 0 for i in range(n)]); b_ub.append(-v[U])
        A_eq = [[1]*n]; b_eq = [v[N]]
        c = [1 if T >> i & 1 else 0 for i in range(n)]   # minimize x(T)
        opt, x = exact_lp_min(c, A_ub, b_ub, A_eq, b_eq)
        assert opt == v[T], f"{name} {coname(T)}: min={opt} != v={v[T]}"
        assert sum(x) == v[N] and all(xS(x, U, n) >= v[U] for U in range(1, N))
        wit[coname(T)] = [str(u) for u in x]
    out[name] = wit
    print(f"{name}: 62 witnesses done", flush=True)
json.dump(out, open("results/cand_exactness_witnesses.json", "w"), indent=1)
print("written")

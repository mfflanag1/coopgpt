"""Generate the complete machine-readable certificate supplement for the paper.

Produces certificates.json containing, for every computational theorem:
  - full game tables (coalition -> worth),
  - exactness witnesses (per proper coalition, a core point attaining its worth),
  - solution points,
  - full satisfaction / excess tables,
  - cumulative level-set balancing weights at EVERY threshold
    (lower sets for SD-Kohlberg, upper sets for classical Kohlberg).

Run from paper/supplement/. Requires ../../src on sys.path.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
from fractions import Fraction as F
from tugame import Game, exact_lp_min, members
from sd import sd_satisfactions
from nucleolus import certified_prenucleolus
from permutation import permutation_game

def coname(S, n):
    return "{" + ",".join(str(i + 1) for i in members(S, n)) + "}"

def game_table(g):
    return {coname(S, g.n): str(g.v[S]) for S in range(1, g.N + 1)}

def exactness_witnesses(g):
    """For each proper S: a core point x with x(S) = v(S) (min x(S) over core)."""
    n, N = g.n, g.N
    A_ub = [[-1 if T >> i & 1 else 0 for i in range(n)] for T in range(1, N)]
    b_ub = [-g.v[T] for T in range(1, N)]
    A_eq = [[1] * n]; b_eq = [g.v[N]]
    out = {}
    for S in range(1, N):
        c = [1 if S >> i & 1 else 0 for i in range(n)]
        opt, x = exact_lp_min(c, A_ub, b_ub, A_eq, b_eq)
        assert opt is not None and opt == g.v[S], (coname(S, n), opt, g.v[S])
        out[coname(S, n)] = [str(u) for u in x]
    return out

def positive_weights(coalitions, n):
    m = len(coalitions)
    c = [0] * m + [-1]
    A_eq = [[1 if S >> i & 1 else 0 for S in coalitions] + [0] for i in range(n)]
    b_eq = [1] * n
    A_ub, b_ub = [], []
    for j in range(m):
        row = [0] * (m + 1); row[j] = -1; row[m] = 1
        A_ub.append(row); b_ub.append(0)
        row2 = [0] * (m + 1); row2[j] = -1
        A_ub.append(row2); b_ub.append(0)
    opt, sol = exact_lp_min(c, A_ub, b_ub, A_eq, b_eq)
    assert opt is not None and -opt > 0, "collection not balanced with positive weights"
    return {coname(S, n): str(sol[j]) for j, S in enumerate(coalitions)}

def sd_certificate(g, x):
    Fx = sd_satisfactions(g, x)
    table = {coname(S, g.n): str(val) for S, val in Fx.items()}
    cumulative = []
    for alpha in sorted(set(Fx.values())):
        D = [S for S, val in Fx.items() if val <= alpha]
        cumulative.append({"threshold": str(alpha),
                           "lower_set": [coname(S, g.n) for S in sorted(D)],
                           "weights": positive_weights(D, g.n)})
    return {"point": [str(u) for u in x], "satisfactions": table,
            "cumulative_lower_sets": cumulative}

def nucleolus_certificate(g, x):
    exc = {S: g.excess(x, S) for S in range(1, g.N)}
    table = {coname(S, g.n): str(val) for S, val in exc.items()}
    cumulative = []
    for alpha in sorted(set(exc.values()), reverse=True):
        D = [S for S, val in exc.items() if val >= alpha]
        cumulative.append({"threshold": str(alpha),
                           "upper_set": [coname(S, g.n) for S in sorted(D)],
                           "weights": positive_weights(D, g.n)})
    return {"point": [str(u) for u in x], "excesses": table,
            "cumulative_upper_sets": cumulative}

out = {"_note": "All values exact rationals as strings. Player i in the paper = index i. "
                "Balancing weights are strictly positive and sum with indicator vectors to 1_N."}

# ---- Theorem 5.1 ----
v = [F(u) for u in "0 0 0 0 0 0 1 1 0 0 13 15 0 14 13 30".split()]
vp = list(v); vp[0b1101] += 1
g, gp = Game(4, v), Game(4, vp)
sd_v = [F(53,12), F(19,4), F(15,4), F(205,12)]
sd_vp = [F(35,8), F(33,8), F(33,8), F(139,8)]
out["theorem_5_1"] = {
    "game_v": game_table(g), "game_vprime": game_table(gp),
    "exactness_witnesses_v": exactness_witnesses(g),
    "exactness_witnesses_vprime": exactness_witnesses(gp),
    "SD_v": sd_certificate(g, sd_v),
    "SD_vprime": sd_certificate(gp, sd_vp),
}

# ---- Theorem 5.3 (SD-prekernel segment) ----
v = [F(u) for u in "0 5 6 20 2 10 8 22 5 12 14 25 12 17 18 32".split()]
g = Game(4, v)
mid = [F(19,2), F(21,2), F(9,2), F(15,2)]
def complaints(x):
    Fx = sd_satisfactions(g, x)
    vals = {}
    for i in range(4):
        for j in range(4):
            if i != j:
                vals[f"s_{i+1}{j+1}"] = str(min(val for S, val in Fx.items()
                                               if S >> i & 1 and not (S >> j & 1)))
    return vals
seg = {}
for tname, t in [("-1/2", F(-1,2)), ("-1/3", F(-1,3)), ("-1/4", F(-1,4)),
                 ("0", F(0)), ("1/4", F(1,4)), ("1/3", F(1,3)), ("1/2", F(1,2))]:
    x = [mid[0]+t, mid[1]-t, mid[2]-t, mid[3]+t]
    Fx = sd_satisfactions(g, x)
    seg[f"t={tname}"] = {"point": [str(u) for u in x],
                         "satisfactions": {coname(S,4): str(val) for S, val in Fx.items()},
                         "complaints": complaints(x)}
out["theorem_5_3"] = {
    "game": game_table(g),
    "exactness_witnesses": exactness_witnesses(g),
    "SD_midpoint": sd_certificate(g, mid),
    "segment_samples": seg,
}

# ---- Theorem 5.4 (population monotonicity; hand-proved, data for completeness) ----
vpm = [F(0)]*8; vpm[0b011] = F(1); vpm[0b110] = F(1); vpm[0b111] = F(2)
gpm = Game(3, vpm)
sub, mem = gpm.subgame(0b110)
out["theorem_5_4"] = {
    "game": game_table(gpm),
    "SD_full": sd_certificate(gpm, [F(1,3), F(4,3), F(1,3)]),
    "SD_subgame_23": {"players": [m+1 for m in mem],
                      "subgame": game_table(sub),
                      "certificate": sd_certificate(sub, [F(1,2), F(1,2)])},
}

# ---- Theorem 6.1 (permutation games) ----
K = [[0,7,0,0],[1,0,0,1],[1,0,0,0],[0,9,1,0]]
K2 = [r[:] for r in K]; K2[3][2] += 1
gK, gK2 = permutation_game(K), permutation_game(K2)
nuc_K = certified_prenucleolus(gK)
nuc_K2 = certified_prenucleolus(gK2)
assert nuc_K == [F(1,2), F(33,4), F(1,2), F(7,4)]
assert nuc_K2 == [F(2,3), F(23,3), F(1,3), F(7,3)]
sd_K = [F(1,2), F(17,2), F(1,2), F(3,2)]
sd_K2 = [F(3,4), F(31,4), F(1,4), F(9,4)]
out["theorem_6_1"] = {
    "matrix_K": K, "matrix_Kprime": K2,
    "game_K": game_table(gK), "game_Kprime": game_table(gK2),
    "nucleolus_K": nucleolus_certificate(gK, nuc_K),
    "nucleolus_Kprime": nucleolus_certificate(gK2, nuc_K2),
    "SD_K": sd_certificate(gK, sd_K),
    "SD_Kprime": sd_certificate(gK2, sd_K2),
}

# ---- Theorem 3.2 / Prop 7.5 data ----
base = [F(u) for u in "0 0 0 0 0 3 3 1 0 3 3 1 3 1 5 6".split()]
out["theorem_3_2"] = {
    "base": game_table(Game(4, base)),
    "core_witness_v_vA": ["1","1","2","2"], "core_witness_vB": ["0","0","3","3"],
    "farkas_multipliers_x13": {
        "core_v_{2,3}": "1", "core_vA_{1,2,3}": "1", "core_vA_{1,4}": "1",
        "core_vA_{2,4}": "1", "efficiency_vA": "2", "core_vB_{1,3}": "1",
        "core_vB_{1,4}": "1", "core_vB_{2,3,4}": "1", "efficiency_vB": "2",
        "mono_A_player3": "1", "mono_B_player2": "1"},
}
b5 = [F(0)]*15 + [F(5)]
gb5 = Game(4, b5)
prop75 = {"base": game_table(gb5), "exactness_witnesses_base": exactness_witnesses(gb5)}
for k in range(4):
    S = 15 ^ (1 << k)
    vv = list(b5); vv[S] += 4
    prop75[f"exactness_witnesses_t{k+1}"] = exactness_witnesses(Game(4, vv))
prop75["family_selection"] = {"theta_b": ["2","1","1","1"],
    "theta_t1": ["1","4/3","4/3","4/3"], "theta_t2": ["3","0","1","1"],
    "theta_t3": ["3","1","0","1"], "theta_t4": ["3","1","1","0"]}
out["proposition_7_5"] = prop75

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "certificates.json"), "w") as f:
    json.dump(out, f, indent=1)
print("certificates.json written:",
      sum(len(json.dumps(v)) for v in out.values()), "bytes of certificate data")

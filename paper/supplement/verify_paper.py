"""One-command exact verification of every computational claim in the paper.

    python3 verify_paper.py

SELF-CONTAINED: uses only the Python standard library (fractions, json).
The SD satisfaction recursion and all game logic are implemented inline;
balancedness of level sets is checked by pure rational arithmetic against the
SUPPLIED strictly positive weights, so no linear programming is needed.

Scope: verifies every certificate-backed claim of the computational
theorems. Two prose side-claims (non-exactness of the Theorem 3.2 games;
largeness of the eight exact cores) require linear programming and are
established by the paper's exact-LP pipeline instead.

Checks, for every computational theorem:
  - bump relations between the stated games,
  - exactness witnesses: coverage of ALL 2^n-2 proper coalitions, core
    membership, and attainment,
  - solution tables (SD satisfactions / nucleolus excesses) recomputed from
    scratch via the inline recursion,
  - cumulative level sets: equality with the recomputed threshold sets AND
    balancedness via the supplied positive weights, at every threshold,
  - class claims used in proofs (superadditivity, convexity/non-convexity),
  - the payoff-drop comparisons, complaint equalities, and family selections.
"""
import sys, os, json
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(HERE, "certificates.json")))
FAIL = []

# ---------------- inline TU-game machinery (stdlib only) ----------------
def members(S, n): return [i for i in range(n) if S >> i & 1]

def coname(S, n): return "{" + ",".join(str(i+1) for i in members(S, n)) + "}"

def parse_set(name):
    S = 0
    for p in name.strip("{}").split(","):
        S |= 1 << (int(p) - 1)
    return S

def parse_game(table, n):
    v = [F(0)] * (1 << n)
    for name, val in table.items():
        v[parse_set(name)] = F(val)
    return v

def xS(x, S, n): return sum(x[i] for i in range(n) if S >> i & 1)

def in_core(v, x, n):
    N = (1 << n) - 1
    return sum(x) == v[N] and all(xS(x, S, n) >= v[S] for S in range(1, N))

def sd_satisfactions(v, x, n):
    """Arin-Katsev SD recursion, exact."""
    N = (1 << n) - 1
    proper = list(range(1, N))
    fixed = {}
    while len(fixed) < len(proper):
        best, arg = None, []
        for S in proper:
            if S in fixed: continue
            fvals = {}
            for T, FT in fixed.items():
                if T & ~S == 0:
                    for i in members(T, n):
                        if i not in fvals or FT < fvals[i]:
                            fvals[i] = FT
            surplus = xS(x, S, n) - v[S]
            free = bin(S).count("1") - len(fvals)
            cand = ((surplus - sum(fvals.values())) / free if free > 0
                    else surplus - sum(fvals.values()) + max(fvals.values()))
            if best is None or cand < best: best, arg = cand, [S]
            elif cand == best: arg.append(S)
        for S in arg: fixed[S] = best
    return fixed

def is_superadditive(v, n):
    N = (1 << n) - 1
    for S in range(1, N + 1):
        T = N ^ S
        sub = T
        while sub:
            if v[S | sub] < v[S] + v[sub]: return False
            sub = (sub - 1) & T
    return True

def is_convex(v, n):
    N = (1 << n) - 1
    for S in range(N + 1):
        out = [i for i in range(n) if not (S >> i & 1)]
        for a in range(len(out)):
            for b in range(a + 1, len(out)):
                i, j = 1 << out[a], 1 << out[b]
                if v[S | i | j] + v[S] < v[S | i] + v[S | j]: return False
    return True

def check(label, cond):
    print(("  ok   " if cond else "  FAIL ") + label)
    if not cond: FAIL.append(label)

def pt(lst): return [F(u) for u in lst]

def verify_exactness(v, wit, n, label):
    N = (1 << n) - 1
    cover = {parse_set(name) for name in wit}
    check(f"{label}: exactness witnesses cover all {N-1} proper coalitions",
          cover == set(range(1, N)))
    ok = True
    for name, xs in wit.items():
        x = pt(xs); S = parse_set(name)
        ok &= in_core(v, x, n) and xS(x, S, n) == v[S]
    check(f"{label}: all witnesses are core points attaining their coalition's worth", ok)

def verify_levels(entry_list, values, n, kind, label):
    """kind='lower': sets {S: F(S)<=alpha}; kind='upper': {S: e(S)>=alpha}.
    Checks: thresholds = all distinct values; each stored set EQUALS the
    recomputed level set; supplied weights strictly positive and balance it."""
    distinct = sorted(set(values.values()), reverse=(kind == "upper"))
    check(f"{label}: threshold list complete ({len(distinct)} levels)",
          [F(e["threshold"]) for e in entry_list] == distinct)
    ok_sets = ok_w = True
    for e in entry_list:
        alpha = F(e["threshold"])
        stored = {parse_set(x) for x in e["lower_set" if kind == "lower" else "upper_set"]}
        recomputed = {S for S, val in values.items()
                      if (val <= alpha if kind == "lower" else val >= alpha)}
        ok_sets &= stored == recomputed
        ok_sets &= set(e["weights"]) == {coname(S, n) for S in stored}
        wsum = [F(0)] * n
        for name, w in e["weights"].items():
            lam = F(w); ok_w &= lam > 0
            for i in members(parse_set(name), n): wsum[i] += lam
        ok_w &= all(s == 1 for s in wsum)
    check(f"{label}: every stored level set equals the recomputed one", ok_sets)
    check(f"{label}: every level set balanced by supplied strictly positive weights", ok_w)

def verify_sd(v, cert, n, label):
    x = pt(cert["point"])
    check(f"{label}: stated point lies in the core", in_core(v, x, n))
    Fx = sd_satisfactions(v, x, n)
    check(f"{label}: SD satisfaction table recomputed from scratch",
          all(F(cert["satisfactions"][coname(S, n)]) == val for S, val in Fx.items())
          and len(cert["satisfactions"]) == len(Fx))
    verify_levels(cert["cumulative_lower_sets"], Fx, n, "lower", label)
    return x, Fx

def verify_nuc(v, cert, n, label):
    x = pt(cert["point"])
    N = (1 << n) - 1
    exc = {S: v[S] - xS(x, S, n) for S in range(1, N)}
    check(f"{label}: excess table recomputed from scratch",
          all(F(cert["excesses"][coname(S, n)]) == val for S, val in exc.items())
          and len(cert["excesses"]) == len(exc))
    verify_levels(cert["cumulative_upper_sets"], exc, n, "upper", label)
    return x

def perm_game(K):
    from itertools import permutations
    n = len(K)
    v = [F(0)] * (1 << n)
    for S in range(1, 1 << n):
        mem = members(S, n)
        best = None
        for p in permutations(mem):
            w = sum(F(K[i][j]) for i, j in zip(mem, p))
            if best is None or w > best: best = w
        v[S] = best
    return v

# ============================ THEOREM 5.1 ============================
print("Theorem 5.1 (SD not coalitionally monotonic on exact games)")
t = C["theorem_5_1"]
v, vp = parse_game(t["game_v"], 4), parse_game(t["game_vprime"], 4)
check("  bump relation: v' = v + e_{1,3,4}",
      all(vp[S] == v[S] + (1 if S == 0b1101 else 0) for S in range(1, 16)))
verify_exactness(v, t["exactness_witnesses_v"], 4, "  v")
verify_exactness(vp, t["exactness_witnesses_vprime"], 4, "  v'")
check("  both superadditive", is_superadditive(v, 4) and is_superadditive(vp, 4))
check("  neither convex", not is_convex(v, 4) and not is_convex(vp, 4))
x, _ = verify_sd(v, t["SD_v"], 4, "  v")
xp, _ = verify_sd(vp, t["SD_vprime"], 4, "  v'")
check("  SD points in cores", in_core(v, x, 4) and in_core(vp, xp, 4))
check("  player 1 (in bumped coalition) drops 53/12 -> 35/8",
      x[0] == F(53,12) and xp[0] == F(35,8) and x[0] > xp[0])

# ============================ THEOREM 5.3 ============================
print("Theorem 5.3 (SD-prekernel segment on an exact game)")
t = C["theorem_5_3"]
v = parse_game(t["game"], 4)
verify_exactness(v, t["exactness_witnesses"], 4, "  game")
check("  game not convex (as stated)", not is_convex(v, 4))
mid, _ = verify_sd(v, t["SD_midpoint"], 4, "  midpoint")
segok = True
count = 0
for tag, s in t["segment_samples"].items():
    x = pt(s["point"]); count += 1
    tval = F(tag.split("=")[1])
    segok &= x == [mid[0]+tval, mid[1]-tval, mid[2]-tval, mid[3]+tval]
    segok &= in_core(v, x, 4)
    Fx = sd_satisfactions(v, x, 4)
    segok &= all(F(s["satisfactions"][coname(S, 4)]) == val for S, val in Fx.items())
    for i in range(4):
        for j in range(4):
            if i != j:
                m = min(val for S, val in Fx.items() if S >> i & 1 and not (S >> j & 1))
                segok &= F(s["complaints"][f"s_{i+1}{j+1}"]) == m
    segok &= all(s["complaints"][f"s_{i+1}{j+1}"] == s["complaints"][f"s_{j+1}{i+1}"]
                 for i in range(4) for j in range(i + 1, 4))
check(f"  {count} segment samples (t = -1/2..1/2): parametrization "
      "x(t)=SD+t(1,-1,-1,1), core membership, recomputed satisfactions, all "
      "complaint equalities", segok and count == 7)

# ============================ THEOREM 5.4 ============================
print("Theorem 5.4 (SD not population monotonic on convex games)")
t = C["theorem_5_4"]
v = parse_game(t["game"], 3)
check("  full game convex", is_convex(v, 3))
xf, _ = verify_sd(v, t["SD_full"], 3, "  full game")
sub = t["SD_subgame_23"]
vsub = parse_game(sub["subgame"], 2)
xs, _ = verify_sd(vsub, sub["certificate"], 2, "  subgame {2,3}")
check("  subgame is the restriction of v to {2,3}",
      vsub[0b01] == v[0b010] and vsub[0b10] == v[0b100] and vsub[0b11] == v[0b110])
check("  drop: player 3 has 1/2 in subgame, 1/3 in full game",
      xs[1] == F(1,2) and xf[2] == F(1,3) and xs[1] > xf[2])

# ============================ THEOREM 6.1 ============================
print("Theorem 6.1 (nucleolus & SD not pairwise monotonic on permutation games)")
t = C["theorem_6_1"]
check("  matrices differ only at K_{43}: 1 -> 2",
      t["matrix_Kprime"][3][2] == t["matrix_K"][3][2] + 1 and
      all(t["matrix_K"][i][j] == t["matrix_Kprime"][i][j]
          for i in range(4) for j in range(4) if (i, j) != (3, 2)))
vK, vK2 = perm_game(t["matrix_K"]), perm_game(t["matrix_Kprime"])
check("  stored game tables equal the matrix-generated games",
      parse_game(t["game_K"], 4) == vK and parse_game(t["game_Kprime"], 4) == vK2)
nx = verify_nuc(vK, t["nucleolus_K"], 4, "  K (nucleolus)")
nxp = verify_nuc(vK2, t["nucleolus_Kprime"], 4, "  K' (nucleolus)")
check("  nucleoli in cores", in_core(vK, nx, 4) and in_core(vK2, nxp, 4))
check("  nucleolus: player 3 drops 1/2 -> 1/3", nx[2] == F(1,2) and nxp[2] == F(1,3))
sx, _ = verify_sd(vK, t["SD_K"], 4, "  K (SD)")
sxp, _ = verify_sd(vK2, t["SD_Kprime"], 4, "  K' (SD)")
check("  SD points in cores", in_core(vK, sx, 4) and in_core(vK2, sxp, 4))
check("  SD: player 3 drops 1/2 -> 1/4", sx[2] == F(1,2) and sxp[2] == F(1,4))

# ============================ THEOREM 3.2 ============================
print("Theorem 3.2 (minimal three-game infeasible family)")
t = C["theorem_3_2"]
b = parse_game(t["base"], 4)
vA = list(b); vA[0b0111] += 3
vB = list(b); vB[0b1110] += 1
w1, w2 = pt(t["core_witness_v_vA"]), pt(t["core_witness_vB"])
check("  (1,1,2,2) in core(v) and core(v_A)", in_core(b, w1, 4) and in_core(vA, w1, 4))
check("  (0,0,3,3) in core(v_B)", in_core(vB, w2, 4))
check("  infeasibility arithmetic: y_3<=2, z_2<=0, then 2+0 < v({2,3})=3",
      2 * vA[15] - 10 == 2 and 2 * vB[15] - 12 == 0 and 2 + 0 < b[0b0110])
# Verify the STORED Farkas multipliers: build the family system over variables
# (x, y, z) in R^12 as rows (a, rhs) meaning a . w >= rhs, aggregate with the
# stored multipliers, and confirm the aggregate is 0 . w >= positive number
# (an unsatisfiable inequality), i.e. the certificate genuinely refutes.
mults = t["farkas_multipliers_x13"]
def var(block, i): return {"x": 0, "y": 4, "z": 8}[block] + i
rowsF = {
    "core_v_{2,3}":    ([("x",1,1),("x",2,1)], b[0b0110]),
    "core_vA_{1,2,3}": ([("y",0,1),("y",1,1),("y",2,1)], vA[0b0111]),
    "core_vA_{1,4}":   ([("y",0,1),("y",3,1)], vA[0b1001]),
    "core_vA_{2,4}":   ([("y",1,1),("y",3,1)], vA[0b1010]),
    "efficiency_vA":   ([("y",0,-1),("y",1,-1),("y",2,-1),("y",3,-1)], -vA[15]),
    "core_vB_{1,3}":   ([("z",0,1),("z",2,1)], vB[0b0101]),
    "core_vB_{1,4}":   ([("z",0,1),("z",3,1)], vB[0b1001]),
    "core_vB_{2,3,4}": ([("z",1,1),("z",2,1),("z",3,1)], vB[0b1110]),
    "efficiency_vB":   ([("z",0,-1),("z",1,-1),("z",2,-1),("z",3,-1)], -vB[15]),
    "mono_A_player3":  ([("y",2,1),("x",2,-1)], 0),
    "mono_B_player2":  ([("z",1,1),("x",1,-1)], 0),
}
agg = [F(0)] * 12; rhs_agg = F(0)
okF = set(mults) == set(rowsF)
for name, lam_s in mults.items():
    lam = F(lam_s); okF &= lam > 0
    coeffs, rhs = rowsF[name]
    for blk, i, c in coeffs: agg[var(blk, i)] += lam * c
    rhs_agg += lam * rhs
check("  stored Farkas multipliers aggregate to 0 . w >= " + str(rhs_agg) +
      " > 0 (refutation)", okF and all(a == 0 for a in agg) and rhs_agg > 0)

# ============================ PROPOSITION 7.5 ============================
print("Proposition 7.5 (core intersection can fail at m=n=4; family feasible)")
t = C["proposition_7_5"]
b = parse_game(t["base"], 4)
verify_exactness(b, t["exactness_witnesses_base"], 4, "  base")
sel = t["family_selection"]
xb = pt(sel["theta_b"])
ok = in_core(b, xb, 4)
for k in range(4):
    S = 15 ^ (1 << k)
    vv = list(b); vv[S] += 4
    verify_exactness(vv, t[f"exactness_witnesses_t{k+1}"], 4, f"  t_{k+1}")
    y = pt(sel[f"theta_t{k+1}"])
    ok &= in_core(vv, y, 4) and all(y[i] >= xb[i] for i in range(4) if i != k)
check("  family selection: core memberships + dominance on constrained coordinates", ok)
# Empty common intersection, derived from the certificate games themselves:
# cap_k = max of x_k over Core(t_k) = t_k(N) - t_k(N\{k}) (face bound; exactness
# of t_k at N\{k} is certified above). A common point would need
# x(N) = b(N) <= sum_k cap_k, so sum_k cap_k < b(N) proves emptiness. The same
# quantities witness unbalancedness of the all-arm game M via the collection
# {N\{k}}_k with weights 1/3: sum_k M(N\{k}) > 3 M(N).
caps = []
Msum = F(0)
for k in range(4):
    S = 15 ^ (1 << k)
    vv = list(b); vv[S] += 4
    caps.append(vv[15] - vv[S])
    Msum += b[S] + 4          # all-arm game's value at N\{k}
check("  empty intersection: sum of certified face caps " + str(sum(caps)) +
      " < b(N) = " + str(b[15]), sum(caps) < b[15])
check(r"  all-arm game unbalanced: sum_k M(N\{k}) = " + str(Msum) +
      " > 3 M(N) = " + str(3 * b[15]), Msum > 3 * b[15])

print()
if FAIL:
    print(f"*** {len(FAIL)} FAILURES ***")
    for f in FAIL: print("   -", f)
    sys.exit(1)
print("ALL CHECKS PASSED. Every certificate-backed claim of Theorems 3.2, "
      "5.1, 5.3, 5.4, 6.1 and Proposition 7.5 is verified here in exact "
      "rational arithmetic using only the Python standard library. (Prose "
      "side-claims that require linear programming -- non-exactness of the "
      "Theorem 3.2 games and largeness of the eight cores -- are established "
      "by the exact-LP pipeline described in the paper, not re-checked here.)")

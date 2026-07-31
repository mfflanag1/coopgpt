"""One-command exact verification of the witness data for
"Core stability does not imply egalitarian stability".

    python3 verify_paper2.py

SELF-CONTAINED: Python standard library only (fractions, json, itertools).
Implements the egalitarian procedure of Dietzenbacher et al. (2017) /
Dietzenbacher (2021) inline, gates it on the two worked examples of
Dietzenbacher (2021), then verifies, for every witness block in
supplement_data.json:
  - the stated class flags that are recomputed here (monotone,
    superadditive, and convexity/non-convexity),
  - exactness where per-coalition witnesses are supplied (coverage of all
    proper coalitions, core membership, attainment),
  - the generator representation v = min(x1, x2) for the primary witness and
    that x1, x2 are core elements,
  - the egalitarian claims, admissible collection, ES verdict (recomputed
    from scratch), and that sum(claims) > v(N) for every witness,
  - PES and its violated core constraints.
"""
import sys, os, json
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
_p1 = os.path.join(HERE, "supplement_data.json")
_p2 = os.path.join(HERE, "..", "supplement_data.json")
with open(_p1 if os.path.exists(_p1) else _p2, encoding="utf-8") as stream:
    D = json.load(stream)
if os.path.exists(_p1) and os.path.exists(_p2):
    with open(_p2, encoding="utf-8") as stream:
        if D != json.load(stream):
            raise ValueError("the two supplement_data.json copies differ")
FAIL = []

def check(label, cond):
    print(("  ok   " if cond else "  FAIL ") + label)
    if not cond:
        FAIL.append(label)

def members(S, n): return [i for i in range(n) if S >> i & 1]

def coname(S, n): return "{" + ",".join(str(i + 1) for i in members(S, n)) + "}"

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

def egalitarian_procedure(n, v, with_history=False):
    N = (1 << n) - 1
    fixed, A, history = {}, [], []
    for _ in range(n + 1):
        if len(fixed) == n:
            break
        chi = {}
        for S in range(1, N + 1):
            mem = members(S, n)
            free = [i for i in mem if i not in fixed]
            if free:
                share = (v[S] - sum(fixed[i] for i in mem if i in fixed)) / len(free)
                chi[S] = {i: (fixed[i] if i in fixed else share) for i in mem}
            else:
                chi[S] = {i: fixed[i] for i in mem}
        A = []
        for S in range(1, N + 1):
            mem = members(S, n)
            if sum(chi[S][i] for i in mem) != v[S]:
                continue
            if all(all(not (T >> i & 1) or chi[T][i] <= chi[S][i]
                       for T in range(1, N + 1)) for i in mem):
                A.append(S)
        for S in A:
            for i in members(S, n):
                if i not in fixed:
                    fixed[i] = chi[S][i]
        maxima = tuple(max(chi[S][i] for S in range(1, N + 1)
                           if S >> i & 1) for i in range(n))
        history.append((tuple(A), dict(fixed), maxima))
    result = (fixed, A, (N in A))
    return result + (history,) if with_history else result

def is_monotone(v, n):
    N = (1 << n) - 1
    return all(v[S | (1 << i)] >= v[S] for S in range(N + 1)
               for i in range(n) if not (S >> i & 1))

def is_superadditive(v, n):
    N = (1 << n) - 1
    for S in range(1, N + 1):
        T = N ^ S
        sub = T
        while sub:
            if v[S | sub] < v[S] + v[sub]:
                return False
            sub = (sub - 1) & T
    return True

def is_convex(v, n):
    N = (1 << n) - 1
    for S in range(N + 1):
        out = [i for i in range(n) if not (S >> i & 1)]
        for a in range(len(out)):
            for b in range(a + 1, len(out)):
                i, j = 1 << out[a], 1 << out[b]
                if v[S | i | j] + v[S] < v[S | i] + v[S | j]:
                    return False
    return True

# ---- gates: Dietzenbacher (2021) Examples 2 and 3 ----
print("Gates (Dietzenbacher 2021 worked examples)")
v = [F(0)] * 16; v[15] = F(24); v[0b1010] = F(14); v[0b1100] = F(14)
c, A, es = egalitarian_procedure(4, v)
check("  Example 2: claims (3,7,7,7), egalitarian stable",
      [c[i] for i in range(4)] == [F(3), F(7), F(7), F(7)] and es)
v = [F(0)] * 8; v[0b101] = F(4); v[0b110] = F(4); v[0b111] = F(4)
c, A, es = egalitarian_procedure(3, v)
check("  Example 3: claims (2,2,2), NOT egalitarian stable",
      [c[i] for i in range(3)] == [F(2)] * 3 and not es
      and sorted(A) == [0b101, 0b110])

n = 5
for block in ["primary_witness_vN4", "minimized_variant_mass41",
              "secondary_witness_hub", "secondary_witness_halfinteger"]:
    t = D[block]
    print(block)
    v = parse_game(t["game_v"], n)
    N = 31
    claims, A, es = egalitarian_procedure(n, v)
    ec = t["egalitarian_claims"]
    stated = ([F(ec[str(i + 1)]) for i in range(n)] if isinstance(ec, dict)
              else [F(u) for u in ec])
    check("  claims recomputed = stated", [claims[i] for i in range(n)] == stated)
    check("  claims sum " + str(sum(stated)) + " > v(N) = " + str(v[N]),
          sum(stated) > v[N])
    check("  NOT egalitarian stable (recomputed)", not es and t["egalitarian_stable"] is False)
    check("  admissible collection matches",
          sorted(A) == sorted(parse_set(s) for s in t["admissible_collection_Ahat"]))
    if "exactness_witnesses" in t:
        wit = t["exactness_witnesses"]
        cover = {parse_set(k) for k in wit}
        ok = cover == set(range(1, N)) and all(
            in_core(v, [F(u) for u in xs], n) and
            xS([F(u) for u in xs], parse_set(k), n) == v[parse_set(k)]
            for k, xs in wit.items())
        check("  exactness: 30 core witnesses, coverage + attainment", ok)
    if "generator_points" in t:
        gp = t["generator_points"]
        pts = [[F(u) for u in p] for p in (gp.values() if isinstance(gp, dict) else gp)]
        ok = all(v[S] == min(xS(p, S, n) for p in pts) for S in range(1, N + 1))
        ok = ok and all(in_core(v, p, n) for p in pts)
        check("  generator: v = min over points; points in core", ok)
    if "PES_core_violations" in t:
        viol = t["PES_core_violations"]
        # reconstruct PES: D = intersection of maximal admissible; rest capped at lambda
        maxA = [S for S in A if not any(T != S and (S & T) == S for T in A)]
        Dset = set(range(n))
        for S in maxA:
            Dset &= set(members(S, n))
        rest = [i for i in range(n) if i not in Dset]
        budget = v[N] - sum(claims[i] for i in Dset)
        lam = budget / len(rest)
        while sum(min(claims[i], lam) for i in rest) != budget:
            capped = [i for i in rest if claims[i] <= lam]
            fp = [i for i in rest if i not in capped]
            if not fp:
                break
            lam = (budget - sum(claims[i] for i in capped)) / len(fp)
        pes = [claims[i] if i in Dset else min(claims[i], lam) for i in range(n)]
        ok = sum(pes) == v[N]
        for name, deficit in viol.items():
            S = parse_set(name)
            ok = ok and (v[S] - xS(pes, S, n) == F(deficit)) and xS(pes, S, n) < v[S]
        check("  PES efficient; stated core violations exact", ok)
    for flag, fn in [("is_monotone", is_monotone), ("is_superadditive", is_superadditive)]:
        if flag in t:
            check(f"  {flag} = {t[flag]}", fn(v, n) == t[flag])
    if "is_convex" in t:
        check("  is_convex = " + str(t["is_convex"]), is_convex(v, n) == t["is_convex"])

n = 6
for block in ["stable_witness_1", "stable_witness_2"]:
    t = D[block]
    print(block)
    v = parse_game(t["game_v"], n)
    N = 63
    check("  coalition table has all 63 nonempty entries",
          len(t["game_v"]) == N and
          {parse_set(name) for name in t["game_v"]} == set(range(1, N + 1)))
    A = [F(u) for u in t["generator_points"]["A"]]
    B = [F(u) for u in t["generator_points"]["B"]]
    check("  generator: v = min(A,B); A,B in core",
          all(v[S] == min(xS(A, S, n), xS(B, S, n)) for S in range(1, N + 1))
          and in_core(v, A, n) and in_core(v, B, n))
    if block == "stable_witness_1":
        claims, Ah, es, history = egalitarian_procedure(n, v, with_history=True)
    else:
        claims, Ah, es = egalitarian_procedure(n, v)
    stated = [F(u) for u in t["egalitarian_claims"]]
    check("  claims recomputed = stated", [claims[i] for i in range(n)] == stated)
    check("  claims sum " + str(sum(stated)) + " > v(N) = " + str(v[N]),
          sum(stated) > v[N] and F(t["claims_sum"]) == sum(stated))
    check("  NOT egalitarian stable (recomputed)",
          not es and t["egalitarian_stable"] is False)
    check("  admissible collection matches",
          sorted(Ah) == sorted(parse_set(s) for s in t["admissible_collection_Ahat"]))
    if block == "stable_witness_1":
        round_one = {parse_set("{1,5}"), parse_set("{5,6}")}
        round_one_fixed = {0: F("3/2"), 4: F("3/2"), 5: F("3/2")}
        round_one_maxima = (
            F("3/2"), F("5/4"), F("4/3"),
            F("5/4"), F("3/2"), F("3/2"),
        )
        check("  two-round trace (round 1 collection, maxima, fixed claims)",
              len(history) == 2 and set(history[0][0]) == round_one and
              history[0][1] == round_one_fixed and
              history[0][2] == round_one_maxima and
              set(history[1][0]) == set(Ah) and
              history[1][1] == claims)
        shift = [F(1), F(0), F(0), F(0), F(1), F(0)]
        base_A = [A[i] - shift[i] for i in range(n)]
        base_B = [B[i] - shift[i] for i in range(n)]
        base_v = [F(0)] * (1 << n)
        for S in range(1, N + 1):
            base_v[S] = min(xS(base_A, S, n), xS(base_B, S, n))
        base_claims, _, base_es = egalitarian_procedure(n, base_v)
        check("  unperturbed classical game is egalitarian stable",
              base_es and [base_claims[i] for i in range(n)] ==
              [F("1/2")] * 4 + [F(1), F(1)])
    ft = [parse_set(s) for s in t["fully_tight_coalitions"]]
    actual_ft = {
        S for S in range(1, N)
        if xS(A, S, n) == v[S] == xS(B, S, n)
    }
    check("  12 fully-tight coalitions (tight at A and B)",
          len(ft) == len(set(ft)) == 12 and set(ft) == actual_ft)
    # Segment core: the tight equalities force an affine line, then all core
    # inequalities restrict its exact parameter interval to [0,1].
    rows = [[F(1)] * n] + [[F(1) if S >> i & 1 else F(0) for i in range(n)]
                           for S in ft]
    M = [r[:] for r in rows]
    rank = 0
    for col in range(n):
        piv = next((r for r in range(rank, len(M)) if M[r][col] != 0), None)
        if piv is None:
            continue
        M[rank], M[piv] = M[piv], M[rank]
        pr = M[rank]
        for r in range(len(M)):
            if r != rank and M[r][col] != 0:
                f = M[r][col] / pr[col]
                M[r] = [a - f * b for a, b in zip(M[r], pr)]
        rank += 1
    direction = [B[i] - A[i] for i in range(n)]
    lower_bounds, upper_bounds = [], []
    for S in range(1, N):
        slope = xS(direction, S, n)
        offset = v[S] - xS(A, S, n)
        if slope > 0:
            lower_bounds.append(offset / slope)
        elif slope < 0:
            upper_bounds.append(offset / slope)
    interval_ok = (
        lower_bounds and upper_bounds and
        max(lower_bounds) == 0 and min(upper_bounds) == 1
    )
    check("  segment core: rank-5 line and exact parameter interval [0,1]",
          rank == 5 and A != B and interval_ok)
    check("  is_monotone = " + str(t["is_monotone"]), is_monotone(v, n) == t["is_monotone"])
    check("  is_superadditive = " + str(t["is_superadditive"]),
          is_superadditive(v, n) == t["is_superadditive"])
    print("  note  core stability has a hand proof in the article; the independent")
    print("        exact arrangement check is re-run by verify_stability.py.")

# The alternate regression witness is a player permutation followed by an
# additive transformation of the reported witness. Check both generators and
# the complete coalition table, so "equivalent normalization" is certified
# rather than merely asserted.
t1, t2 = D["stable_witness_1"], D["stable_witness_2"]
eq = t2["equivalence_to_stable_witness_1"]
order = [i - 1 for i in eq["old_player_order"]]
shift = [F(u) for u in eq["additive_shift"]]
pairs1 = [[F(u) for u in t1["generator_points"][key]] for key in ("A", "B")]
pairs2 = [[F(u) for u in t2["generator_points"][key]] for key in ("A", "B")]
mapped = [[point[i] + shift[j] for j, i in enumerate(order)] for point in pairs1]
if eq["endpoint_swap"]:
    mapped.reverse()
v1, v2 = parse_game(t1["game_v"], n), parse_game(t2["game_v"], n)
table_ok = True
for S in range(1, 1 << n):
    old_S = sum(1 << order[j] for j in range(n) if S >> j & 1)
    table_ok &= v2[S] == v1[old_S] + xS(shift, S, n)
check("alternate normalization: stated permutation + additive shift maps generators and game",
      sorted(order) == list(range(n)) and mapped == pairs2 and table_ok)

print()
if FAIL:
    print(f"*** {len(FAIL)} FAILURES ***")
    for f in FAIL:
        print("   -", f)
    sys.exit(1)
print("ALL CHECKS PASSED. Witness tables, procedural claims, generator "
      "representations, and segment-core systems were verified in exact "
      "rational arithmetic using only the Python standard library. Run "
      "verify_stability.py for the independent exact arrangement check.")

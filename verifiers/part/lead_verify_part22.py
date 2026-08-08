"""Lead's independent verification of r23's PART(2,2) witness.

Checks, all exact:
  1. v = lower envelope of the 5 rows; singleton-normalized (v({i})=0 all i).
     (Exactness is the archived lower-envelope lemma: rows are common-total
      nonnegative allocations, hence core points, hence v exact.)
  2. Lmin(v) = (1,1,2,2,1,1) by staged exact leximin over the core
     (z3 Optimize, rational arithmetic; every opt call must be sat).
  3. All PART(2,2) clauses per verifiers/zp/PROOF.txt definitions:
     H = {c,d} top strict suffix, slack s_phi(H) = 4 > 0,
     S1 = {c,e,f}, S2 = {a,b,d} phi-tight, singleton traces {c},{d},
     disjoint, covering, p = q = 2 = |Si ∩ L|, p+q = m = 4.
"""
from fractions import Fraction as F
from itertools import combinations
import z3

names = "abcdef"
n = 6
rows = [(0,0,1,4,2,1),(0,0,4,4,0,0),(4,0,0,0,2,2),(1,0,2,3,0,2),(0,1,2,3,1,1)]
T = 8
assert all(sum(r) == T for r in rows), "rows must have common total 8"
assert all(all(c >= 0 for c in r) for r in rows)

def v(S):
    return min(sum(r[i] for i in S) for r in rows)

# 1. singleton normalization
for i in range(n):
    assert v((i,)) == 0, f"v({{{names[i]}}}) = {v((i,))} != 0"
print("singleton-normalized: OK (exactness via lower-envelope lemma)")

coals = [c for k in range(1, n) for c in combinations(range(n), k)]

def frac_of(model, var):
    r = model[var]
    return F(r.numerator_as_long(), r.denominator_as_long())

def core_constraints(x):
    cs = [z3.Sum(list(x)) == T]
    cs += [xi >= 0 for xi in x]
    cs += [z3.Sum([x[i] for i in c]) >= v(c) for c in coals]
    return cs

# 2. staged exact leximin
fixed = {}          # player -> exact level
levels = []
while len(fixed) < n:
    free = [i for i in range(n) if i not in fixed]
    # stage: maximize min over free players
    o = z3.Optimize()
    x = [z3.Real(f"x{i}") for i in range(n)]
    t = z3.Real("t")
    for c in core_constraints(x):
        o.add(c)
    for i, val in fixed.items():
        o.add(x[i] == val)
    for i in free:
        o.add(x[i] >= t)
    h = o.maximize(t)
    assert o.check() == z3.sat
    tval = frac_of(o.model(), t)
    # pin exactly the free players that cannot exceed tval
    newly = []
    for i in free:
        o2 = z3.Optimize()
        y = [z3.Real(f"y{j}") for j in range(n)]
        for c in core_constraints(y):
            o2.add(c)
        for j, val in fixed.items():
            o2.add(y[j] == val)
        for j in free:
            o2.add(y[j] >= tval)
        h2 = o2.maximize(y[i])
        assert o2.check() == z3.sat
        if frac_of(o2.model(), y[i]) == tval:
            newly.append(i)
    assert newly, "no player pinned at stage level — staged leximin broken"
    for i in newly:
        fixed[i] = tval
    levels.append((tval, [names[i] for i in newly]))

phi = [fixed[i] for i in range(n)]
print("Lmin =", [str(p) for p in phi], " stages:", [(str(t), g) for t, g in levels])
assert phi == [F(1), F(1), F(2), F(2), F(1), F(1)], "Lmin mismatch with claim"

# 3. PART clauses
H = (2, 3)                      # {c,d}
L = tuple(i for i in range(n) if i not in H)
assert min(phi[i] for i in H) > max(phi[i] for i in L), "H not strict suffix"
# H is the TOP stratum (innermost strict suffix)
assert len({phi[i] for i in H}) == 1
slack = sum(phi[i] for i in H) - v(H)
print(f"s_phi(H) = {slack}  (v(cd) = {v(H)})")
assert slack == 4 and slack > 0
S1 = (2, 4, 5)                  # cef
S2 = (0, 1, 3)                  # abd
for S, nm in ((S1, "cef"), (S2, "abd")):
    assert sum(phi[i] for i in S) == v(S), f"{nm} not phi-tight"
assert set(S1) & set(S2) == set()
assert set(S1) | set(S2) == set(range(n))
assert set(S1) & set(H) == {2} and set(S2) & set(H) == {3}, "traces not singletons"
p = len(set(S1) & set(L)); q = len(set(S2) & set(L))
m = len(L)
assert (p, q) == (2, 2) and p + q == m == 4
print(f"PART({p},{q}) at m={m}: ALL CLAUSES VERIFIED")

# n=7 suspension (Lemma 4, mechanical): v'(S) = v(S \ {g7}) with null player 7
def v7(S):
    return v(tuple(i for i in S if i != 6))
# spot-check tightness of S1+e, S2+e at (phi,0) and that v7 is singleton-normalized
assert v7((6,)) == 0
assert sum(phi[i] for i in S1) == v7(S1 + (6,)) and sum(phi[i] for i in S2) == v7(S2 + (6,))
print("n=7 suspension: Lemma-4 tightness relations hold -> ZP(2,2) at m=5 realized")
print("\nVERDICT: witness GENUINE; Conjecture 10 refuted; correct threshold p+q>=4 supported")

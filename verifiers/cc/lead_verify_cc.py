"""Lead's independent verification of r12's C-C-left counterexample.

Checks, all exact, no shared code with r12's drivers:
  1. v (from the value list) and v' = v + 20 on S={1,3,4,5} are both EXACT:
     for every proper coalition C, min over the core of x(C) equals v(C)
     (z3 Optimize, exact rationals; every call must be sat).
  2. Lmin(v) = (121,121,121,146,151); Lmin(v') = (136,106,136,141,141)
     by staged exact leximin (same independent algorithm I used on r23).
  3. Configuration: strata {1,2,3}<{4}<{5}; suffix slacks s({4,5})=121,
     s({5})=151 (both slack -> H* = {5}, Hhat = {4,5}); s_phi(S)=5, alpha=20
     exceeds it and the bump is a monotonicity failure; W = strict losers in
     S = {4,5}; W not a subset of H*; H* subset of S; W subset of Hhat.
"""
from fractions import Fraction as F
from itertools import combinations
import z3

n = 5
T = 660
vals = {
    (1,2):106, (1,3):136, (1,2,3):136, (1,4):161, (1,2,4):161, (3,4):176,
    (2,3,4):176, (1,3,4):297, (1,2,3,4):297, (1,5):242, (1,2,5):242,
    (3,5):242, (2,3,5):242, (1,3,5):393, (1,2,3,5):484, (4,5):176,
    (2,4,5):176, (1,4,5):418, (1,2,4,5):418, (3,4,5):418, (2,3,4,5):418,
    (1,3,4,5):534,
}
S_bump = (1,3,4,5)
alpha = 20

coals = [c for k in range(1, n) for c in combinations(range(1, n+1), k)]
def make_v(bumped):
    def v(C):
        base = vals.get(tuple(sorted(C)), 0)
        if bumped and tuple(sorted(C)) == S_bump:
            base += alpha
        return base
    return v

def frac_of(m, var):
    r = m[var]
    return F(r.numerator_as_long(), r.denominator_as_long())

def core_cs(x, v):
    cs = [z3.Sum(list(x.values())) == T]
    cs += [xi >= 0 for xi in x.values()]
    cs += [z3.Sum([x[i] for i in c]) >= v(c) for c in coals]
    return cs

def check_exact(v, label):
    for c in coals:
        o = z3.Optimize()
        x = {i: z3.Real(f"x{i}") for i in range(1, n+1)}
        for cc in core_cs(x, v):
            o.add(cc)
        obj = z3.Sum([x[i] for i in c])
        o.minimize(obj)
        assert o.check() == z3.sat, f"{label}: core empty?"
        got = sum(frac_of(o.model(), x[i]) for i in c)
        assert got == v(c), f"{label}: exactness FAILS at {c}: min={got} v={v(c)}"
    print(f"{label}: exact at all {len(coals)} proper coalitions")

def leximin(v):
    fixed = {}
    while len(fixed) < n:
        free = [i for i in range(1, n+1) if i not in fixed]
        o = z3.Optimize()
        x = {i: z3.Real(f"x{i}") for i in range(1, n+1)}
        t = z3.Real("t")
        for cc in core_cs(x, v): o.add(cc)
        for i, val in fixed.items(): o.add(x[i] == val)
        for i in free: o.add(x[i] >= t)
        o.maximize(t)
        assert o.check() == z3.sat
        tv = frac_of(o.model(), t)
        newly = []
        for i in free:
            o2 = z3.Optimize()
            y = {j: z3.Real(f"y{j}") for j in range(1, n+1)}
            for cc in core_cs(y, v): o2.add(cc)
            for j, val in fixed.items(): o2.add(y[j] == val)
            for j in free: o2.add(y[j] >= tv)
            o2.maximize(y[i])
            assert o2.check() == z3.sat
            if frac_of(o2.model(), y[i]) == tv:
                newly.append(i)
        assert newly
        for i in newly: fixed[i] = tv
    return [fixed[i] for i in range(1, n+1)]

v = make_v(False); vp = make_v(True)
for i in range(1, n+1):
    assert v((i,)) == 0
check_exact(v, "v ")
check_exact(vp, "v'")

phi = leximin(v)
phip = leximin(vp)
print("Lmin(v)  =", [str(p) for p in phi])
print("Lmin(v') =", [str(p) for p in phip])
assert phi == [F(121)]*3 + [F(146), F(151)], "phi mismatch"
assert phip == [F(136), F(106), F(136), F(141), F(141)], "phi' mismatch"

# configuration
s45 = phi[3] + phi[4] - v((4,5)); s5 = phi[4] - v((5,))
print(f"s_phi({{4,5}}) = {s45}, s_phi({{5}}) = {s5}")
assert s45 == 121 and s5 == 151        # both slack -> multi-slack base
Hstar = {5}; Hhat = {4,5}; S = set(S_bump)
sS = sum(phi[i-1] for i in S_bump) - v(S_bump)
assert sS == 5 and alpha > sS          # genuine bump beyond the slack
W = {i for i in S if phip[i-1] < phi[i-1]}
losers = {i for i in range(1, n+1) if phip[i-1] < phi[i-1]}
print(f"W = {W}, all strict losers = {losers}")
assert W == {4,5} and losers == {2,4,5}
assert not W <= Hstar, "left inclusion should FAIL"
assert Hstar <= S, "right inclusion should hold"
assert W <= Hhat <= S, "repair C-C^ should hold on the witness"
print("\nVERDICT: counterexample GENUINE — C-C left inclusion FALSE;"
      " right holds; repair holds on the witness")

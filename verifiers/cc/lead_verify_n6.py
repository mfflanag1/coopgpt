"""Lead's independent verification of r12's n=6 multi-slack C-C-left failure
(Case A of REPORT2.txt).  Own code; no r12 drivers imported."""
from fractions import Fraction as F
from itertools import combinations
import z3

n = 6
rows = [(6,7,11,0,13,3),(0,22,0,10,0,8),(0,0,21,0,19,0)]
T = 40
assert all(sum(r) == T for r in rows)
S_bump = (1,2,3,4,5)          # players 2..6, 0-indexed
alpha = F(25,16)

coals = [c for k in range(1, n) for c in combinations(range(n), k)]
def make_v(bumped):
    def v(C):
        base = min(sum(r[i] for i in C) for r in rows)
        if bumped and tuple(sorted(C)) == S_bump:
            base += alpha
        return base
    return v

def frac_of(m, var):
    r = m[var]
    return F(r.numerator_as_long(), r.denominator_as_long())

def core_cs(x, v):
    cs = [z3.Sum(list(x)) == T]
    cs += [xi >= 0 for xi in x]
    cs += [z3.Sum([x[i] for i in c]) >= v(c) for c in coals]
    return cs

def check_exact(v, label):
    for c in coals:
        o = z3.Optimize()
        x = [z3.Real(f"x{i}") for i in range(n)]
        for cc in core_cs(x, v): o.add(cc)
        o.minimize(z3.Sum([x[i] for i in c]))
        assert o.check() == z3.sat
        got = sum(frac_of(o.model(), x[i]) for i in c)
        assert got == v(c), f"{label} exactness FAILS at {c}: {got} vs {v(c)}"
    print(f"{label}: exact at all {len(coals)} proper coalitions")

def leximin(v):
    fixed = {}
    while len(fixed) < n:
        free = [i for i in range(n) if i not in fixed]
        o = z3.Optimize(); x = [z3.Real(f"x{i}") for i in range(n)]; t = z3.Real("t")
        for cc in core_cs(x, v): o.add(cc)
        for i, val in fixed.items(): o.add(x[i] == val)
        for i in free: o.add(x[i] >= t)
        o.maximize(t); assert o.check() == z3.sat
        tv = frac_of(o.model(), t)
        newly = []
        for i in free:
            o2 = z3.Optimize(); y = [z3.Real(f"y{j}") for j in range(n)]
            for cc in core_cs(y, v): o2.add(cc)
            for j, val in fixed.items(): o2.add(y[j] == val)
            for j in free: o2.add(y[j] >= tv)
            o2.maximize(y[i]); assert o2.check() == z3.sat
            if frac_of(o2.model(), y[i]) == tv: newly.append(i)
        assert newly
        for i in newly: fixed[i] = tv
    return [fixed[i] for i in range(n)]

v = make_v(False); vp = make_v(True)
for i in range(n): assert v((i,)) == 0
check_exact(v, "v "); check_exact(vp, "v'")
phi = leximin(v); phip = leximin(vp)
print("Lmin(v)  =", [str(p) for p in phi]); print("Lmin(v') =", [str(p) for p in phip])
assert phi == [F(9,2),F(23,2),F(13,2),F(11,2),F(15,2),F(9,2)]
assert phip == [p+d for p,d in zip(phi,[F(-1,16),F(1,16),F(-1,16),F(1,16),F(-1,16),F(1,16)])]

# strata (0-idx): {0,5}@9/2 < {3}@11/2 < {2}@13/2 < {4}@15/2 < {1}@23/2
sfx = {}
for H in [(1,), (1,4), (1,2,4), (1,2,3,4)]:
    sfx[H] = sum(phi[i] for i in H) - v(H)
print("suffix slacks:", {str(k): str(x) for k,x in sfx.items()})
assert sfx[(1,)] == F(23,2) and sfx[(1,2,4)] == F(7,2)
assert sfx[(1,4)] == 0 and sfx[(1,2,3,4)] == 0     # interleaved!
Hstar = {1}; Hhat = {1,2,4}; S = set(S_bump)
sS = sum(phi[i] for i in S) - v(S_bump)
assert sS == F(3,2) and alpha > sS
W = {i for i in S if phip[i] < phi[i]}
print("W =", W)
assert W == {2,4}
assert not W <= Hstar, "C-C left must FAIL"
assert W <= Hhat <= S, "C-C^ must hold"
print("\nVERDICT: Case A GENUINE — C-C left fails at n=6; C-C^ holds; suffixes interleave")

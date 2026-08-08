"""THIRD, INDEPENDENT verification that Lmin of the PART(2,2) witness is
(1,1,2,2,1,1) -- using ONLY plain LP maximizations, not the staged leximin
routine of lib23/audit.py (which shares its lineage with the code that
produced the witness).

Discharges: the sole load-bearing numeric claim of the refutation.
"""
import sys
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import lib23 as L
import z3

n = 6
FULL = (1 << n) - 1
gens = [tuple(F(x) for x in g) for g in
        [[0,0,1,4,2,1],[0,0,4,4,0,0],[4,0,0,0,2,2],[1,0,2,3,0,2],[0,1,2,3,1,1]]]
v = L.envelope(n, gens)
w, sh = L.normalize(n, v)
assert all(x == 0 for x in sh)

def core_constraints(x):
    c = [z3.Sum(x) == L.to_z3(w[FULL])]
    for S in range(1, FULL):
        c.append(z3.Sum([x[i] for i in range(n) if S >> i & 1]) >= L.to_z3(w[S]))
    return c

def maximize(extra, obj):
    x = [z3.Real(f"x{i}") for i in range(n)]
    o = z3.Optimize()
    o.add(core_constraints(x))
    for e in extra(x):
        o.add(e)
    h = o.maximize(obj(x))
    assert o.check() == z3.sat
    return L.rat(o.upper(h))

lam = z3.Real("lam")
# STAGE 1 level
x = [z3.Real(f"x{i}") for i in range(n)]
o = z3.Optimize(); o.add(core_constraints(x))
for i in range(n):
    o.add(x[i] >= lam)
h = o.maximize(lam); assert o.check() == z3.sat
lvl1 = L.rat(o.upper(h))
print("stage 1 level  =", lvl1, " (expect 1)")

print("stage 1 per-player maxima subject to all x_i >= 1:")
for i in range(n):
    m = maximize(lambda xx: [xx[j] >= L.to_z3(lvl1) for j in range(n)],
                 lambda xx, i=i: xx[i])
    print(f"   max x_{L.LETTERS[i]} = {m}   pinned={m == lvl1}")

pinned = {0: F(1), 1: F(1), 4: F(1), 5: F(1)}
free = [2, 3]
x = [z3.Real(f"y{i}") for i in range(n)]
o = z3.Optimize(); o.add(core_constraints(x))
for j, val in pinned.items():
    o.add(x[j] == L.to_z3(val))
for k in free:
    o.add(x[k] >= lam)
h = o.maximize(lam); assert o.check() == z3.sat
lvl2 = L.rat(o.upper(h))
print("stage 2 level  =", lvl2, " (expect 2)")
for i in free:
    m = maximize(lambda xx: [xx[j] == L.to_z3(val) for j, val in pinned.items()]
                            + [xx[k] >= L.to_z3(lvl2) for k in free],
                 lambda xx, i=i: xx[i])
    print(f"   max x_{L.LETTERS[i]} = {m}   pinned={m == lvl2}")

print("\nboundary H={c,d}: v(cd) =", w[(1<<2)|(1<<3)],
      " phi(cd) =", lvl2*2, " slack =", lvl2*2 - w[(1<<2)|(1<<3)])
print("S1=cef tight:", w[(1<<2)|(1<<4)|(1<<5)] == lvl2 + 2*lvl1)
print("S2=abd tight:", w[(1<<0)|(1<<1)|(1<<3)] == lvl2 + 2*lvl1)

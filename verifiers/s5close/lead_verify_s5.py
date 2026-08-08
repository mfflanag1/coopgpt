"""Lead's independent falsification sweep for r22's s(5)=1/2 claims.

My own code end to end (generator, staged leximin, staged leximax; no r22
code imported).  On fresh random exact 5-player games (lower envelopes of
nonnegative common-total rows with every coordinate vanishing in some row):
  T0:  ||Lmin - Lmax||_1 <= T/2
  T2:  Lmin composition (4,1)  =>  ratio <= 1/3
  L1': the Lmax top stratum has >= 2 players
  L2': Lmax composition (1,4) with the singleton at zero => that player is
       in the Lmin bottom stratum
Also tallies how often 1/2 and 1/3 are attained.
"""
import random
from fractions import Fraction as F
from itertools import combinations
import z3

random.seed(20260808)
n = 5
coals = [c for k in range(1, n) for c in combinations(range(n), k)]

def gen_game():
    T = random.randint(6, 24)
    k = random.randint(3, 5)
    rows = []
    zero_cover = set()
    while True:
        rows = []
        for _ in range(k):
            zeros = random.sample(range(n), random.randint(1, 3))
            pos = [i for i in range(n) if i not in zeros]
            cuts = sorted(random.randint(0, T) for _ in range(len(pos) - 1))
            parts = [b - a for a, b in zip([0] + cuts, cuts + [T])]
            row = [0] * n
            for i, p in zip(pos, parts):
                row[i] = p
            rows.append(tuple(row))
        if set().union(*[{i for i in range(n) if r[i] == 0} for r in rows]) == set(range(n)):
            return rows, T

def v_of(rows):
    def v(C):
        return min(sum(r[i] for i in C) for r in rows)
    return v

def frac_of(m, var):
    r = m[var]
    return F(r.numerator_as_long(), r.denominator_as_long())

def core_cs(x, v, T):
    cs = [z3.Sum(list(x)) == T]
    cs += [xi >= 0 for xi in x]
    cs += [z3.Sum([x[i] for i in c]) >= v(c) for c in coals]
    return cs

def staged(v, T, side):
    """side=+1: leximin (max the min, pin);  side=-1: leximax-min (min the max, pin)."""
    fixed = {}
    while len(fixed) < n:
        free = [i for i in range(n) if i not in fixed]
        o = z3.Optimize()
        x = [z3.Real(f"x{i}") for i in range(n)]
        t = z3.Real("t")
        for c in core_cs(x, v, T): o.add(c)
        for i, val in fixed.items(): o.add(x[i] == val)
        for i in free:
            o.add(x[i] >= t if side > 0 else x[i] <= t)
        o.maximize(t) if side > 0 else o.minimize(t)
        assert o.check() == z3.sat
        tv = frac_of(o.model(), t)
        newly = []
        for i in free:
            o2 = z3.Optimize()
            y = [z3.Real(f"y{j}") for j in range(n)]
            for c in core_cs(y, v, T): o2.add(c)
            for j, val in fixed.items(): o2.add(y[j] == val)
            for j in free:
                o2.add(y[j] >= tv if side > 0 else y[j] <= tv)
            o2.maximize(y[i]) if side > 0 else o2.minimize(y[i])
            assert o2.check() == z3.sat
            if frac_of(o2.model(), y[i]) == tv:
                newly.append(i)
        assert newly
        for i in newly: fixed[i] = tv
    return [fixed[i] for i in range(n)]

NGAMES = 400
hit_half = hit_third = n41 = 0
maxr = F(0)
for g in range(NGAMES):
    rows, T = gen_game()
    v = v_of(rows)
    x = staged(v, T, +1)          # Lmin
    z = staged(v, T, -1)          # Lmax
    ratio = sum(abs(a - b) for a, b in zip(x, z)) / F(T)
    assert ratio <= F(1, 2), f"T0 VIOLATED: {rows} ratio={ratio}"
    maxr = max(maxr, ratio)
    if ratio == F(1, 2): hit_half += 1
    # L1'
    M = max(z)
    assert sum(1 for zi in z if zi == M) >= 2, f"L1' VIOLATED: {rows} z={z}"
    # T2
    mu = min(x)
    comp_min = sorted(x)
    if sum(1 for xi in x if xi == mu) == 4 and len(set(x)) == 2:
        n41 += 1
        assert ratio <= F(1, 3), f"T2 VIOLATED: {rows} ratio={ratio}"
        if ratio == F(1, 3): hit_third += 1
    # L2'
    zs = sorted(z)
    if zs[0] == 0 and zs[1] == zs[4] and zs[1] > 0:   # Lmax comp (1,4), singleton at 0
        j = z.index(F(0)) if F(0) in z else z.index(0)
        assert x[j] == mu, f"L2' VIOLATED: {rows} x={x} z={z}"
    if (g + 1) % 100 == 0:
        print(f"{g+1}/{NGAMES} ok; max ratio so far {maxr}; (4,1) seen {n41}")

print(f"\nALL {NGAMES} GAMES PASS.  max ratio {maxr}; ratio=1/2 hit {hit_half}x; "
      f"(4,1) games {n41}, ratio=1/3 hit {hit_third}x")

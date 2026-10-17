"""Finite exact checks, not a proof of the all-profile corollary."""
from fractions import Fraction as Q
from itertools import product


def worth(profile, mask):
    return min(sum(b[j] for i, b in enumerate(profile) if mask >> i & 1)
               for j in range(len(profile[0])))


def pay(profile):
    f = [min(a, b) for a, b in profile]
    u = [max(a-b, 0) for a, b in profile]
    v = [max(b-a, 0) for a, b in profile]
    U, V = sum(u), sum(v)
    if U == V == 0:
        return [Q(3, 2)*x for x in f]
    if U >= V:
        p = Q(V, 2*U)
        q = 1-p
    else:
        q = Q(U, 2*V)
        p = 1-q
    return [Q(3, 2)*f[i]+p*u[i]+q*v[i] for i in range(len(f))]


counts = dict(profiles=0, coalition_covers=0, dummy_zero_checks=0,
              coalition_restorations=0, min3_dummy_marginals=0)
for flat in product(range(3), repeat=6):
    b = [tuple(flat[2*i:2*i+2]) for i in range(3)]
    y = pay(b)
    counts['profiles'] += 1
    assert min(y) >= 0
    assert sum(y) <= Q(3, 2)*worth(b, 7)
    for S in range(1, 8):
        assert sum(y[i] for i in range(3) if S >> i & 1) >= worth(b, S)
        counts['coalition_covers'] += 1
    for i in range(3):
        off = [R for R in range(8) if not (R >> i & 1)]
        if all(worth(b, R | (1 << i)) == worth(b, R) for R in off):
            assert y[i] == 0
            counts['dummy_zero_checks'] += 1
        for j in range(2):
            if b[i][j] == 2:
                continue
            high = [list(z) for z in b]
            high[i][j] += 1
            yp = pay(high)
            for S in range(1, 8):
                if S >> i & 1:
                    assert sum(yp[h]-y[h] for h in range(3) if S >> h & 1) >= 0
                    counts['coalition_restorations'] += 1

b3 = [(1, 0, 0), (2, 0, 1), (2, 1, 0)]
for R in (0, 2, 4, 6):
    assert worth(b3, R | 1)-worth(b3, R) == 0
    counts['min3_dummy_marginals'] += 1
# Integral of 1-2t+t^2 on [0,1], divided by aggregate resource 1.
assert Q(1, 5)*(1-Q(2, 2)+Q(1, 3)) == Q(1, 15)
print('PASS', counts)

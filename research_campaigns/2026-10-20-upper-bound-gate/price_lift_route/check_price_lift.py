"""Exact finite checks supplementing NO_SCALAR_PRICE_LIFT.txt."""

from fractions import Fraction as Q
from itertools import product
import json


def value(bundle):
    return min(bundle)


def total(bundles):
    return tuple(map(sum, zip(*bundles)))


def payments(profile, repaired=False):
    v = value(total(profile))
    return (v if repaired else value(profile[0]), v)


def check_grid(r):
    # Finite subset of the fixed real boxes. Each owner may restore any subset
    # of rows. Separate eligibility grids retain the actual two-owner roster.
    coords = (Q(0), Q(1, 2), Q(1))
    reports1 = list(product(coords, repeat=r))
    reports2 = list(product(coords, *(tuple(2 * x for x in coords) for _ in range(r - 1))))
    profiles = list(product(reports1, reports2))
    coalitions = ((), (0,), (1,), (0, 1))
    checks = {"profiles": len(profiles), "coverage_rows": 0, "out_rows": 0,
              "repaired_out_rows": 0, "funding_rows": 0, "zero_output_profiles": 0}
    for b in profiles:
        y, yp = payments(b), payments(b, repaired=True)
        v = value(total(b))
        assert all(x >= 0 for x in y)
        assert sum(y) <= 2 * v and sum(yp) <= 2 * v
        assert yp[0] - y[0] >= 0 and sum(yp) - sum(y) <= v
        checks["funding_rows"] += 2
        if v == 0:
            assert y == (0, 0) and yp == (0, 0)
            checks["zero_output_profiles"] += 1
        for c in coalitions:
            bc = tuple(sum(b[i][a] for i in c) for a in range(r))
            assert sum(y[i] for i in c) >= value(bc)
            assert sum(yp[i] for i in c) >= value(bc)
            checks["coverage_rows"] += 2

    # For each low profile, form coordinatewise higher reports; include every
    # protected coalition containing the changed owners (including passive ones).
    uppers = []
    for reports in (reports1, reports2):
        uppers.append({lo: [hi for hi in reports if all(a <= b for a, b in zip(lo, hi))]
                       for lo in reports})
    for lo in profiles:
        yl, ypl = payments(lo), payments(lo, True)
        for hi in product(uppers[0][lo[0]], uppers[1][lo[1]]):
            changed = {i for i in range(2) if lo[i] != hi[i]}
            yh, yph = payments(hi), payments(hi, True)
            for c in coalitions:
                if not changed.issubset(c):
                    continue
                delta = tuple(sum(hi[i][a] - lo[i][a] for i in c) for a in range(r))
                rhs = value(delta)
                assert sum(yh[i] - yl[i] for i in c) >= rhs
                assert sum(yph[i] - ypl[i] for i in c) >= rhs
                checks["out_rows"] += 1
                checks["repaired_out_rows"] += 1
    return checks


def static_witnesses():
    rows = []
    for r in (2, 3, 4):
        for m in (2, 3, 10, 100, 1000):
            t = Q(1, m)
            b = ((Q(1),) + (t,) * (r - 1), (t,) + (Q(2),) * (r - 1))
            y = (t, Q(1))
            B = total(b)
            assert B == (1 + t,) + (2 + t,) * (r - 1)
            assert value(b[0]) == value(b[1]) == t
            assert sum(y) == value(B) == 1 + t
            assert y[0] >= value(b[0]) and y[1] >= value(b[1])
            # Dual constraint sum(p)>=1 and this decomposition force the
            # unique optimum p=e1: all other row coefficients exceed B1 by 1.
            assert all(B[a] - B[0] == 1 for a in range(1, r))
            u = (b[0][0], b[1][0])
            assert sum(u) == value(B)
            assert max(u[i] / y[i] for i in range(2)) == m
            Y = payments(b)
            assert max(u[i] / Y[i] for i in range(2)) == m
            rows.append({"arity": r, "t": str(t), "static_y": list(map(str, y)),
                         "dynamic_y": list(map(str, Y)), "unique_price_charges": list(map(str, u)),
                         "exact_minimum_scalar": m})
    return rows


if __name__ == "__main__":
    result = {"static_witnesses": static_witnesses(),
              "grid_checks": {str(r): check_grid(r) for r in (2, 3)},
              "scope": "Exact finite checks supplement the all-real written proof; no optimized funding lower bound."}
    print(json.dumps(result, indent=2))

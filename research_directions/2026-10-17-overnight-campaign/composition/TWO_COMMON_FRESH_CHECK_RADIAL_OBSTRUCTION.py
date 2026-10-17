"""Exact dual-cell certificate; run with python3 -I (assertions enabled)."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
A = (Q(1), Q(1), Q(1, 4))
B = (Q(1), Q(1, 4), Q(1))
W = (Q(3, 2), Q(1), Q(1))
lines = [(Q(1), Q(0), Q(0)), (Q(0), Q(1), Q(0)), *zip(A, B, W)]
vertices = set()
for (a, b, w), (aa, bb, ww) in combinations(lines, 2):
    determinant = a * bb - aa * b
    if determinant:
        p = (w * bb - ww * b) / determinant
        q = (a * ww - aa * w) / determinant
        if min(p, q) >= 0:
            vertices.add((p, q))
forms = sorted({(p + q, tuple(max(Q(0), w - a*p - b*q)
                            for a, b, w in zip(A, B, W)))
                for p, q in vertices})

def dot(x, y):
    return sum((a*b for a, b in zip(x, y)), Q(0))

base = (Q(1), Q(1), Q(1))
high = (Q(1), Q(3, 2), Q(1))
base_expected = [
    (Q(0), Q(4, 9), Q(0), Q(7, 2), {(Q(3, 2), Q(1), Q(1))}),
    (Q(4, 9), Q(4, 5), Q(3, 2), Q(1, 8),
     {(Q(0), Q(1, 8), Q(0)), (Q(0), Q(0), Q(1, 8))}),
    (Q(4, 5), Q(2), Q(8, 5), Q(0), {(Q(0), Q(0), Q(0))})]
high_expected = [
    (Q(0), Q(4, 11), Q(0), Q(4), {(Q(3, 2), Q(1), Q(1))}),
    (Q(4, 11), Q(4, 9), Q(1), Q(5, 4), {(Q(1, 2), Q(0), Q(3, 4))}),
    (Q(4, 9), Q(4, 5), Q(3, 2), Q(1, 8), {(Q(0), Q(0), Q(1, 8))}),
    (Q(4, 5), Q(2), Q(8, 5), Q(0), {(Q(0), Q(0), Q(0))})]

checked = 0

def verify(c, expected):
    global checked
    for lo, hi, value_intercept, value_slope, gradients in expected:
        mid = (lo + hi)/2
        active = set()
        for intercept, g in forms:
            # Each affine form lies above the claimed lower envelope at both
            # endpoints, hence on the entire interval. The active forms match
            # it identically. This certifies the whole real interval.
            differences = [intercept + t*dot(c, g)
                           - value_intercept - t*value_slope for t in (lo, hi)]
            assert min(differences) >= 0
            if intercept + mid*dot(c, g) == value_intercept + mid*value_slope:
                assert differences == [0, 0]
                active.add(g)
            checked += 1
        assert active == gradients, (c, lo, hi, active, gradients)
    # Last form is constant and all other affine slopes are nonnegative, so
    # the final interval extends to infinity without a further switch.
    assert all(dot(c, g) >= 0 for _, g in forms)
    assert expected[-1][3] == 0

verify(base, base_expected)
verify(high, high_expected)
# Reflected restoration has exactly the reflected private gradients.
reflected = (Q(1), Q(1), Q(3, 2))
reflection_expected = [(lo, hi, a, b, {(g[0], g[2], g[1]) for g in gs})
                       for lo, hi, a, b, gs in high_expected]
verify(reflected, reflection_expected)

base_0 = Q(0)
base_12 = Q(0)
for lo, hi, _, _, gs in base_expected:
    hi = min(hi, Q(1))
    if hi <= lo:
        continue
    g0s = {g[0] for g in gs}
    g12s = {g[1]+g[2] for g in gs}
    assert len(g0s) == len(g12s) == 1
    base_0 += (hi-lo) * next(iter(g0s))
    base_12 += (hi-lo) * next(iter(g12s))
assert base_0 == Q(2, 3)
assert base_12 == Q(14, 15)
prices_high = [Q(0)]*3
for lo, hi, _, _, gs in high_expected:
    hi = min(hi, Q(1))
    if hi <= lo:
        continue
    assert len(gs) == 1
    g = next(iter(gs))
    for j in range(3):
        prices_high[j] += (hi-lo)*g[j]
assert prices_high == [Q(58, 99), Q(4, 11), Q(232, 495)]
old_minimum = base_0 + base_12/2
new_payment = prices_high[0] + Q(3, 2)*prices_high[1]
assert old_minimum == Q(17, 15)
assert new_payment == Q(112, 99)
assert old_minimum-new_payment == Q(1, 495)

certificate = {
    'status': 'PASS',
    'method': 'Exact rational dual arrangement enumeration; full-interval inequalities.',
    'dual_vertices': [[str(p), str(q)] for p, q in sorted(vertices)],
    'dual_forms': [{'intercept': str(a), 'private_gradient': list(map(str, g))}
                   for a, g in forms],
    'affine_interval_checks': checked,
    'base_private0': str(base_0),
    'base_private12_sum': str(base_12),
    'minimum_larger_old_coalition': str(old_minimum),
    'restored_private_prices': list(map(str, prices_high)),
    'new_coalition': str(new_payment),
    'tie_independent_loss': str(old_minimum-new_payment),
    'analytic_extensions': 'Version2 Cesaro axis proof covers every nonnegative integrable kernel without continuity; see companion v2 note. No numerical inference.'
}
(ROOT/'TWO_COMMON_FRESH_RADIAL_OBSTRUCTION_CHECKS.json').write_text(json.dumps(certificate, indent=2)+'\n')
print(json.dumps(certificate, indent=2))

#!/usr/bin/env python3
"""Independent exact audit of uniform-full pointwise inflation examples."""
from fractions import Fraction as F
from itertools import combinations
from math import comb
import json


def explicit_rows(a, b, k, r, h):
    owners_a = tuple(range(1, a + 1))
    owners_b = tuple(range(a + 1, a + b + 1))
    g = frozenset((0,) + owners_a)
    off = [frozenset(x) for x in combinations(owners_b, k)]
    mixed = [frozenset((0,) + x + y)
             for x in combinations(owners_a, r) for y in combinations(owners_b, h)]
    rows = [g] + off + mixed
    assert len(rows) == len(set(rows)) == 1 + comb(b, k) + comb(a, r) * comb(b, h)
    assert all(len(row) == k for row in rows)
    assert [row for row in rows if 0 not in row] == off
    return rows, len(off), len(mixed)


def rowwise_certificate(a, b, k, r, h, qi, qa, qb, mass_b):
    n = 1 + a + b
    rows, off_count, mixed_count = explicit_rows(a, b, k, r, h)
    z = [F(1, k)] * n
    full_multipliers = [F(1, k)] + [F(b, k * k * off_count)] * off_count + [F(0)] * mixed_count
    q = [qi] + [qa] * a + [qb] * b
    multipliers = [F(0)] + [mass_b / off_count] * off_count + [qi / mixed_count] * mixed_count
    demands = [F(0)] + [F(1)] * (len(rows) - 1)
    for point, weights, rhs in ((z, full_multipliers, [F(1)] * len(rows)),
                               (q, multipliers, demands)):
        assert all(x >= 0 for x in point) and all(x >= 0 for x in weights)
        assert [sum(weight for row, weight in zip(rows, weights) if i in row)
                for i in range(n)] == point
        for row, weight, demand in zip(rows, weights, rhs):
            payment = sum(point[i] for i in row)
            assert payment >= demand
            assert weight * (payment - demand) == 0
        assert sum(x * x for x in point) == sum(weight * demand for weight, demand in zip(weights, rhs))
    assert all(demand == 1 for row, demand in zip(rows, demands) if 0 not in row)
    assert sum(full_multipliers) == F(n, k * k)
    full_hull = [x / sum(full_multipliers) for x in z]
    assert full_hull == [F(k, n)] * n
    assert sum(qi for qi in full_hull) == k
    mass = sum(multipliers)
    assert mass == sum(x * x for x in q)
    degrees = [sum(i in row for row in rows) for i in range(n)]
    return {'owners': n, 'rows': len(rows), 'off_owner_rows': off_count,
            'mixed_rows': mixed_count, 'degrees_by_group': [degrees[0], degrees[1], degrees[-1]],
            'rho': str(sum(full_multipliers)), 'mass': str(mass),
            'theta': str(qi / mass), 'full_hull_coordinate': str(F(k, n)),
            'normalized_ratio': str(qi / mass / F(k, n))}


def general(s, count_bins=False):
    assert s >= 2
    n, k = s ** 3, s * s
    a, b = k - 1, (s - 1) * k
    r, h = s - 1, k - s
    assert 1 + a + b == n and 1 + r + h == k
    assert 1 <= r <= a and 1 <= h <= b and k <= b
    if count_bins:
        mixed = comb(a, r) * comb(b, h)
        off = comb(b, k)
        count_a = comb(a - 1, r - 1) * comb(b, h)
        count_b = comb(a, r) * comb(b - 1, h - 1)
        off_b = comb(b - 1, k - 1)
        assert F(count_a, mixed) == F(1, s + 1)
        assert F(count_b, mixed) == F(1, s)
        assert F(off_b, off) == F(1, s - 1)
    mix_mass = F(s + 1, 2 * s * s)
    off_mass = F((s - 1) ** 2, 2 * s ** 3)
    qi, qa, qb = mix_mass, F(1, 2 * s * s), F(1, s * s)
    assert mix_mass * F(r, a) == qa
    assert mix_mass * F(h, b) + off_mass * F(k, b) == qb
    assert qi + r * qa + h * qb == 1 and k * qb == 1
    assert 0 < qi + a * qa == F(s + 1, 2 * s) < 1
    mass = mix_mass + off_mass
    assert mass == F(2 * s * s - s + 1, 2 * s ** 3)
    assert qi * qi + a * qa * qa + b * qb * qb == mass
    rho = F(n, k * k)
    full_mass = F(1, k) + F(b, k * k)
    assert rho == full_mass == F(1, s)
    assert F(b, k * k) * F(k, b) == F(1, k)
    p = F(k, n)
    theta = qi / mass
    assert theta == F(s * (s + 1), 2 * s * s - s + 1)
    ratio = theta / p
    assert ratio == F(s * s * (s + 1), 2 * s * s - s + 1) > F(s + 1, 2)
    assert qi / F(1, k) == F(s + 1, 2)
    assert 0 < theta < 1
    if s >= 3:
        assert theta > 2 * p
        polynomial = lambda x: x ** 3 - 3 * x * x + 2 * x - 2
        assert polynomial(s) > 0
        assert polynomial(s + 1) - polynomial(s) == 3 * s * (s - 1)
    aggregate = rho * (theta * theta + (n - 1) * p * p)
    assert aggregate == 1 - F(1, s ** 3) + theta * theta / s
    assert aggregate < 1 + F(1, s) <= F(3, 2)
    assert n * rho == s * s
    return {'s': s, 'owners': n, 'row_size': k, 'theta': str(theta),
            'normalized_ratio': str(ratio), 'raw_ratio': str(F(s + 1, 2)),
            'one_focal_H': str(aggregate)}


def main():
    compact = rowwise_certificate(5, 7, 6, 1, 4, F(5, 18), F(1, 18), F(1, 6), F(1, 108))
    assert compact['rows'] == 183 and compact['degrees_by_group'] == [176, 36, 106]
    assert compact['theta'] == '30/31' and compact['normalized_ratio'] == '65/31'
    assert F(compact['theta']) - 2 * F(compact['full_hull_coordinate']) == F(18, 403)
    smallest = rowwise_certificate(3, 4, 4, 1, 2, F(3, 8), F(1, 8), F(1, 4), F(1, 16))
    counted = [general(s, True) for s in range(2, 13)]
    for s in range(2, 101):
        general(s)
    large = [general(s) for s in (1000, 1000000)]
    print(json.dumps({'verified': True,
                      'scope': 'Pointwise proxy obstruction only; no H>4 or funding counterexample.',
                      'compact_complete_row_check': compact,
                      'smallest_family_complete_row_check': smallest,
                      'exact_binomial_parameter_checks': len(counted),
                      'parameter_identity_checks': 101,
                      'explicit_unbounded_bound': 'theta_i/p > (s+1)/2',
                      'large_parameter_checks': large}, indent=2))


if __name__ == '__main__':
    main()

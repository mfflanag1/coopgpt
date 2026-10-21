#!/usr/bin/env python3
"""Independent stdlib-only hypercube certificate and funding checks."""
from fractions import Fraction as F
from itertools import combinations
from math import comb
import json


def parameters(d):
    assert d >= 4
    n = 1 << d
    a, b = n // 2 - 1, n // 2 - d
    m = n - d - 1
    pair_count = d * (d - 1) // 2
    allowed_pairs = (d - 1) * (d - 2) // 2
    higher_count = a - pair_count
    k = a * (d - 2) // d
    c = n - k - 1
    f = F(k, a)
    mu = pair_count * f
    lo = mu.numerator // mu.denominator
    hi = -((-mu.numerator) // mu.denominator)
    choices = [(lo, F(1))] if lo == hi else [(lo, hi - mu), (hi, mu - lo)]
    assert a + b == m and n - 2 > d * (d - 1)
    assert higher_count > 0 and 0 < k <= b
    assert 0 < f <= F(d - 2, d) < 1
    assert max(0, k - higher_count) <= mu <= min(k, allowed_pairs)
    assert sum(prob for _, prob in choices) == 1
    assert sum(count * prob for count, prob in choices) == mu
    for count, prob in choices:
        assert prob > 0 and 0 <= count <= allowed_pairs
        assert 0 <= k - count <= higher_count
    # All three outside-vertex types have the claimed marginal.
    assert (mu / pair_count + (d - 2) * mu / allowed_pairs) / (d + 1) == f
    assert (k - mu) / higher_count == f
    assert F(a, m) * f == F(k, m)
    assert F(b, m) * F(k, b) == F(k, m)
    theta = F(d, d + 1)
    gamma = F(m - k, m)
    tau = F(d * d, d + 1) + F((m - k) ** 2, m)
    rho = F(n, c * c)
    ell = 1 / tau
    p = theta / tau
    assert (d + 1) * theta + m * gamma == c
    assert (d + 1) * theta * theta + m * gamma * gamma == tau
    assert d * theta + (c - d) * gamma == tau
    assert 0 < theta <= 1 and 0 < gamma <= 1
    assert F(c * c, n) <= tau <= n
    variance = F((d + 1) * m, n) * (theta - gamma) ** 2
    assert tau - F(c * c, n) == variance <= d + 1
    assert 0 < ell <= rho <= F(4, n)
    coefficient = F(n, 2 * c) * theta
    assert 0 < coefficient <= 1
    assert coefficient >= 1 - F(4, d)
    assert n * rho * theta * theta == 4 * coefficient * coefficient
    return dict(d=d, n=n, a=a, b=b, m=m, k=k, c=c, theta=theta,
                gamma=gamma, tau=tau, rho=rho, ell=ell, p=p,
                choices=choices, coefficient=coefficient)


def enumerate_certificate(d):
    v = parameters(d)
    n, k = v['n'], v['k']
    star = {0} | {1 << bit for bit in range(d)}
    pairs = [x for x in range(n) if x.bit_count() == 2]
    higher = [x for x in range(n) if x.bit_count() >= 4 and x.bit_count() % 2 == 0]
    odd = [x for x in range(n) if x.bit_count() % 2 == 1 and x not in star]
    assert len(odd) == v['b'] and len(pairs) + len(higher) == v['a']
    adjacency = [{x ^ (1 << bit) for bit in range(d)} for x in range(n)]
    edges = {(x, y) for x in range(n) for y in adjacency[x] if x < y}
    assert len(edges) == n * d // 2
    for shift in range(n):
        assert {tuple(sorted((x ^ shift, y ^ shift))) for x, y in edges} == edges
    support = []
    for focal_star in sorted(star):
        odd_weight = F(v['b'], v['m'] * (d + 1) * comb(v['b'], k))
        for background in combinations(odd, k):
            support.append((frozenset((focal_star,) + background), odd_weight))
        allowed = [x for x in pairs if x not in adjacency[focal_star]]
        for count, prob in v['choices']:
            atom_weight = (F(v['a'], v['m'] * (d + 1)) * prob /
                           (comb(len(allowed), count) * comb(len(higher), k - count)))
            for selected_pairs in combinations(allowed, count):
                for selected_higher in combinations(higher, k - count):
                    independent = frozenset((focal_star,) + selected_pairs + selected_higher)
                    support.append((independent, atom_weight))
    assert len(support) == {4: 71, 5: 2480}[d]
    assert sum(weight for _, weight in support) == 1
    marginal = [F(0)] * n
    for independent, weight in support:
        assert weight > 0 and len(independent) == k + 1
        assert len(independent & star) == 1
        assert all(not (adjacency[x] & independent) for x in independent)
        for x in independent:
            marginal[x] += weight
    assert marginal == [F(1, d + 1) if x in star else F(k, v['m']) for x in range(n)]
    w = [1 - x for x in marginal]
    q = [x / v['tau'] for x in w]
    assert q[0] == v['p'] and sum(x * x for x in q) == v['ell']
    stationarity = [F(0)] * n
    universe = set(range(n))
    for independent, weight in support:
        row = universe - independent
        assert len(row) == v['c'] and len(row & star) == d
        assert sum(q[x] for x in row) == 1
        for x in row:
            stationarity[x] += weight / v['tau']
    assert stationarity == q
    first_row = universe - support[0][0]
    orbit_counts = [0] * n
    for shift in range(n):
        for x in first_row:
            orbit_counts[x ^ shift] += 1
    assert orbit_counts == [v['c']] * n
    assert [F(x, v['c'] ** 2) for x in orbit_counts] == [F(1, v['c'])] * n
    off_rows_checked = 0
    all_rows = 0
    if d == 4:
        for vertices in combinations(range(n), k + 1):
            independent = set(vertices)
            if any(adjacency[x] & independent for x in independent):
                continue
            row = universe - independent
            all_rows += 1
            if 0 in independent:
                assert len(row & star) == d and sum(q[x] for x in row) == 1
                off_rows_checked += 1
    return {'d': d, 'support_entries': len(support),
            'complete_row_universe_checked': all_rows,
            'complete_off_row_universe_checked': off_rows_checked}


def direct_bound(d):
    v = parameters(d)
    n, rho, ell, p = v['n'], v['rho'], v['ell'], v['p']
    blocks = v['c'] ** 2 // n
    owners = blocks * n + 1
    z = blocks * rho
    assert blocks >= 1 and 1 - rho < z <= 1
    conservative = blocks * n * p / (1 + z)
    relaxed_scale = 1 / (1 + (blocks - 1) * rho + ell)
    veto = 1 - relaxed_scale
    assert relaxed_scale * ((blocks - 1) * rho + ell) == veto
    assert relaxed_scale * p >= p / (1 + z)
    # Equation(5), squared using only exact fractions.
    factor_one = v['c'] * p / 2
    factor_two_squared = 4 * z / (1 + z) ** 2
    factor_three_squared = F(blocks * n, blocks * n + 1)
    assert conservative ** 2 / owners == factor_one ** 2 * factor_two_squared * factor_three_squared
    assert factor_two_squared >= (1 - rho) ** 2
    assert factor_three_squared >= (1 - F(1, 2 * n)) ** 2
    if d >= 9:
        assert n >= 4 * d * (d + 1)
        assert rho * v['tau'] <= 1 + F(1, d)
        assert factor_one >= 1 - F(5, d)
        assert rho + F(1, 2 * n) <= F(1, d)
        assert conservative ** 2 / owners >= (1 - F(6, d)) ** 2
    return v, blocks, owners, conservative ** 2 / owners


def union_bound(d, t):
    v = parameters(d)
    n, rho, ell, p = v['n'], v['rho'], v['ell'], v['p']
    denominator = rho + (t - 1) * ell
    alpha = rho / denominator
    beta = ell / denominator
    assert alpha + (t - 1) * beta == 1
    assert alpha * ell == beta * rho
    p_t, ell_t = alpha * p, alpha * ell
    x = F(t) / rho
    blocks = -((-x.numerator) // x.denominator)
    owners = blocks * n * t + 1
    scale = 1 / (1 + (blocks - 1) * rho / t + ell_t)
    assert scale * ((blocks - 1) * rho / t + ell_t) == 1 - scale
    funding = blocks * n * t * scale * p_t
    c0 = rho / ell - 1
    assert 0 <= c0 <= 3
    assert c0 + rho * (1 + F(1, n)) / 2 < 4
    finite_factor_squared = ((F(t) / (t + c0)) ** 2 /
                             (1 + rho / t + rho / (n * t * t)))
    assert finite_factor_squared >= (1 - F(4, t)) ** 2 if t >= 4 else True
    assert funding ** 2 / owners >= v['coefficient'] ** 2 * finite_factor_squared
    claimed = 1 - F(4, d) - F(4, t)
    if claimed >= 0:
        assert funding ** 2 / owners >= claimed ** 2


def main():
    enumerated = [enumerate_certificate(d) for d in (4, 5)]
    dimensions = list(range(4, 129)) + [256, 512, 1024]
    for d in dimensions:
        direct_bound(d)
    for d in (4, 8, 9, 16, 32, 64):
        for t in (4, 8, 16, 100):
            union_bound(d, t)
    # Explicit epsilon quantifiers, checked through their exact finite instances.
    quantified = []
    for epsilon in (F(1, 2), F(1, 4), F(1, 10), F(1, 100)):
        dimension = max(9, -((-6 * epsilon.denominator) // epsilon.numerator))
        v, blocks, owners, ratio_squared = direct_bound(dimension)
        assert 1 - F(6, dimension) >= 1 - epsilon
        assert ratio_squared >= (1 - epsilon) ** 2
        quantified.append({'epsilon': str(epsilon), 'dimension': dimension,
                           'owner_count_digits': len(str(owners)),
                           'certified_coefficient': str(1 - F(6, dimension))})
    print(json.dumps({'verified': True,
                      'scope': 'True own-report projection envelope; no arbitrary-mechanism lower bound.',
                      'direct_finite_bound': 'funding/sqrt(N) >= 1-6/d for d>=9; B=floor(c^2/n), N=B*2^d+1',
                      'quantifiers': 'For every epsilon>0 and N0, some finite N>=N0 satisfies funding >= (1-epsilon)*sqrt(N).',
                      'enumerated_certificates': enumerated,
                      'dimensions_checked': len(dimensions),
                      'maximum_dimension_checked': max(dimensions),
                      'union_cases_checked': 24,
                      'exact_epsilon_cases': quantified}, indent=2))


if __name__ == '__main__':
    main()

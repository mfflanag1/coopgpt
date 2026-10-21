#!/usr/bin/env python3
"""Exact independent checks for the architecture-specific funding corollary.

No numerical solver, generator imports, or external packages are used.
Prints a compact report and does not write other campaign files.
"""
from fractions import Fraction as F
from math import comb
import json


def add(a, b):
    c = [F(0)] * max(len(a), len(b))
    for i, x in enumerate(a):
        c[i] += x
    for i, x in enumerate(b):
        c[i] += x
    while len(c) > 1 and not c[-1]:
        c.pop()
    return c


def mul(a, b):
    c = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i + j] += x * y
    return c


def scale(c, a):
    return [c * x for x in a]


def positive_from_four(a):
    """Nonnegative coefficients of P(4+x) certify P(s)>0 for s>=4."""
    shifted = [sum(F(a[j]) * comb(j, i) * 4 ** (j - i)
                   for j in range(i, len(a))) for i in range(len(a))]
    assert shifted[0] > 0 and all(x >= 0 for x in shifted)
    return shifted


def check_polynomials():
    d = [-18, 9, 2]
    k2 = [9, 6, 1]
    q = add(mul(d, add(k2, [0, -2, 1])),
            scale(4, mul([-2, 1], k2)))
    assert q == [-234, -3, 34, 30, 4]
    numerator = scale(3, mul([0, 0, 1], mul([-2, 1], k2)))
    assert numerator == [0, 0, -54, -9, 12, 3]
    gap = add(scale(3, mul([0, 1], q)), scale(-4, numerator))
    assert gap == [0, -702, 207, 138, 42]
    finite_bound = add(scale(21, q), scale(-2, gap))
    assert finite_bound == [-4914, 1341, 300, 354]
    veto_bound = [-27, -18, -6, 8]
    for p in (d, q, gap, finite_bound, veto_bound):
        positive_from_four(p)
    # Leading and next coefficients prove f_s=(3/4)s-21/8+O(1/s).
    assert F(numerator[-1], q[-1]) == F(3, 4)
    assert (F(numerator[-2]) - F(3, 4) * q[-2]) / q[-1] == -F(21, 8)
    return 5


def explicit_support(s):
    """Rebuild the four sets from explicit layer rules, not stored JSON."""
    support = []
    for h in range(2, s, 2):
        holes = ({h - 1, h, h + 1}, {1, h, s - 1},
                 {0, h, h + 1}, {0, h - 1, h})
        for kind, missing in enumerate(holes):
            chosen = set()
            for j in range(s):
                if j in missing:
                    continue
                if kind == 0:
                    top = (j % 2 == 0) if j < h else (j % 2 == 1)
                elif kind == 1:
                    top = (j % 2 == 1) if j < h else (j % 2 == 0)
                elif kind == 2:
                    top = j % 2 == 1
                else:
                    top = j % 2 == 0
                chosen.add(j if top else s + j)
            support.append(chosen)
    return support


def check_base(s):
    assert s >= 4 and s % 2 == 0
    n = 2 * s
    # A separate pairwise distance description of the graph.
    edges = {(u, v) for u in range(n) for v in range(u + 1, n)
             if v - u in (1, s, n - 1)}
    adjacency = [set() for _ in range(n)]
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    assert len(edges) == 3 * s and all(len(a) == 3 for a in adjacency)
    assert {tuple(sorted(((u + 1) % n, (v + 1) % n)))
            for u, v in edges} == edges
    local = {0} | adjacency[0]
    assert local == {0, 1, s, n - 1}
    support = explicit_support(s)
    assert len(support) == 2 * (s - 2)
    counts = [0] * n
    d = 2 * s * s + 9 * s - 18
    qn = [3 * (s - 2) if v in local else 2 * s for v in range(n)]
    for independent in support:
        assert len(independent) == s - 3
        assert all(not (adjacency[v] & independent) for v in independent)
        assert len(independent & local) == 1
        for v in independent:
            counts[v] += 1
        row = set(range(n)) - independent
        assert len(row) == s + 3 and len(row & local) == 3
        assert sum(qn[v] for v in row) == d
    assert counts == [(s - 2) // 2 if v in local else s - 4
                      for v in range(n)]
    # Each support entry has multiplier2/d, proving stationarity exactly.
    assert [2 * (len(support) - count) for count in counts] == qn
    ell = F(4 * (s - 2), d)
    p = F(3 * (s - 2), d)
    q = [F(v, d) for v in qn]
    assert sum(x * x for x in q) == ell
    assert p / ell == F(3, 4)
    # This is the potential of EVERY off-owner row by independent-set logic.
    assert 3 * q[0] + s * F(2 * s, d) == 1
    # The full projection is certified by an orbit of one row, with repetitions
    # allowed: each vertex occurs s+3 times among the 2s translates.
    first_row = set(range(n)) - support[0]
    orbit_counts = [0] * n
    for shift in range(n):
        for v in first_row:
            orbit_counts[(v + shift) % n] += 1
    assert orbit_counts == [s + 3] * n
    full_lambda = F(1, (s + 3) ** 2)
    assert [count * full_lambda for count in orbit_counts] == [F(1, s + 3)] * n
    rho = F(n, (s + 3) ** 2)
    assert ell <= rho and sum(F(1, s + 3) ** 2 for _ in range(n)) == rho
    assert n * rho * (p / ell) ** 2 == F(9 * s * s, 4 * (s + 3) ** 2)
    return len(support)


def direct(s):
    n = 2 * s
    d = 2 * s * s + 9 * s - 18
    rho = F(n, (s + 3) ** 2)
    ell = F(4 * (s - 2), d)
    p = F(3 * (s - 2), d)
    blocks = s // 2
    owners = blocks * n + 1
    assert owners == s * s + 1
    a = 1 / (1 + (blocks - 1) * rho + ell)
    u = 1 - a
    assert a * ((blocks - 1) * rho + ell) == u
    assert u + a == 1 and 0 < a < 1
    veto = blocks * rho / (1 + blocks * rho)
    nonveto = blocks * n * a * p
    qpoly = 4 * s ** 4 + 30 * s ** 3 + 34 * s * s - 3 * s - 234
    assert nonveto == F(3 * s * s * (s - 2) * (s + 3) ** 2, qpoly)
    assert veto == F(s * s, 2 * s * s + 6 * s + 9)
    assert nonveto >= F(3, 4) * s - F(21, 8)
    assert veto >= F(3, 8 * s)
    funding = nonveto + veto
    # Squaring is valid because both sides are positive.
    assert (funding + F(21, 8)) ** 2 >= F(9, 16) * owners
    return {'s': s, 'owners': owners, 'funding_lower': str(funding),
            'funding_lower_squared_over_N': str(funding * funding / owners)}


def union_veto(n, rho, p, ell, t):
    assert 0 < ell <= rho and t >= 1
    denominator = rho + (t - 1) * ell
    alpha = rho / denominator
    beta = ell / denominator
    assert alpha + (t - 1) * beta == 1
    assert alpha * ell == beta * rho
    rho_t = rho / t
    p_t = alpha * p
    ell_t = alpha * ell
    x = F(t) / rho
    blocks = (x.numerator + x.denominator - 1) // x.denominator
    owners = blocks * n * t + 1
    a = 1 / (1 + (blocks - 1) * rho_t + ell_t)
    assert a * ((blocks - 1) * rho_t + ell_t) == 1 - a
    nonveto = blocks * n * t * a * p_t
    theta = p / ell
    c = rho / ell - 1
    b = blocks * rho / t
    assert 1 <= b < 1 + rho / t
    assert nonveto / t == (n * theta * F(t, 1) / (t + c) * b /
                          (1 + b - rho * c / (t * (t + c))))
    assert F(owners, t * t) == n * b / rho + F(1, t * t)
    coefficient_squared = theta * theta * n * rho / 4
    finite_bound_squared = (coefficient_squared * (F(t) / (t + c)) ** 2 /
                            (1 + rho / t + rho / (n * t * t)))
    assert nonveto * nonveto / owners >= finite_bound_squared
    return nonveto * nonveto / owners


def main():
    polynomial_checks = check_polynomials()
    sizes = list(range(4, 202, 2)) + [300, 500]
    checked_supports = sum(check_base(s) for s in sizes)
    direct_cases = [direct(s) for s in (4, 6, 50, 86, 100, 200, 1000, 10000)]
    fixed = (172, F(172, 7921), F(63, 3887), F(84, 3887))
    assert fixed[0] * fixed[1] * (fixed[2] / fixed[3]) ** 2 / 4 == F(129, 178) ** 2
    times = (1, 2, 3, 5, 10, 100, 1000, 1000000)
    for t in times:
        union_veto(*fixed, t)
    # Exact finite violations of a leading coefficient1/2 also follow from
    # the old k=3 interval witness; no novelty is inferred from this check.
    intervals = []
    for k in (3, 4, 10, 100):
        base = (2 * k - 1, F(2 * k - 1, k * k),
                F(4, 3 * k + 2), F(6, 3 * k + 2))
        coefficient = F(2 * k - 1, 3 * k)
        assert base[0] * base[1] * (base[2] / base[3]) ** 2 / 4 == coefficient ** 2
        ratio_squared = union_veto(*base, 10000)
        assert ratio_squared > F(1, 4)
        intervals.append({'k': k, 'coefficient': str(coefficient),
                          'finite_ratio_squared_exceeds_one_quarter': True})
    print(json.dumps({'verified': True,
                      'scope': 'Own-report projection-envelope architecture only; not arbitrary mechanisms.',
                      'general_finite_bound': 'funding >= 3*sqrt(N)/4 - 21/8 for N=s^2+1, even s>=4',
                      'general_coefficient': '3/4',
                      'fixed_172_union_coefficient': '129/178',
                      'polynomial_positivity_certificates': polynomial_checks,
                      'base_sizes_checked': sizes,
                      'independent_support_sets_checked': checked_supports,
                      'fixed_base_union_cases_checked': len(times),
                      'old_interval_cases': intervals,
                      'direct_cases': direct_cases}, indent=2))


if __name__ == '__main__':
    main()

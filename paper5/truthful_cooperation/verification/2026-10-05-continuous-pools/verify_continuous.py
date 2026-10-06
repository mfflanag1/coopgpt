"""Exact finite checks supplementing CONTINUOUS_THEOREM.txt; standard Python only.

Full labeled profiles and coalitions are enumerated on the stated grids. Rational
payments are independently checked against actual coalition values and report
edges. These finite tests do not prove the theorem's universal quantifiers.
"""
from fractions import Fraction as Q
from itertools import combinations, product
from math import comb, lcm
from pathlib import Path
import hashlib
import json
import platform


def check(condition, message):
    if not condition:
        raise ValueError(message)


def payments(c):
    k, r = len(c), len(c[0])
    check(k >= 2 and r >= 2 and all(len(p) == r for p in c), 'ownership')
    check(all(isinstance(x, Q) and 0 <= x <= 1 for p in c for x in p), 'domain')
    totals = tuple(map(sum, c))
    T = min(totals)
    if T == 0:
        return (Q(0),) * (k * r)
    b = min(Q(1), 2 * T / (r - 1)) / k
    return tuple(b + 2 * sum(1 - pool[h] for h in range(r) if h != i)
                 * T * cap / ((r - 1) * totals[j])
                 for j, pool in enumerate(c) for i, cap in enumerate(pool))


def marginals(c):
    totals = list(map(sum, c))
    T = min(totals)
    result = []
    for j, pool in enumerate(c):
        for cap in pool:
            reduced = totals.copy()
            reduced[j] -= cap
            result.append(T - min(reduced))
    return tuple(result)


def subset_sums(values):
    result = [0] * (1 << len(values))
    for mask in range(1, len(result)):
        bit = mask & -mask
        result[mask] = result[mask ^ bit] + values[bit.bit_length() - 1]
    return result


def integer_scaled(x, denominator):
    y = x * denominator
    check(isinstance(y, Q) and y.denominator == 1, 'inexact integer scaling')
    return y.numerator


def profiles(k, r, grid, max_altered):
    check(tuple(sorted(set(grid))) == grid and grid[-1] == 1, 'grid order')
    unit = (Q(1),) * r
    local = [p for p in product(grid, repeat=r) if p != unit]
    found = []
    for m in range(min(k, max_altered) + 1):
        for selected in combinations(range(k), m):
            for pools in product(local, repeat=m):
                c = [unit] * k
                for j, pool in zip(selected, pools):
                    c[j] = pool
                found.append(tuple(c))
    expected = sum(comb(k, m) * (len(grid) ** r - 1) ** m
                   for m in range(min(k, max_altered) + 1))
    check(len(found) == len(set(found)) == expected, 'profile enumeration')
    return found


def exhaustive(k, r, grid, max_altered=2, payment_rule=payments):
    all_c = profiles(k, r, grid, max_altered)
    stored = {}
    coalitions = edges = zero_profiles = low_regime = high_regime = 0
    largest_base = largest_fair = Q(0)
    base_witness = None
    for c in all_c:
        y = payment_rule(c)
        M = marginals(c)
        fair = tuple(max(p, m / k) for p, m in zip(y, M))
        check(all(isinstance(v, Q) for v in y + M + fair), 'lost rational type')
        check(min(y) >= 0, 'negative payment')
        T = min(map(sum, c))
        m = sum(any(cap != 1 for cap in pool) for pool in c)
        lower_bounded = all(cap >= Q(1, r) for pool in c for cap in pool)
        B = 2 * m + (3 if lower_bounded else 4)
        check(sum(y) <= B * T, 'base budget')
        check(sum(fair) <= (B + 1) * T, 'fair budget')
        check(sum(M) <= k * T, 'marginal total')
        for j, pool in enumerate(c):
            C = sum(pool)
            for i, cap in enumerate(pool):
                check(M[j * r + i] == max(cap - (C - T), Q(0)), 'marginal formula')
        if T == 0:
            zero_profiles += 1
            check(not any(y) and not any(fair), 'zero profile')
        else:
            if 2 * T <= r - 1:
                low_regime += 1
            if 2 * T >= r - 1:
                high_regime += 1
            if sum(y) / T > largest_base:
                largest_base = sum(y) / T
                base_witness = {'profile': [[str(x) for x in p] for p in c],
                                'payments': list(map(str, y))}
            largest_fair = max(largest_fair, sum(fair) / T)
        D = lcm(*(v.denominator for p in c for v in p),
                *(v.denominator for v in y + fair))
        ys = subset_sums([integer_scaled(v, D) for v in y])
        fs = subset_sums([integer_scaled(v, D) for v in fair])
        cs = [subset_sums([integer_scaled(v, D) for v in p]) for p in c]
        pool_mask = (1 << r) - 1
        for mask in range(1 << (k * r)):
            v = min(cs[j][(mask >> (j * r)) & pool_mask] for j in range(k))
            check(ys[mask] >= v, 'base coalition violation')
            check(fs[mask] >= v, 'fair coalition violation')
            coalitions += 1
        stored[c] = y, fair
    for c, (y, fair) in stored.items():
        for j, pool in enumerate(c):
            for i, old in enumerate(pool):
                for new in grid:
                    if new <= old:
                        continue
                    changed = [list(p) for p in c]
                    changed[j][i] = new
                    changed = tuple(map(tuple, changed))
                    check(changed in stored, 'increase left retained domain')
                    yp, fp = stored[changed]
                    owner = j * r + i
                    check(yp[owner] >= y[owner], 'own report monotonicity')
                    check(fp[owner] >= fair[owner], 'fair own report monotonicity')
                    edges += 1
    return dict(k=k, r=r, max_altered=max_altered, grid=list(map(str, grid)),
                labeled_profiles=len(all_c), all_coalitions=coalitions,
                directed_base_and_fair_edges=edges, zero_profiles=zero_profiles,
                low_regime_profiles=low_regime, high_regime_profiles=high_regime,
                max_base_factor=str(largest_base), max_fair_factor=str(largest_fair),
                base_witness=base_witness)


def direct_checks():
    # Boundary revision, independently transcribed expected values.
    c = ((Q(1, 2), Q(1, 2)), (Q(1), Q(1)))
    check(payments(c) == (Q(1), Q(1), Q(1, 2), Q(1, 2)), 'revised boundary')
    boundary = {'new_base': list(map(str, payments(c))),
                'old_base': ['1/4', '1/4', '1/2', '1/2']}
    # Independently check the delegate's stated rejected mixture.
    def rejected(c):
        k, r = len(c), len(c[0])
        active = [j for j, pool in enumerate(c) if any(v < 1 for v in pool)]
        check(len(active) == 2, 'counterexample active pools')
        out = []
        for j, pool in enumerate(c):
            for cap in pool:
                out.append(sum((1 - sum(c[a]) / r) * cap if a == j else
                               sum(c[a]) / (r * (k - 1)) for a in active) / 2)
        return tuple(out)
    before = ((Q(1), Q(3, 4)), (Q(1), Q(1, 2)))
    after = ((Q(1), Q(7, 8)), (Q(1), Q(1, 2)))
    check(rejected(before)[1] == Q(27, 64), 'delegate old payment')
    check(rejected(after)[1] == Q(103, 256), 'delegate new payment')
    check(rejected(before)[1] - rejected(after)[1] == Q(5, 256), 'delegate decrease')
    check(payments(after)[1] >= payments(before)[1], 'new rule failed same edge')
    # Exercise the exhaustive verifier's actual failure paths with corrupt rules.
    grid = (Q(1, 2), Q(3, 4), Q(1))
    def no_payments(c):
        return (Q(0),) * 4
    def decreasing_bonus(c):
        y = list(payments(c))
        if c[0][0] == Q(1, 2):
            y[0] += Q(1, 100)
        return tuple(y)
    for rule, expected in ((no_payments, 'base coalition violation'),
                           (decreasing_bonus, 'own report monotonicity')):
        try:
            exhaustive(2, 2, grid, payment_rule=rule)
        except ValueError as error:
            check(str(error) == expected, 'negative control failed at wrong guard')
        else:
            raise ValueError('exhaustive checker accepted corrupt payments')
    try:
        integer_scaled(Q(1, 3), 2)
    except ValueError as error:
        check(str(error) == 'inexact integer scaling', 'wrong arithmetic guard')
    else:
        raise ValueError('integer guard did not reject fractional scaling')
    # A wider all-unit parameter boundary; no universality inferred from it.
    boundary_count = 0
    for k in (2, 3, 8, 216):
        for r in (2, 3, 4, 7, 16, 40):
            H = ((Q(1),) * r,) * k
            check(payments(H) == (Q(1, k),) * (k * r), 'unit boundary')
            boundary_count += 1
    return dict(boundary_revision=boundary, all_unit_cases=boundary_count,
                rejected_mixture={'old': '27/64', 'new': '103/256', 'drop': '5/256'},
                corrected_edge={'old': str(payments(before)[1]),
                                'new': str(payments(after)[1])},
                negative_controls=['coverage rejection via exhaustive checker',
                                   'own-monotonicity rejection via exhaustive checker',
                                   'nonintegral scaling rejection'])


def main():
    cases = [(2, 2, (Q(1, 2), Q(3, 4), Q(1)), 2),
             (2, 3, (Q(1, 3), Q(2, 3), Q(1)), 2),
             (2, 4, (Q(1, 4), Q(1, 2), Q(1)), 2),
             (3, 2, (Q(1, 2), Q(3, 4), Q(1)), 2),
             (3, 3, (Q(1, 3), Q(1, 2), Q(1)), 2),
             (4, 2, (Q(1, 2), Q(7, 8), Q(1)), 2),
             (2, 2, tuple(Q(4 + i, 8) for i in range(5)), 2),
             (2, 2, tuple(Q(8 + i, 16) for i in range(9)), 2),
             (2, 2, (Q(0), Q(1, 2), Q(1)), 2),
             (2, 3, (Q(0), Q(1, 3), Q(1)), 2),
             (3, 2, (Q(0), Q(1, 2), Q(1)), 2),
             (3, 2, (Q(1, 2), Q(3, 4), Q(1)), 3),
             (3, 2, (Q(0), Q(1, 2), Q(1)), 3),
             (2, 2, (Q(0), Q(1, 4), Q(1, 2), Q(1)), 2),
             (2, 3, (Q(0), Q(1, 6), Q(1, 3), Q(1)), 2)]
    results = []
    for k, r, grid, m in cases:
        item = exhaustive(k, r, grid, m)
        results.append(item)
        print(json.dumps({a: b for a, b in item.items() if a != 'base_witness'}), flush=True)
    result = dict(status='PASS', python=platform.python_version(),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope='Exhaustive finite labeled tests; real-report theorem relies on written proof.',
                  cases=results, direct_checks=direct_checks(),
                  totals={name: sum(v[name] for v in results) for name in
                          ('labeled_profiles', 'all_coalitions', 'directed_base_and_fair_edges')})
    Path(__file__).with_name('EXACT_CHECKS.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({a: b for a, b in result.items() if a != 'cases'}, indent=2))


if __name__ == '__main__':
    main()

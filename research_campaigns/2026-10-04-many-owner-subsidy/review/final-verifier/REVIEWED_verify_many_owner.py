#!/usr/bin/env python3
"""Exact finite stress checks; the continuum/limit proof is in HALF_FACTOR_THEOREM.txt."""
from fractions import Fraction as F
from itertools import product, permutations
from math import comb, factorial
from pathlib import Path
import hashlib
import json
import random


def require(condition, label):
    if not condition:
        raise ValueError(label)


def worth(capacities, left, owners):
    return min(sum((capacities[i] for i in owners if i < left), F(0)),
               sum((capacities[i] for i in owners if i >= left), F(0)))


def shapley_subsets(capacities, left):
    n = len(capacities)
    values = [worth(capacities, left, [i for i in range(n) if mask >> i & 1])
              for mask in range(1 << n)]
    phi = []
    for i in range(n):
        total = F(0)
        for mask in range(1 << n):
            if mask >> i & 1:
                continue
            k = mask.bit_count()
            total += F(factorial(k) * factorial(n - k - 1), factorial(n)) * (
                values[mask | 1 << i] - values[mask])
        phi.append(total)
    return phi, values


def shapley_orders(capacities, left):
    n = len(capacities)
    phi = [F(0)] * n
    for order in permutations(range(n)):
        before = []
        last = F(0)
        for i in order:
            before.append(i)
            current = worth(capacities, left, before)
            phi[i] += current - last
            last = current
    return [x / factorial(n) for x in phi]


def count_family(m, r):
    """m left units, r right units, one right capacity-m owner; distinct owners.

    A count state with k predecessors occurs comb(m,x)*comb(r,y) times,
    each with ordinary Shapley subset weight k!(n-k-1)!/n!.
    For a focal left unit remove that unit from the left count.
    """
    require(m >= 1 and r >= 0, 'family parameters')
    n = m + r + 1
    den = factorial(n)
    left_num = 0
    for x in range(m):
        for y in range(r + 1):
            multiplicity = comb(m - 1, x) * comb(r, y)
            k = x + y
            if y > x:  # giant absent; strict inequality is necessary
                left_num += multiplicity * factorial(k) * factorial(n - k - 1)
            k += 1  # giant present; a left unit always has marginal one
            left_num += multiplicity * factorial(k) * factorial(n - k - 1)
    giant_num = 0
    for x in range(m + 1):
        for y in range(r + 1):
            k = x + y
            giant_num += (comb(m, x) * comb(r, y) * factorial(k) *
                          factorial(n - k - 1) * max(x - y, 0))
    phi_left, phi_giant = F(left_num, den), F(giant_num, den)
    return phi_left, phi_giant, phi_left + phi_giant / m


def main():
    counts = dict(profiles=0, coalition_inequalities=0, marginal_floors=0,
                  cross_pair_prices=0, strict_own_report_checks=0,
                  zero_halvings_skipped=0, direct_order_profiles=0)

    def check(capacities, left):
        phi, values = shapley_subsets(capacities, left)
        n = len(capacities)
        full = (1 << n) - 1
        require(sum(phi) == values[full], 'efficiency')
        require(min(phi) >= 0, 'nonnegativity')
        for mask in range(1, full + 1):
            paid = sum(phi[i] for i in range(n) if mask >> i & 1)
            require(2 * paid >= values[mask], 'coalition half factor')
            counts['coalition_inequalities'] += 1
        for i in range(n):
            require(2 * phi[i] >= values[full] - values[full ^ 1 << i],
                    'removal marginal half floor')
            counts['marginal_floors'] += 1
        for i in range(left):
            for j in range(left, n):
                if capacities[i] and capacities[j]:
                    require(phi[i]/capacities[i] + phi[j]/capacities[j] >= F(1, 2),
                            'cross-pair normalized price')
                    counts['cross_pair_prices'] += 1
        counts['profiles'] += 1
        return phi

    grids = []
    for n in range(2, 7):
        for left in range(1, n):
            total = 0
            for capacities in product(range(3), repeat=n):
                check(capacities, left)
                total += 1
            grids.append(dict(owners=n, left=left, right=n-left, profiles=total))

    rng = random.Random(20261004)
    for _ in range(150):
        n = rng.randrange(2, 9)
        left = rng.randrange(1, n)
        capacities = [F(rng.randrange(0, 51), rng.randrange(1, 14)) for _ in range(n)]
        phi = check(capacities, left)
        for i in range(n):
            if not capacities[i]:
                counts['zero_halvings_skipped'] += 1
                continue
            reduced = capacities.copy()
            reduced[i] /= 2
            lower, _ = shapley_subsets(reduced, left)
            require(lower[i] <= phi[i], 'own-report monotonicity')
            counts['strict_own_report_checks'] += 1

    witnesses = []
    for capacities, left, mask, expected in [
        ((1, 1, 1, 1, 2), 2, 19, F(49, 60)),
        ((2, 2, 1, 1, 1), 1, 3, F(33, 40)),
        ((2, 1, 1, 1), 2, 6, F(5, 6)),
    ]:
        phi, values = shapley_subsets(capacities, left)
        require(phi == shapley_orders(capacities, left), 'independent permutation check')
        counts['direct_order_profiles'] += 1
        paid = sum(phi[i] for i in range(len(phi)) if mask >> i & 1)
        ratio = paid / values[mask]
        require(ratio == expected, 'exact witness ratio')
        witnesses.append(dict(capacities=capacities, left=left, coalition_mask=mask,
                              phi=list(map(str, phi)), value=str(values[mask]),
                              ratio=str(ratio), scaled_6_over_5_payment=str(F(6, 5)*paid)))
    family_cross_checks = 0
    for m in range(1, 5):
        for r in range(4):
            capacities = [1] * m + [1] * r + [m]
            phi, _ = shapley_subsets(capacities, m)
            unit, giant, ratio = count_family(m, r)
            require(all(x == unit for x in phi[:m]) and phi[-1] == giant,
                    'count-state versus individual subset formula')
            require(ratio == (sum(phi[:m]) + phi[-1]) / m, 'family ratio')
            family_cross_checks += 1
    families = []
    for q in (2, 3):
        m, r = q**4, q**4 - q**3
        unit, giant, ratio = count_family(m, r)
        rational_bound = F(1, 2) + F(3*q*q, 2*(q**3-1)) + F(1, 2*q) + F(3, 4*q*q)
        require(F(1, 2) <= ratio <= rational_bound, 'family proof-bound calibration')
        families.append(dict(q=q, left_units=m, right_units=r, giant_capacity=m,
                             phi_left=str(unit), phi_giant=str(giant),
                             coalition_ratio=str(ratio), decimal_ratio=float(ratio)))
    q = 13
    rational_bound = F(1, 2) + F(3*q*q, 2*(q**3-1)) + F(1, 2*q) + F(3, 4*q*q)
    require(rational_bound < F(2, 3), 'explicit finite obstruction to 50%-scaled Shapley')
    report = dict(status='PASS', source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  seed=20261004, counts=counts, integer_grids=grids, rational_profiles=150,
                  witnesses=witnesses, family_count_cross_checks=family_cross_checks,
                  exact_families=families,
                  q13_bound=dict(q=q, owners=2*q**4-q**3+1,
                                 rational_upper_bound=str(rational_bound),
                                 below_two_thirds=True,
                                 note='Verifies arithmetic of the proved bound; does not enumerate this game.'),
                  limitations=['Finite checks do not prove all real profiles or the limit.',
                               'Fairness checked against removal marginal, not LP-computed H.',
                               'No novelty or human specialist certification.'])
    Path(__file__).with_name('EXACT_CHECKS.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

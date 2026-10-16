#!/usr/bin/env python3
"""Finite Decimal corroboration; the accompanying analytic proofs are essential."""
from decimal import Decimal, localcontext
from fractions import Fraction
from itertools import product
from pathlib import Path
import hashlib
import json
import random

BASE = Path(__file__).resolve().parent
D = Decimal
TOL = D('1e-65')


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def dec(value):
    if isinstance(value, Fraction):
        return D(value.numerator) / D(value.denominator)
    return D(value)


def primitive(left, right):
    """Direct definition, reimplemented without importing campaign code."""
    a, b = list(map(dec, left)), list(map(dec, right))
    sa, sb = sum(a), sum(b)
    if min(sa, sb) == 0:
        return [D(0)] * len(a)
    short, long = (a, b) if sa <= sb else (b, a)
    total = min(sa, sb)
    capped = [min(x, total) for x in long]
    q = (D(1) - sum(capped) / total).exp() / 2
    return [(1 - q) * x + q * y for x, y in zip(short, capped)]


def l1(a, b):
    return sum(abs(x - y) for x, y in zip(a, b))


def nested(hardware, local, grid):
    count = len(grid)
    h = [D(0)] * count
    z = [D(0)] * count
    for a, b in zip(hardware, local):
        branch = primitive(a, b)
        h = [x + dec(y) for x, y in zip(h, a)]
        z = [x + y for x, y in zip(z, branch)]
    return primitive(h, [dec(p) + x for p, x in zip(grid, z)])


def run():
    report = {'arithmetic': 'Decimal precision 90; finite corroboration, not an exact certificate'}
    vals = [Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(1), Fraction(2)]
    rng = random.Random(20261016)
    primitive_checks = 0
    largest_ratio = D(0)
    for n in (1, 2, 3, 7):
        for trial in range(100):
            a, b = [[rng.choice(vals) for _ in range(n)] for _ in range(2)]
            aa, bb = a[:], b[:]
            side = aa if trial % 2 == 0 else bb
            index = trial % n
            side[index] = rng.choice(vals)
            distance = sum(abs(dec(x)-dec(y)) for x, y in zip(a+b, aa+bb))
            change = l1(primitive(a, b), primitive(aa, bb))
            require(change <= 2 * distance + TOL, 'Primitive Lipschitz violation')
            if distance:
                largest_ratio = max(largest_ratio, change / distance)
            primitive_checks += 1
    report['primitive_lipschitz_checks'] = primitive_checks
    report['largest_observed_primitive_ratio'] = str(largest_ratio)

    nested_checks = 0
    for n in (1, 3, 6):
        for trial in range(100):
            h = [[rng.choice(vals) for _ in range(n)] for _ in range(2)]
            l = [[rng.choice(vals) for _ in range(n)] for _ in range(2)]
            p = [rng.choice(vals) for _ in range(n)]
            hh, ll, pp = [row[:] for row in h], [row[:] for row in l], p[:]
            i = trial % n
            before = [h[0][i], h[1][i], l[0][i], l[1][i], p[i]]
            after = [rng.choice(vals) for _ in before]
            hh[0][i], hh[1][i], ll[0][i], ll[1][i], pp[i] = after
            distance = sum(abs(dec(x)-dec(y)) for x, y in zip(before, after))
            change = abs(nested(h, l, p)[i] - nested(hh, ll, pp)[i])
            require(change <= 6 * distance + TOL, 'Nested Lipschitz violation')
            nested_checks += 1
    report['whole_bundle_lipschitz_checks'] = nested_checks

    obstruction_checks = 0
    obstruction = []
    for r in (2, 3, 5):
        h = [[Fraction(1, r) if i == j else Fraction(0) for i in range(r+1)] for j in range(r)]
        best = D(0)
        for multipliers in product(range(4), repeat=r):
            x = [Fraction(t, 3*r) for t in multipliers]
            l = [[Fraction(0)] * r + [xx] for xx in x]
            actual = nested(h, l, [0] * (r+1))[r]
            total = sum(map(dec, x))
            if total:
                rho = r * min(D(1)/r, total) / total
                formula = total * (1 - (1-rho).exp()/2)/2
            else:
                formula = D(0)
            require(abs(actual-formula) <= TOL, 'Obstruction formula mismatch')
            require(actual <= D(1)/4 + TOL, 'Obstruction optimum exceeded')
            best = max(best, actual)
            obstruction_checks += 1
        require(abs(best-D(1)/4) <= TOL, 'Truthful maximum not attained')
        relaxed = primitive([Fraction(1,r)] * r + [0], [0] * r + [Fraction(1,2)])[r]
        predicted = D(1)/2 - D(-1).exp()/4
        require(abs(relaxed-predicted) <= TOL, 'Relaxation value mismatch')
        obstruction.append({'branches': r, 'owners': r+1, 'actual_max': str(best),
                            'relaxed': str(relaxed), 'gap': str(relaxed-best)})
    report['obstruction_profiles_checked'] = obstruction_checks
    report['obstruction_values'] = obstruction

    # A fixed, one-coordinate lattice isolates exact set nesting and padding.
    # Owner B has local resources on one branch and no other eligibility.
    step = Fraction(1, 100)
    padding = D(6) * dec(step)
    previous = None
    lattice_checks = 0
    for numerator in range(201):
        b = Fraction(numerator, 100)
        candidates = [Fraction(j,100) for j in range(numerator+1)]
        values = [nested([[1,0]], [[0,x]], [0,0])[1] for x in candidates]
        approximation = padding + max(values)
        require(previous is None or approximation + TOL >= previous, 'Lattice monotonicity violation')
        # Compare with all half-step feasible points, including the full report.
        finer = [nested([[1,0]], [[0,Fraction(j,200)]], [0,0])[1]
                 for j in range(2*numerator+1)]
        require(approximation + TOL >= max(finer), 'Lattice domination violation')
        require(approximation <= max(finer) + padding + TOL, 'Additive error violation')
        previous = approximation
        lattice_checks += 1
    report['fixed_lattice_profile_checks'] = lattice_checks
    report['zero_profile_payment'] = str(padding)
    report['source_sha256'] = {name: hashlib.sha256((BASE/name).read_bytes()).hexdigest()
        for name in ('LIPSCHITZ_TRUTHFUL_ADDITIVE_APPROXIMATION.txt',
                     'EXACT_FLOOR_EVALUATION_OBSTRUCTION.txt')}
    report['status'] = 'PASS'
    return report


if __name__ == '__main__':
    with localcontext() as ctx:
        ctx.prec = 90
        print(json.dumps(run(), indent=2, sort_keys=True))

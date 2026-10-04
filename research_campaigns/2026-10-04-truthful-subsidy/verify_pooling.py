"""Exact stress checks; the universal theorem is the separate analytic proof."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib
import json

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def integrate_product(totals, omitted, end):
    coeff = [F(1)]
    for j, a in enumerate(totals):
        if j == omitted:
            continue
        new = [F(0)] * (len(coeff) + 1)
        for degree, value in enumerate(coeff):
            new[degree] += value
            new[degree + 1] -= value / a
        coeff = new
    return sum(v * end ** (d + 1) / (d + 1) for d, v in enumerate(coeff))

def value(c, groups, mask):
    return min(sum(c[i] for i in group if mask >> i & 1) for group in groups)

def payments(c, groups, alpha=None):
    totals = tuple(sum(c[i] for i in group) for group in groups)
    t = min(totals)
    if not t:
        return (F(0),) * len(c)
    prices = [integrate_product(totals, j, t) / a for j, a in enumerate(totals)]
    require(sum(prices) == 1, 'prices do not sum to one')
    y = [F(0)] * len(c)
    for j, group in enumerate(groups):
        for i in group:
            base = c[i] * prices[j]
            if alpha is not None and alpha > F(1, 2):
                full = c[i] * t / totals[j]
                base = (2 - 2 * alpha) * base + (2 * alpha - 1) * full
            y[i] = base
    return tuple(y)

def check_grid(groups, grid, alpha=None):
    n, k = sum(map(len, groups)), len(groups)
    full = (1 << n) - 1
    expected = len(grid) ** n
    cover = floors = monotone = 0
    maximum = F(0)
    for c in product(grid, repeat=n):
        t = value(c, groups, full)
        y = payments(c, groups, alpha)
        floor_factor = F(1, k) if alpha is None else alpha
        bound = F(k - 1, 2) if alpha is None else max(F(1, 2), alpha)
        require(min(y) >= 0, 'negative payment')
        require(sum(y) <= (1 + bound) * t, 'budget violation')
        if t:
            maximum = max(maximum, (sum(y) - t) / t)
        else:
            require(sum(y) == 0, 'zero-flow payment')
        for mask in range(1, full + 1):
            require(sum(y[i] for i in range(n) if mask >> i & 1) >= value(c, groups, mask),
                    'coalition violation')
            cover += 1
        for i in range(n):
            # Removal marginal is an upper bound for H, not an LP-computed ideal.
            marginal = t - value(c, groups, full ^ (1 << i))
            require(y[i] >= floor_factor * marginal, 'marginal floor violation')
            floors += 1
            pos = grid.index(c[i])
            if pos:
                low = list(c)
                low[i] = grid[pos - 1]
                require(y[i] >= payments(tuple(low), groups, alpha)[i], 'monotonicity violation')
                monotone += 1
    require(cover == expected * full, 'incomplete grid')
    require(floors == expected * n, 'incomplete floor checks')
    require(monotone == n * (len(grid)-1) * len(grid) ** (n-1), 'incomplete monotonicity checks')
    return {'groups': groups, 'grid': list(map(str, grid)), 'alpha': str(alpha),
            'profiles': expected, 'coalition_checks': cover, 'marginal_floor_checks': floors,
            'adjacent_own_report_checks': monotone, 'maximum_grid_subsidy_ratio': str(maximum)}

def main():
    grid = tuple(map(F, [0, 1, 2, 5]))
    results = [check_grid(((0, 1),), grid),
               check_grid(((0, 1), (2, 3)), grid),
               check_grid(((0, 1), (2, 3), (4, 5)), grid)]
    rational_grid = (F(0), F(1, 2), F(1), F(3))
    for alpha in (F(0), F(1, 3), F(1, 2), F(3, 4), F(1)):
        results.append(check_grid(((0, 1), (2, 3)), rational_grid, alpha))
    # Exact specializations and approach to formula-specific worst budget.
    for a, b in product((F(1, 2), F(1), F(3), F(100)), repeat=2):
        y = payments((a, b), ((0,), (1,)))
        t, m = min(a, b), max(a, b)
        require(sum(y) == F(3, 2)*t-t*t/(2*m), 'two-pool closed form')
    for alpha in (F(0), F(1, 3), F(1, 2), F(3, 4), F(1)):
        y = payments((F(1000), F(1)), ((0,), (1,)), alpha)
        optimum = max(F(1, 2), alpha)
        require(optimum - (sum(y)-1) < F(1, 1000), 'sharp-class asymptotic witness')
    # A deliberately wrong scaling must be rejected by coalition coverage.
    bad = tuple(z / 2 for z in payments((F(1),)*4, ((0, 1), (2, 3))))
    require(sum(bad) < 2, 'corruption fixture did not fail')
    report = {'status': 'passed', 'arithmetic': 'fractions.Fraction',
              'scope': 'finite stress checks, not proof of the continuum theorem',
              'cases': results,
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()

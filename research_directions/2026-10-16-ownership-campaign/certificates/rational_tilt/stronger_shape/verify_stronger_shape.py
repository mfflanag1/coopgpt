#!/usr/bin/env python3
"""Exact finite diagnostics; continuous claims are proved in the theorem file."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
from random import Random
import json

BASE = Path(__file__).parent
COUNTS = {'profiles': 0, 'coalitions': 0, 'own_comparisons': 0,
          'balance_boundary_comparisons': 0, 'attainers': 0,
          'balance_identities': 0, 'shape_inequalities': 0, 'balance_inequalities': 0,
          'dominant_long_bounds': 0, 'negative_controls': 0}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def f(s):
    s = Q(s)
    return Q(0) if s <= Q(2, 3) else (3*s-2)**2/(5*(3*s-1))


def df(s):
    s = Q(s)
    return Q(0) if s <= Q(2, 3) else Q(3, 5)-Q(3, 5)/(3*s-1)**2


def quartic(s):
    return -162*s**4+306*s**3-255*s**2+104*s-13


def g(s):
    base = Q(1, 8) if s <= Q(1, 2) else (1+s)**3/(54*s)
    return (1-2*f(s))*base


def rule(reports, scale=Q(1)):
    n = len(reports)
    totals = [sum(row[j] for row in reports) for j in (0, 1)]
    short = 0 if totals[0] <= totals[1] else 1
    A = totals[short]
    if A == 0:
        return (Q(0),)*n
    x = [row[short] for row in reports]
    d = [min(row[1-short], A) for row in reports]
    M, D, L = max(x), sum(d), max(d)
    caps = sorted([M]+[v for v in d if v > 0])
    target = A+M
    prefix = Q(0)
    previous = Q(0)
    for k, cap in enumerate(caps):
        water = (target-prefix)/(len(caps)-k)
        if previous <= water <= cap:
            break
        prefix += cap
        previous = cap
    else:
        raise RuntimeError('water level not found')
    require(sum(min(v, water) for v in caps) == target, 'water equation')
    P = Q(1)
    for v in caps:
        P *= min(v, water)/v
    h = Q(1, 2)+scale*(f(L/D)-f(M/A))
    p = h*P
    return tuple((1-p)*a+p*b for a, b in zip(x, d))


def isolation():
    lo, hi = Q(2, 3), Q(1)
    for _ in range(150):
        mid = (lo+hi)/2
        if quartic(mid) > 0:
            lo = mid
        else:
            hi = mid
    require(quartic(lo) > 0 and quartic(hi) < 0, 'quartic root isolation')
    lower = 1+g(lo)
    upper = 1+(1-2*f(lo))*(1+hi)**3/(54*hi)
    require(Q('1.1297546061279509') < lower < upper < Q('1.1297546061279511'),
            'funding decimal enclosure')
    return lo, hi, lower, upper


def check_profile(r, y, bound, all_coalitions=True):
    COUNTS['profiles'] += 1
    T = min(sum(row[j] for row in r) for j in (0, 1))
    require(all(v >= 0 for v in y), ('nonnegative', r, y))
    require(sum(y) <= bound*T, ('funding', r, y))
    if all_coalitions:
        for mask in range(1 << len(r)):
            value = min(sum(r[i][j] for i in range(len(r)) if mask >> i & 1) for j in (0, 1))
            payment = sum(y[i] for i in range(len(r)) if mask >> i & 1)
            require(payment >= value, ('coverage', r, mask, y))
            COUNTS['coalitions'] += 1


def run():
    lo, hi, lower, upper = isolation()
    best = Q(0)
    best_profile = None
    for n in range(1, 5):
        values = tuple(product((Q(0), Q(1), Q(2)), repeat=2))
        states = tuple(product(values, repeat=n))
        payments = {r: rule(r) for r in states}
        for r, y in payments.items():
            check_profile(r, y, upper)
            T = min(sum(row[j] for row in r) for j in (0, 1))
            if T and sum(y)/T > best:
                best, best_profile = sum(y)/T, r
            for i in range(n):
                for j in (0, 1):
                    if r[i][j] == 2:
                        continue
                    high = [list(row) for row in r]
                    high[i][j] += 1
                    high = tuple(tuple(row) for row in high)
                    require(payments[high][i] >= y[i], ('grid own monotonicity', r, high, i))
                    COUNTS['own_comparisons'] += 1
    rng = Random(16613077)
    for trial in range(5000):
        n = 2+trial%7
        r = tuple((Q(rng.randrange(25), rng.randrange(1, 14)),
                   Q(rng.randrange(25), rng.randrange(1, 14))) for _ in range(n))
        y = rule(r)
        check_profile(r, y, upper, all_coalitions=trial < 300)
        i, j = rng.randrange(n), rng.randrange(2)
        high = [list(row) for row in r]
        high[i][j] += Q(1, rng.choice([10, 100, 1000, 1000000]))
        high = tuple(tuple(row) for row in high)
        require(rule(high)[i] >= y[i], ('random small own increment', r, high, i))
        COUNTS['own_comparisons'] += 1
    for k in range(50, 101):
        s = Q(k, 100)
        r = ((s, Q(0)), (1-s, Q(0)), (Q(0), Q(1)), (Q(0), Q(1)))
        require(sum(rule(r)) == 1+g(s), ('exact concentration attainer', s))
        COUNTS['attainers'] += 1
    for k in range(1, 100):
        s = Q(2, 3)+Q(k, 300)
        v = 3*s-2
        require((1+s)*(f(1)-f(s))/(1-s)-s*df(s) == Q(1, 2)-v/(5*(1+v)**2), 'balance identity')
        COUNTS['balance_identities'] += 1
        for gap in [Q(1, 100), Q(1, 1000000)]:
            L = 1-gap
            if L <= s:
                continue
            balanced = ((s, Q(0)), (1-s, Q(0)), (Q(0), L), (Q(0), 1-L))
            low = list(balanced)
            low[0] = (s-Q(1, 10**10), Q(0))
            low = tuple(low)
            require(rule(balanced)[0] >= rule(low)[0], ('balance derivative boundary', s, L))
            swapped = tuple((b, a) for a, b in balanced)
            require(rule(balanced) == rule(swapped), 'orientation tie agreement')
            COUNTS['balance_boundary_comparisons'] += 1
    for k in range(1, 101):
        v = Q(k, 100)
        t = (v+2)/3
        require(0 <= df(t) <= Q(1, 2), ('shape derivative', t))
        require(df(t)*t*(1-t) <= Q(1, 20), ('shape quartic bound', t))
        require(df(t)*t*(1-t) <= Q(4, 5)*(t-Q(2, 3)), ('long nonmaximum bound', t))
        cost = (2*f(t)+df(t)*t*(1-t)/2)/(t-Q(2, 3))
        gap = (1-v)*(2+2*v-v*v)/(10*(1+v)**2)
        require(Q(3, 5)-cost == gap >= 0, ('cost identity', t))
        COUNTS['shape_inequalities'] += 4
    for a in range(1, 101):
        s = Q(a, 100)
        for b in range(a, 101):
            L = Q(b, 100)
            rhs = (f(L)-f(s))*(L+s)-L*s*(1-s)*df(s)
            require(rhs <= (L-s)/2, ('full balance inequality', s, L))
            COUNTS['balance_inequalities'] += 1
        for b in range(0, 51):
            R = Q(b, 100)
            h = Q(1, 2)+f(1/(1+R))-f(s)
            if s <= 1-R:
                excess = h*R*(1-R)
                require(excess <= Q(1, 8), ('inactive dominant-long budget', s, R))
            else:
                K = h*(1+s-3*R)-Q(9, 5)*(1-2*R)*R*(1+s-R)/((1+R)**2*(2-R)**2)
                require(K >= Q(7, 20)*(1-2*R), ('active dominant-long derivative', s, R))
                excess = h*R*(1+s-R)**2/(4*s)
                require(excess <= g(s), ('active dominant-long budget', s, R))
            COUNTS['dominant_long_bounds'] += 1
    high = ((Q(3, 4), Q(0)), (Q(1, 4), Q(0)),
            (Q(0), Q(999999, 1000000)), (Q(0), Q(1, 1000000)))
    low = list(high)
    low[0] = (Q(3, 4)-Q(1, 10**9), Q(0))
    low = tuple(low)
    gap = rule(high, Q(11, 10))[0]-rule(low, Q(11, 10))[0]
    require(gap < 0, 'over-scaled tilt negative control')
    COUNTS['negative_controls'] += 1
    result = {'status': 'PASS: exact finite diagnostics plus rational root enclosure',
              'scope': 'Finite tests do not prove all-real incentives or the funding theorem.',
              'counts': COUNTS, 'root_interval': [str(lo), str(hi)],
              'gamma_interval': [str(lower), str(upper)], 'gamma_decimal': float(lower), 'root_decimal': float(lo),
              'largest_ternary_grid_factor': str(best),
              'largest_grid_profile': [[str(v) for v in row] for row in best_profile],
              'over_scaled_negative_control': {'scale': '11/10', 'high_minus_low_payment': str(gap)}}
    (BASE/'stronger-shape-verification.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    run()

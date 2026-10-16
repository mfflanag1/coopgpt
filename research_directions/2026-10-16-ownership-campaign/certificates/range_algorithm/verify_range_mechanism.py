#!/usr/bin/env python3
"""Independent floating-point falsification of the mixed-owner range mechanism.

All finite physical domains are explicit rational Cartesian grids, converted to
binary floats for math.exp. These are numerical stress tests, not exact proofs
or guarantees about implementations of truthful payments. No sparse/root
verifier code is imported. Coalition worth and maximizer witnesses are rebuilt
directly from definitions. Adjacent own-coordinate comparisons generate every
componentwise own-bundle comparison inside each tested Cartesian domain.
"""
from fractions import Fraction
from itertools import product
from pathlib import Path
import argparse
import hashlib
import json
import math
import random


C0 = 1 + 1/(2*math.e)
EPS = 2e-10


def require(condition, message):
    if not condition:
        raise ValueError(message)


def primitive(a, b):
    """Direct definition, with explicit zero and equality conventions."""
    A, B = math.fsum(a), math.fsum(b)
    if min(A, B) <= 0:
        return (0.,)*len(a)
    if A == B:
        return tuple((x+y)/2 for x, y in zip(a, b))
    if A < B:
        rho = math.fsum(min(y, A) for y in b)/A
        q = math.exp(1-rho)/2
        return tuple((1-q)*x+q*min(y, A) for x, y in zip(a, b))
    rho = math.fsum(min(x, B) for x in a)/B
    q = math.exp(1-rho)/2
    return tuple((1-q)*y+q*min(x, B) for x, y in zip(a, b))


def abstract_options(h, p, beta, cap, i):
    """Each closed-form region paired with a directly feasible maximizing b."""
    n, H, P = len(h), math.fsum(h), math.fsum(p)
    scale = 1+H+P+cap+beta
    require(beta+EPS*scale >= p[i], 'Own upper account below lower account')
    pm = math.fsum(p[k] for k in range(n) if k != i)
    require(cap+EPS*scale >= beta+pm, 'Own upper account not feasible')
    if H == 0:
        return [{'region': 'zero', 'value': 0., 'b': tuple(p)}]
    if n == 1:
        return [{'region': 'single', 'value': min(H, beta), 'b': (beta,)}]
    a, options = h[i], []
    other = next(k for k in range(n) if k != i)
    if P <= H:
        upper = min(cap, H)
        total = upper if beta <= a else min(upper, beta+pm)
        own = min(beta, total-pm)
        q = (math.exp(1-math.fsum(min(x, total) for x in h)/total)/2
             if total > 0 else 0.)
        value = (1-q)*own+q*min(a, total) if total > 0 else 0.
        b = list(p)
        b[i] = own
        b[other] += total-math.fsum(b)
        options.append({'region': 'short', 'value': value, 'b': tuple(b),
                        'total': total, 'rho': None if total == 0 else
                        math.fsum(min(x, total) for x in h)/total})
    if cap >= H:
        d = min(beta, H)
        b = list(p)
        b[i] = beta
        if d >= a:
            s = math.fsum(min(p[k], H) for k in range(n) if k != i)
            rho = max(1., (d+s)/H)
            b[other] += max(0., H-math.fsum(b))
            region = 'long-positive'
        else:
            waste = math.fsum(max(0., p[k]-H) for k in range(n) if k != i)
            rho = min((d+(n-1)*H)/H, (cap-waste)/H)
            remaining = max(0., cap-math.fsum(b))
            for k in range(n):
                if k == i:
                    continue
                increment = min(remaining, max(0., H-b[k]))
                b[k] += increment
                remaining -= increment
            region = 'long-negative'
        options.append({'region': region,
                        'value': a+math.exp(1-rho)*(d-a)/2,
                        'b': tuple(b), 'rho': rho})
    require(options, 'No region for nonempty domain')
    return options


def inspect_options(h, p, beta, cap, i, options):
    scale = 1+math.fsum(h)+cap
    discrepancy = 0.
    for option in options:
        b = option['b']
        require(all(x+EPS*scale >= y for x, y in zip(b, p)),
                f'Witness violates lower account: {h,p,beta,cap,i,option}')
        require(b[i] <= beta+EPS*scale and math.fsum(b) <= cap+EPS*scale,
                f'Witness violates ceiling: {h,p,beta,cap,i,option}')
        if option['region'] == 'short':
            require(math.fsum(b) <= math.fsum(h)+EPS*scale,
                    'Short witness lies outside short region')
        elif option['region'].startswith('long'):
            require(math.fsum(b)+EPS*scale >= math.fsum(h),
                    'Long witness lies outside long region')
        direct = primitive(h, b)[i]
        error = abs(direct-option['value'])
        discrepancy = max(discrepancy, error/scale)
        require(error <= EPS*scale,
                f'Witness does not attain region formula: {h,p,beta,cap,i,option,direct}')
    return discrepancy


def unpack(profile, n, m):
    width = 2*m+1
    h = [profile[i*width:i*width+m] for i in range(n)]
    ell = [profile[i*width+m:i*width+2*m] for i in range(n)]
    p = [profile[(i+1)*width-1] for i in range(n)]
    return h, ell, p


def physical_worth(profile, n, m, mask):
    h, ell, p = unpack(profile, n, m)
    members = [i for i in range(n) if mask & (1 << i)]
    hardware = math.fsum(h[i][j] for i in members for j in range(m))
    local = math.fsum(min(math.fsum(h[i][j] for i in members),
                         math.fsum(ell[i][j] for i in members)) for j in range(m))
    return min(hardware, math.fsum(p[i] for i in members)+local)


def payments(profile, n, m, inspect=True):
    h, ell, p = unpack(profile, n, m)
    local_payments = [primitive([h[i][j] for i in range(n)],
                                [ell[i][j] for i in range(n)]) for j in range(m)]
    z = [math.fsum(row[i] for row in local_payments) for i in range(n)]
    M = math.fsum(min(math.fsum(h[i][j] for i in range(n)),
                      math.fsum(ell[i][j] for i in range(n))) for j in range(m))
    H = [math.fsum(row) for row in h]
    K = math.fsum(p)+C0*M
    result, discrepancy, regions = [], 0., {}
    for i in range(n):
        options = abstract_options(H, p, p[i]+z[i], K, i)
        result.append(max(item['value'] for item in options))
        if inspect:
            discrepancy = max(discrepancy, inspect_options(H, p, p[i]+z[i], K, i, options))
        for item in options:
            regions[item['region']] = regions.get(item['region'], 0)+1
    return tuple(result), discrepancy, regions


def finite_grid(n, m, rational_levels):
    levels = tuple(float(Fraction(x)) for x in rational_levels)
    require(levels == tuple(sorted(set(levels))) and min(levels) >= 0,
            'Levels must be strictly increasing and nonnegative')
    d = n*(2*m+1)
    profiles = list(product(levels, repeat=d))
    lookup = {b: q for q, b in enumerate(profiles)}
    all_payments, discrepancy, regions = [], 0., {}
    for b in profiles:
        y, error, current = payments(b, n, m)
        all_payments.append(y)
        discrepancy = max(discrepancy, error)
        for key, value in current.items():
            regions[key] = regions.get(key, 0)+value
    coalitions = transitions = zeros = 0
    min_coalition = min_incentive = 0.
    max_factor, maximizer = 0., None
    for q, b in enumerate(profiles):
        y = all_payments[q]
        T = physical_worth(b, n, m, (1 << n)-1)
        scale = 1+T+math.fsum(b)
        require(min(y) >= -EPS*scale, 'Negative payment')
        if T == 0:
            require(abs(math.fsum(y)) <= EPS*scale, 'Nonzero payment at zero production')
            zeros += 1
        else:
            factor = math.fsum(y)/T
            require(factor <= 7/4+EPS*scale/T, f'Budget violation: {b,y,T}')
            if factor > max_factor:
                max_factor, maximizer = factor, {'profile': b, 'payments': y, 'production': T}
        for mask in range(1 << n):
            slack = math.fsum(y[i] for i in range(n) if mask & (1 << i))-physical_worth(b, n, m, mask)
            min_coalition = min(min_coalition, slack/scale)
            require(slack >= -EPS*scale, f'Coalition violation: {b,y,mask,slack}')
            coalitions += 1
        for j in range(d):
            pos = levels.index(b[j])
            if pos+1 == len(levels):
                continue
            high = list(b)
            high[j] = levels[pos+1]
            high = tuple(high)
            owner = j//(2*m+1)
            slack = all_payments[lookup[high]][owner]-y[owner]
            min_incentive = min(min_incentive, slack/scale)
            require(slack >= -EPS*scale, f'Incentive violation: {b,high,owner,slack}')
            transitions += 1
    return {'status': 'NUMERICAL PASS', 'owners': n, 'branches': m,
            'rational_levels': list(rational_levels), 'profiles': len(profiles),
            'coalitions': coalitions, 'adjacent_own_coordinate_reports': transitions,
            'zero_production_profiles': zeros, 'region_attainment_checks': regions,
            'max_scaled_attainment_discrepancy': discrepancy,
            'min_scaled_coalition_slack': min_coalition,
            'min_scaled_incentive_slack': min_incentive,
            'max_observed_funding_factor': max_factor, 'maximizer': maximizer}


def opposing_grid(h, p, beta, cap, i, resolution):
    """Enumerate own-account fractions, then a simplex of other extra accounts."""
    n = len(h)
    others = [k for k in range(n) if k != i]
    require(n <= 4, 'Keep exhaustive simplex dimension bounded')
    best, checked = 0., 0
    for own_step in range(resolution+1):
        c = p[i]+(beta-p[i])*own_step/resolution
        spare = max(0., cap-c-math.fsum(p[k] for k in others))
        for allocation in product(range(resolution+1), repeat=len(others)):
            if sum(allocation) > resolution:
                continue
            b = list(p)
            b[i] = c
            for k, step in zip(others, allocation):
                b[k] += spare*step/resolution
            best = max(best, primitive(h, b)[i])
            checked += 1
    return best, checked


def abstract_tests(trials=1200, seed=16102026):
    rng = random.Random(seed)
    cases = []
    # Exact account-space boundaries and long-account overflow, independent of
    # physical z. The own ceiling always satisfies beta+P_minus<=K.
    for h in ((0.,1.), (1.,0.), (1.,1.), (0.,0.), (1.,2.,0.), (1.,)):
        n, H = len(h), math.fsum(h)
        for p in product((0., H/2, H, 2*H), repeat=n):
            P = math.fsum(p)
            for K in sorted(set((P, max(P,H), P+H, P+2*H))):
                for i in range(n):
                    for beta in sorted(set((p[i], p[i]+(K-P)/2, p[i]+K-P))):
                        cases.append((h,p,beta,K,i))
                    if p[i] <= h[i] <= p[i]+K-P:
                        cases.append((h,p,h[i],K,i))
    for _ in range(trials):
        n = rng.randrange(2, 9)
        h = tuple(0. if rng.random()<.2 else 10**rng.uniform(-3,3) for _ in range(n))
        p = tuple(0. if rng.random()<.3 else 10**rng.uniform(-3,3) for _ in range(n))
        P, H = math.fsum(p), math.fsum(h)
        K = max(P,H) if rng.random()<.25 else P+10**rng.uniform(-3,3)
        i = rng.randrange(n)
        beta = p[i]+rng.random()*(K-P)
        cases.append((h,p,beta,K,i))
    max_discrepancy = max_grid_excess = 0.
    grid_vectors = 0
    regions = {}
    for q, (h,p,beta,K,i) in enumerate(cases):
        options = abstract_options(h,p,beta,K,i)
        max_discrepancy = max(max_discrepancy, inspect_options(h,p,beta,K,i,options))
        for option in options:
            regions[option['region']] = regions.get(option['region'], 0)+1
        if len(h) <= 3 and (q % 7 == 0 or q >= len(cases)-50):
            direct, checked = opposing_grid(h,p,beta,K,i,12)
            grid_vectors += checked
            formula = max(item['value'] for item in options)
            scale = 1+math.fsum(h)+K
            max_grid_excess = max(max_grid_excess, (direct-formula)/scale)
            require(direct <= formula+EPS*scale,
                    f'Feasible opposing vector exceeds formula: {h,p,beta,K,i,direct,formula}')
    return {'status': 'NUMERICAL PASS', 'seed': seed, 'abstract_cases': len(cases),
            'region_attainment_checks': regions, 'feasible_grid_vectors': grid_vectors,
            'max_scaled_attainment_discrepancy': max_discrepancy,
            'max_scaled_grid_value_above_formula': max_grid_excess}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owners', type=int, default=2)
    parser.add_argument('--branches', type=int, default=1)
    parser.add_argument('--levels', default='0,1,2')
    parser.add_argument('--abstract', action='store_true')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = (abstract_tests() if args.abstract else
              finite_grid(args.owners, args.branches, tuple(args.levels.split(','))))
    result['numeric_scope'] = 'Binary floats with math.exp, scaled tolerance 2e-10; not an exact certificate.'
    result['script_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))

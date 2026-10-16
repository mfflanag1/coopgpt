#!/usr/bin/env python3
"""Independent finite floating falsification, not a universal certificate."""
from math import exp
from pathlib import Path
from random import Random
import json

R = Random(16612187)
BASE = Path(__file__).parent
c = .5 / exp(1)
C = 1 + c
kappa = .7 - exp(1) / 5
kappa_p = (7*c-1)**2 / (24*c)


def require(ok, text):
    if not ok:
        raise AssertionError(text)


def primitive(a, b):
    ta, tb = sum(a), sum(b)
    t = min(ta, tb)
    if not t:
        return [0.] * len(a)
    short, long = (a, b) if ta <= tb else (b, a)
    capped = [min(v, t) for v in long]
    q = .5 * exp(1 - sum(capped) / t)
    return [(1-q)*x+q*y for x, y in zip(short, capped)]


def data(a, b):
    pay = primitive(a, b)
    t = min(sum(a), sum(b))
    if not t:
        return pay, 0., 0., 1.
    long = b if sum(a) <= sum(b) else a
    rho = sum(min(v, t) for v in long) / t
    return pay, t, max(0., C*t-sum(pay)), rho


def shares(n):
    x = [R.random()**R.choice([1, 2, 5]) for _ in range(n)]
    if R.randrange(4) == 0:
        x = [0.] * n
        x[R.randrange(n)] = 1.
    total = sum(x)
    return [v/total for v in x]


def branch(n):
    rho = R.choice([v for v in [1., 1.01, 1.1, 1.5, 1.8, 1.99, 2., 2.01, 2.5, 4., float(n)] if v <= n])
    long = [0.] * n
    left = rho
    for i in R.sample(range(n), n):
        x = min(1., left) * R.random()
        long[i] = x
        left -= x
    for i in R.sample(range(n), n):
        add = min(1.-long[i], left)
        long[i] += add
        left -= add
    require(abs(left) < 1e-10, 'invalid capped-ratio generator')
    long = [v + (R.choice([0., .5, 2.]) if v > 1-1e-12 else 0.) for v in long]
    return shares(n), long


def local_checks():
    profile_count = 0
    deviations = switches = long_checks = high_ratio_checks = 0
    worst_retention = worst_long = -1e100
    positive_short_owners = positive_long_owners = 0
    for _ in range(650):
        n = R.randrange(2, 15)
        short, long = branch(n)
        full, _, delta, rho = data(short, long)
        total = sum(full)
        owner_defects = [0.] * n
        short_gainers = set()
        long_gainers = set()
        for i in range(n):
            for trial in range(32):
                ss, ll = short[:], long[:]
                fs = R.choice([0., .01, .25, .5, .8, .99, 1.]) if trial < 20 else R.random()
                fl = R.choice([0., .01, .25, .5, .8, .99, 1.]) if trial < 20 else R.random()
                ss[i] *= fs
                intermediate, ti, di, ri = data(ss, ll)
                fi = intermediate[i]-sum(intermediate)/3
                f0 = full[i]-total/3
                if fi > f0 + 2e-11:
                    short_gainers.add(i)
                ll[i] *= fl
                final, _, _, _ = data(ss, ll)
                ff = final[i]-sum(final)/3
                if ff > fi + 2e-11:
                    long_gainers.add(i)
                if ti:
                    long_bound = 13*di/42 if ri < 2 else 0.
                    residual = ff-fi-long_bound
                    worst_long = max(worst_long, residual)
                    require(residual <= 2e-10, ('LONG bound', short, long, i, fs, fl, ri, residual))
                    long_checks += 1
                switches += int(sum(ll) < sum(ss)-1e-12)
                defect = max(0., ff-f0)
                owner_defects[i] = max(owner_defects[i], defect)
                if rho >= 2-1e-11:
                    require(defect <= 2e-10, ('high-ratio retention', rho, defect))
                    high_ratio_checks += 1
                deviations += 1
        require(len(short_gainers) <= 1, ('SHORT count', short_gainers))
        require(len(long_gainers) <= 2, ('LONG count', long_gainers))
        residual = sum(owner_defects)-20*delta/21
        worst_retention = max(worst_retention, residual)
        require(residual <= 2e-10, ('aggregate retention', rho, residual))
        positive_short_owners += len(short_gainers)
        positive_long_owners += len(long_gainers)
        profile_count += 1
    return dict(full_branch_profiles=profile_count, whole_owner_deviations=deviations,
                post_switch_reports=switches, long_stage_checks=long_checks,
                high_ratio_zero_defect_checks=high_ratio_checks,
                observed_short_gaining_owners=positive_short_owners,
                observed_long_gaining_owners=positive_long_owners,
                largest_long_bound_residual=worst_long,
                largest_retention_bound_residual=worst_retention)


def evaluate(h, l, p):
    n, m = len(h), len(h[0])
    z = [0.] * n
    M = dl = dh = 0.
    rhos = []
    for j in range(m):
        v, t, delta, rho = data([row[j] for row in h], [row[j] for row in l])
        z = [x+y for x, y in zip(z, v)]
        M += t
        if t:
            rhos.append(rho)
        if rho <= 2+1e-10:
            dl += delta
        else:
            dh += delta
    H = [sum(row) for row in h]
    b = [x+y for x, y in zip(p, z)]
    return primitive(H, b), z, H, M, dl, dh, rhos


def funding_checks():
    profiles = checks = positive_grid = grid_changes = total_increases = 0
    max_ratio = max_grid_share = 0.
    worst_residual = -1e100
    for _ in range(260):
        n, m = R.randrange(3, 15), R.randrange(1, 6)
        h = [[] for _ in range(n)]
        l = [[] for _ in range(n)]
        for j in range(m):
            a, b = branch(n)
            if R.randrange(2):
                a, b = b, a
            scale = R.choice([.1, .5, 1., 3.])
            for i in range(n):
                h[i].append(a[i]*scale)
                l[i].append(b[i]*scale)
        for i in range(n):
            h[i].append(0.)
            l[i].append(0.)
        M = sum(min(sum(row[j] for row in h), sum(row[j] for row in l)) for j in range(m))
        grid_total = R.choice([0., .01, .1, .5, 1., 3., 10.])*M
        p = [grid_total*x for x in shares(n)]
        full, z, H, M, dl, dh, rhos = evaluate(h, l, p)
        B = grid_total+sum(z)
        deficit = max(0., 2*B-sum(min(x, B) for x in H))
        for i in R.sample(range(n), n):
            add = min(max(0., B-H[i]), deficit)
            h[i][-1] += add
            H[i] += add
            deficit -= add
        require(deficit < 1e-8, 'outer-dominance fill failed')
        full, z, H, M, dl, dh, rhos = evaluate(h, l, p)
        B = grid_total+sum(z)
        require(sum(min(x, B) for x in H) >= 2*B-1e-8, 'outer condition')
        sampled_envelope = full[:]
        for i in range(n):
            for trial in range(32):
                hh, ll, pp = [row[:] for row in h], [row[:] for row in l], p[:]
                if trial < 2*(m+1):
                    target = hh if trial < m+1 else ll
                    target[i][trial % (m+1)] *= R.choice([0., .5, .99])
                else:
                    hh[i] = [x*R.choice([0., .25, .5, .9, 1.]) for x in hh[i]]
                    ll[i] = [x*R.choice([0., .25, .5, .9, 1.]) for x in ll[i]]
                    pp[i] *= R.choice([0., .25, .5, .9, 1.])
                pay, zz, _, _, _, _, _ = evaluate(hh, ll, pp)
                sampled_envelope[i] = max(sampled_envelope[i], pay[i])
                grid_changes += int(pp[i] < p[i])
                total_increases += int(sum(pp)+sum(zz) > B+1e-10)
                checks += 1
        bound = C*B+(20*C/21)*dl+(1+kappa)*dh+kappa_p*grid_total
        alternate = C*C*(grid_total+M)-(C*c-kappa_p)*grid_total-C*dl/21-(c-kappa)*dh
        require(abs(bound-alternate) <= 1e-8*max(1., bound), 'budget identity')
        residual = sum(sampled_envelope)-bound
        worst_residual = max(worst_residual, residual)
        require(residual <= 2e-8*max(1., bound), ('funding bound', residual))
        max_ratio = max(max_ratio, sum(sampled_envelope)/(grid_total+M))
        max_grid_share = max(max_grid_share, grid_total/(grid_total+M))
        profiles += 1
        positive_grid += int(grid_total > 0)
    return dict(full_profiles=profiles, positive_grid_profiles=positive_grid,
                whole_owner_underreports=checks, grid_underreports=grid_changes,
                total_increasing_underreports=total_increases,
                largest_sampled_funding_ratio=max_ratio,
                largest_grid_fraction_of_physical_value=max_grid_share,
                largest_funding_residual=worst_residual)


if __name__ == '__main__':
    result = {'status': 'PASS: finite floating corroboration only',
              'seed': 16612187, 'retention': local_checks(), 'funding': funding_checks(),
              'scope': 'Finite sampled envelopes are lower bounds. Continuous proofs, not these tests, establish the theorem.'}
    path = BASE/'universal-retention-positive-grid-checks.json'
    path.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))

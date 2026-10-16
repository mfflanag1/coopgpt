#!/usr/bin/env python3
"""Finite floating diagnostics for the exact dominant-hardware proof."""
from random import Random
from pathlib import Path
import json
from check_universal_retention_positive_grid import primitive, evaluate, c, C, require

R = Random(16612242)
BASE = Path(__file__).parent


def split(total, n):
    x = [R.random() for _ in range(n)]
    s = sum(x)
    return [total*v/s for v in x]


def accounts(total, own, n, i):
    rest = iter(split(total-own, n-1))
    return [own if j == i else next(rest) for j in range(n)]


def abstract_checks():
    down = up = cross = 0
    worst_down = worst_up = -1e100
    for _ in range(150):
        n = R.randrange(2, 9)
        h = [R.choice([0., .01, .1, .5, 1., 2.])*R.random() for _ in range(n)]
        h[R.randrange(n)] = R.choice([1., 1.01, 2., 10.])
        for i in range(n):
            for b0 in [0., .01, .2, .5, .8, 1.]:
                full = primitive(h, accounts(1., b0, n, i))[i]
                for t in [.01, .1, .25, .5, .75, .99, 1.]:
                    for fraction in [0., .1, .5, .9, 1.]:
                        b = min(b0, t*fraction)
                        actual = primitive(h, accounts(t, b, n, i))[i]
                        eps = max(0., (1-t)/3-(b0-b))
                        residual = actual-full-eps
                        worst_down = max(worst_down, residual)
                        require(residual <= 1e-11, ('dominant down', h, b0, t, b, residual))
                        down += 1
    for _ in range(16000):
        n = R.randrange(2, 10)
        h = split(1., n)
        a = [R.random() for _ in range(n)]
        b = [R.random() for _ in range(n)]
        i = R.randrange(n)
        b[i] = a[i]*R.random()
        G, D = sum(b)-sum(a), a[i]-b[i]
        if G <= 0:
            continue
        actual = primitive(h, b)[i]-primitive(h, a)[i]
        residual = actual-.5*max(0., G-D)
        worst_up = max(worst_up, residual)
        require(residual <= 1e-11, ('cross-pool up', h, a, b, i, residual))
        cross += int(sum(a)<1.<sum(b))
        up += 1
    return dict(total_down_checks=down, total_up_checks=up,
                outer_tie_crossings=cross, largest_down_residual=worst_down,
                largest_up_residual=worst_up)


def funding_checks():
    profiles = checks = cross = below_two = 0
    worst = -1e100
    maxratio = 0.
    for profile in range(220):
        n, m = R.randrange(3, 14), R.randrange(1, 6)
        h = [[0.]*(m+1) for _ in range(n)]
        l = [[0.]*(m+1) for _ in range(n)]
        for j in range(m):
            # Concentrated hardware makes actual total-up crossings common.
            hardware_owner = 0 if profile%2 == 0 else R.randrange(n)
            h[hardware_owner][j] = R.choice([.1, 1., 2.])
            for i in range(n):
                l[i][j] = h[hardware_owner][j]*R.choice([0., .1, .5, 1., 2.])
        p = split(R.choice([0., 0., .1, 1., 5.]), n)
        _, z, H, M, _, _, _ = evaluate(h, l, p)
        if M == 0:
            continue
        B = sum(p)+sum(z)
        owner = 0 if profile%2 == 0 else R.randrange(n)
        h[owner][-1] += max(0., B-H[owner])
        full, z, H, M, dl, dh, _ = evaluate(h, l, p)
        B = sum(p)+sum(z)
        require(max(H) >= B-1e-10, 'dominance generator')
        below_two += int(sum(min(x, B) for x in H) < 2*B-1e-10)
        finite = full[:]
        for i in range(n):
            for trial in range(30):
                hh, ll, pp = [row[:] for row in h], [row[:] for row in l], p[:]
                if trial < 2*(m+1):
                    target = hh if trial < m+1 else ll
                    target[i][trial%(m+1)] *= R.choice([0., .5, .9, .99])
                else:
                    hh[i] = [x*R.choice([0., .5, .99, 1.]) for x in hh[i]]
                    ll[i] = [x*R.choice([0., .5, .99, 1.]) for x in ll[i]]
                    pp[i] *= R.choice([0., .5, .99, 1.])
                pay, zz, _, _, _, _, _ = evaluate(hh, ll, pp)
                finite[i] = max(finite[i], pay[i])
                cross += int(sum(pp)+sum(zz) > sum(H)+1e-10)
                checks += 1
        bound = C*B+(20/21)*dl+dh
        alternate = C*C*(sum(p)+M)-C*c*sum(p)-(C-20/21)*dl-c*dh
        require(abs(bound-alternate) <= 1e-8, 'funding identity')
        residual = sum(finite)-bound
        worst = max(worst, residual)
        require(residual <= 1e-8, ('dominant funding', residual))
        maxratio = max(maxratio, sum(finite)/(sum(p)+M))
        profiles += 1
    return dict(full_profiles=profiles, full_outer_ratio_below_two=below_two,
                whole_owner_deviations=checks,
                restored_outer_pool_crossing_deviations=cross,
                largest_sampled_funding_ratio=maxratio,
                largest_funding_residual=worst)


if __name__ == '__main__':
    result = {'status': 'PASS: floating falsification diagnostics only',
              'abstract': abstract_checks(), 'funding': funding_checks(),
              'scope': 'Sampled envelope maxima are lower bounds; no numerical sample establishes a universal upper bound.'}
    (BASE/'dominant-hardware-funding-checks.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))

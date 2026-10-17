"""Floating diagnostics, not an exact proof or interval certificate."""
import importlib.util
import itertools
import json
import math
from pathlib import Path
import random

base = Path(__file__).parent
spec = importlib.util.spec_from_file_location('two_pool', base / 'check_outside_logarithmic.py')
two = importlib.util.module_from_spec(spec)
spec.loader.exec_module(two)
C = two.C

def require(ok, message):
    if not ok:
        raise ValueError(message)

def payments(xs):
    totals = list(map(sum, zip(*xs)))
    order = sorted(range(len(totals)), key=totals.__getitem__)
    shortest, second = order[:2]
    T = totals[shortest]
    if T == 0:
        return [0.0] * len(xs)
    _, q, _, _ = two.prices(T / totals[second])
    ps = [C*T/a for a in totals]
    ps[shortest] = q
    return [sum(p*a for p, a in zip(ps, row)) for row in xs]

rng = random.Random(17052026)
profiles = coalitions = out_checks = corners = 0
worst_out = 0.0
for r in (2,3,4,5,8,12,24,64):
    for trial in range(400):
        n = rng.randint(2,8)
        xs = [[0.0 if rng.random() < .2 else 10**rng.uniform(-2,2) for _ in range(r)] for _ in range(n)]
        if trial % 7 == 0:
            for row in xs:
                row[1] = row[0]
        if trial % 11 == 0:
            for row in xs:
                row[0] = 0.0
        totals = list(map(sum, zip(*xs)))
        ys = payments(xs)
        scale = max(1., sum(totals))
        tol = 1e-10*scale
        require(sum(ys) <= (1+C*(r-1))*min(totals)+tol, 'budget')
        for _ in range(12):
            chosen = [i for i in range(n) if rng.random()<.6]
            if not chosen:
                chosen=[0]
            held = [sum(xs[i][j] for i in chosen) for j in range(r)]
            high = sum(ys[i] for i in chosen)
            require(high >= min(held)-tol, 'coverage')
            low_xs = [row[:] for row in xs]
            withheld = [0.0]*r
            for i in chosen:
                for j in range(r):
                    low_xs[i][j] *= rng.choice([0., 1., rng.random()])
                    withheld[j] += xs[i][j]-low_xs[i][j]
            low_ys = payments(low_xs)
            slack = high-sum(low_ys[i] for i in chosen)-min(withheld)
            worst_out = min(worst_out,slack)
            require(slack >= -tol, 'full coalition outside production')
            coalitions += 1
            out_checks += 1
        profiles += 1
for r in range(2,9):
    for _ in range(100):
        ratios = sorted([rng.random() for _ in range(r-1)], reverse=True)
        t = ratios[0]
        _,q,_,qp = two.prices(t)
        for alpha in itertools.product((0.,1.),repeat=r):
            g = [q+C*sum(alpha[1:])+alpha[0]*t*qp]
            for j,tj in enumerate(ratios,1):
                g.append(C*tj*(1-alpha[j])-(alpha[0]*t*t*qp if j==1 else 0.))
            require(min(g)>=-1e-11 and sum(g)>=1-1e-11,'directional corner')
            corners +=1
result={'status':'PASS','c_float':C,'profiles':profiles,'coverage_checks':coalitions,
 'full_OUT_checks':out_checks,'derivative_corner_checks':corners,
 'dimensions_tested':[2,3,4,5,8,12,24,64],'minimum_outside_slack_float':worst_out,
 'scope':'floating diagnostics only; analytic proof in MULTIPOOL_OUTSIDE_LOGARITHMIC.txt'}
print(json.dumps(result,indent=2))
(base/'multipool_outside_checks.json').write_text(json.dumps(result,indent=2)+'\n')

#!/usr/bin/env python3
"""Numerical physical-profile boundary and whole-owner report tests."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import random
from verify_range_mechanism import C0, EPS, primitive, unpack, payments, physical_worth, require


def run(seed=16102027, seeds=120):
    rng = random.Random(seed)
    cases = []
    for _ in range(seeds):
        n, m = rng.randrange(1, 7), rng.randrange(1, 5)
        width = 2*m+1
        base = tuple(rng.choice((0., 1/3, 1., 2., 5.)) for _ in range(n*width))
        h, ell, p = unpack(base,n,m)
        H = math.fsum(math.fsum(row) for row in h)
        M = math.fsum(min(math.fsum(h[i][j] for i in range(n)),
                          math.fsum(ell[i][j] for i in range(n))) for j in range(m))
        z = [math.fsum(primitive([h[k][j] for k in range(n)],
                                 [ell[k][j] for k in range(n)])[i]
                       for j in range(m)) for i in range(n)]
        cases.append((n,m,base,'base'))
        targets = [(H,'P=H')]
        if H >= C0*M:
            targets.append((H-C0*M,'K=H'))
        for target, tag in targets:
            b = list(base)
            for i in range(n):
                b[(i+1)*width-1] = 0.
            b[width-1] = target
            cases.append((n,m,tuple(b),tag))
        for i in range(n):
            Hi = math.fsum(h[i])
            if Hi >= z[i]:
                b = list(base)
                b[(i+1)*width-1] = Hi-z[i]
                cases.append((n,m,tuple(b),'B_i=H_i'))
        for j in range(m):
            b = list(base)
            hs = math.fsum(h[i][j] for i in range(n))
            ls = math.fsum(ell[i][j] for i in range(n))
            if hs >= ls:
                b[(n-1)*width+m+j] += hs-ls
            else:
                b[(n-1)*width+j] += ls-hs
            cases.append((n,m,tuple(b),'local tie'))
    counts = {'profiles':len(cases),'coalitions':0,'coordinate_comparisons':0,
              'whole_owner_underreports':0,'null_owner_payments':0}
    tags, min_coalition, min_incentive, max_factor = {}, 0., 0., 0.
    for n,m,b,tag in cases:
        tags[tag] = tags.get(tag,0)+1
        width = 2*m+1
        y = payments(b,n,m)[0]
        T = physical_worth(b,n,m,(1 << n)-1)
        scale = 1+math.fsum(b)+T
        require(math.fsum(y) <= 1.75*T+EPS*scale, f'Budget fails at {n,m,b}')
        if T > 0:
            max_factor = max(max_factor,math.fsum(y)/T)
        for mask in range(1 << n):
            slack = math.fsum(y[i] for i in range(n) if mask & (1 << i))-physical_worth(b,n,m,mask)
            require(slack >= -EPS*scale, f'Coalition fails at {n,m,b,mask,slack}')
            min_coalition = min(min_coalition,slack/scale)
            counts['coalitions'] += 1
        for j in range(len(b)):
            i = j//width
            step = 1e-7*(1+b[j])
            lo, hi = list(b), list(b)
            lo[j] = max(0.,b[j]-step)
            hi[j] = b[j]+step
            low_pay = payments(tuple(lo),n,m)[0][i]
            high_pay = payments(tuple(hi),n,m)[0][i]
            for slack in (y[i]-low_pay,high_pay-y[i]):
                require(slack >= -EPS*scale, f'Boundary incentive fails at {n,m,b,j,slack}')
                min_incentive = min(min_incentive,slack/scale)
                counts['coordinate_comparisons'] += 1
        for i in range(n):
            if not any(b[i*width:(i+1)*width]):
                require(abs(y[i]) <= EPS*scale, 'Null owner paid')
                counts['null_owner_payments'] += 1
            low = list(b)
            for j in range(i*width,(i+1)*width):
                low[j] *= rng.random()
            slack = y[i]-payments(tuple(low),n,m)[0][i]
            require(slack >= -EPS*scale, f'Whole-owner incentive fails at {n,m,b,i,slack}')
            min_incentive = min(min_incentive,slack/scale)
            counts['whole_owner_underreports'] += 1
    return {'status':'NUMERICAL PASS','seed':seed,'counts':counts,'boundary_counts':tags,
            'min_scaled_coalition_slack':min_coalition,
            'min_scaled_incentive_slack':min_incentive,
            'max_observed_funding_factor':max_factor,
            'numeric_scope':'Binary floats with math.exp; perturbations are numerical, not exact incentive proofs.',
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args = parser.parse_args()
    result = run()
    encoded = json.dumps(result,indent=2)+'\n'
    args.output.write_text(encoded)
    print(encoded,end='')

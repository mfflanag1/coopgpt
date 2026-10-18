#!/usr/bin/env python3
"""Independent exact diagnostics for the shared-cardinality rigidity extension."""
from fractions import Fraction as Q
from itertools import product
from math import comb
from pathlib import Path
import json


def choose(n, k):
    return comb(n, k) if 0 <= k <= n else 0


def bernoulli(p, d, t):
    return p**t * (1-p)**(d-t)


def local_marginals(profile, focal, m, k):
    others = [i for i in range(len(profile)) if i != focal]
    d = len(others)
    assert d <= m
    p = Q(k, m)
    hyper = independent = Q(0)
    for bits in product((0, 1), repeat=d):
        t = sum(bits)
        a = sum(profile[i][0] for i, bit in zip(others, bits) if bit)
        b = sum(profile[i][1] for i, bit in zip(others, bits) if bit)
        gain = min(a+profile[focal][0], b+profile[focal][1])-min(a, b)
        hyper += Q(choose(m-d, k-t), choose(m, k))*gain
        independent += bernoulli(p, d, t)*gain
    return hyper, independent


def main():
    tv_cases = 0
    max_tv = Q(0)
    for m in range(1, 41):
        for d in range(min(m, 12)+1):
            for k in range(m+1):
                p = Q(k, m)
                tv = sum(Q(choose(d,t),2)*abs(
                    Q(choose(m-d,k-t),choose(m,k))-bernoulli(p,d,t))
                    for t in range(d+1))
                assert tv <= Q(d*(d-1), 2*m)
                max_tv = max(max_tv, tv)
                tv_cases += 1

    threshold_cases = marginal_error_checks = 0
    for centers in range(1, 5):
        for q in range(2, 5):
            for t in range(centers):
                low = [(Q(1,centers),Q(0))]*centers + [(Q(0),Q(t,centers))] + [(Q(0),Q(1))]*(q-1)
                high = list(low)
                high[centers] = (Q(0),Q(t+1,centers))
                d = len(low)-1
                for padding in range(3):
                    m = d+padding
                    for k in range(m+1):
                        p = Q(k,m)
                        totals = [Q(0),Q(0)]
                        for endpoint, profile in enumerate((low,high)):
                            for focal in range(centers,centers+q):
                                h,b = local_marginals(profile,focal,m,k)
                                assert 0 <= h <= 1 and 0 <= b <= 1
                                assert abs(h-b) <= Q(d*(d-1),2*m)
                                totals[endpoint] += b
                                marginal_error_checks += 1
                        tail = sum(Q(choose(centers,j))*p**j*(1-p)**(centers-j)
                                   for j in range(t+1,centers+1))
                        formula = Q(1,centers)*(1-p)**(q-2)*(1-q*p)*tail
                        assert totals[1]-totals[0] == formula
                        threshold_cases += 1

    actual, bern = local_marginals([(Q(1),Q(0)),(Q(0),Q(1))],0,3,1)
    active_only, _ = local_marginals([(Q(1),Q(0)),(Q(0),Q(1))],0,1,1)
    assert actual == bern == Q(1,3) and active_only == 1
    report = {
        'status':'PASS', 'arithmetic':'fractions.Fraction',
        'scope':'finite diagnostic; full analytic proof in CARDINALITY_AUDIT.txt',
        'hypergeometric_tv_cases':tv_cases, 'largest_tested_tv':str(max_tv),
        'threshold_polynomial_cases':threshold_cases,
        'individual_marginal_error_checks':marginal_error_checks,
        'zero_report_owner_diagnostic':{'fixed_roster_expectation':str(actual),
                                        'active_filtered_expectation':str(active_only)},
    }
    Path(__file__).with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,sort_keys=True))


if __name__ == '__main__':
    main()

"""Exact continuous-interval certificate for the joint-role range bound.
Uses Fraction arithmetic and signed Taylor remainder bounds, no tolerances.
"""
from fractions import Fraction as Q
from math import factorial
import json
from pathlib import Path


def exp_lower(x):
    if x < 0:
        raise ValueError('nonnegative exponent magnitude required')
    return max(Q(0), sum(((-x) ** j / factorial(j) for j in range(20)), Q(0)))


def exp_upper(x):
    if x < 0:
        raise ValueError('nonnegative exponent magnitude required')
    return sum(((-x) ** j / factorial(j) for j in range(11)), Q(0))


def floor_grid(x):
    scale = 10**12
    return Q((x*scale).numerator // (x*scale).denominator, scale)


def main():
    target = Q(69, 40)
    # On[0,1/4], B<=1 and q0>= (1-p-23/125)/2 >11/40.
    # exp(-x)<=1/(1+x), so this elementary bound is sufficient.
    initial = Q(5, 4) + Q(20, 51)
    if initial >= target:
        raise ArithmeticError('initial interval failed')
    rows = []
    for j in range(256):
        lo = Q(1, 4) + Q(3*j, 1024)
        hi = Q(1, 4) + Q(3*(j+1), 1024)
        # q1 increases with p; q0 decreases with p. The objective increases
        # in B,p and decreases in q0, allowing independent endpoint bounds.
        B = 1 - floor_grid(exp_lower(1/lo - 1)/2)
        q0 = floor_grid(exp_lower(hi + Q(23, 125))/2)
        bound = 1 + B*(hi + exp_upper(q0/B)/2)
        if not q0 > 0 or not B > 0 or not bound < target:
            raise ArithmeticError(('interval failed', str(lo), str(hi), str(bound)))
        rows.append({'lo':str(lo), 'hi':str(hi), 'B_upper':str(B),
                     'q0_lower':str(q0), 'upper':str(bound),
                     'gap':str(target-bound)})
    worst = max(rows, key=lambda r:Q(r['upper']))
    result = {'status':'EXACT PASS', 'target':str(target),
              'initial_interval_upper':str(initial), 'intervals':len(rows),
              'worst_interval':worst, 'all_intervals':rows,
              'evidence':'rational intervals and signed Taylor remainders, not sampled maxima'}
    Path(__file__).with_name('joint_role_scalar_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'], 'target':str(target),
                      'intervals':len(rows), 'worst_interval':[worst['lo'],worst['hi']],
                      'worst_upper_decimal_for_display':float(Q(worst['upper'])),
                      'exact_positive_gaps':True}))


if __name__ == '__main__':
    main()

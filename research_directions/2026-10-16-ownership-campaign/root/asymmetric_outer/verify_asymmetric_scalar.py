"""Exact interval proof obligations for the proposed 171/100 range bound.

Rational arithmetic and signed Taylor remainders cover full real intervals.
This verifies scalar budget steps, not the mechanism's incentive proof.
"""
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
import json


def require(condition, message):
    if not condition:
        raise ArithmeticError(message)


def exp_lower(x):
    require(x >= 0, "negative exponent magnitude")
    return max(Q(0), sum(((-x)**j / factorial(j) for j in range(20)), Q(0)))


def exp_upper(x):
    require(x >= 0, "negative exponent magnitude")
    return sum(((-x)**j / factorial(j) for j in range(11)), Q(0))


def floor_grid(x):
    scale = 10**14
    y = x*scale
    return Q(y.numerator//y.denominator, scale)


def main():
    w, v, alpha = Q(49, 100), Q(51, 100), Q(49, 51)
    C, target = Q(148, 125), Q(171, 100)
    low = C*(1+v/alpha*exp_upper(1-alpha/C))
    high = 1+w*Q(57, 40)
    intermediate_power = 2-w+(C-1)
    initial = Q(5, 4)+Q(50, 127)
    e_lower = sum((Q(1, factorial(j)) for j in range(8)), Q(0))
    require(e_lower > Q(125, 46), 'C enclosure needs e > 125/46')
    q0_initial_lower = w*(2-Q(1,4)-C)
    require(q0_initial_lower > Q(27,100), 'initial q0 lower bound')
    for name, bound in [('low_K',low),('high_P',high),
                        ('intermediate_F_less_H',intermediate_power),
                        ('initial_p_interval',initial)]:
        require(bound < target, (name, str(bound)))
    rows = []
    for j in range(3072):
        lo, hi = Q(1,4)+Q(j,4096), Q(1,4)+Q(j+1,4096)
        # W increases in B and p, decreases in q0. B decreases with p;
        # q0 decreases with p. Hence use B(lo), hi, and q0(hi).
        B = 1-floor_grid(v*exp_lower(alpha*(1/lo-1)))
        q0 = floor_grid(w*exp_lower(hi+C-1))
        require(B > 0 and q0 > 0, 'invalid coefficient enclosure')
        upper = 1+B*(hi+exp_upper(q0/B)/2)
        require(upper < target, ('interval failed',str(lo),str(hi),str(upper)))
        rows.append({'lo':str(lo),'hi':str(hi),'B_upper':str(B),
                     'q0_lower':str(q0),'upper':str(upper),'gap':str(target-upper)})
    worst = max(rows, key=lambda row:Q(row['upper']))
    result = {'status':'EXACT PASS','target':str(target),
              'parameters':{'hardware_short_coefficient':str(w),
                            'power_short_coefficient':str(v),'power_short_decay':str(alpha)},
              'other_regime_bounds':{'low_K':str(low),'high_P':str(high),
                                     'intermediate_F_less_H':str(intermediate_power),
                                     'initial_p_interval':str(initial)},
              'elementary_bounds':{'e_lower':str(e_lower),'q0_initial_lower':str(q0_initial_lower)},
              'intervals':len(rows),'worst_interval':worst,'all_intervals':rows,
              'scope':'Continuous scalar interval proof; incentive and coverage proofs separate.'}
    Path(__file__).with_name('asymmetric_scalar_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'target':str(target),
                      'intervals':len(rows),'worst_upper_display':float(Q(worst['upper'])),
                      'low_K_display':float(low)}))


if __name__ == '__main__':
    main()

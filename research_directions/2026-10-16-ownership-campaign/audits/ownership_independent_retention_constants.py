#!/usr/bin/env python3
"""Independent exact rational checks for the global-retention audit."""
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
import json


def require(condition, label):
    if not condition:
        raise ArithmeticError(label)


def taylor(x, degree):
    return sum((x**j / factorial(j) for j in range(degree+1)), Q())


def main():
    checks = {}
    def above(label, left, right):
        require(left > right, label)
        checks[label] = str(left-right)
    above('e_lower_19_over_7', taylor(Q(1), 5), Q(19, 7))
    above('e_lower_8_over_3', taylor(Q(1), 5), Q(8, 3))
    above('e_upper_87_over_32', Q(87, 32), taylor(Q(1), 6)+Q(1, 4410))
    above('retention_threshold', taylor(Q(4, 5), 4), Q(221, 100))
    above('low_ratio_slack', Q(16, 87)-Q(2, 5)/taylor(Q(4, 5), 5), Q(1, 250))
    exp_fifth_upper = Q(6, 5)+Q(1, 50)/(1-Q(1, 15))
    require(exp_fifth_upper == Q(171, 140), 'geometric exponential bound')
    above('exp_six_fifths_upper', Q(10, 3), Q(87, 32)*exp_fifth_upper)
    above('two_sided_small_total_margin', Q(1, 6), Q(7, 38)*Q(51, 70))
    margin = Q(31, 114)-Q(51, 190)
    require(margin == Q(1, 285), 'two-sided large-total identity')
    above('two_sided_large_total_margin', margin, Q())
    above('outer_199_over_100_coefficient', taylor(Q(99, 100), 4), Q(8, 3))
    above('outer_neighborhood_small_margin', Q(1, 6), Q(3, 16)*Q(51, 70))
    above('outer_neighborhood_large_margin', Q(13, 48), Q(1020, 3781))
    above('positive_charge_coefficient_comparison', taylor(Q(4, 5), 1), Q(3, 2))
    require(Q(1, 3)**2/(4*(1-Q(1, 3))) == Q(1, 24), 'triangle area coefficient')
    out = dict(status='EXACT RATIONAL PASS', strict_inequalities=len(checks), gaps=checks,
               scope='Constant/algebra corroboration of analytical audit; no finite sampling promoted to an all-profile proof.')
    Path(__file__).with_name('ownership_independent_retention_constants.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(out))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Exact polynomial arithmetic for the stated two-dimensional event integrals."""
from fractions import Fraction as Q
import json


def require(test, message):
    if not test:
        raise RuntimeError(message)


def integral(coefficients, lower=Q(0), upper=Q(1)):
    return sum(a*(upper**(k+1)-lower**(k+1))/Q(k+1)
               for k, a in enumerate(coefficients))


f_half = 1-Q(1, 2)/2-Q(1, 2)**2/6
f_one = integral((Q(0), Q(1, 2), Q(1, 2), -Q(1, 6)))
f_two = integral((Q(0), Q(1, 2), Q(1, 2)))/4
require((f_half, f_one, f_two) == (Q(17, 24), Q(3, 8), Q(5, 48)), 'event integrals')
rows = []
for t, x, y in ((Q(1), f_one, f_one), (Q(2), f_two, f_half)):
    z = 1-x-y
    p = (x, y+z, x+z, y)
    require(all(p[u]+p[v] >= 1 for u, v in ((0, 1), (1, 2), (2, 3))), 'average dual feasibility')
    rows.append({'t': t, 'cover_probabilities': (x, y, z), 'expected_prices': p,
                 'owner_A_payment': t*(p[0]+p[2])})
require(rows[0]['owner_A_payment'] == 1 and rows[1]['owner_A_payment'] == Q(19, 24), 'payments')
require(rows[0]['owner_A_payment']-rows[1]['owner_A_payment'] == Q(5, 24), 'profitable underreport')
print(json.dumps({'status': 'PASS', 'scope': 'Exact arithmetic checks of analytic event integrals and incentive counterexample',
                  'profiles': rows, 'withholding_gain': Q(5, 24)}, default=str, indent=2))

#!/usr/bin/env python3
"""Exact rational verification of constants, not a replacement for the proof."""
from fractions import Fraction as F
from math import factorial
import json

def require(condition, name, details=None):
    if not condition:
        raise RuntimeError(name)
    return {'check': name, 'passed': True, 'details': details}

checks=[]
e_lo=sum((F(1,factorial(j)) for j in range(9)),F(0))
# Tail from term 9: successive ratios are at most 1/10.
e_hi=e_lo+F(1,factorial(9))*F(10,9)
checks.append(require(e_hi<F(68,25), 'e < 68/25', str(e_hi)))
checks.append(require(e_hi<F(11,4), 'e < 11/4'))
checks.append(require(e_lo**3>20, 'log 20 < 3', str(e_lo**3)))
checks.append(require(F(80,73)<F(11,10), 'A < 11/10'))
B_lo=1-F(3,4)+F(3,4)**2/2-F(3,4)**3/6
checks.append(require(B_lo==F(59,128), 'B Taylor lower = 59/128'))
bound=1+F(11,10)**2/(2*(F(11,10)+B_lo))
checks.append(require(bound==F(6931,4995), 'funding rational value', str(bound)))
checks.append(require(bound<F(7,5), 'funding < 7/5', str(F(7,5)-bound)))
checks.append(require(F(161,136)**2>F(7,5), '7/5 < C^2 via e < 68/25'))
print(json.dumps({'status':'PASS','arithmetic':'fractions.Fraction','checks':checks},indent=2))

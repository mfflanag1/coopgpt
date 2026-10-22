#!/usr/bin/env python3
"""Exact finite calibration for the all-parameter proof in the sibling note."""
from fractions import Fraction as F
from math import comb, factorial
from itertools import permutations
import json


def probability(r, k):
    return sum((F((-1)**j * comb(r, j), k*j+1) for j in range(r+1)), F(0))


def rank_probability(r, k):
    n = r*k+1
    good = 0
    for ranks in permutations(range(n)):
        if all(ranks[0] <= max(ranks[1+l*k:1+(l+1)*k]) for l in range(r)):
            good += 1
    return F(good, factorial(n))


def lex_formula(veto, petals):
    sums = [sum(p, F(0)) for p in petals]
    m = min(sums)
    a = veto/(veto+m)
    x = [a] + [(1-a)*w/s for p, s in zip(petals, sums) for w in p]
    assert all(a+sum(x[1+l*len(p):1+(l+1)*len(p)], F(0)) == 1
               for l, p in enumerate(petals))
    assert sum(x, F(0)) == (veto+len(petals)*m)/(veto+m)
    return sum(x, F(0))


records=[]
for r,k in [(1,1),(1,2),(2,1),(2,2),(2,3),(3,2)]:
    p=probability(r,k)
    assert p == rank_probability(r,k)
    records.append({'r':r,'k':k,'rank_probability':str(p)})
for r in range(1,101):
    k=(4*r-1).bit_length()
    p=probability(r,k)
    assert p >= F(3,8)
    assert F(1,2)*(1-F(1,2**k))**r >= F(3,8)
    assert (r+1)*p/2 >= F(3*(r+1),16)
for veto, petals in [
    (F(3,7), [[F(1,5),F(2,3)],[F(4,9),F(2,11)]]),
    (F(1,17), [[F(1),F(2),F(3)],[F(1,2),F(1,3),F(1,4)]]),
]:
    lex_formula(veto,petals)
print(json.dumps({'status':'PASS','exact_rank_checks':records,
                  'rational_parameter_checks':100,
                  'scope':'finite calibration; general proof in sibling txt'},indent=2))

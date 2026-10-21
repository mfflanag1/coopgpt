#!/usr/bin/env python3
"""Exact independent replay of all-real direct-F generator preservation.
This finite check supports, but does not replace, the general proof.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json

N = 6
veto = 0
rows = [frozenset([0,1,2]), frozenset([0,2,3]),
        frozenset([0,1,3]), frozenset([0,4,5])]
coalitions = [frozenset(i for i in range(N) if mask >> i & 1)
              for mask in range(1 << N)]
full = [F(1)]*len(rows)
arrays = [[F(1) if j == veto or j not in row else F(((r+j)%3)+1,4)
           for r,row in enumerate(rows)] for j in range(N)]

def game(array, coalition):
    return max([array[r] for r,row in enumerate(rows) if row <= coalition]+[F(0)])

# Directly construct every linear form; no generator-preservation formula
# is used on the left side of the comparison.
forms = []
for array in [full]+arrays:
    forms.append([tuple(F(1) if i not in A else game(array,A) if i == veto else F(0)
                        for i in range(N)) for A in coalitions[1:]])

checks = 0
for j,t,z,S in product(range(N), [F(0),F(1,3),F(1)],
                       [F(0),F(2,5),F(1)], coalitions):
    X = [(t if i == j else F(1)) if i in S else F(0) for i in range(N)]
    minima = [min(sum(h[i]*X[i] for i in range(N)) for h in family)
              for family in forms]
    actual = min([minima[0]]+[minima[k+1]+((z if k == j else F(1)) if k in S else F(0))
                              for k in range(N)])
    if j == veto:
        expected = t*game(full,S)
    else:
        changed = [F(1) if j not in row else min(F(1),t,arrays[j][r]+z)
                   for r,row in enumerate(rows)]
        expected = game(changed,S)
    assert actual == expected, (j,t,z,S,actual,expected)
    checks += 1

# Exact scalar identities used in the heterogeneous upper theorem.
algebra_checks = 0
for R in [F(a,b) for b in range(1,13) for a in range(0,25)]:
    assert F(4,3)-(R*R+4*R)/(1+R)**2 == (R-2)**2/(3*(1+R)**2)
    assert 4*R <= (1+R)**2
    algebra_checks += 1
for rho,other,Lratio in product([F(1,9),F(3,4),F(5,2)],
                               [F(0),F(1,7),F(4)],
                               [F(0),F(1,5),F(1)]):
    L = Lratio*rho
    assert L/(1+other+L) <= rho/(1+other+rho)
    algebra_checks += 1

result = dict(status='PASS',owners=N,
              generator_blocks=[[sorted(row) for row in rows[:3]], [sorted(rows[3])]],
              supporting_sets_per_game=len(coalitions)-1,
              exact_real_report_coalition_checks=checks,
              exact_algebra_checks=algebra_checks,
              scope='Finite exact replay; all-d and all-profile proof is in mass_geometry_final_upper_attempt.txt.')
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))

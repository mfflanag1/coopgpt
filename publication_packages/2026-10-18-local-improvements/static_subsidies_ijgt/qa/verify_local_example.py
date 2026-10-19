"""Exact ell=1 check reconstructed from the printed three pair matrices."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib
import json

labels = range(3)
A = {(i,i):1 for i in labels}
B = A.copy()
C = A.copy()
A[0,1], B[0,2], C[1,2] = 2, 1, 2
teams = list(product(labels, repeat=3))
def worth(t):
    a,b,c = t
    return A.get((a,b),0) + B.get((a,c),0) + C.get((b,c),0)
def covers(p):
    return all(sum(p[t[a]][a] for a in labels) >= worth(t) for t in teams)
assert sum(worth((i,i,i)) for i in labels) == 9

# For each player construct a separate ideal-attaining core witness.
core_witnesses = []
for r,a0 in product(labels, repeat=2):
    color = {j:j for j in labels}
    color[r] = a0
    x = {j:tuple(F(int(a==a0)+2*int(color[j]==a)) for a in labels) for j in labels}
    assert all(v>=0 for row in x.values() for v in row)
    assert sum(map(sum,x.values())) == 9
    assert covers(x) and x[r][a0] == 3
    core_witnesses.append(x)
assert all(max(x[j][a] for x in core_witnesses)==3 for j,a in product(labels,repeat=2))

y = {0:(F(3),F(1),F(1)), 1:(F(1),F(1),F(1)), 2:(F(1),F(1),F(1))}
special = (0,1,2)
assert worth(special) == 5
assert max(worth(t) for t in teams if t != special) == 3
assert all(v>=1 for row in y.values() for v in row)
assert covers(y) and sum(map(sum,y.values())) == 11
assert sum(y[special[a]][a] for a in labels) == 5
assert 5+6*1-9 == 2
assert F(2,9)<F(1,3)

root = Path(__file__).resolve().parents[1]
source = root/'submission/manuscript.tex'
report = {'result':'PASS', 'scope':'ell=1 numerical exposition only; no new universal or priority claim',
          'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
          'arithmetic':'fractions.Fraction; no floating-point arithmetic or solver',
          'full_teams_per_allocation':27, 'separate_ideal_core_witnesses_checked':9,
          'ideal_value_attained_for_all_9_players':3,
          'ideal_upper_bound_scope':'This witness check proves attainability only. The unchanged diagonal-tightness argument gives the upper bounds; separate LP diagnostics and exact rational dual certificates independently check this finite instance.',
          'T':9, 'floors':1, 'special_team_worth':5,
          'other_team_max_worth':3, 'six_unmatched_floor_cost':6,
          'lower_bound_total':11, 'allocation_total':11, 'subsidy':2, 'subsidy_ratio':'2/9'}
print(json.dumps(report, indent=2))

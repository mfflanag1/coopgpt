"""Exact q=1 check reconstructed from the printed pair-entry definitions."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib
import json

labels = ('L0', 'O1', 'L1', 'R1')
A = {('O1', 'O1'): 2, ('O1', 'R1'): 2}
B = {('O1', 'O1'): 2, ('O1', 'L1'): 2}
C = {('L0', 'L0'): 1, ('L1', 'L1'): 1, ('R1', 'R1'): 1,
     ('R1', 'L1'): 1, ('L0', 'O1'): 1}
teams = list(product(labels, repeat=3))
def worth(t):
    a, b, c = t
    return A.get((a, b), 0) + B.get((a, c), 0) + C.get((b, c), 0)
def check_core(p):
    assert all(x >= 0 for row in p.values() for x in row)
    assert sum(sum(row) for row in p.values()) == 7
    assert all(sum(p[t[a]][a] for a in range(3)) >= worth(t) for t in teams)

H = {'L0': (F(1,2), F(1), F(1)), 'O1': (F(4), F(1), F(1)),
     'L1': (F(1,2), F(1), F(1)), 'R1': (F(1,2), F(1), F(1))}
p = {'L0': (F(1,10), F(7,10), F(1,5)), 'O1': (F(18,5), F(1,5), F(1,5)),
     'L1': (F(1,10), F(1,5), F(7,10)), 'R1': (F(1,10), F(7,10), F(1,5))}
check_core(p)
assert sum(worth((t,t,t)) for t in labels) == 7
assert min(p[t][a]/H[t][a] for t in labels for a in range(3)) == F(1,5)

# Seven vertices of the printed q=1 simplex independently recover all ideals.
vertices = []
for j in range(7):
    z = [F(0)]*7
    z[j] = F(1,2) if j == 0 else F(1)
    alpha, l0, d, r, e, f, h = z
    o = l0+e
    l1 = l0+alpha+d+r+e+f
    v = {'L0': (alpha, 1-alpha-l0, l0), 'O1': (4-d-o, d, o),
         'L1': (alpha, 1-alpha-l1, l1), 'R1': (alpha, 1-alpha-r, r)}
    check_core(v)
    vertices.append(v)
assert all(max(v[t][a] for v in vertices) == H[t][a]
           for t in labels for a in range(3))

partial = [('O1','R1','L1'), ('L0','L0','O1')]
assert sum(map(worth, partial)) == 6
used = {(a,t[a]) for t in partial for a in range(3)}
assert len(used) == 6
unmatched = {(a,t) for a in range(3) for t in labels} - used
assert sum(H[t][a] for a,t in unmatched) == 5
u = {'L0': (F(1,6), F(2,3), F(1,6)), 'O1': (F(11,3), F(1,6), F(1,6)),
     'L1': (F(1,6), F(1,6), F(2,3)), 'R1': (F(1,6), F(2,3), F(1,6))}
check_core(u)
assert min(x for row in u.values() for x in row) == F(1,6)
assert len(unmatched) == 6 and (2,'L0') in unmatched

root = Path(__file__).resolve().parents[1]
source = root/'submission/manuscript.tex'
report = {'result':'PASS', 'scope':'q=1 numerical exposition only; no new universal or priority claim',
          'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
          'arithmetic':'fractions.Fraction; no floating-point arithmetic or solver',
          'full_teams_per_allocation':64, 'core_allocations_checked':9,
          'simplex_vertices_checked':7, 'ideals_attained_at_vertices':True,
          'ideal_upper_bound_scope':'This witness check proves attainability only. The unchanged simplex proof gives the upper bounds; separate LP diagnostics and exact rational dual certificates independently check this finite instance.',
          'T':7, 'partial_matching_worth':6, 'unmatched_ideals_sum':5,
          'optimal_ratio':'1/5', 'target_ideal':'1', 'target_leximin_payoff':'1/6',
          'leximin_scope':'Checks feasible first-stage witness and binding residual budget; does not claim u is the complete final leximin vector.'}
print(json.dumps(report, indent=2))

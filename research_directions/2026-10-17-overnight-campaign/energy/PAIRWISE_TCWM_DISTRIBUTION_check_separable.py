"""Exact polyhedral feasibility/KKT-incidence checks; no numerical solver."""
from fractions import Fraction as F
import json
from pathlib import Path

# Coefficients of (1,s,delta,h).
P = [(0,0,0,0),(2,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),(2,1,0,0)]
N = [(2,0,1,0),(0,0,0,0),(2,1,0,0),(1,1,0,0),(1,0,0,0),(0,0,0,0)]
X = [(1,0,0,0),(1,0,0,0),(2,0,0,-1),(1,0,1,-1),(1,0,-1,0),(0,1,0,1)]
VERTICES = [(1,2,0,0),(1,2,F(1,2),0),(1,2,F(1,2),F(1,2))]

def total(rows, mask):
    return tuple(sum(rows[i][j] for i in range(6) if mask>>i&1) for j in range(4))
def sub(a,b):
    return tuple(x-y for x,y in zip(a,b))
def dot(a,b):
    return sum(x*y for x,y in zip(a,b))
def nonnegative(a):
    return a[1]>=0 and all(dot(a,v)>=0 for v in VERTICES)

tight=[]
certificates=[]
for mask in range(64):
    p,n,x = total(P,mask),total(N,mask),total(X,mask)
    difference=sub(p,n)
    if nonnegative(difference):
        value=n
        branch='negative'
    elif nonnegative(tuple(-t for t in difference)):
        value=p
        branch='positive'
    else:
        raise AssertionError(('uncertified minimum branch',mask,difference))
    gap=sub(x,value)
    assert nonnegative(gap), (mask,gap)
    if not any(gap):
        tight.append(mask)
    certificates.append({'mask':mask,'min_branch':branch,'gap':list(gap)})

assert set((0,3,36,39,43,56,59)) == set(tight)
# Formal symbols: g1,g2mh,g1dm,r. High gradients from multipliers.
weights={3:(1,0,0,-1),36:(0,1,0,0),43:(0,0,0,1),56:(0,0,1,0)}
stationarity=[tuple(sum(w[j] for m,w in weights.items() if m>>i&1) for j in range(4)) for i in range(6)]
assert stationarity==[(1,0,0,0),(1,0,0,0),(0,1,0,0),(0,0,1,1),(0,0,1,0),(0,1,1,1)]
# Coordinates 3 and 5 equal intended gradients using r and equation (3).
assert sub(total(X,5),(3,0,0,0))==(0,0,0,-1)
result={'status':'PASS','coalitions':64,'polyhedron_vertices':3,'recession_directions':1,
        'identically_tight_masks':tight,'high_kkt_masks':list(weights),
        'pair_mask':5,'pair_change':'-h','certificates':certificates}
Path(__file__).with_name('PAIRWISE_TCWM_DISTRIBUTION_separable_exact.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: 64 symbolic coalition inequalities, 3 vertices, 1 ray, exact KKT incidence, pair loss h.')

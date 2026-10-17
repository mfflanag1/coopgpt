"""Independently replay the sparse rational9/7 certificate, without SciPy."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json

base=Path(__file__).parent
raw=json.loads((base/'pair_gain_ternary_n4_s2.json').read_text())
types=list(product(range(3),repeat=2))
swap=[types.index(t[::-1]) for t in types]
def canon(state,t):
    state=tuple(state)
    sw=tuple(state[swap[j]] for j in range(9))
    return min((state,t),(sw,swap[t]))
def plus(row,key,v):row[key]=row.get(key,Q(0))+v
combined={};bound=Q(0);certificate=[]
for entry in raw['dual']:
    weight=-Q(entry['multiplier']).limit_denominator(100000)
    assert weight>0
    label=entry['label'];kind=label[0];state=label[1]
    row={}
    if kind=='budget':
        t=min(sum(state[j]*types[j][e] for j in range(9)) for e in range(2))
        s=sum(state[j]*min(types[j]) for j in range(9))
        rhs=Q(s)
        row['K']=-Q(t-s)
        for j,c in enumerate(state):
            if c:plus(row,canon(state,j),Q(c))
    elif kind=='coverage':
        chosen=label[2]
        value=min(sum(c*types[j][e] for j,c in chosen) for e in range(2))
        rhs=-Q(value)
        for j,c in chosen:plus(row,canon(state,j),-Q(c))
    elif kind=='outside':
        picked,lowstate,lows,removed=label[2:]
        assert len(picked)<=2
        reconstructed=list(state)
        actual=[0,0]
        for hi,lo in zip(picked,lows):
            assert all(types[lo][e]<=types[hi][e] for e in range(2))
            reconstructed[hi]-=1;reconstructed[lo]+=1
            for e in range(2):actual[e]+=types[hi][e]-types[lo][e]
        assert reconstructed==lowstate and actual==removed
        rhs=-Q(min(removed))
        for j in picked:plus(row,canon(state,j),-Q(1))
        for j in lows:plus(row,canon(lowstate,j),Q(1))
    else:raise AssertionError(kind)
    for key,v in row.items():plus(combined,key,weight*v)
    bound+=weight*rhs
    certificate.append({'weight':str(weight),'constraint':label})
assert combined['K']==-1
other={str(key):str(value) for key,value in combined.items() if key!='K' and value}
assert all(value>=0 for key,value in combined.items() if key!='K')
assert bound==-Q(9,7)
result={'status':'PASS','arithmetic':'exact rational summed valid inequalities',
        'constraint_count':len(certificate),'K_coefficient':str(combined['K']),
        'right_hand_side':str(bound),'gain_coefficient_lower':'9/7',
        'nonzero_nonnegative_payment_coefficients':other,'certificate':certificate}
(base/'pair_gain_four_owner_exact_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='certificate'},indent=2))

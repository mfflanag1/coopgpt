"""Standard-library exact proof certificate; no LP solver or floating arithmetic."""
from pathlib import Path
from fractions import Fraction as Q
from math import comb
import json

B=Path(__file__).resolve().parent
data=json.loads((B/'POSITIVE_MARGINAL_FINITE_CERT_N16_S4_FACTOR5.json').read_text())
N,s=data['N'],data['s']
assert (N,s)==(16,4)

def choose(n,k):
    return comb(n,k) if 0<=k<=n else 0

def formula(q,k,t):
    z=N-q-k
    return [Q(sum(choose(k,j)*(choose(z,l-j)-(q-1)*choose(z,l-1-j))
                  for j in range(t+1,k+1)),comb(N-1,l)) for l in range(N)]

def direct_transition(q,k,t):
    # Integer-scaled min3 games with center owners(q,...,q+k-1) each holding
    # (1/k,1/k,0), protected keeper owners1..q-1 each(0,0,1), focal0 initially
    # (0,0,t/k), adding(0,0,1/k) to reach(0,0,(t+1)/k); remaining owners are null.
    center_mask=((1<<k)-1)<<q
    keeper_mask=((1<<q)-1)^1
    delta=[]
    for S in range(1<<N):
        center=(S&center_mask).bit_count()
        leaf=k*(S&keeper_mask).bit_count()+t*(S&1)
        low=min(center,center,leaf)
        high=min(center,center,leaf+(S&1))
        delta.append(high-low)
    numerators=[0]*N
    for i in range(q):
        for R in range(1<<N):
            if not R>>i&1:
                numerators[R.bit_count()]+=delta[R|(1<<i)]-delta[R]
    return [Q(a,comb(N-1,l)) for l,a in enumerate(numerators)]

beta=Q(data['coverage_weight'])
assert beta==5
coverage=[Q(3*l*(l-1),(N-1)*(N-2)) for l in range(N)]
# Independent pure-three game: coalition worth1 iff owner slots0,1,2 present.
direct_coverage=[0]*N
for i in range(3):
    for R in range(1<<N):
        if not R>>i&1:
            low=int(R&7==7)
            high=int((R|(1<<i))&7==7)
            direct_coverage[R.bit_count()]+=high-low
assert coverage==[Q(a,comb(N-1,l)) for l,a in enumerate(direct_coverage)]

coefficients=[beta*c for c in coverage]
checked_rows=0
for entry in data['transition_weights']:
    q,k,t=entry['q'],entry['k'],entry['t']
    weight=Q(entry['weight'])
    assert 2<=q<=s and 1<=k<=N-q and 0<=t<k and weight>=0
    exact_row=formula(q,k,t)
    assert exact_row==direct_transition(q,k,t),(q,k,t)
    for l in range(N):
        coefficients[l]+=weight*exact_row[l]
    checked_rows+=1
assert coefficients==list(map(Q,data['verification_coefficients']))
assert all(a<=1 for a in coefficients)
assert all(min(l+1,l+1,l+1)-min(l,l,l)==1 for l in range(N))
maximum=max(coefficients)
out={'status':'PASS','N':N,'maximum_protected_coalition':s,
     'certified_funding_lower':'5','exact_transition_rows':checked_rows,
     'raw_min3_profile_subsets_checked':checked_rows*(1<<N),
     'cardinality_coefficients_checked':N,
     'maximum_dual_coefficient':str(maximum),'minimum_dual_slack':str(1-maximum),
     'scope':'Finite lower for arbitrary fixed nonnegative whole-owner marginal-contribution weights, including asymmetric weights after finite symmetrization. General min3 mechanisms retain factor2.'}
(B/'POSITIVE_MARGINAL_FINITE_CERT_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))

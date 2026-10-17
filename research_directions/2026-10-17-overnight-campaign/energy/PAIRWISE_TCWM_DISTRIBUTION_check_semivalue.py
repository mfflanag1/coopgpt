from fractions import Fraction as Q
import json
from pathlib import Path

def bz(z,p):
    n=len(z)
    def v(mask):
        return min(sum(max(x,0) for i,x in enumerate(z) if mask>>i&1),
                   sum(max(-x,0) for i,x in enumerate(z) if mask>>i&1))
    ans=[]
    for i in range(n):
        total=Q(0)
        for mask in range(1<<n):
            if mask>>i&1:continue
            k=mask.bit_count()
            total+=p**k*(1-p)**(n-1-k)*(v(mask|1<<i)-v(mask))
        ans.append(total)
    return ans

checks=0
for p in (Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1)):
    for eps in (Q(0),Q(1,3),Q(1)):
        y=bz([Q(1),eps,Q(-1)],p)
        assert y[0]==p-p*p*eps
        assert y[1]==p*(1-p)*eps
        checks+=1
y=bz([Q(2),Q(-1),Q(-1),Q(1)],Q(1,2))
assert sum(y[:3])==Q(15,8)
assert Q(2)-sum(y[:3])==Q(1,8)
out={'status':'PASS','polynomial_sample_checks':checks,'four_owner_payments':list(map(str,y)),
     'protected_coalition_payment':'15/8','coalition_worth':2,'shortfall':'1/8',
     'scope':'Exact enumeration corroborates the analytic polynomial and moment proof.'}
Path(__file__).with_name('PAIRWISE_TCWM_DISTRIBUTION_semivalue_exact.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS: exact marginal formulas and four-owner Banzhaf coverage deficit1/8.')

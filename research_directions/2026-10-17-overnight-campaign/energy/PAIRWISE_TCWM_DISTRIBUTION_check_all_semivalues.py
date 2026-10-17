from fractions import Fraction as Q
from itertools import product
import json
from pathlib import Path

def add(a,b):
    n=max(len(a),len(b))
    return [(a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0) for i in range(n)]
def scale(a,t):return [x*t for x in a]
def mul(a,b):
    r=[Q(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):r[i+j]+=x*y
    return r
I=[0,1,-2]
C=[0,4,-5,2]
square=mul([0,1],mul([1,-2],[1,-2]))
assert add(C,[0,-2])==add(scale(I,Q(3,2)),scale(square,Q(1,2)))

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
for p,x in product((Q(0),Q(1,7),Q(1,2),Q(4,5),Q(1)),(Q(1,4),Q(1,2),Q(1))):
    y=bz([x,Q(-1),Q(-1),Q(-1)],p)
    assert y[0]==x*(1-(1-p)**3)
    assert y[1]==x*p*(1-p)**2
    assert y[0]+y[1]==x*(4*p-5*p*p+2*p**3)
    checks+=1
y=bz([Q(2),Q(-1),Q(-1),Q(1)],Q(1,2))
assert sum(y[:3])==Q(15,8)
result={'status':'PASS','polynomial_identity':'C-2p=(3/2)p(1-2p)+(1/2)p(1-2p)^2',
        'exact_marginal_checks':checks,'coverage_shortfall':'1/8',
        'scope':'Finite positive measure may depend on fixed n>=4.'}
Path(__file__).with_name('PAIRWISE_TCWM_DISTRIBUTION_all_semivalues_exact.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: exact cubic identity, 15 marginal checks, coverage shortfall1/8.')

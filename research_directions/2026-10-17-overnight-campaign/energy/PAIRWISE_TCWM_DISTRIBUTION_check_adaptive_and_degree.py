from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json

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

for p in (Q(0),Q(1,7),Q(1,2),Q(4,5),Q(1)):
    low=bz([Q(2),Q(1),Q(-1),Q(0)],p)
    high=bz([Q(2),Q(1),Q(-1),Q(-1)],p)
    assert low[0]==low[1]==p*(1-p)
    assert low[2]==2*p-p*p
    assert 3*low[0]+p*p==low[0]+low[2]
    assert high[0]==high[2]==high[3]==2*p-2*p*p+p**3

degree=lambda z:[sum(min(abs(x),abs(y)) for y in z if x*y<0) for x in z]
lowz=[Q(1),Q(1,4),Q(-1),Q(0)]
highz=[Q(1),Q(1,4),Q(-1),Q(-1,4)]
dl,dh=degree(lowz),degree(highz)
assert dl==[Q(1),Q(1,4),Q(5,4),Q(0)]
assert dh==[Q(5,4),Q(1,2),Q(5,4),Q(1,2)]
gl=1/(dl[0]+dl[2]);gh=1/(dh[0]+dh[2])
assert gl==Q(4,9) and gh==Q(2,5)
before=(dh[0]+dh[3])*gh;after=dl[0]*gl+Q(1,4)
assert before-after==Q(1,180)
out={'status':'PASS','adaptive_semivalue_polynomial_checks':5,
     'degree_low':list(map(str,dl)),'degree_high':list(map(str,dh)),
     'forced_low_scale':'4/9','high_scale_lower':'2/5','pair_drop_lower':'1/180'}
Path(__file__).with_name('PAIRWISE_TCWM_DISTRIBUTION_adaptive_degree_exact.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS: adaptive-mixture identities and exact common-degree obstruction1/180.')

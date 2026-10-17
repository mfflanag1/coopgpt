"""Exact targeted falsification of the minimum common degree-cover scale."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import random,json

def allocate(z):
    n=len(z)
    d=[sum(min(abs(z[i]),abs(z[j])) for j in range(n) if z[i]*z[j]<0) for i in range(n)]
    gamma=Q(0);tight=[]
    for mask in range(1,1<<n):
        worth=min(sum(max(t,0) for i,t in enumerate(z) if mask>>i&1),sum(max(-t,0) for i,t in enumerate(z) if mask>>i&1))
        den=sum(d[i] for i in range(n) if mask>>i&1)
        if worth:
            assert den>0
            ratio=worth/den
            if ratio>gamma:gamma=ratio;tight=[mask]
            elif ratio==gamma:tight.append(mask)
    return [gamma*t for t in d],d,gamma,tight

rng=random.Random(1137);failure=None;checks=0
for trial in range(1000):
    n=rng.choice([4,5,6,7])
    z=[rng.choice([-1,1])*Q(rng.choice([1,2,3,4,6,8]),2) for _ in range(n)]
    if min(z)>0 or max(z)<0:continue
    y,d,g,t=allocate(z)
    for j in range(n):
        dz=Q(1,8);high=z.copy();high[j]+=(1 if z[j]>0 else -1)*dz
        yh,dh,gh,th=allocate(high)
        for i in range(n):
            change=yh[j]-y[j] if i==j else yh[i]+yh[j]-y[i]-y[j]
            checks+=1
            if change<0 or change>dz:
                failure={'low':z,'high':high,'i':i,'j':j,'delta':dz,'change':change,'low_payment':y,'high_payment':yh,'low_degrees':d,'high_degrees':dh,'low_gamma':g,'high_gamma':gh,'low_tight':t,'high_tight':th}
                break
        if failure:break
    if failure:break
out={'status':'EXACT_COUNTEREXAMPLE' if failure else 'NO_FAILURE_IN_BOUNDED_SCOUT','checks':checks,'failure':failure}
Path(__file__).with_name('PAIRWISE_TCWM_DISTRIBUTION_degree_scale_scout.json').write_text(json.dumps(out,default=str,indent=2)+'\n')
print(json.dumps(out,default=str,indent=2))

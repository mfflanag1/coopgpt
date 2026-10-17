"""Discovery only: choose largest p<=1/2 giving scaled-semivalue coverage."""
import json,random
from pathlib import Path
from math import comb
import numpy as np

def allocation(z):
    n=len(z);size=1<<n
    v=np.array([min(sum(max(z[i],0) for i in range(n) if m>>i&1),sum(max(-z[i],0) for i in range(n) if m>>i&1)) for m in range(size)])
    coeff=np.zeros((n,n-1))
    for i in range(n):
        for m in range(size):
            if m>>i&1:continue
            k=m.bit_count()
            if not k:continue
            delta=v[m|1<<i]-v[m]
            for j in range(n-k):
                coeff[i,k-1+j]+=0.5*delta*comb(n-1-k,j)*(-1)**j
    cover=[];roots=[0.,.5]
    for m in range(1,size):
        c=sum((coeff[i] for i in range(n) if m>>i&1),np.zeros(n-1));c[0]-=v[m]
        cover.append(c)
        trimmed=np.trim_zeros(c,'b')
        if len(trimmed)>1:
            for r in np.polynomial.polynomial.polyroots(trimmed):
                if abs(r.imag)<1e-7 and 1e-8<r.real<.5-1e-8:roots.append(float(r.real))
    roots=sorted(set(round(r,11) for r in roots))
    feasible=lambda p:all(np.polynomial.polynomial.polyval(p,c)>=-1e-7 for c in cover)
    p=max(r for r in roots if feasible(r))
    y=np.array([np.polynomial.polynomial.polyval(p,c) for c in coeff])
    return y,p,coeff

rng=random.Random(1741)
checks=0;failure=None
for trial in range(150):
    n=rng.choice([4,5,6])
    z=np.array([rng.choice([-1,1])*rng.choice([.25,.5,1,1.5,2,3,4]) for _ in range(n)])
    if min(z)>0 or max(z)<0:continue
    y,p,coeff=allocation(z)
    for j in range(n):
        delta=.125
        high=z.copy();high[j]+=np.sign(z[j])*delta
        yh,ph,ch=allocation(high)
        for i in range(n):
            d=yh[j]-y[j] if i==j else yh[i]+yh[j]-y[i]-y[j]
            checks+=1
            if d < -1e-5 or d > delta+1e-5:
                failure={'low':z.tolist(),'high':high.tolist(),'i':i,'j':j,'delta':delta,'change':float(d),'low_payment':y.tolist(),'high_payment':yh.tolist(),'p_low':p,'p_high':ph,'coeff_low':coeff.tolist(),'coeff_high':ch.tolist()}
                break
        if failure:break
    if failure:break
out={'status':'COUNTEREXAMPLE_DISCOVERY' if failure else 'NO_FAILURE_IN_BOUNDED_SCOUT','checks':checks,'failure':failure}
Path(__file__).with_name('PAIRWISE_TCWM_DISTRIBUTION_adaptive_sampling_scout.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))

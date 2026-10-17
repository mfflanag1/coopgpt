from fractions import Fraction as Q
import json
from pathlib import Path

def solve(a,b):
    n=len(b)
    a=[[Q(x) for x in row]+[Q(y)] for row,y in zip(a,b)]
    for j in range(n):
        k=next(k for k in range(j,n) if a[k][j])
        a[j],a[k]=a[k],a[j]
        q=a[j][j]
        a[j]=[x/q for x in a[j]]
        for k in range(n):
            if k!=j:
                q=a[k][j]
                a[k]=[x-q*y for x,y in zip(a[k],a[j])]
    return [row[-1] for row in a]

results=[]
for delta in (Q(0),Q(1,8)):
    z=[-Q(3,2)-delta,-Q(5,2),Q(7,2),-Q(1,2),Q(-1)]
    value=lambda m:min(sum(max(t,0) for i,t in enumerate(z) if m>>i&1),sum(max(-t,0) for i,t in enumerate(z) if m>>i&1))
    T=value(31)
    w=[min(abs(t),T) for t in z]
    masks=[7,22,29]
    A=[[sum(w[i] for i in range(5) if m>>i&1 and n>>i&1) for n in masks] for m in masks]
    lam=solve(A,[value(m) for m in masks])
    x=[w[i]*sum(l for l,m in zip(lam,masks) if m>>i&1) for i in range(5)]
    assert all(t>0 for t in x+lam+w)
    assert all(sum(x[i] for i in range(5) if m>>i&1)>=value(m) for m in range(32))
    assert all(sum(x[i] for i in range(5) if m>>i&1)==value(m) for m in masks)
    assert all(x[i]/w[i]==sum(l for l,m in zip(lam,masks) if m>>i&1) for i in range(5))
    results.append({'z':z,'x':x,'multipliers':lam,'pair':x[0]+x[1]})
loss=results[0]['pair']-results[1]['pair']
assert loss==Q(21277,789880)
out={'status':'PASS','coalition_checks':64,'loss':str(loss),'profiles':results}
Path(__file__).with_name('PAIRWISE_TCWM_DISTRIBUTION_weighted_exact.json').write_text(json.dumps(out,default=str,indent=2)+'\n')
print('PASS: 64 exact covers, positive KKT certificates, pair loss',loss)

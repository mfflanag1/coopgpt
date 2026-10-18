from itertools import permutations
from fractions import Fraction as Q
from pathlib import Path
import random,json
from adaptive_local_probe import worths

def pay(b,kind):
 v=worths(b,kind);n=len(b);acc=[0]*n;count=0
 for order in permutations(range(n)):
  y=[0]*n;prior=0
  for i in order:
   t=prior;best=0
   while True:
    value=v[t|1<<i]-sum(y[j] for j in range(n) if t>>j&1)
    best=max(best,value)
    if t==0:break
    t=(t-1)&prior
   y[i]=best;prior|=1<<i
  assert all(sum(y[i] for i in range(n) if mask>>i&1)>=v[mask] for mask in range(1<<n))
  acc=[a+z for a,z in zip(acc,y)];count+=1
 return [Q(a,count) for a in acc],v

def run(seed=292,trials=1000):
 rng=random.Random(seed);best=Q(0)
 for t in range(trials):
  n=rng.choice([3,4,5]);d=rng.choice([2,3]);s=rng.choice([2,3]);kind='min'
  b=[[rng.randrange(4) for _ in range(d)] for _ in range(n)]
  if t%2:b=[[z if rng.random()<.5 else 0 for z in row] for row in b]
  y,v=pay(b,kind);i=rng.randrange(n);j=rng.randrange(d);hi=[r[:] for r in b];hi[i][j]+=rng.choice([1,2,5]);yy,vv=pay(hi,kind)
  delta=[yy[k]-y[k] for k in range(n)];other=sorted((delta[k],k) for k in range(n) if k!=i);C=[i]+[k for z,k in other[:s-1] if z<0]
  if v[-1]:best=max(best,sum(y)/v[-1])
  if sum(delta[k] for k in C)<0:
   return dict(status='exact_counterexample',trial=t,s=s,kind=kind,b=b,high=hi,C=C,old=list(map(str,y)),new=list(map(str,yy)),delta=str(sum(delta[k] for k in C)),best_ratio=str(best))
 return dict(status='no_failure_in_bounded_probe',trials=trials,best_ratio=str(best))
if __name__=='__main__':
 r=run();Path(__file__).with_suffix('.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

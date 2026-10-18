from fractions import Fraction as Q
from itertools import combinations
import random,json
from pathlib import Path

def worths(b,kind):
 n=len(b);d=len(b[0]);out=[]
 for mask in range(1<<n):
  c=[sum(b[i][j] for i in range(n) if mask>>i&1) for j in range(d)]
  if kind=='min': v=min(c)
  elif kind=='cap': v=min(c[0],sum(min(c[j],c[j+1]) for j in range(1,d,2)))
  out.append(v)
 return out

def pay(b,s,kind):
 n=len(b);v=worths(b,kind);z=[]
 for i in range(n):
  z.append(sum((s-1)**(n-1-mask.bit_count())*(v[mask|1<<i]-v[mask]) for mask in range(1<<n) if not mask>>i&1))
 factors=[];arg=[]
 for i in range(n):
  candidates=[(Q(v[mask],sum(z[j] for j in range(n) if mask>>j&1)),mask) for mask in range(1<<n) if mask>>i&1 and v[mask]>0]
  ratio,mask=max(candidates,default=(Q(0),0))
  factors.append(ratio);arg.append(mask)
 return [z[i]*factors[i] for i in range(n)],v,z,arg

def run(seed=17,trials=3000):
 rng=random.Random(seed);best=(Q(0),None)
 for t in range(trials):
  n=rng.choice([3,4,5,6]);s=rng.choice([2,3]);kind=rng.choice(['min','min','cap']);d=rng.choice([2,3]) if kind=='min' else 5
  b=[[rng.randrange(4) for _ in range(d)] for _ in range(n)]
  if t%2:
   b=[[x if rng.random()<.4 else 0 for x in row] for row in b]
  y,v,z,arg=pay(b,s,kind)
  if v[-1]:
   ratio=sum(y)/v[-1]
   if ratio>best[0]:best=(ratio,dict(b=b,s=s,kind=kind,y=list(map(str,y))))
  i=rng.randrange(n);j=rng.randrange(d)
  hi=[row[:] for row in b];hi[i][j]+=rng.choice([1,2,5])
  yy,vv,zz,aarg=pay(hi,s,kind)
  changes=[yy[k]-y[k] for k in range(n)]
  others=sorted((changes[k],k) for k in range(n) if k!=i)
  C=[i]+[k for delta,k in others[:s-1] if delta<0]
  delta=sum(changes[k] for k in C)
  if delta<0:
   return dict(status='exact_counterexample',trial=t,seed=seed,s=s,kind=kind,b=b,high=hi,coalition=C,old_payments=list(map(str,y)),new_payments=list(map(str,yy)),delta=str(delta),old_integer_marginals=z,new_integer_marginals=zz,old_argmax_masks=arg,new_argmax_masks=aarg,best_ratio=str(best[0]),best_profile=best[1])
 return dict(status='no_counterexample_in_bounded_probe',seed=seed,trials=trials,best_ratio=str(best[0]),best_profile=best[1])
if __name__=='__main__':
 result=run()
 path=Path(__file__).with_suffix('.json');path.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))

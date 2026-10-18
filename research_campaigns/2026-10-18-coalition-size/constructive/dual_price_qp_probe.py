from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import random,json

def solve_linear(A,b):
 A=[list(map(Q,row))+[Q(z)] for row,z in zip(A,b)];n=len(A)
 for j in range(n):
  k=next((k for k in range(j,n) if A[k][j]),None)
  if k is None:return None
  A[j],A[k]=A[k],A[j];den=A[j][j];A[j]=[x/den for x in A[j]]
  for k in range(n):
   if k!=j:
    c=A[k][j];A[k]=[x-c*y for x,y in zip(A[k],A[j])]
 return [r[-1] for r in A]

def pay(b,s):
 n=len(b);d=len(b[0]);lam=Q(1,s*s);tot=[sum(r[j] for r in b) for j in range(d)]
 M=[[sum(r[j]*r[k] for r in b)+lam*tot[j]*tot[k] for k in range(d)] for j in range(d)]
 best=None
 for size in range(1,d+1):
  for face in combinations(range(d),size):
   x=solve_linear([[M[j][k] for k in face] for j in face],[1]*size)
   if x is None or sum(x)==0:continue
   p=[Q(0)]*d
   for j,z in zip(face,x):p[j]=z/sum(x)
   if min(p)<0:continue
   value=sum(p[j]*M[j][k]*p[k] for j in range(d) for k in range(d))
   if best is None or value<best[0]:best=(value,p)
 if best is None:return [Q(0)]*n,[Q(0)]*d
 p=best[1];return [sum(Q(x)*z for x,z in zip(row,p)) for row in b],p

def run(seed=719,trials=3000):
 rng=random.Random(seed)
 for t in range(trials):
  n=rng.choice([3,4,5,6]);d=rng.choice([2,3]);s=rng.choice([2,3,4]);b=[[rng.randrange(5) for _ in range(d)] for _ in range(n)]
  if t%2:b=[[z if rng.random()<.5 else 0 for z in row] for row in b]
  if not min(map(sum,zip(*b))):continue
  y,p=pay(b,s);i=rng.randrange(n);j=rng.randrange(d);hi=[r[:] for r in b];hi[i][j]+=rng.choice([1,2,7]);yy,pp=pay(hi,s)
  delta=[yy[k]-y[k] for k in range(n)];other=sorted((delta[k],k) for k in range(n) if k!=i);C=[i]+[k for z,k in other[:s-1] if z<0]
  if sum(delta[k] for k in C)<0:
   return dict(status='exact_counterexample',trial=t,s=s,b=b,high=hi,C=C,old=list(map(str,y)),new=list(map(str,yy)),p=list(map(str,p)),pp=list(map(str,pp)),delta=str(sum(delta[k] for k in C)))
 return dict(status='no_failure_in_bounded_probe',trials=trials)
if __name__=='__main__':
 r=run();Path(__file__).with_suffix('.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

"""Exact PSD mask and leverage checks, including noncommuting and singular cases."""
from fractions import Fraction as Q
from math import isqrt, comb
from itertools import product
from random import Random
from pathlib import Path
import json
rng=Random(2610170750)
counts=dict(noncommuting_profiles=0,mask_coverage=0,individual_out=0,order_m_grand=0,sampling=0,leverage_ratios=0,leverage_sums=0)
def root(x):
 a=isqrt(x.numerator);b=isqrt(x.denominator);assert a*a==x.numerator and b*b==x.denominator;return Q(a,b)
def val(X):
 a,b,c=X;return (a+c-root((a-c)**2+4*b*b))/2
def add(rows):return tuple(sum(x[j] for x in rows) for j in range(3))
def sub(x,y):return tuple(a-b for a,b in zip(x,y))
def pair(P,X):return P[0]*X[0]+2*P[1]*X[1]+P[2]*X[2]
def projector(X):
 a,b,c=X;gap=root((a-c)**2+4*b*b)
 if not gap:return (Q(1),Q(0),Q(0))
 top=(a+c+gap)/2;return ((top-a)/gap,-b/gap,(top-c)/gap)
def rule(rows,mask):
 C=add(rows);own=list(map(val,rows));G=val(C)-sum(own);CB=add([rows[i] for i in range(len(rows)) if mask>>i&1]);P=projector(CB)
 return [val(CB)-val(sub(CB,x)) if mask>>i&1 else min(pair(P,x),own[i]+G) for i,x in enumerate(rows)]
def weight(n,k,a):return sum((-1)**ell*comb(k,ell)*a**(n-k+ell)/Q(n-k+ell+1) for ell in range(k+1))
def mixture(rows,a):
 n=len(rows);y=[Q(0)]*n
 for mask in range(1<<n):
  w=weight(n,mask.bit_count(),a)
  for i,x in enumerate(rule(rows,mask)):y[i]+=w*x
 return y
u=(Q(1),Q(0),Q(0));v=(Q(9,25),Q(12,25),Q(16,25));z=(Q(0),Q(0),Q(0))
for f1,f2,f3,t1,t2 in product([Q(0),Q(1,3),Q(1)],[Q(0),Q(1,3),Q(1)],[Q(0),Q(1,2)],[0,1],[0,1]):
 rows=[(f1+t1*u[0],t1*u[1],f1+t1*u[2]),(f2+t2*v[0],t2*v[1],f2+t2*v[2]),(f3,Q(0),f3)]
 own=list(map(val,rows));S=sum(own);C=add(rows);T=val(C);G=T-S;a=Q(1,2);y=mixture(rows,a)
 bn=3*a/2+Q(3,4)*(1-(1-a)**4)/a;assert sum(y)<=S+bn*G
 for mask in range(8):
  ym=rule(rows,mask)
  for coal in range(8):
   ids=[i for i in range(3) if coal>>i&1];assert sum(ym[i] for i in ids)>=val(add([rows[i] for i in ids]));counts['mask_coverage']+=1
 for i in range(3):
  candidates=[rows[i],(own[i],Q(0),own[i])]
  if i<2:candidates.append(tuple(t*(u if i==0 else v)[j] for j in range(3)) if (t:=t1 if i==0 else t2) else z)
  for withdrawn in candidates:
   low=list(rows);low[i]=sub(rows[i],withdrawn);assert val(low[i])>=0
   yl=mixture(low,a);assert y[i]-yl[i]>=val(withdrawn);counts['individual_out']+=1
 marg=[T-val(sub(C,x)) for x in rows];assert sum(marg)<=S+2*G;counts['order_m_grand']+=1
 residual=[(x[0]-fi,x[1],x[2]-fi) for x,fi in zip(rows,own)]
 for mask in range(8):assert rule(rows,mask)==[fi+yy for fi,yy in zip(own,rule(residual,mask))]
 for q in [Q(1,4),Q(1,2),Q(3,4)]:
  closed=Q(0)
  for mask in range(8):
   UB=add([residual[i] for i in range(3) if mask>>i&1]);P=projector(UB)
   excess=sum(min(pair(P,residual[i]),G) for i in range(3) if not(mask>>i&1))
   closed+=q**(3-mask.bit_count())*(1-q)**mask.bit_count()*excess
  assert closed<=4*q/(1-q)*G;counts['sampling']+=1
 counts['noncommuting_profiles']+=1

def inverse(A):
 n=len(A);x=[list(A[i])+[Q(i==j) for j in range(n)] for i in range(n)]
 for j in range(n):
  p=next(i for i in range(j,n) if x[i][j]);x[j],x[p]=x[p],x[j];q=x[j][j];x[j]=[v/q for v in x[j]]
  for i in range(n):
   if i!=j:
    q=x[i][j];x[i]=[a-q*b for a,b in zip(x[i],x[j])]
 return [r[n:] for r in x]
for m in range(1,7):
 for r in range(1,m+1):
  for trial in range(20):
   n=rng.randrange(1,8);mat=[]
   for i in range(n):
    vec=[Q(rng.randrange(-4,5),3) for _ in range(r)]
    mat.append([[vec[j]*vec[k]+Q(j==k,rng.randrange(1,4)) for k in range(r)] for j in range(r)])
   U=[[sum(A[j][k] for A in mat) for k in range(r)] for j in range(r)];Ui=inverse(U);ratios=Q(0);trace_sum=Q(0)
   for A in mat:
    test=[Q(rng.randrange(-4,5),3) for _ in range(m)];active=test[:r]
    num=sum(active[j]*A[j][k]*active[k] for j in range(r) for k in range(r));den=sum(active[j]*U[j][k]*active[k] for j in range(r) for k in range(r))
    ratio=num/den if den else Q(0);tr=sum(Ui[j][k]*A[k][j] for j in range(r) for k in range(r));assert ratio<=tr
    ratios+=ratio;trace_sum+=tr;counts['leverage_ratios']+=1
   assert trace_sum==r and ratios<=r<=m;counts['leverage_sums']+=1
out={'status':'PASS','arithmetic':'exact rational matrices, eigenvalues and mask weights','limits':'Finite checks corroborate the all-real analytic proof; no general matrix algorithm claimed',**counts}
Path(__file__).with_name('CONE_PSD_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

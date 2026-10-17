"""Exact refined sampling checks plus numerical positive-density integration."""
from fractions import Fraction as Q
from math import comb, factorial, exp, log1p, sqrt, pi
from random import Random
from pathlib import Path
import json
from scipy.integrate import quad
rng=Random(202610170752)
counts=dict(profiles=0,mask_trace_bounds=0,conditioning_bounds=0,density_integrals=0,zero_gain_profiles=0)
def rank(a):
 a=[list(row) for row in a]
 if not a:return 0
 r=0
 for c in range(len(a[0])):
  s=next((i for i in range(r,len(a)) if a[i][c]),None)
  if s is None:continue
  a[r],a[s]=a[s],a[r]; v=a[r][c]; a[r]=[x/v for x in a[r]]
  for i in range(len(a)):
   if i!=r:
    v=a[i][c];a[i]=[x-v*y for x,y in zip(a[i],a[r])]
  r+=1
  if r==len(a):break
 return r
def zconst(d):return sum(Q(comb(d-1,k)*factorial(k),d**(k+1)) for k in range(d))
def weight(d,n,s):
 z=float(zconst(d))
 def integrand(q):
  if q<=0:return 1/z if n==s else 0
  if q>=1:return 0
  p=1-q
  exponent=(n-s)*__import__('math').log(q)+(s-d-1)*__import__('math').log(p)-d*q/p
  return exp(exponent)/z if exponent>-745 else 0
 val,err=quad(integrand,0,1,epsabs=1e-12,epsrel=1e-12,limit=150)
 assert err<1e-9
 return val
weights={}
for n in range(2,8):
 for d in range(1,5):
  D=d+1
  ws=[weight(D,n,s) for s in range(n+1)]
  assert abs(sum(comb(n,s)*ws[s] for s in range(n+1))-1)<1e-10
  weights[n,D]=ws
  for trial in range(6):
   b=[[Q(rng.randrange(5)) for _ in range(d)] for _ in range(n)]
   forms=[[Q(rng.randrange(5)) for _ in range(d)] for _ in range(5)]
   def f(x):return min(sum(u*v for u,v in zip(x,w)) for w in forms)
   fs=[f(x) for x in b]; S=sum(fs)
   vals={};a={};w={}
   for B in range(1<<n):
    cb=[sum(b[i][j] for i in range(n) if B>>i&1) for j in range(d)]
    sel=min(range(len(forms)),key=lambda k:sum(u*v for u,v in zip(cb,forms[k])))
    vals[B]=f(cb);w[B]=vals[B]-sum(fs[i] for i in range(n) if B>>i&1)
    a[B]=[sum(u*v for u,v in zip(b[i],forms[sel]))-fs[i] for i in range(n)]
    assert sum(a[B][i] for i in range(n) if B>>i&1)==w[B]
   G=w[(1<<n)-1]
   if G==0:
    assert all(v==0 for v in w.values());counts['zero_gain_profiles']+=1;continue
   assert rank(list(a.values()))<=D
   for B in range(1<<n):
    members=[i for i in range(n) if B>>i&1]
    mat=[[Q(0)]*len(members) for _ in members]
    lhs=Q(0)
    for c,i in enumerate(members):
     vec=a[B^(1<<i)];x=vec[i];h=w[B^(1<<i)]
     assert h<=w[B]
     den=x+h
     if den:
      for r,j in enumerate(members):mat[r][c]=vec[j]/den
      assert min(x,G)<=(G+h)*x/den<=(G+w[B])*x/den
     else:assert x==0
     lhs+=min(x,G)
    tr=sum(mat[i][i] for i in range(len(members)))
    assert tr<=rank(mat)<=D
    assert lhs<=(G+w[B])*tr<=(G+w[B])*D
    counts['mask_trace_bounds']+=1
   for q in [Q(1,5),Q(1,2),Q(4,5)]:
    p=1-q;C=Q(0);g=Q(0)
    for B in range(1<<n):
     s=B.bit_count();prob=p**s*q**(n-s)
     C+=prob*sum(min(a[B][i],G) for i in range(n) if not B>>i&1)
     g+=prob*w[B]
    assert C<=D*q/p*(G+g)
    counts['conditioning_bounds']+=1
   excess=0.0
   for B in range(1<<n):
    payments=sum(w[B]-w[B^(1<<i)] if B>>i&1 else min(a[B][i],G) for i in range(n))
    excess+=weights[n,D][B.bit_count()]*float(payments)
   assert excess<=float(2/zconst(D)*G)+1e-9
   counts['density_integrals']+=1;counts['profiles']+=1
# Exact polynomial integration of t moment: D int t(1+t)^(D-1)e^-Dt =1.
for D in range(1,81):
 moment=sum(Q(D*comb(D-1,k)*factorial(k+1),D**(k+2)) for k in range(D))
 assert moment==1
 for q in [Q(1,10),Q(1,2),Q(9,10)]:
  p=1-q;logder=1/p-D*q/p**2
  assert p*logder-1+D*q/p==0
constants=[{'D':D,'K_exact':str(2/zconst(D)),'K':float(2/zconst(D)),'old':1+2*sqrt(D),'asymptotic':sqrt(8*D/pi)} for D in [1,2,3,4,8,16,32,64]]
result={'status':'PASS','exact_scope':'rational refined trace, conditioning and density differential/moment identities','numerical_scope':'positive density quadrature checks; not a global proof',**counts,'constants':constants}
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))

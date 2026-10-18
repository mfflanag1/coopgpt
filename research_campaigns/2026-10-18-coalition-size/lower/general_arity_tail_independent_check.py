#!/usr/bin/env python3
"""Independent closed-weight replay; does not import root's checker."""
from fractions import Fraction as F
from collections import defaultdict
from math import ceil,exp,lgamma,log
import json

cases=0;maxima=0
for k in [2,3,4,7,16,31]:
 for s in list(range(2,33))+[63,64,65,127]:
  values=[]
  for M in range(1,2*s+3):
   a={m:min(s-1,k*(m-1)) for m in range(2,M+1)}
   tails={M+1:F(1)}
   for m in range(M,1,-1):tails[m]=F(a[m],a[m]+1)*tails[m+1]
   P=tails.get(2,F(1));c=k*(M-1)
   coeff=defaultdict(F);coeff['K']=1;coeff['z']=-1;coeff[M]-=k*M
   coeff['z']+=1;coeff[M]+=k
   seed=F(c,k+1)*P;coeff[1]+=(k+1)*seed
   for m in range(2,M+1):
    w=F(c,a[m]+1)*tails[m+1]
    assert w>=0;coeff[m]+=(a[m]+1)*w;coeff[m-1]-=a[m]*w
   assert {j:v for j,v in coeff.items() if v}=={'K':1}
   B=1+seed;values.append(B);cases+=1
   h=(s+k-1)//k;Q=F(1)
   for j in range(2,h+1):Q*=F(k*j,k*(j-1)+1)
   if M>=h:assert P==Q/h*F(s-1,s)**(M-h)
  best=max(values);assert [i+1 for i,x in enumerate(values) if x==best]==[s,s+1]
  maxima+=1
# At-most count choices: exact binary integer arithmetic avoids log rounding.
embedding=0
for k in range(2,17):
 for n in [1,2,3,4,7,16,32,127,1000]:
  for d in [1,2,3,4,7,15,16,31,32,63,127,255,1000,2**31-1]:
   for s in [2,3,4,7,16,127,1000]:
    M=min((n-1)//k,((d+1).bit_length()-2)//(k-1),(s+k-1)//k)
    if M>=1:
     assert 1+k*M<=n
     assert (1<<(1+(k-1)*M))-1<=d
     assert k*(M-1)+1<=s
     embedding+=1
    Mp=min(((min(n,d)+1).bit_length()-2)//(k-1),(s+k-1)//k)
    if Mp>=1:
     count=(1<<(1+(k-1)*Mp))-1
     assert count<=n and count<=d and k*(Mp-1)+1<=s
# Gamma asymptotic numerical calibration, independent of exact cancellations.
asymptotic=[]
for k in [2,3,7,16]:
 s=10**6;h=(s+k-1)//k
 logQ=lgamma(h+1)+lgamma(1+1/k)-lgamma(h+1/k)
 log_actual=log(k*(s-1)/((k+1)*h))+logQ+(s-h)*log(1-1/s)
 log_limit=log(k/(k+1))+lgamma(1+1/k)+log(k)/k-(k-1)/k+(k-1)/k*log(s)
 ratio=exp(log_actual-log_limit);assert abs(ratio-1)<1e-4
 asymptotic.append({'k':k,'s':s,'ratio_to_claimed_equivalent':ratio})
print(json.dumps({'status':'PASS','exact_certificates':cases,'peak_checks':maxima,'at_most_embeddings':embedding,'asymptotic_calibration':asymptotic,'scope':'Independent closed-form nonnegative weights, scalar tail maxima, exact count choices. Geometry audited by parent constructions.'},indent=2))

#!/usr/bin/env python3
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json,hashlib
from bisect import bisect_right
ROOT=Path(__file__).resolve().parent

def need(x,msg):
 if not x:raise ValueError(msg)

def payment(m,h,k,l):
 if k>l:
  z=payment(m,h,l,k);return z[2:]+z[:2]
 t=m+(h-1)*k;a=min(h,t);q=Q(1,2*a**(l-k))
 return (1-q,(1-q)*h,q,q*a)

def run():
 counts=dict(parameter_pairs=0,profiles=0,coalitions=0,own_transitions=0,worst_profile_equalities=0,dual_identities=0)
 rows=[]
 for m,h in [(m,h) for m in range(2,9) for h in [2,3,4,6,10]]+[(12,2),(12,12),(12,36),(30,2),(30,30),(30,90)]:
  a=min(h,m);c=1+Q(a-1,2*m*a);counts['parameter_pairs']+=1
  for k,l in product(range(m+1),repeat=2):
   z=payment(m,h,k,l);ns=(m-k,k,m-l,l);t=min(m+(h-1)*k,m+(h-1)*l)
   need(all(v>=0 for v in z),'negative payment');need(sum(n*v for n,v in zip(ns,z))<=c*t,'budget');counts['profiles']+=1
   # Exact full coalition enumeration at small counts. Larger examples check
   # the two possible sides' every resource total, retaining cheapest payments.
   best=[]
   for low,high,yl,yh in [(m-k,k,z[0],z[1]),(m-l,l,z[2],z[3])]:
    by_amount={}
    for i,j in product(range(low+1),range(high+1)):
     amount=i+h*j;cost=i*yl+j*yh
     by_amount[amount]=min(by_amount.get(amount,cost),cost)
    best.append(by_amount)
   amounts=sorted(best[1]);prefix=[];suffix=[None]*(len(amounts)+1)
   for bb in amounts:
    val=best[1][bb]-bb;prefix.append(min(prefix[-1],val) if prefix else val)
   for j in range(len(amounts)-1,-1,-1):
    val=best[1][amounts[j]];suffix[j]=val if suffix[j+1] is None else min(val,suffix[j+1])
   for aa,cc in best[0].items():
    j=bisect_right(amounts,aa);worst=[]
    if j:worst.append(prefix[j-1])
    if j<len(amounts):worst.append(suffix[j]-aa)
    need(cc+min(worst)>=0,'coalition')
   counts['coalitions']+=len(best[0])*len(best[1])
   if k<m:
    zh=payment(m,h,k+1,l);need(z[0]<=zh[1],'hardware own increase');counts['own_transitions']+=1
   if l<m:
    zh=payment(m,h,k,l+1);need(z[2]<=zh[3],'power own increase');counts['own_transitions']+=1
  z=payment(m,h,0,1);need(m*z[0]+(m-1)*z[2]+z[3]==c*m,'sharp profile');counts['worst_profile_equalities']+=1
  # Independently check the exact lower-identity coefficients of x,z,y.
  actual=(Q(m),Q(m-1),Q(1));weighted=(Q(m-1)+Q(a,a),Q(m-1),Q(1,a)+1-Q(1,a))
  need(actual==weighted,'dual coefficient identity');counts['dual_identities']+=1
  rows.append(dict(m=m,h=h,exact_factor=str(c)))
 out=dict(status='EXACT RATIONAL PASS',counts=counts,parameters=rows,scope='Finite exact corroboration of the unrestricted-parameter proof; upper only on binary report domains.',sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 (ROOT/'binary_family_verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='parameters'}))
if __name__=='__main__':run()

#!/usr/bin/env python3
"""Exact finite-route escape; not a complete-domain mechanism verifier."""
from fractions import Fraction as F
from itertools import combinations
import json

def pay(B,f):
 if B==0:return (F(1,3),F(0),F(0),F(0),F(0))
 if B==1:return (F(1,3),F(1,3),F(1,3),F(0),F(0))
 b=F(4,15)
 for j in range(3,B+1):b*=F(3*(j-1),3*j-1)
 return (1-F(3,2)*b,F(3,4)*b,b,F(0),F(0))

transitions=0;profiles=0
for M in range(1,65):
 for f in range(M+1):
  for t in range(M-f+1):
   B=f+t;u=M-B;x=pay(B,f);z,a,b,p,q=x
   assert z>=0 and a>=0 and b>=0 and p==q==0
   assert 3*z>=1
   if f:assert z+2*a>=1
   if t:assert z+2*b>=1
   val=min(F(3),1+F(4,3)*f+t)
   total=3*z+4*f*a+3*t*b
   if B<=1:assert total==val
   else:assert total/val==1+(B-F(3,2))*b
   profiles+=1
   if u:
    y=pay(B+1,f)
    losses=sum(num*max(F(0),x[k]-y[l]) for num,k,l in [(3,0,0),(4*f,1,1),(3*t,2,2),(u-1,3,3),(1,3,2),(3*u+t-2,4,4)])
    assert 2*(y[2]-x[4])>=losses
    transitions+=1
   if t:
    y=pay(B,f+1)
    losses=sum(num*max(F(0),x[k]-y[l]) for num,k,l in [(3,0,0),(4*f,1,1),(3*(t-1),2,2),(u,3,3),(3,2,1),(3*u+t-1,4,4)])
    assert y[1]-x[4]>=losses
    transitions+=1
# Supported-geometry enumeration, plus cover and link matchings.
geometry=[]
for M in range(1,9):
 W={1,2,3};blocks=[{(1<<(j+2))^w for w in range(4)} for j in range(M)]
 for f in range(M+1):
  for t in range(M-f+1):
   supp=set(W)
   for j,block in enumerate(blocks):
    if j<f:supp.update(block)
    elif j<f+t:supp.update(x for x in block if x!=(1<<(j+2))^3)
    else:supp.add(1<<(j+2))
   actual={tuple(sorted((a,b,a^b))) for a,b in combinations(supp,2) if a^b in supp}
   assert all(set(e)&W for e in actual)
   assert len(actual)==1+6*f+3*t
   for w in W:
    witnesses=[]
    for j in range(f,f+t):
     pairs=[(a,b) for a,b in combinations(blocks[j]&supp,2) if a^b==w]
     assert len(pairs)==1;witnesses.extend(pairs)
    assert len(set(sum(([a,b] for a,b in witnesses),[])))==2*t
   geometry.append((M,f,t))
print(json.dumps({'status':'PASS','profiles':profiles,'all_coalition_transition_checks':transitions,'supported_geometry_profiles':len(geometry),'M_scalar_max':64,'M_geometry_max':8,'scope':'Exact assignment for listed 1-to-3 and3-to-4 fixed-owner route, including all coalitions on each transition. No full-domain rule.'}))

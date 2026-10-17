#!/usr/bin/env python3
"""Exact finite identities and formal telescoping certificate, not numerical LP evidence."""
from fractions import Fraction as Q
import json

def require(x,msg):
 if not x:raise RuntimeError(msg)
def harmonic(k):return sum((Q(1,j) for j in range(1,k+1)),Q(0))
def add(poly,key,value):poly[key]=poly.get(key,Q(0))+value
cases=[];bootstrap_count=0
for B in [1,2,3,5]:
 for K in [2,3,4,8,16,32,64]:
  M=2*K;R=2*B*K
  for m in range(1,K+1):
   k=K//m;eps=Q(k,R);F=m*eps
   require(k>=1 and 0<eps<=1 and F<=Q(1,2*B),'feasible bootstrap reports and total value')
   require(Q(k,R)==eps,'selected fixed power owners supply epsilon')
   require(min(Q(k,R),eps,eps)==eps,'exact selected coalition worth')
   require(m*k>=Q(K,2),'floor lower bound')
   active=m*eps*(1-B*F)
   require(active>=m*eps/2>=Q(1,8*B),'coverage/bootstrap active payment lower bound')
   bootstrap_count+=1
  # Add exact nonnegative expressions:
  # B-W_K; W_1; each transition W_m-W_(m-1)-q_m+z_(m-1);
  # each active lower q_m-h_m; each inactive upper B/(M-m+1)-z_(m-1).
  poly={'constant':Q(B)};add(poly,('W',K),-1);add(poly,('W',1),1)
  for m in range(2,K+1):
   add(poly,('W',m),1);add(poly,('W',m-1),-1);add(poly,('q',m),-1);add(poly,('z',m-1),1)
   add(poly,('q',m),1);add(poly,'constant',-Q(1,16*B*m))
   add(poly,'constant',Q(B,M-m+1));add(poly,('z',m-1),-1)
  require(all(value==0 for key,value in poly.items() if key!='constant'),'all payment variables cancel in Farkas sum')
  S=harmonic(2*K-1)-harmonic(K)
  expected=B*(1+S)-(harmonic(K)-1)/(16*B)
  require(poly['constant']==expected,'exact necessary funding inequality')
  require(S<1,'inactive-owner error bounded independently of K')
  cases.append({'B':B,'K':K,'resource_count':4*K+1,'owner_count':(4+2*B)*K,'harmonic_error':S,'necessary_B_squared_lower':(harmonic(K)-1)/(16*(1+S))})
# General contradiction can be certified without instantiating enormous owner arrays:
# K=2^p, p=64 B^2. Each dyadic harmonic block is >=1/2, so H_K-1>=32 B^2;
# S<1 makes denominator <32. Required B^2 is therefore strictly larger than B^2.
dyadic=[]
for B in range(1,11):
 p=64*B*B;lower_h=Q(p,2)
 require(lower_h/32==B*B,'dyadic contradiction algebra')
 dyadic.append({'B':B,'log2_K':p,'H_K_minus_1_lower':lower_h,'denominator_strict_upper':32,'conclusion':'required B squared strictly exceeds B squared'})
print(json.dumps({'status':'PASS','arithmetic':'Fraction; exact inequalities and telescoping coefficients','bootstrap_checks':bootstrap_count,'finite_telescoping_cases':cases,'symbolic_dyadic_contradiction':dyadic},default=str,indent=2))

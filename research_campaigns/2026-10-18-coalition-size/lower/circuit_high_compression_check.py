#!/usr/bin/env python3
from fractions import Fraction as F
from itertools import combinations
from functools import reduce
from operator import xor
import json

def lin(images,x):return reduce(xor,(a for i,a in enumerate(images) if (x>>i)&1),0)
def profile(h,v,m):return [v]+h+[x^v if j<m else 0 for j,x in enumerate(h)]
def check_map(h,v,m,images,owner_perm):
 M=len(h); rows=range(1,1<<M); P=profile(h,v,m)
 assert len({lin(images,x) for x in rows})==(1<<M)-1
 assert sorted(owner_perm)==list(range(len(P)))
 assert all(lin(images,P[i])==P[owner_perm[i]] for i in range(len(P)))

geometries=maps=transitions=0
for M in range(4,10):
 h=[1<<i for i in range(M-1)]+[(1<<(M-1))-1];v=1<<(M-1)
 assert reduce(xor,h)==0
 for m in range(1,M+1):
  P=profile(h,v,m);S=set(P)-{0}
  got={tuple(sorted((a,b,a^b))) for a,b in combinations(S,2) if a^b in S}
  want={tuple(sorted((v,h[j],v^h[j]))) for j in range(m)}
  assert got==want
  # Full production dual: price1 on v and all unavailable rows.
  price={x:int(x==v or x not in S) for x in range(1,1<<M)}
  assert sum(price[x] for x in S)==1
  assert all(price[a]+price[b]+price[a^b]>=1 for a in range(1,1<<M) for b in range(a+1,1<<M))
  geometries+=1
  if m==1:
   images=h[:-1]+[v^h[0]];perm=list(range(2*M+1));perm[0],perm[M+1]=perm[M+1],perm[0]
   check_map(h,v,m,images,perm);maps+=1
  if m>=2:
   for i in range(m):
    j=(i+1)%m
    # Flip two active pairs. Functional values sum to0 on unique relation.
    vals=[int(t in {i,j}) for t in range(M)]
    assert reduce(xor,vals)==0
    images=[h[t]^(v if vals[t] else 0) for t in range(M-1)]+[v]
    perm=list(range(2*M+1))
    for t in (i,j):perm[1+t],perm[1+M+t]=perm[1+M+t],perm[1+t]
    check_map(h,v,m,images,perm);maps+=1
   for i in range(m-1):
    ph=list(range(M));ph[i],ph[i+1]=ph[i+1],ph[i]
    images=[h[ph[t]] for t in range(M-1)]+[v];perm=list(range(2*M+1))
    for t in range(M):perm[1+t]=1+ph[t];perm[1+M+t]=1+M+ph[t]
    check_map(h,v,m,images,perm);maps+=1
   old=profile(h,v,m-1);new=profile(h,v,m);rest=1+M+(m-1)
   assert all(old[i]==new[i] for i in range(len(old)) if i!=rest)
   assert old[rest]==0 and new[rest]==v^h[m-1]
   C=[1+i for i in range(m-1)]+[1+M+i for i in range(m-1)]+[rest]
   assert len(C)==len(set(C))==2*m-1
   transitions+=1
# Exact scalar seed and recurrence through128 branches.
for M in range(4,129):
 q=F(1,5)
 for m in range(3,M+1):q*=F(2*m-2,2*m-1)
 Q=F(1)
 for m in range(2,M+1):Q*=F(2*m,2*m-1)
 assert 2*M*q==F(3,5)*Q
 assert 1+(2*M-2)*q==1+F(3*(M-1),5*M)*Q
 if M==4:assert 1+(2*M-2)*q==F(319,175)
print(json.dumps({'status':'PASS','geometry_profiles':geometries,'explicit_profile_stabilizers':maps,'fixed_owner_transitions':transitions,'M_geometry_max':9,'M_scalar_max':128,'finite_M4':'319/175'}))

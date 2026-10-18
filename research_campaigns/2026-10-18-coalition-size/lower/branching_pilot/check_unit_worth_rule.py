#!/usr/bin/env python3
"""Exact all-endpoint/full-OUT check on the entire PG(3,2) unit-worth ideal.
Tests the explicit intrinsic rule, not the numerical optimization output.
"""
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
import json
import numpy as np
P=Path(__file__).resolve().parent
meta=json.loads((P/'quotient.json').read_text());arr=np.load(P/'quotient.npz');profiles=arr['profile'];edges=[tuple(e) for e in meta['edges']]
values=[F(meta['oracles'][str(mask)]['value']) for mask in meta['profile_reps']]
low=[mask for mask in range(32768) if values[int(profiles[mask])]<=1]
reps=[mask for mask in meta['profile_reps'] if values[int(profiles[mask])]<=1]
@lru_cache(None)
def geometry(mask):
 supported=[e for e in edges if all(mask&(1<<i) for i in e)]
 if not supported:return (0,None,())
 common=set(supported[0])
 for e in supported[1:]:common.intersection_update(e)
 assert common
 if len(supported)>1:assert len(common)==1
 cap=min(common);private=tuple(v for e in supported for v in e if v!=cap)
 assert len(private)==len(set(private))==2*len(supported)
 return len(supported),cap,private
@lru_cache(None)
def q(s,m):
 out=F(1,3)
 for j in range(2,m+1):
  a=min(s-1,2*j-2);out*=F(a,a+1)
 return out
@lru_cache(None)
def pay(mask,s):
 m,cap,private=geometry(mask);out=[F(0)]*15
 if m:
  out[cap]=1-2*q(s,m)
  for v in private:out[v]=q(s,m)
 return tuple(out)
coverage=endpoints=productive_restorations=zero_to_positive=0
bounds=[]
for s in range(1,16):
 bound=F(1) if s==1 else 1+2*(s-1)*q(s,s)
 if s>1:
  U=[1+2*(m-1)*q(s,m) for m in range(1,2*s+3)]
  assert [i+1 for i,u in enumerate(U) if u==max(U)]==[s,s+1]
  assert max(U)==bound
 bounds.append({'s':s,'B_s':str(bound)})
 # All final profile orbits; every actual lower subset and unchanged owner.
 for T in reps:
  high=pay(T,s);assert all(v>=0 for v in high)
  assert sum(high)<=bound*values[int(profiles[T])]
  S=T
  while True:
   assert sum(high[i] for i in range(15) if S&(1<<i))>=values[int(profiles[S])]
   coverage+=1
   D=T^S
   if D.bit_count()<=s:
    lowpay=pay(S,s);delta=[high[i]-lowpay[i] for i in range(15)]
    gain=sum(delta[i] for i in range(15) if D&(1<<i))
    losses=sorted([max(F(0),-delta[i]) for i in range(15) if not D&(1<<i)],reverse=True)
    assert gain-sum(losses[:s-D.bit_count()])>=values[int(profiles[D])]
    endpoints+=1
    if D:
     if values[int(profiles[S])]==1:
      assert values[int(profiles[D])]==0;productive_restorations+=1
     elif values[int(profiles[T])]==1:zero_to_positive+=1
   if S==0:break
   S=(S-1)&T
# Direct combinatorial classification on all actual single restoration edges.
actual_edges=0;one_edge_additions=0
for S in low:
 oldm,oldcap,oldprivate=geometry(S)
 for i in range(15):
  if S&(1<<i):continue
  T=S|(1<<i)
  if values[int(profiles[T])]>1:continue
  newm,newcap,newprivate=geometry(T);actual_edges+=1
  if oldm:
   assert newm-oldm in (0,1)
   if newm==oldm+1:
    assert i!=newcap and S&(1<<newcap)
    gained=set(newprivate)-set(oldprivate)
    # For oldm1 cap choice may differ; compare actual old-edge other vertices.
    oldedge=next(e for e in edges if all(S&(1<<j) for j in e))
    oldpriv=set(oldprivate) if oldm>1 else set(oldedge)-{newcap}
    gained=set(newprivate)-oldpriv
    assert len(gained)==2 and i in gained
    other=next(j for j in gained if j!=i)
    assert S&(1<<other) and all(other not in e for e in edges if all(S&(1<<j) for j in e))
    one_edge_additions+=1
print(json.dumps({'status':'PASS','all_actual_low_ideal_profiles':len(low),'all_actual_endpoint_pairs_represented':sum(2**m.bit_count() for m in low),'final_profile_orbits':len(reps),'coalition_coverage_checks':coverage,'all_coalition_full_OUT_endpoint_checks':endpoints,'positive_low_endpoint_checks':productive_restorations,'zero_to_positive_endpoint_checks':zero_to_positive,'direct_actual_single_restoration_classifications':actual_edges,'productive_one_edge_additions':one_edge_additions,'bounds':bounds,'scope':'Full OUT and coverage on the complete binary unit-worth ideal only; general theorem proved separately.'},indent=2))

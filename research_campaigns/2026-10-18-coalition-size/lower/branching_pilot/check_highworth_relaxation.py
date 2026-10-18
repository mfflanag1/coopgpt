#!/usr/bin/env python3
"""Independent exact replay; imports no discovery code or optimization library."""
from array import array
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path
import hashlib,json
import numpy as np
P=Path(__file__).resolve().parent
meta=json.loads((P/'quotient.json').read_text());data=np.load(P/'quotient.npz')
qmaps=data['qmaps'];profile=data['profile'];d=meta['d'];N=1<<d;K=len(meta['pointed_reps'])
assert (d,N,K)==(15,32768,172) and qmaps.shape==(N,d)
edges=[tuple(e) for e in meta['edges']];edge_set=set(edges)
assert len(edge_set)==35 and all(len(set(e))==3 and (e[0]+1)^(e[1]+1)^(e[2]+1)==0 for e in edges)
class DSU:
 def __init__(self,n):self.p=array('I',range(n));self.sz=array('I',[1])*n
 def root(self,x):
  while self.p[x]!=x:self.p[x]=self.p[self.p[x]];x=self.p[x]
  return x
 def join(self,a,b):
  a=self.root(a);b=self.root(b)
  if a==b:return
  if self.sz[a]<self.sz[b]:a,b=b,a
  self.p[b]=a;self.sz[a]+=self.sz[b]
u=DSU(N);v=DSU(N*d)
for g in meta['generators']:
 assert sorted(g)==list(range(d)) and {tuple(sorted(g[i] for i in e)) for e in edges}==edge_set
 pm=array('I',[0])*N
 for mask in range(1,N):
  low=mask&-mask;pm[mask]=pm[mask^low]|(1<<g[low.bit_length()-1])
 for mask in range(N):
  new=pm[mask];u.join(mask,new)
  for i in range(d):v.join(mask*d+i,new*d+g[i])
profile_pairs={(int(profile[m]),u.root(m)) for m in range(N)}
point_pairs={(int(qmaps[m,i]),v.root(m*d+i)) for m in range(N) for i in range(d)}
assert len(profile_pairs)==len({a for a,b in profile_pairs})==len({b for a,b in profile_pairs})==46
assert len(point_pairs)==len({a for a,b in point_pairs})==len({b for a,b in point_pairs})==172
assert set(int(profile[m]) for m in meta['profile_reps'])==set(range(46))
assert len(set(v.root(m*d+i) for m,i in meta['transitions']))==86
assert all(not m&(1<<i) for m,i in meta['transitions'])
assert set(v.root(m*d+i) for m,i in meta['transitions'])=={v.root(m*d+i) for m in range(N) for i in range(d) if not m&(1<<i)}
# Every production value has exact full-technology primal/dual witnesses.
values={}
for mask in meta['profile_reps']:
 oracle=meta['oracles'][str(mask)];x=list(map(F,oracle['primal']));y=list(map(F,oracle['dual']));val=F(oracle['value'])
 assert len(x)==35 and len(y)==15 and all(z>=0 for z in x+y)
 assert all(sum(x[t] for t,e in enumerate(edges) if j in e)<=((mask>>j)&1) for j in range(d))
 assert all(sum(y[j] for j in e)>=1 for e in edges)
 assert sum(x)==sum(y[j] for j in range(d) if mask&(1<<j))==val
 values[mask]=val
answers=[]
for fpath in sorted(P.glob('highworth_result_s*.json'),key=lambda p:int(p.stem[len('highworth_result_s'):])):
 result=json.loads(fpath.read_text());s=result['s'];payment=list(map(F,result['candidate_payments']));assert len(payment)==K+1 and all(x>=0 for x in payment)
 # Funding includes all15 owners, including every inactive owner.
 for mask in meta['profile_reps']:
  q=qmaps[mask]
  if values[mask]!=1: assert sum(payment[j] for j in q)<=payment[K]*values[mask]
  for e in edges:
   if all(mask&(1<<j) for j in e):assert sum(payment[q[j]] for j in e)>=1
 for old,i in meta['transitions']:
  new=old|(1<<i);q=qmaps[old];r=qmaps[new]
  losses=sorted([max(F(0),payment[q[j]]-payment[r[j]]) for j in range(d) if j!=i],reverse=True)
  assert payment[r[i]]-payment[q[i]]>=sum(losses[:s-1])
 combo=defaultdict(F);right=F(0)
 for item in result['certificate']:
  w=F(item['weight']);assert w>=0;tag=item['row'];kind=tag[0];old=tag[1];q=qmaps[old];row=defaultdict(F);b=F(0)
  if kind=='budget':
   assert old in values and values[old]!=1
   for var in q:row[int(var)]+=1
   row[K]-=values[old]
  elif kind=='coverage':
   e=tuple(tag[2]);assert tuple(sorted(e)) in edge_set and all(old&(1<<j) for j in e)
   for j in e:row[int(q[j])]-=1
   b=-1
  elif kind=='tcwm':
   new,i,C=tag[2:];assert not old&(1<<i) and new==old|(1<<i)
   assert i in C and len(C)==len(set(C))<=s and all(0<=j<d for j in C)
   r=qmaps[new]
   for j in C:row[int(q[j])]+=1;row[int(r[j])]-=1
  else:raise AssertionError(kind)
  for j,c in row.items():combo[j]+=w*c
  right+=w*b
 assert combo[K]<0 and all(c>=0 for j,c in combo.items() if j!=K)
 lower=right/combo[K];assert lower==payment[K]==F(result['exact_lower'])==F(result['exact_upper'])
 inactive_vars={int(qmaps[mask,i]) for mask,i in meta['pointed_reps'] if not mask&(1<<i)}
 answers.append({'s':s,'exact_optimum':str(lower),'dual_rows':len(result['certificate']),'positive_inactive_orbits':sum(payment[j]>0 for j in inactive_vars),'sha256':hashlib.sha256(fpath.read_bytes()).hexdigest()})
print(json.dumps({'status':'PASS','independent_orbit_method':'union-find on all generator edges','profile_states':N,'pointed_states':N*d,'profile_orbits':46,'pointed_orbits':172,'actual_single_restoration_edges':N*d//2,'transition_orbits':86,'full_LP_oracles':46,'solutions':answers,'scope':'Exact optimum of value>1 funding diagnostic: unit-worth funding constraints omitted, all coverage/TCWM retained. Not a whole-domain mechanism funding factor.'},indent=2))

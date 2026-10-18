#!/usr/bin/env python3
"""Independent exact replay of ternary Fano certificates; no optimizer import."""
from array import array
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path
import hashlib,json
import numpy as np
P=Path(__file__).resolve().parent;m=json.loads((P/'ternary_quotient.json').read_text());data=np.load(P/'ternary_quotient.npz')
profile=data['profile'];qmaps=data['qmaps'];caps=data['caps'];d=7;N=3**d;K=198;pw=[3**i for i in range(d)];edges=[tuple(e) for e in m['edges']];es=set(edges)
assert len(es)==7 and all(len(set(e))==3 and (e[0]+1)^(e[1]+1)^(e[2]+1)==0 for e in es)
assert qmaps.shape==(N,d) and len(profile)==N and caps.shape==(N,d)
for c in range(N):assert list(caps[c])==[c//pw[i]%3 for i in range(d)]
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
for g in m['generators']:
 assert sorted(g)==list(range(d)) and {tuple(sorted(g[i] for i in e)) for e in es}==es
 for c in range(N):
  new=sum(int(caps[c,i])*pw[g[i]] for i in range(d));u.join(c,new)
  for i in range(d):v.join(c*d+i,new*d+g[i])
pp={(int(profile[c]),u.root(c)) for c in range(N)};qq={(int(qmaps[c,i]),v.root(c*d+i)) for c in range(N) for i in range(d)}
assert len(pp)==len({a for a,b in pp})==len({b for a,b in pp})==60
assert len(qq)==len({a for a,b in qq})==len({b for a,b in qq})==198
assert set(v.root(c*d+i) for c,new,i in m['transitions'])=={v.root(c*d+i) for c in range(N) for i in range(d) if caps[c,i]<2}
assert len(m['transitions'])==132
for c,new,i in m['transitions']:assert caps[c,i]<2 and new==c+pw[i]
vals={};byoid={}
for c in m['profile_reps']:
 o=m['oracles'][str(c)];x=list(map(F,o['primal']));p=list(map(F,o['dual']));val=F(o['value'])
 assert len(x)==len(p)==7 and all(z>=0 for z in x+p)
 assert all(sum(x[t] for t,e in enumerate(edges) if j in e)<=int(caps[c,j]) for j in range(d))
 assert all(sum(p[j] for j in e)>=1 for e in es)
 assert sum(x)==sum(int(caps[c,j])*p[j] for j in range(d))==val
 vals[c]=val;byoid[int(profile[c])]=val
assert set(byoid)==set(range(60))
def worth(c,mask=127):
 sub=sum(int(caps[c,j])*pw[j] for j in range(d) if mask>>j&1);return byoid[int(profile[sub])]
answers=[];coverage_checks=0
for f in sorted(P.glob('ternary_result_s*.json'),key=lambda f:int(f.stem[len('ternary_result_s'):])):
 z=json.loads(f.read_text());s=z['s'];y=list(map(F,z['candidate_payments']));assert len(y)==K+1 and all(t>=0 for t in y)
 for c in m['profile_reps']:
  q=qmaps[c];assert sum(y[j] for j in q)<=y[K]*vals[c]
  for mask in range(128):assert sum(y[q[j]] for j in range(d) if mask>>j&1)>=worth(c,mask);coverage_checks+=1
 for c,new,i in m['transitions']:
  q=qmaps[c];r=qmaps[new];loss=sorted([max(F(0),y[q[j]]-y[r[j]]) for j in range(d) if j!=i],reverse=True)
  assert y[r[i]]-y[q[i]]>=sum(loss[:s-1])
 combo=defaultdict(F);right=F(0)
 for item in z['certificate']:
  w=F(item['weight']);assert w>=0;tag=item['row'];kind=tag[0];c=tag[1];q=qmaps[c];row=defaultdict(F);rhs=F(0)
  if kind=='budget':
   assert c in vals
   for var in q:row[int(var)]+=1
   row[K]-=vals[c]
  elif kind=='coverage':
   mask=tag[2];assert 0<=mask<128
   for j in range(d):
    if mask>>j&1:row[int(q[j])]-=1
   rhs=-worth(c,mask)
  elif kind=='tcwm':
   new,i,C=tag[2:];assert caps[c,i]<2 and new==c+pw[i] and i in C and len(C)==len(set(C))<=s
   assert all(0<=j<d for j in C);r=qmaps[new]
   for j in C:row[int(q[j])]+=1;row[int(r[j])]-=1
  else:raise AssertionError(kind)
  for j,a in row.items():combo[j]+=w*a
  right+=w*rhs
 assert combo[K]<0 and all(a>=0 for j,a in combo.items() if j!=K)
 lower=right/combo[K];assert lower==y[K]==F(z['exact_upper'])==F(z['exact_lower'])
 inactive={int(qmaps[c,i]) for c,i in m['pointed_reps'] if caps[c,i]==0}
 answers.append({'s':s,'exact_optimum':str(lower),'dual_rows':len(z['certificate']),'positive_inactive_orbits':sum(y[j]>0 for j in inactive),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
print(json.dumps({'status':'PASS','independent_orbit_method':'union-find over complete ternary generator graph','profiles':N,'pointed_states':N*d,'profile_orbits':60,'pointed_orbits':K,'inactive_pointed_orbits':66,'actual_elementary_transitions':10206,'transition_orbits':132,'full_production_oracles':60,'coalition_coverage_checks':coverage_checks,'solutions':answers,'scope':'Finite ternary pure-owner TCWM exact optima only; no arbitrary-real upper claim.'},indent=2))

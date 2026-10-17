#!/usr/bin/env python3
"""Floating static LP scout; exact maxflow values, no promotion from output."""
from pathlib import Path
from functools import lru_cache
import random,json,itertools
from scipy.optimize import linprog

def scout(e,h,edges,oe=None,oh=None):
 ne=len(e);nh=len(h);oe=list(range(ne)) if oe is None else oe;ke=max(oe)+1
 oh=list(range(ke,ke+nh)) if oh is None else oh;n=max(oe+oh)+1;owner=oe+oh;caps=e+h
 adj=[{i for j,i in edges if j==a} for a in range(ne)]
 cuts=[]
 for mask in range(1<<ne):
  cuts.append([j for j in range(ne) if not mask>>j&1]+[ne+i for i in set().union(*(adj[j] for j in range(ne) if mask>>j&1))])
 @lru_cache(None)
 def F(mask):return min(sum(caps[j] for j in cut if mask>>owner[j]&1) for cut in cuts)
 N=(1<<n)-1;grand=F(N)
 if not grand:return None
 A=[];b=[]
 for mask in range(1<<n):
  W=F(mask)
  if W:A.append([-int(mask>>i&1) for i in range(n)]);b.append(-W)
 for i in range(ke):
  m=grand-F(N^(1<<i))
  if m:A.append([-int(i==j) for j in range(n)]);b.append(-m)
 r=linprog([1]*n,A_ub=A,b_ub=b,bounds=(0,None),method='highs')
 return dict(ratio=r.fun/grand,F=grand,e=e,h=h,edges=edges,oe=oe,oh=oh,payments=r.x.tolist())
if __name__=='__main__':
 rng=random.Random(483);best=[];counts=0
 for ne,nh in [(2,2),(3,3),(4,4),(5,5),(6,6)]:
  for z in range(1200):
   e=[rng.randrange(1,7) for _ in range(ne)];h=[rng.randrange(1,7) for _ in range(nh)];edges=[(j,i) for j in range(ne) for i in range(nh) if rng.random()<.4]
   ke=min(ne,3);kh=min(nh,3)
   oe=[j%ke for j in range(ne)];oh=[ke+i%kh for i in range(nh)]
   if z%2==0 and ne<=4:oe=None;oh=None
   r=scout(e,h,edges,oe,oh);counts+=1
   if r and (not best or r['ratio']>best[-1]['ratio']+1e-10):
    best.append(r);print(r,flush=True)
 Path(__file__).with_name('access_static_discovery.json').write_text(json.dumps(dict(profiles=counts,record_improvements=best),indent=2)+'\n')

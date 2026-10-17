#!/usr/bin/env python3
"""Exact integer primal DP vs exact threshold mincuts. See analytic all-real proof."""
import itertools,random,json
from functools import lru_cache
from pathlib import Path

def check(ok,msg):
 if not ok:raise RuntimeError(msg)
def weighted(e,h,c,v,edges):
 ne=len(e);nh=len(h);edge=set(edges)
 @lru_cache(None)
 def dp(j,remaining):
  if j==ne:return 0
  best=0
  for allocation in itertools.product(*(range(min(e[j],remaining[i])+1) if (j,i) in edge and v[i]>c[j] else range(1) for i in range(nh))):
   if sum(allocation)>e[j]:continue
   profit=sum(z*(v[i]-c[j]) for i,z in enumerate(allocation))
   best=max(best,profit+dp(j+1,tuple(x-z for x,z in zip(remaining,allocation))))
  return best
 return dp(0,tuple(h))
def unit(e,h,edges):
 ne=len(e);adj=[set(i for j,i in edges if j==a) for a in range(ne)]
 return min(sum(e[j] for j in range(ne) if not(mask>>j&1))+sum(h[i] for i in set().union(*(adj[j] for j in range(ne) if mask>>j&1))) for mask in range(1<<ne))
def layer(e,h,c,v,edges):
 br=sorted(set(c+v));total=0
 for l,r in zip(br,br[1:]):
  ee=[x if cost<=l else 0 for x,cost in zip(e,c)];hh=[x if val>=r else 0 for x,val in zip(h,v)]
  total+=(r-l)*unit(ee,hh,edges)
 return total
rng=random.Random(451);profiles=0;coalitions=0
for ne,nh in [(1,1),(2,2),(2,3),(3,2),(3,3),(3,4),(4,3)]:
 for z in range(500):
  e=[rng.randrange(3) for _ in range(ne)];h=[rng.randrange(3) for _ in range(nh)]
  c=[rng.randrange(6) for _ in e];v=[rng.randrange(7) for _ in h]
  edges=[(j,i) for j in range(ne) for i in range(nh) if rng.random()<.6]
  for trial in range(8):
   if trial==0:ee=e;hh=h;profiles+=1
   else:
    ee=[x if rng.randrange(2) else 0 for x in e];hh=[x if rng.randrange(2) else 0 for x in h];coalitions+=1
   p=weighted(ee,hh,c,v,edges);q=layer(ee,hh,c,v,edges)
   check(p==q,('identity',ee,hh,c,v,edges,p,q))
out={'status':'PASS','independent_integer_profiles':profiles,'coalition_deletions':coalitions,'note':'Integer DP values equal continuous LP values by transportation total unimodularity; general all-real identity is established by the accompanying primal/dual proof. No floating arithmetic used.'}
Path(__file__).with_name('access_coarea_checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

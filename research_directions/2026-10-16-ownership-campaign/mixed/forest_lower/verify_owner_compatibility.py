#!/usr/bin/env python3
"""Independent exact actual-owner/coalition checks for the compatibility lemma."""
from fractions import Fraction as Q
from pathlib import Path
import json,random,hashlib

def need(ok,msg):
 if not ok:raise ValueError(msg)

def graph(elig,edges):
 n=len(elig);adj=[set() for _ in range(n)]
 for u,v in edges:
  for i in range(n):
   for j in range(i+1,n):
    if (elig[i][u] and elig[j][v]) or(elig[j][u] and elig[i][v]):adj[i].add(j);adj[j].add(i)
 return adj

def root_forest(adj):
 n=len(adj);par=[-2]*n;order=[]
 for r in range(n):
  if par[r]!=-2:continue
  par[r]=-1;stack=[r]
  while stack:
   i=stack.pop();order.append(i)
   for j in adj[i]:
    if j==par[i]:continue
    if par[j]!=-2:return None
    par[j]=i;stack.append(j)
 return par,order

def covers(v,edges):
 answer=[]
 for mask in range(1<<v):
  if not all(mask>>a&1 or mask>>b&1 for a,b in edges):continue
  if any(all((mask^(1<<j))>>a&1 or(mask^(1<<j))>>b&1 for a,b in edges) for j in range(v) if mask>>j&1):continue
  answer.append([j for j in range(v) if mask>>j&1])
 return answer

def worth(b,mask,cv):
 cap=[sum(b[i][j] for i in range(len(b)) if mask>>i&1) for j in range(len(b[0]))]
 return min(sum(cap[j] for j in c) for c in cv)

def payments(b,par,order,cv):
 n=len(b);subs=[1<<i for i in range(n)];F=[Q()]*n;y=[Q()]*n
 for i in reversed(order):
  for j in range(n):
   if par[j]==i:subs[i]|=subs[j]
  F[i]=worth(b,subs[i],cv);y[i]=F[i]-sum(F[j] for j in range(n) if par[j]==i)
 return y,subs

def components(mask,adj):
 remaining={i for i in range(len(adj)) if mask>>i&1};ans=[]
 while remaining:
  i=remaining.pop();stack=[i];part=1<<i
  while stack:
   u=stack.pop()
   for v in adj[u]&remaining:remaining.remove(v);stack.append(v);part|=1<<v
  ans.append(part)
 return ans

def main():
 rng=random.Random(162016);counts=dict(profiles=0,coalitions=0,component_identities=0,bundle_underreports=0,shared_resource_profiles=0,physical_cycle_profiles=0);maxowners=0
 cases=[]
 for trial in range(240):
  v=rng.randrange(2,9);edges=[(i,rng.randrange(i)) for i in range(1,v)];uf=list(range(v))
  def get(i):
   while uf[i]!=i:i=uf[i]
   return i
  for a,b in edges:
   if rng.random()<.3:uf[get(a)]=get(b)
  labs={};own=[labs.setdefault(get(i),len(labs)) for i in range(v)];n=len(labs);elig=[[own[j]==i for j in range(v)] for i in range(n)]
  degrees=[sum(i in e for e in edges) for i in range(v)]
  for j in range(v):
   if degrees[j]==1 and rng.random()<.35 and len(elig)<8:elig.append([k==j for k in range(v)])
  if root_forest(graph(elig,edges)) is None:continue
  cases.append((edges,elig,False))
 # Physical K2,2/K2,3 cycles, with shared hardware capacities and one actual power owner.
 for trial in range(20):
  left=2;right=rng.choice([2,3]);v=left+right;edges=[(a,left+b) for a in range(left) for b in range(right)]
  nleft=rng.randrange(2,5);elig=[[j<left for j in range(v)] for _ in range(nleft)]+[[j>=left for j in range(v)]]
  cases.append((edges,elig,True))
 for edges,elig,cyclic in cases:
  n=len(elig);v=len(elig[0]);maxowners=max(maxowners,n);adj=graph(elig,edges);root=root_forest(adj);need(root is not None,'fixed owner graph not forest');par,order=root;cv=covers(v,edges)
  b=[[Q(rng.randrange(12),rng.randrange(1,5)) if elig[i][j] else Q() for j in range(v)] for i in range(n)]
  y,subs=payments(b,par,order,cv);vals=[worth(b,mask,cv) for mask in range(1<<n)];need(all(z>=0 for z in y) and sum(y)==vals[-1],'nonnegative efficiency')
  for mask,val in enumerate(vals):
   need(sum(y[i] for i in range(n) if mask>>i&1)>=val,'actual coalition coverage');counts['coalitions']+=1
   need(sum(vals[c] for c in components(mask,adj))==val,'production owner-component additivity');counts['component_identities']+=1
  for i in range(n):
   for trial in range(5):
    low=[r.copy() for r in b];low[i]=[x*rng.choice([Q(),Q(1,3),Q(2,3),Q(1)]) for x in b[i]]
    other,_=payments(low,par,order,cv);need(other[i]<=y[i],'actual whole-bundle monotonicity');counts['bundle_underreports']+=1
  counts['profiles']+=1;counts['shared_resource_profiles']+=int(any(sum(elig[i][j] for i in range(n))>1 for j in range(v)));counts['physical_cycle_profiles']+=int(cyclic)
 # The standard two-pool4-owner eligibility has an actual-owner cycle.
 need(root_forest(graph([[1,0],[1,0],[0,1],[0,1]],[(0,1)])) is None,'K2,2 calibration incorrectly included')
 report=dict(status='EXACT RATIONAL PASS',counts=counts,max_actual_owners=maxowners,scope='Finite independent corroboration of conventional all-profile proof; no novelty claim',script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 Path(__file__).with_name('owner_compatibility_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()

"""Exact cut weights and max-flow realization on specified incidence trees."""
from fractions import Fraction as F
from collections import defaultdict,deque
from pathlib import Path
import json
from universal_template import junctions

def flow(rows,cols,supply,demand,capacity):
 source=('source',);sink=('sink',);adj=defaultdict(set);cap=defaultdict(F)
 def edge(a,b,v):adj[a].add(b);adj[b].add(a);cap[a,b]+=v
 for i in rows:edge(source,('r',i),supply[i])
 for j in cols:edge(('c',j),sink,demand[j])
 for i in rows:
  for j in cols:
   if capacity[i,j]>0:edge(('r',i),('c',j),capacity[i,j])
 total=F(0)
 while True:
  parent={source:None};todo=deque([source])
  while todo and sink not in parent:
   a=todo.popleft()
   for b in sorted(adj[a],key=str):
    if b not in parent and cap[a,b]>0:parent[b]=a;todo.append(b)
  if sink not in parent:break
  b=sink;delta=None
  while parent[b]is not None:
   a=parent[b];delta=cap[a,b]if delta is None else min(delta,cap[a,b]);b=a
  b=sink
  while parent[b]is not None:
   a=parent[b];cap[a,b]-=delta;cap[b,a]+=delta;b=a
  total+=delta
 if total!=sum(demand.values()):raise ValueError(f'flow shortfall {sum(demand.values())-total}')
 return {(i,j):cap[('c',j),('r',i)]for i in rows for j in cols}

def construct(m,P):
 P=[tuple(t)for t in P];r=len(P);owner={s*m+j:e for e,t in enumerate(P)for s,j in enumerate(t)};U=sorted(set(range(3*m))-set(owner));u=len(U);h=u//3
 adj=[set()for _ in range(m+r)]
 for e,t in enumerate(P):
  for j in t:adj[j].add(m+e);adj[m+e].add(j)
 seen={0};todo=[0]
 while todo:
  for j in adj[todo.pop()]-seen:seen.add(j);todo.append(j)
 if m!=2*r+1 or len(owner)!=3*r or len(seen)!=m+r:raise ValueError('tree matching counts')
 cuts={}
 for e,t in enumerate(P):
  for root in t:
   seen={root};todo=[root]
   while todo:
    for j in adj[todo.pop()]-seen-{m+e}:seen.add(j);todo.append(j)
   count=sum(i%m in seen for i in U)
   if not count:raise ValueError('empty branch')
   for j in seen:
    if j<m:cuts[e,j]=count
 p={i:[F(2,u)+F(1,3*cuts[e,i%m])for e in range(r)]for i in U}
 degree=[sum(a*m+j in owner for a in range(3))for j in range(m)]
 d={};source={};capacity={};supply={}
 for i in U:
  s,root=divmod(i,m)
  def load(a,j):return p[i][owner[a*m+j]]if a*m+j in owner else F(0)
  d[i]=[F(0)if j==root else 1-max(load(a,j)for a in range(3))for j in range(m)]
  source[i]=[F(0)if j==root else 1-load(s,j)-d[i][j]for j in range(m)]
  supply[i]=sum(source[i])
  if supply[i]!=sum(p[i]):raise ValueError('rooted tree identity')
  for j in range(m):capacity[i,j]=min(1-load(a,j)for a in range(3)if a!=s)-d[i][j]
 demand={j:F((3-degree[j])*(h-2),3*h)for j in range(m)if degree[j]<3};allocation={}
 for s in range(3):allocation.update(flow([i for i in U if i//m==s],list(demand),supply,demand,capacity))
 out=defaultdict(F)
 for i in U:
  s=i//m
  for e,t in enumerate(P):out[i,t]+=p[i][e]
  for j,v in enumerate(d[i]):out[i,(j,j,j)]+=v
  remaining=list(source[i])
  for j in demand:
   amount=allocation[i,j]
   if amount and remaining[j]:raise ValueError('source and destination overlap')
   for a in range(m):
    take=min(amount,remaining[a])
    if take:
     t=[j]*3;t[s]=a;out[i,tuple(t)]+=take;remaining[a]-=take;amount-=take
   if amount:raise ValueError('unfilled row destination')
 return {'m':m,'P':P,'parameter':'1','packings':[[i,list(t),str(v)]for (i,t),v in sorted(out.items())if v]}

if __name__=='__main__':
 out=[]
 for b in (2,8,16):
  d=construct(*junctions(b));d['junctions']=b;out.append(d);print(b,len(d['packings']),flush=True)
 Path(__file__).with_name('CUT_TRANSPORT_CERTIFICATES.json').write_text(json.dumps(out,indent=2)+'\n')

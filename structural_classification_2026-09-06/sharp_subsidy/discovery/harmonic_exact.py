from fractions import Fraction as F
from collections import deque
def probabilities(m,P):
 P=[tuple(t)for t in P];r=len(P);owner={s*m+j:e for e,t in enumerate(P)for s,j in enumerate(t)};U=sorted(set(range(3*m))-set(owner));u=len(U);h=u//3
 adj=[set()for _ in range(m+r)]
 for e,t in enumerate(P):
  for j in t:adj[j].add(m+e);adj[m+e].add(j)
 seen={0};todo=[0]
 while todo:
  for j in adj[todo.pop()]-seen:seen.add(j);todo.append(j)
 if m!=2*r+1 or len(owner)!=3*r or len(seen)!=m+r:raise ValueError('tree matching counts')
 harmonic={}
 for sector in range(3):
  roots=[i for i in U if i//m==sector];absorbers={i%m:i for i in roots};unknown=set(range(m+r))-set(absorbers)
  neighbors={v:adj[v]&unknown for v in unknown};diag={v:F(len(adj[v]))for v in unknown}
  rhs={v:{absorbers[w]:F(1)for w in adj[v]if w in absorbers}for v in unknown};queue=deque(v for v in sorted(unknown)if len(neighbors[v])<=1);records=[]
  while queue:
   v=queue.popleft()
   if v not in unknown:continue
   w=next(iter(neighbors[v]),None);a=diag[v];b=rhs[v];records.append((v,w,a,b));unknown.remove(v)
   if not a:raise ValueError('singular harmonic system')
   if w is not None:
    diag[w]-=1/a
    for i,value in b.items():rhs[w][i]=rhs[w].get(i,F(0))+value/a
    neighbors[w].remove(v)
    if len(neighbors[w])<=1:queue.append(w)
  if unknown:raise ValueError('harmonic elimination needs a tree')
  values={}
  for v,w,a,b in reversed(records):
   out=dict(b)
   if w is not None:
    for i,value in values[w].items():out[i]=out.get(i,F(0))+value
   values[v]={i:value/a for i,value in out.items()}
  for i in roots:
   harmonic[i]=[values[m+e].get(i,F(0))for e in range(r)]
 return harmonic

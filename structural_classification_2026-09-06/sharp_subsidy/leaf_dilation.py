"""Exact leaf-dilation lift of a stationary, sector-balanced tree certificate."""
from fractions import Fraction as F
from collections import defaultdict
from pathlib import Path
import json

def lift(seed,k):
 if type(k)is not int or k<1:raise ValueError('positive integer dilation')
 m0=seed['m'];P0=[tuple(t)for t in seed['P']];r0=len(P0);own0={s*m0+j:e for e,t in enumerate(P0)for s,j in enumerate(t)}
 degree0=[sum(s*m0+j in own0 for s in range(3))for j in range(m0)]
 leaves=[j for j in range(m0)if degree0[j]==1];hubs=[j for j in range(m0)if degree0[j]==3]
 if any(v not in (1,3)for v in degree0):raise ValueError('seed must have no degree-two labels')
 used_sector={j:next(s for s in range(3)if s*m0+j in own0)for j in leaves};leaf_block={j:own0[used_sector[j]*m0+j]for j in leaves}
 P=list(P0);block=list(range(r0));clones={j:[j]for j in leaves};m=m0
 for j in leaves:
  s=used_sector[j];b=leaf_block[j]
  for _ in range(k-1):
   e=next(e for e,b1 in enumerate(block)if b1==b);old=P[e];a,c=[v for v in range(3)if v!=s];middle,newleaf=m,m+1;m+=2
   first=list(old);second=list(old);first[c]=middle;second[a]=middle;second[s]=newleaf
   P[e]=tuple(first);P.append(tuple(second));block.append(b);clones[j].append(newleaf)
 own={s*m+j:e for e,t in enumerate(P)for s,j in enumerate(t)};U=sorted(set(range(3*m))-set(own));out=defaultdict(F)
 seedrows={i:(list(map(F,p)),list(map(F,d)),list(map(F,f)))for i,p,d,f in seed['rows']}
 root_origin={s*m+j1:s*m0+j for j,js in clones.items()for j1 in js for s in range(3)if s!=used_sector[j]}
 for i in U:
  s,root=divmod(i,m)
  if i not in root_origin:
   for j in range(m):
    if j!=root:out[i,(j,j,j)]+=1
   continue
  oldi=root_origin[i];oldp,_,oldflow=seedrows[oldi];p=[oldp[b]/k for b in block]
  def load(a,j):return p[own[a*m+j]]if a*m+j in own else F(0)
  d=[F(0)if j==root else 1-max(load(a,j)for a in range(3))for j in range(m)]
  source=[F(0)if j==root else 1-load(s,j)-d[j]for j in range(m)]
  destination={root:oldflow[oldi%m0]/k+F(k-1,k)}
  for j in leaves:
   if used_sector[j]==s:
    value=oldflow[j]/(k*k)+F(k-1,k*k)*oldp[leaf_block[j]]
    for j1 in clones[j]:destination[j1]=value
  for j in hubs:destination[j]=oldflow[j]/k
  for e,t in enumerate(P):out[i,t]+=p[e]
  for j,v in enumerate(d):out[i,(j,j,j)]+=v
  for j,amount in sorted(destination.items()):
   cap=min(1-load(a,j)for a in range(3)if a!=s)-d[j]
   if amount<0 or amount>cap or (amount and source[j]):raise ValueError('destination capacity or overlapping support')
   for a in range(m):
    take=min(amount,source[a])
    if take:
     t=[j]*3;t[s]=a;out[i,tuple(t)]+=take;source[a]-=take;amount-=take
   if amount:raise ValueError('insufficient row supply')
 return dict(m=m,P=P,parameter='1',dilation=k,blocks=block,clones=[[j,js]for j,js in clones.items()],packings=[[i,list(t),str(v)]for(i,t),v in sorted(out.items())if v])

if __name__=='__main__':
 here=Path(__file__).resolve().parent;seed=json.loads((here/'STATIONARY_EXACT_SEED.json').read_text());cases=[lift(seed,k)for k in (1,2,3,5)]
 (here/'LEAF_DILATION_CERTIFICATES.json').write_text(json.dumps(cases)+'\n')
 print(json.dumps(dict(cases=len(cases),entries=sum(len(d['packings'])for d in cases))))

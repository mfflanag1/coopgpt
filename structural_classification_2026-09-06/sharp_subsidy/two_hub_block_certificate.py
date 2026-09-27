"""Realize retained rational block parameters; no numerical optimizer needed."""
from pathlib import Path
from fractions import Fraction as F
import sys,json
from collections import defaultdict
from verify_variable_p import check,topology
def structure(m,P):
 r=len(P);own={s*m+j:e for e,t in enumerate(P)for s,j in enumerate(t)};degree=[sum(s*m+j in own for s in range(3))for j in range(m)]
 parent=list(range(r))
 def root(e):
  while parent[e]!=e:e=parent[e]
  return e
 for j in range(m):
  edges=[own[s*m+j]for s in range(3)if s*m+j in own]
  if len(edges)==2:parent[root(edges[0])]=root(edges[1])
 keys=sorted({root(e)for e in range(r)});block=[keys.index(root(e))for e in range(r)];B=len(keys);rb=[block.count(b)for b in range(B)];L=[[0]*3 for _ in range(B)];hubs=[j for j in range(m)if degree[j]==3]
 for j in range(m):
  if degree[j]==1:
   s=next(s for s in range(3)if s*m+j in own);L[block[own[s*m+j]]][s]+=1
 ports=[[block[own[s*m+j]]for s in range(3)]for j in hubs];adj=[set()for _ in range(B+len(hubs))]
 for h,bs in enumerate(ports):
  for b in bs:adj[b].add(B+h);adj[B+h].add(b)
 toward={}
 for b in range(B):
  pa={b:None};queue=[b]
  for v in queue:
   for w in adj[v]-set(pa):pa[w]=v;queue.append(w)
  if len(pa)!=len(adj):raise ValueError('disconnected block tree')
  toward[b]=[pa[B+h]for h in range(len(hubs))]
 return own,degree,block,rb,L,hubs,ports,toward



def realize(d):
 m=d['m'];P=d['P'];own,degree,block,rb,L,hubs,ports,toward=structure(m,P)
 B=len(L);q=d['stride'];values=list(map(F,d['values']));lookup={tuple(t):k for k,t in enumerate(d['types'])};out=defaultdict(F)
 U=sorted(set(range(3*m))-set(own))
 def add(i,e,w):
  if w:out[i,tuple(e)]+=w
 for i in U:
  s,j=divmod(i,m)
  if degree[j]==2:
   for a in range(m):
    if a!=j:add(i,(a,a,a),F(1))
   continue
  if degree[j]!=1:raise ValueError('unexpected root')
  t=next(a for a in range(3)if a*m+j in own);b0=block[own[t*m+j]];k=lookup[b0,t,s];v=values[k*q:(k+1)*q];p=[v[b]for b in block]
  diag=[F(0)if a==j else 1-max(p[own[c*m+a]]for c in range(3)if c*m+a in own)for a in range(m)]
  source=[F(0)if a==j else 1-diag[a]-(p[own[s*m+a]]if s*m+a in own else 0)for a in range(m)]
  dest=[F(0)]*m;dest[j]=v[-1]
  for a in range(m):
   if degree[a]==1 and s*m+a in own:dest[a]=v[B+block[own[s*m+a]]]
  for h,a in enumerate(hubs):dest[a]=v[2*B+h]
  if any(x<0 for x in source+dest):raise ValueError('negative marginal')
  if any(source[a] and dest[a]for a in range(m)):raise ValueError('overlapping supply demand')
  for e,w in zip(P,p):add(i,e,w)
  for a,w in enumerate(diag):add(i,(a,a,a),w)
  for a,demand in enumerate(dest):
   for b in range(m):
    z=min(demand,source[b])
    if z:
     e=[a]*3;e[s]=b;add(i,e,z);demand-=z;source[b]-=z
   if demand:raise ValueError('unmet demand')
 result={'name':d['name'],'m':m,'P':P,'parameter':'1','packings':[[i,list(e),str(v)]for (i,e),v in sorted(out.items())]}
 result['verified_entries']=check(result)
 degree,connected,cycles=topology(result)
 if not connected or cycles or degree.count(3)!=2:raise ValueError('wrong topology')
 return result

if __name__=='__main__':
 parameters=json.loads(Path(__file__).with_name('TWO_HUB_BLOCK_PARAMETERS.json').read_text())
 cases=[]
 for same in (False,True):
  for seed in range(3):
   d=next(d for d in parameters if d['name']==f'{same}_{seed}');r=realize(d);cases.append(r);print(r['name'],r['m'],r['verified_entries'],flush=True)
 Path(__file__).with_name('TWO_HUB_BLOCK_CERTIFICATES.json').write_text(json.dumps(cases)+'\n')

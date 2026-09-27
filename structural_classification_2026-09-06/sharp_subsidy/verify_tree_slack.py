"""Exact independent accounting of the all-size tree slack identity."""
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
import json
from verify_variable_p import check as check_packing

def require(ok,msg):
 if not ok:raise ValueError(msg)

def check(data):
 entries=check_packing(data);m=data['m'];P=[tuple(t)for t in data['P']];r=len(P);PS=set(P)
 require(m==2*r+1 and all(len(set(t))==3 for t in P),'tree counts and distinct labels')
 own={s*m+j:e for e,t in enumerate(P)for s,j in enumerate(t)};U=sorted(set(range(3*m))-set(own));u=len(U)
 adj=[set()for _ in range(m+r)]
 for e,t in enumerate(P):
  for j in t:adj[j].add(m+e);adj[m+e].add(j)
 diag=defaultdict(F);block=defaultdict(F);p=defaultdict(F)
 for i,t,value in data['packings']:
  t=tuple(t);v=F(value);s=i//m
  if t in PS:p[i,t]+=v
  else:
   require(t[(s+1)%3]==t[(s+2)%3],'same-sector support')
   j=t[(s+1)%3];block[i,j]+=v
   if len(set(t))==1:diag[i,j]+=v
 require(all(sum(p[i,t]for i in U)==3 for t in P),'exact P totals')
 E=F(0);L=F(0);first=F(0);second=F(0);coverage=F(0)
 for i in U:
  root=i%m;parent={root:None};queue=[root]
  for j in queue:
   for k in sorted(adj[j]):
    if k not in parent:parent[k]=j;queue.append(k)
  require(len(parent)==m+r,'connected tree')
  pi=sum(p[i,t]for t in P);di=sum(diag[i,j]for j in range(m));qi=sum(block[i,j]for j in range(m))
  ei=m-1-di-2*pi;li=m-1-qi-pi;a=F(0);b=F(0)
  require(diag[i,root]==0,'root diagonal')
  for j in range(m):
   if j==root:continue
   maximum=max(p[i,P[e-m]]for e in adj[j]);parent_weight=p[i,P[parent[j]-m]]
   loss=1-maximum-diag[i,j];order=maximum-parent_weight
   require(loss>=0 and order>=0,'nonnegative slack summands');a+=loss;b+=order
  require(ei==a+b and ei>=0 and li>=0,'row loss identity')
  E+=ei;L+=li;first+=a;second+=b;coverage+=2*di+qi
 G=coverage-3*m*(u-4)
 require(G>=0 and G+2*E+L==3,'global budget identity')
 return dict(m=m,rows=u,entries=entries,coverage_surplus=str(G),diagonal_loss=str(first),order_loss=str(second),unused_sector_capacity=str(L),weighted_loss_budget='3')

def main():
 root=Path(__file__).resolve().parent;cases=[]
 for filename in ['VARIABLE_P_CERTIFICATES.json','CUT_TRANSPORT_CERTIFICATES.json']:
  cases.extend(json.loads((root/filename).read_text()))
 cases.append(json.loads((root/'HARMONIC_FREE_CONTROL.json').read_text()))
 results=[check(d)for d in cases]
 bad=dict(cases[0]);bad['packings']=[]
 try:check(bad)
 except ValueError:pass
 else:raise ValueError('empty packing accepted')
 print(json.dumps(dict(status='PASS',cases=len(results),rows=sum(d['rows']for d in results),entries=sum(d['entries']for d in results),results=results,negative_controls=1)))
if __name__=='__main__':main()

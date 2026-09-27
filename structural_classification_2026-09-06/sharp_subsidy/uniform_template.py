"""Closed-form deletion certificates under the count condition; no optimizer."""
from fractions import Fraction as F
from collections import defaultdict
from pathlib import Path
import json


def construct(m,P):
 P=[tuple(t)for t in P]
 if not isinstance(m,int) or m<1 or any(len(t)!=3 or any(not isinstance(v,int)or not 0<=v<m for v in t)for t in P):raise ValueError('invalid configuration')
 used={k*m+t[k]for t in P for k in range(3)}
 if len(used)!=3*len(P):raise ValueError('P is not a partial matching')
 degree=[sum(k*m+j in used for k in range(3))for j in range(m)]
 if min(degree)<1:raise ValueError('isolated labels are outside this construction')
 U=sorted(set(range(3*m))-used);h=m-len(P)
 if h<2:raise ValueError('h<2 is handled by the elementary zero-obstruction bound')
 alpha=F(1,h);beta=1-alpha;flows={};counts=[]
 for s in range(3):
  rows=[i for i in U if i//m==s]
  leaves=[j for j in range(m)if degree[j]==1 and s*m+j in used]
  strong=sum(degree[i%m]==2 for i in rows);L=len(leaves)
  if L and L*(h-2)>strong*min(h-1,L)+h-strong:raise ValueError('count condition failed')
  counts.append({'sector':s,'L':L,'N':strong,'h':h})
  if not L:
   for i in rows:flows[i]={}
   continue
  cs=min(F(1),F(h-1,L));cw=F(1,L)
  capacity=strong*cs+(h-strong)*cw
  theta=F(h-2)/capacity
  for i in rows:
   amount=theta*(cs if degree[i%m]==2 else cw)/h
   flows[i]={j:amount for j in leaves if amount}
 coeff=defaultdict(F)
 for i in U:
  s,j=divmod(i,m)
  for label in range(m):
   if label!=j:coeff[i,(label,)*3]+=beta
  for t in P:coeff[i,t]+=alpha
  destinations=dict(flows[i]);destinations[j]=beta-sum(destinations.values())
  for label,mass in destinations.items():
   if mass<0:raise ValueError('negative residual mass')
   for other in U:
    if other//m==s and other!=i:
     t=[label]*3;t[s]=other%m;coeff[i,tuple(t)]+=mass/(h-1)
 return {'m':m,'P':P,'counts':counts,'packings':[[i,list(t),str(v)]for (i,t),v in sorted(coeff.items())if v]}


def run():
 out=[]
 for q in range(1,13):
  P=[(s,q+s,s-1 if s else 2*q)for s in range(q)]
  d=construct(2*q+1,P);d['shape']='chain';d['q']=q;out.append(d)
 d=construct(7,[(0,1,2),(3,0,4),(5,6,0)]);d['shape']='star';out.append(d)
 P=[(0,1,2),(3,0,4),(5,6,0),(1,7,8),(9,10,1)]
 try:construct(11,P)
 except ValueError as e:
  if str(e)!='count condition failed':raise
 else:raise ValueError('outside-condition test was incorrectly accepted')
 Path(__file__).with_name('UNIFORM_TEMPLATE_CERTIFICATES.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':'GENERATED','configurations':len(out),'outside_condition_rejected':True}))


if __name__=='__main__':run()

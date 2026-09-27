"""Independent packing checks and equality conditions for minimum root mass."""
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
import json
from verify_variable_p import check,topology,require

def verify(d):
 count=check(d);m=d['m'];P=[tuple(e)for e in d['P']];degree,connected,cycles=topology(d)
 require(connected and cycles==0,'tree');g=degree.count(3);r=len(P)
 own={s*m+j:e for e,t in enumerate(P)for s,j in enumerate(t)};U=sorted(set(range(3*m))-set(own));p=defaultdict(F);diag=defaultdict(F);extra=defaultdict(F)
 for i,e,w in d['packings']:
  e=tuple(e);w=F(w)
  if e in P:p[i,P.index(e)]+=w
  elif len(set(e))==1:diag[i,e[0]]+=w
  else:
   s=i//m;j=e[(s+1)%3];require(e[(s+2)%3]==j,'same-sector transfer');extra[i,j]+=w
 for e in range(r):
  require(sum(p[i,e]for i in U)==3,'P column total')
  for s in range(3):require(sum(p[i,e]for i in U if i//m==s)==1,'sector balance')
 for i in U:
  if degree[i%m]==2:require(all(p[i,e]==0 for e in range(r)),'degree-two root P mass')
  require(m-1-sum(diag[i,j]for j in range(m))-2*sum(p[i,e]for e in range(r))==0,'E=0')
  for j in range(m):
   target=F(0)if j==i%m else 1-max(p[i,own[s*m+j]]for s in range(3)if s*m+j in own)
   require(diag[i,j]==target,'maximal diagonal')
  require(sum(extra[i,j]for j in range(m))==sum(p[i,e]for e in range(r)),'unused source supply')
 R=F(0)
 for j in range(m):
  if degree[j]!=1:
   require(all(extra[i,j]==0 for i in U),'nonleaf transfer destination')
   continue
  t=next(s for s in range(3)if s*m+j in own);e=own[t*m+j];roots=[s*m+j for s in range(3)if s!=t];a=sum(p[i,e]for i in roots);R+=a;delta=1-a
  require(delta>=0,'negative leaf deficit')
  for s in range(3):require(sum(extra[i,j]for i in U if i//m==s)==delta,'leaf equality')
 require(R==g+2,'root lower bound not attained')
 hub_loads=[sum(max(p[i,own[s*m+j]]for s in range(3))for i in U)for j in range(m)if degree[j]==3]
 require(sum(hub_loads)==R+3*g-3,'hub identity')
 require(all(a<=4 for a in hub_loads)and sum(4-a for a in hub_loads)==1,'single unit hub slack')
 return {'m':m,'hubs':g,'root_mass':str(R),'entries':count,'hub_slacks':[str(4-a)for a in hub_loads]}

def run():
 ds=json.loads(Path(__file__).with_name('ROOT_MASS_CERTIFICATES.json').read_text());require([d['name']for d in ds]==['ROOT_MIN_False','ROOT_MIN_True'],'inventory')
 results=[verify(d)for d in ds]
 bad=dict(ds[0]);bad['packings']=[]
 try:verify(bad)
 except ValueError:pass
 else:raise ValueError('empty packing accepted')
 print(json.dumps({'status':'PASS','cases':results,'negative_controls':1,'scope':'exact attainment of root-mass bound on two seed supports'}))
if __name__=='__main__':run()

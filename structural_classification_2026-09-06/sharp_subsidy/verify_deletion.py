"""Independent rational pair-coverage checker; no optimizer is imported."""
import json
from fractions import Fraction as F
from pathlib import Path


def require(ok,msg):
 if not ok:raise ValueError(msg)


def check(d):
 m=d['m'];P=[tuple(t)for t in d['P']];n=3*m
 used=[s*m+t[s]for t in P for s in range(3)]
 require(all(len(t)==3 and all(0<=j<m for j in t)for t in P),'bad matching')
 require(len(set(used))==len(used),'matching overlaps')
 U=sorted(set(range(n))-set(used));u=len(U)
 require(u>=6,'template domain')
 cap={i:[F(0)]*n for i in U};coverage={};demand={}
 def pairs(t):
  return[(0,t[0],t[1]),(1,t[0],t[2]),(2,t[1],t[2])]
 for j in range(m):
  for edge in pairs((j,j,j)):demand[edge]=demand.get(edge,F(0))+u-4
 for t in P:
  for edge in pairs(t):demand[edge]=demand.get(edge,F(0))+3
 for i,t,raw in d['packings']:
  f=F(raw)
  require(i in U and len(t)==3 and all(isinstance(v,int)and 0<=v<m for v in t)and f>=0,'invalid packing entry')
  require(t[i//m]!=i%m,'deleted player used')
  for s,v in enumerate(t):cap[i][s*m+v]+=f
  for edge in pairs(t):coverage[edge]=coverage.get(edge,F(0))+f
 require(all(v<=1 for vals in cap.values()for v in vals),'capacity exceeded')
 require(all(coverage.get(edge,F(0))>=v for edge,v in demand.items()),'pair demand missed')
 return len(d['packings'])


def run():
 data=json.loads(Path(__file__).with_name('DELETION_CERTIFICATES.json').read_text())
 expected={(3,((0,1,2),)),(5,((0,2,4),(1,3,0))),(7,((0,3,6),(1,4,0),(2,5,1))),(9,((0,4,8),(1,5,0),(2,6,1),(3,7,2))),(7,((0,1,2),(3,0,4),(5,6,0)))}
 actual={(d['m'],tuple(tuple(t)for t in d['P']))for d in data}
 require(len(data)==5 and actual==expected,'certificate set incomplete or duplicated')
 count=sum(check(d)for d in data)
 bad=dict(data[0]);bad['packings']=[]
 try:check(bad)
 except ValueError:pass
 else:raise ValueError('negative control accepted')
 print(json.dumps({'status':'PASS','fixed_matching_configurations':len(data),'rational_packing_entries':count,'negative_controls':1,'scope':'all nonnegative pair coefficients for each retained fixed matching configuration'}))


if __name__=='__main__':run()

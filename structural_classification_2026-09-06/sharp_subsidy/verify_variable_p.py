"""Independent rational coefficient verification of the variable-P fixed-pattern certificates."""
import json
from fractions import Fraction as F
from pathlib import Path


def require(ok,msg):
 if not ok:raise ValueError(msg)


def check(d):
 m=d['m'];t=F(d['parameter']);P=[tuple(e)for e in d['P']];n=3*m
 require(t==1,'parameter outside theorem')
 require(m>0 and all(len(e)==3 and all(isinstance(v,int)and 0<=v<m for v in e)for e in P),'invalid matching data')
 used=[s*m+e[s]for e in P for s in range(3)]
 require(len(used)==len(set(used)),'matching overlap')
 U=sorted(set(range(n))-set(used));u=len(U);require(u>=6,'wrong elementary branch')
 cap={i:[F(0)]*n for i in U};got={};need={}
 def pairs(e):return[(0,e[0],e[1]),(1,e[0],e[2]),(2,e[1],e[2])]
 for j in range(m):
  for edge in pairs((j,j,j)):need[edge]=need.get(edge,F(0))+u-5+t
 for e in P:
  for edge in pairs(e):need[edge]=need.get(edge,F(0))+3
 for i,e,raw in d['packings']:
  v=F(raw);require(i in U and len(e)==3 and all(isinstance(j,int)and 0<=j<m for j in e)and v>=0,'bad packing entry')
  require(e[i//m]!=i%m,'deleted player used')
  for s,j in enumerate(e):cap[i][s*m+j]+=v
  for edge in pairs(e):got[edge]=got.get(edge,F(0))+v
 require(all(v<=1 for a in cap.values()for v in a),'capacity exceeded')
 require(all(got.get(edge,F(0))>=v for edge,v in need.items()),'pair domination failed')
 return len(d['packings'])


def topology(d):
 m=d['m'];P=d['P'];degree=[0]*m;adj=[set()for _ in range(m+len(P))]
 for r,e in enumerate(P):
  for v in e:degree[v]+=1;adj[v].add(m+r);adj[m+r].add(v)
 seen={0};pending=[0]
 while pending:
  for v in adj[pending.pop()]-seen:seen.add(v);pending.append(v)
 return degree,len(seen)==len(adj),3*len(P)-(m+len(P))+1


def run():
 rows=json.loads(Path(__file__).with_name('VARIABLE_P_CERTIFICATES.json').read_text())
 require([d['m']for d in rows]==[11,19,35],'case inventory')
 count=0
 for d in rows:
  count+=check(d);m=d['m'];P={tuple(e)for e in d['P']};amounts={e:F(0)for e in P}
  for i,e,v in d['packings']:
   e=tuple(e)
   if e in P:amounts[e]+=F(v)
   else:
    s=i//m
    require(e[(s+1)%3]==e[(s+2)%3],'transfer in another sector')
  require(all(v==3 for v in amounts.values()),'P team total is not three')
  degree,connected,cycles=topology(d)
  require(connected and cycles==0 and degree.count(3)==d['junctions'],'junction topology')
 bad=dict(rows[0]);bad['packings']=[]
 try:check(bad)
 except ValueError:pass
 else:raise ValueError('empty certificate accepted')
 print(json.dumps({'status':'PASS','cases':len(rows),'rational_entries':count,'fixed_pattern_upper':'1/3','same_sector_transfers':True,'exact_P_totals':3,'negative_controls':1}))
if __name__=='__main__':run()

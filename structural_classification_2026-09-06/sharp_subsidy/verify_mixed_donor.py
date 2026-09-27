"""Independent rational coefficient verification of the mixed-donor bound samples."""
import json
from fractions import Fraction as F
from pathlib import Path


def require(ok,msg):
 if not ok:raise ValueError(msg)


def check(d,*,finite=False,localization=False):
 m=d['m'];t=F(d['parameter']);P=[tuple(e)for e in d['P']];n=3*m
 require(m-len(P)>=2,'elementary branch')
 require(not (finite and localization),'ambiguous parameter scope')
 expected=F(4,5)+F(1,20*(m-len(P))) if finite else F(4,5)
 if localization:
  h=m-len(P);degree=[sum(team.count(j)for team in P)for j in range(m)];B=F(degree.count(1),h)
  if B<=1:expected=F(81,100)
  else:
   x=[F(sum(degree[team[s]]==1 for team in P),h)for s in range(3)]
   eta=F(2,3)*(F(3,2)-B)*(B-F(3,5))+sum((v-B/3)**2 for v in x)+F(m-2*h+1,h)
   require(eta>=0,'negative localization gap')
   expected=F(4,5)+min(F(1),eta)/100
 require(t==expected,'parameter outside theorem')
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
 rows=json.loads(Path(__file__).with_name('MIXED_DONOR_CERTIFICATES.json').read_text())
 expected={'chain_1':3,'chain_4':9,'chain_12':25,'junctions_1':7,'junctions_2':11,'junctions_3':15,'junctions_4':19,'near_worst_count':23,'cyclic_junctions':12,'overlapping_pair':4,'active_donors_8':35,'active_donors_12':51,'alternating_cycle':12,'active_degree_two':64}
 require(len(rows)==len(expected)and {d['case']:d['m']for d in rows}==expected,'wrong case inventory')
 count=0
 for d in rows:
  require(F(d['parameter'])==F(4,5),'unexpected sample parameter')
  count+=check(d);degree,connected,cycles=topology(d)
  require(connected,'sample graph disconnected')
  if d['case'].startswith('junctions_'):require(degree.count(3)==int(d['case'].split('_')[1])and cycles==0,'wrong junction topology')
  if d['case']=='cyclic_junctions':require(cycles>0,'cyclic sample is acyclic')
  if d['case']=='overlapping_pair':require(any(len(set(e))<3 for e in d['P']),'missing shared pair')
  if d['case']=='near_worst_count':
   h=d['m']-len(d['P']);used={s*d['m']+e[s]for e in d['P']for s in range(3)}
   L=sum(degree[j]==1 and d['m']+j in used for j in range(d['m']))
   N=sum(degree[j]==2 and d['m']+j not in used for j in range(d['m']))
   require(F(L,h)==F(7,12)and F(N,h)==F(1,6),'wrong near-worst counts')
 require(all(F(d['total_donor_transfer'])>0 for d in rows if d['case'].startswith('active_donors_')),'new transfer branch not exercised')
 active=next(d for d in rows if d['case']=='active_degree_two');degree,connected,_=topology(active)
 require(connected and degree.count(3)==0 and F(active['total_donor_transfer'])>0,'degree-two donors not exercised')
 bad=dict(rows[-1]);bad['packings']=[]
 try:check(bad)
 except ValueError:pass
 else:raise ValueError('empty-certificate negative control accepted')
 bad=dict(rows[0]);bad['parameter']='1'
 try:check(bad)
 except ValueError:pass
 else:raise ValueError('out-of-range parameter accepted')
 # This cycle family obstructs raising t using only degree-three donors.
 h=32;m=2*h;P=[(h+j,j,(j+1)%h)if j%2==0 else(j,h+j,(j+1)%h)for j in range(h)]
 used={s*m+j for e in P for s,j in enumerate(e)}
 require(len(used)==3*h,'negative-control cycle matching')
 degree=[sum(s*m+j in used for s in range(3))for j in range(m)]
 require(degree.count(3)==0 and degree.count(1)==h and degree.count(2)==h,'negative-control cycle degrees')
 L=sum(degree[j]==1 and j in used for j in range(m));N=sum(degree[j]==2 and j not in used for j in range(m))
 t=F(4,5);alpha=F(1,h);beta=1-alpha;delta=t-2*alpha
 deficit=L*delta-N*min(L*alpha,beta)-(h-N)*min(L*alpha,beta-delta)
 require(L==N==h//2 and deficit==F(1,10),'out-of-range template obstruction')
 h=30;t=F(5,6);L=h//2;beta=1-F(1,h);delta=t-F(2,h)
 required=3*(L*delta-h*(beta-delta));budget=(2-t)*(h//2-1)
 require(required-budget==F(1,6),'balanced-junction extrapolation control')
 print(json.dumps({'status':'PASS','independent_coefficient_check':True,'cases':len(rows),'rational_entries':count,'negative_controls':4,'rational_upper':'2/5'}))


if __name__=='__main__':run()

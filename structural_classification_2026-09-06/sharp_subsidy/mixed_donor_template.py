"""Connected-label deletion construction proving the universal upper bound 2/5."""
from fractions import Fraction as F
from collections import defaultdict
from pathlib import Path
import json
from universal_template import cases,junctions
from localization_parameter import parameter as localization_parameter


def construct(m,P,*,t=F(4,5)):
 P=[tuple(e)for e in P]
 if not isinstance(m,int)or m<1 or any(len(e)!=3 or any(not isinstance(j,int)or not 0<=j<m for j in e)for e in P):raise ValueError('invalid labels')
 used={s*m+j for e in P for s,j in enumerate(e)}
 if len(used)!=3*len(P):raise ValueError('not a matching')
 degree=[sum(s*m+j in used for s in range(3))for j in range(m)]
 adj=[set()for _ in range(m)]
 for e in P:
  for j in e:adj[j].update(e)
 seen={0};todo=[0]
 while todo:
  for j in adj[todo.pop()]-seen:seen.add(j);todo.append(j)
 if len(seen)!=m or min(degree)<1:raise ValueError('connected nontrivial reduction required')
 h=m-len(P)
 if h<2:raise ValueError('elementary branch')
 if t not in (F(4,5),F(4,5)+F(1,20*h),localization_parameter(m,P)):raise ValueError("parameter outside proved bounds")
 alpha=F(1,h);beta=1-alpha;delta=max(F(0),t-2*alpha)
 U=sorted(set(range(3*m))-used);donors=[j for j in range(m)if degree[j]>=2];budget={j:1-t if degree[j]==2 else 2-t for j in donors};total_budget=sum(budget.values(),F(0));n3=sum(degree[j]==3 for j in donors)
 extra={};base={};leaves_by_sector={};total_extra=F(0)
 for s in range(3):
  rows=[i for i in U if i//m==s];leaves=[j for j in range(m)if degree[j]==1 and s*m+j in used];leaves_by_sector[s]=leaves;L=len(leaves)
  if not L or not delta:
   for i in rows:base[i]=extra[i]=F(0)
   continue
  caps={i:min(L*alpha,beta if degree[i%m]==2 else beta-delta)for i in rows}
  available=sum(caps.values());demand=L*delta;D=max(F(0),demand-available)
  if D:
   headroom={i:L*alpha-caps[i]for i in rows};room=sum(headroom.values())
   if not room or D>room or not total_budget:raise ValueError('extra transfer unavailable')
   for i in rows:base[i]=caps[i];extra[i]=D*headroom[i]/room
  else:
   theta=demand/available
   for i in rows:base[i]=theta*caps[i];extra[i]=F(0)
  total_extra+=D
 if total_extra>total_budget:raise ValueError('donor budget lemma failed')
 out=defaultdict(F)
 for i in U:
  s,j=divmod(i,m);leaves=leaves_by_sector[s];L=len(leaves)
  if extra[i] and degree[j]!=1:raise ValueError('extra row is not a leaf')
  reductions={k:extra[i]*budget[k]/total_budget for k in donors}if extra[i] else {}
  if any(z>beta for z in reductions.values()):raise ValueError('negative donor diagonal')
  for k in range(m):
   if k!=j:out[i,(k,k,k)]+=beta-reductions.get(k,F(0))
  for e in P:out[i,e]+=alpha
  destinations={j:beta-base[i]}
  if L:
   for k in leaves:destinations[k]=base[i]/L
  for k,mass in destinations.items():
   for other in U:
    if other//m==s and other!=i:
     e=[k]*3;e[s]=other%m;out[i,tuple(e)]+=mass/(h-1)
  if extra[i]:
   for k in donors:
    for l in leaves:
     e=[l]*3;e[s]=k;out[i,tuple(e)]+=reductions[k]/L
 return {'m':m,'P':P,'parameter':str(t),'obstruction_upper':str((2-t)/3),'total_donor_transfer':str(total_extra),'donor_budget':str(total_budget),'packings':[[i,list(e),str(v)]for (i,e),v in sorted(out.items())if v]}


def run():
 configs=cases()
 h=6;P=[(h+j,j,(j+1)%h)if j%2==0 else(j,h+j,(j+1)%h)for j in range(h)]
 configs.append(('alternating_cycle',2*h,P))
 h=32;P=[(h+j,j,(j+1)%h)if j%2==0 else(j,h+j,(j+1)%h)for j in range(h)]
 configs.append(('active_degree_two',2*h,P))
 for b in (8,12):
  m,P=junctions(b);configs.append((f'active_donors_{b}',m,P))
 out=[]
 for name,m,P in configs:
  d=construct(m,P);d['case']=name;out.append(d)
 Path(__file__).with_name('MIXED_DONOR_CERTIFICATES.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':'GENERATED','cases':len(out),'upper':'2/5','active_donor_cases':[d['case']for d in out if F(d['total_donor_transfer'])>0]}))
if __name__=='__main__':run()

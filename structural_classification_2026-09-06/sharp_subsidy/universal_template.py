"""Universal rational deletion template for 0 <= t <= 4*sqrt(2)-5."""
from fractions import Fraction as F
from collections import defaultdict
from pathlib import Path
import json


def construct(m,P,t=F(13137,20000)):
 P=[tuple(e)for e in P];t=F(t)
 if t<0 or t*t+10*t-7>0:raise ValueError('parameter outside proved range')
 if not isinstance(m,int)or m<1 or any(len(e)!=3 or any(not isinstance(v,int)or not 0<=v<m for v in e)for e in P):raise ValueError('invalid configuration')
 used={s*m+e[s]for e in P for s in range(3)}
 if len(used)!=3*len(P):raise ValueError('P overlaps')
 degree=[sum(s*m+j in used for s in range(3))for j in range(m)]
 if min(degree)<1:raise ValueError('remove isolated labels before this construction')
 h=m-len(P)
 if h<2:raise ValueError('h<2 uses the elementary zero-obstruction lemma')
 U=sorted(set(range(3*m))-used);alpha=F(1,h);beta=1-alpha;delta=max(F(0),t-2*alpha)
 flows={};counts=[]
 for s in range(3):
  rows=[i for i in U if i//m==s]
  leaves=[j for j in range(m)if degree[j]==1 and s*m+j in used];L=len(leaves)
  N=sum(degree[i%m]==2 for i in rows)
  if len(rows)!=h or 2*L>h+N:raise ValueError('structural counting identity failed')
  counts.append({'sector':s,'h':h,'L':L,'N':N})
  if not L or not delta:
   for i in rows:flows[i]={}
   continue
  cs=min(alpha,beta/L);cw=min(alpha,(beta-delta)/L)
  capacity=N*cs+(h-N)*cw
  if capacity<delta:raise ValueError('universal flow inequality failed')
  theta=delta/capacity
  for i in rows:
   x=theta*(cs if degree[i%m]==2 else cw)
   flows[i]={j:x for j in leaves if x}
 out=defaultdict(F)
 for i in U:
  s,j=divmod(i,m)
  for label in range(m):
   if label!=j:out[i,(label,)*3]+=beta
  for e in P:out[i,e]+=alpha
  destinations=dict(flows[i]);destinations[j]=beta-sum(destinations.values())
  for label,mass in destinations.items():
   if mass<0:raise ValueError('negative pair mass')
   for other in U:
    if other//m==s and other!=i:
     e=[label]*3;e[s]=other%m;out[i,tuple(e)]+=mass/(h-1)
 return {'m':m,'P':P,'parameter':str(t),'counts':counts,'obstruction_upper':str((2-t)/3),'packings':[[i,list(e),str(v)]for (i,e),v in sorted(out.items())if v]}


def junctions(b):
 P=[];used=set();n=b
 for j in range(b-1):
  P.append((j,j+1,n));used.update([(0,j),(1,j+1)]);n+=1
 for j in range(b):
  for s in range(3):
   if (s,j)in used:continue
   e=[None]*3;e[s]=j
   for k in range(3):
    if k!=s:e[k]=n;n+=1
   P.append(tuple(e))
 return n,P


def graft(m,P,target_sector,count):
 P=list(P)
 for _ in range(count):
  positions={j:[]for j in range(m)}
  for e in P:
   for s,j in enumerate(e):positions[j].append(s)
  label=next(j for j,ss in positions.items()if len(ss)==1 and ss[0]!=target_sector)
  old=positions[label][0];new=next(s for s in range(3)if s not in [old,target_sector])
  e=[None]*3;e[new]=label
  for s in range(3):
   if s!=new:e[s]=m;m+=1
  P.append(tuple(e))
 return m,P


def cases():
 out=[]
 for q in [1,4,12]:out.append((f'chain_{q}',2*q+1,[(s,q+s,s-1 if s else 2*q)for s in range(q)]))
 for b in range(1,5):
  m,P=junctions(b);out.append((f'junctions_{b}',m,P))
 m,P=graft(*junctions(4),1,2);out.append(('near_worst_count',m,P))
 out.append(('cyclic_junctions',12,[(0,1,3),(1,2,4),(2,0,5),(6,7,0),(8,9,1),(10,11,2)]))
 out.append(('overlapping_pair',4,[(0,0,1),(1,2,3)]))
 return out


def run():
 out=[]
 for name,m,P in cases():
  d=construct(m,P);d['case']=name;out.append(d)
 Path(__file__).with_name('UNIVERSAL_TEMPLATE_CERTIFICATES.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':'GENERATED','cases':len(out),'parameter':'13137/20000','rational_universal_upper':'26863/60000'}))


if __name__=='__main__':run()

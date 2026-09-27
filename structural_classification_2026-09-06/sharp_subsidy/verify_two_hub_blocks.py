"""Check full rational packings without importing the compressed LP or realizer."""
import json
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path
from verify_variable_p import check,topology,require


def verify(rows):
 require([d['name']for d in rows]==[f'{same}_{seed}'for same in (False,True)for seed in range(3)],'inventory')
 require([d['m']for d in rows]==[11,61,55,13,63,57],'sizes')
 count=0
 for d in rows:
  count+=check(d);m=d['m'];P=[tuple(e)for e in d['P']];pset=set(P)
  degree,connected,cycles=topology(d)
  require(connected and cycles==0 and degree.count(3)==2,'two-hub tree')
  require(all(len(set(e))==3 for e in P),'repeated label in team')
  own={s*m+j:e for e,t in enumerate(P)for s,j in enumerate(t)}
  U=sorted(set(range(3*m))-set(own));p=defaultdict(F);diag=defaultdict(F)
  for i,e,w in d['packings']:
   e=tuple(e);w=F(w)
   if e in pset:p[i,P.index(e)]+=w
   elif len(set(e))==1:diag[i,e[0]]+=w
   else:
    s=i//m;require(e[(s+1)%3]==e[(s+2)%3],'wrong transfer sector')
  for e in range(len(P)):
   for s in range(3):require(sum(p[i,e]for i in U if i//m==s)==1,'sector balance')
  # Independent degree-two components; no discovery topology routines used.
  adj=[set()for _ in P]
  for j in range(m):
   es=[own[s*m+j]for s in range(3)if s*m+j in own]
   if degree[j]==2:
    a,b=es;adj[a].add(b);adj[b].add(a)
    require(all(p[i,a]==p[i,b]for i in U),'nonconstant block')
  groups=[];unseen=set(range(len(P)))
  while unseen:
   group={min(unseen)};queue=list(group)
   for e in queue:
    for f in adj[e]-group:group.add(f);queue.append(f)
   groups.append(group);unseen-=group
  require(len(groups)==5,'five blocks')
  hub=[j for j in range(m)if degree[j]==3]
  shared=[group for group in groups if all(any(own[s*m+j]in group for s in range(3))for j in hub)]
  require(len(shared)==1,'unique central block')
  central=shared[0];ports=[next(s for s in range(3)if own[s*m+j]in central)for j in hub]
  require((ports[0]==ports[1])==d['name'].startswith('True'),'central port case')
  for i in U:
   root=i%m
   if degree[root]==2:require(all(p[i,e]==0 for e in range(len(P))),'non-leaf P row')
   for j in range(m):
    target=F(0)if j==root else 1-max(p[i,own[s*m+j]]for s in range(3)if s*m+j in own)
    require(diag[i,j]==target,'maximal diagonal')
   require(m-1-sum(diag[i,j]for j in range(m))-2*sum(p[i,e]for e in range(len(P)))==0,'E=0')
 return count


def run():
 rows=json.loads(Path(__file__).with_name('TWO_HUB_BLOCK_CERTIFICATES.json').read_text())
 count=verify(rows)
 bad=[dict(d)for d in rows];bad[0]['packings']=[]
 try:verify(bad)
 except ValueError:pass
 else:raise ValueError('empty certificate accepted')
 bad=[dict(d)for d in rows];bad[0]['name']='True_0'
 try:verify(bad)
 except ValueError:pass
 else:raise ValueError('wrong inventory accepted')
 print(json.dumps({'status':'PASS','cases':len(rows),'rational_entries':count,'port_types':2,'negative_controls':2,'scope':'six fixed two-hub supports; not arbitrary leaf counts'}))
if __name__=='__main__':run()

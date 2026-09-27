"""Independent stationary seed and leaf-dilation certificate verification."""
from fractions import Fraction as F
from pathlib import Path
from collections import defaultdict
import json
from verify_variable_p import check as check_packing,topology

def require(ok,msg):
 if not ok:raise ValueError(msg)

def seed_check(d):
 count=check_packing(d);m=d['m'];P=[tuple(t)for t in d['P']];r=len(P);degree,connected,cycles=topology(d)
 require(connected and cycles==0 and set(degree)<={1,3}and degree.count(3)==2,'seed topology')
 own={s*m+j:e for e,t in enumerate(P)for s,j in enumerate(t)};U=sorted(set(range(3*m))-set(own));leaves=[j for j in range(m)if degree[j]==1]
 p=defaultdict(F);diag=defaultdict(F);flow=defaultdict(F)
 for i,t,v in d['packings']:
  t=tuple(t);v=F(v);s=i//m
  if t in P:p[i,P.index(t)]+=v
  elif len(set(t))==1:diag[i,t[0]]+=v
  else:
   require(t[(s+1)%3]==t[(s+2)%3],'same-sector seed');flow[i,t[(s+1)%3]]+=v
 require(len(d['rows'])==len(U)and {row[0]for row in d['rows']}==set(U),'seed row metadata')
 for i,ps,ds,fs in d['rows']:
  require(list(map(F,ps))==[p[i,e]for e in range(r)]and list(map(F,ds))==[diag[i,j]for j in range(m)]and list(map(F,fs))==[flow[i,j]for j in range(m)],'seed metadata equals certificate')
  s,root=divmod(i,m)
  require(sum(p[i,e]*sum(degree[j]==1 and a!=s for a,j in enumerate(t))for e,t in enumerate(P))==1,'stationarity')
  require(m-1-sum(diag[i,j]for j in range(m))-2*sum(p[i,e]for e in range(r))==0,'seed E=0')
 for s in range(3):
  for e in range(r):require(sum(p[i,e]for i in U if i//m==s)==1,'sector balance')
 return count,m,P,own,degree,leaves

def main():
 here=Path(__file__).resolve().parent;seed=json.loads((here/'STATIONARY_EXACT_SEED.json').read_text());seed_entries,m0,P0,own0,degree0,leaves=seed_check(seed)
 cases=json.loads((here/'LEAF_DILATION_CERTIFICATES.json').read_text());require([d['dilation']for d in cases]==[1,2,3,5],'case inventory');entries=0
 for d in cases:
  entries+=check_packing(d);m=d['m'];P=d['P'];k=d['dilation'];degree,connected,cycles=topology(d);blocks=d['blocks'];clones={j:js for j,js in d['clones']};own={s*m+j:e for e,t in enumerate(P)for s,j in enumerate(t)}
  require(m==18*k-7 and len(P)==9*k-4 and connected and cycles==0 and degree.count(3)==2,'dilated counts')
  require(len(blocks)==len(P)and all(type(b)is int and 0<=b<len(P0)for b in blocks),'block map')
  require(set(clones)==set(leaves)and len(d['clones'])==len(leaves),'clone map')
  all_clones=[j1 for js in clones.values()for j1 in js]
  require(len(set(all_clones))==9*k and set(all_clones)=={j for j in range(m)if degree[j]==1},'all leaf clones')
  for j,js in clones.items():
   s=next(s for s in range(3)if s*m0+j in own0);b=own0[s*m0+j]
   require(len(js)==k and all(s*m+j1 in own and blocks[own[s*m+j1]]==b for j1 in js),'clone sectors and blocks')
  for j in range(m0):
   if degree0[j]==3:require(all(blocks[own[s*m+j]]==own0[s*m0+j]for s in range(3)),'hub ports preserved')
  for j in range(m):
   if degree[j]==2:require(len({blocks[own[s*m+j]]for s in range(3)if s*m+j in own})==1,'degree-two links remain within block')
  for b,t in enumerate(P0):require(blocks.count(b)==1+(k-1)*sum(degree0[j]==1 for j in t),'block sizes')
  for i,t,v in d['packings']:
   if tuple(t)not in {tuple(t)for t in P}:
    s=i//m;require(t[(s+1)%3]==t[(s+2)%3],'same-sector lift')
 bad=dict(cases[-1]);bad['packings']=[]
 try:check_packing(bad)
 except ValueError:pass
 else:raise ValueError('empty lift accepted')
 print(json.dumps(dict(status='PASS',seed_entries=seed_entries,dilated_cases=len(cases),lifted_entries=entries,negative_controls=1,all_size_family='m=18k-7, k>=1; two degree-three labels',bound='fixed obstruction <= T/3')))
if __name__=='__main__':main()

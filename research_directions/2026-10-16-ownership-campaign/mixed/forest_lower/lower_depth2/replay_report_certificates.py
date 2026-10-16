#!/usr/bin/env python3
"""Independent Fraction replay with enumerated production vertex covers."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import gzip,json,copy,hashlib
ROOT=Path(__file__).resolve().parent

def need(ok,msg):
 if not ok:raise ValueError(msg)

def inspect(d,primal=True):
 domains=d['domains'];n=len(domains);v=len(domains[0][0]);m=(v-1)//2
 need(v==2*m+1,'resource shape');states=list(product(*[range(len(z)) for z in domains]));need([list(s) for s in states]==d['states'],'states mismatch');ix={s:j for j,s in enumerate(states)};N=len(states);ci=N*n
 profiles=[tuple(tuple(domains[i][s[i]]) for i in range(n)) for s in states]
 edges=[(j,m+j) for j in range(m)]+[(j,2*m)for j in range(m)]
 covers=[mask for mask in range(1<<v) if all(mask>>a&1 or mask>>b&1 for a,b in edges)]
 covers=[mask for mask in covers if not any(other!=mask and other&mask==other for other in covers)]
 coal={}
 def worth(q,mask):
  key=(q,mask)
  if key not in coal:
   caps=[sum(profiles[q][i][j] for i in range(n) if mask>>i&1) for j in range(v)]
   coal[key]=min(sum(caps[j]for j in range(v)if c>>j&1)for c in covers)
  return coal[key]
 def row(tag):
  if tag[0]=='budget':
   _,q=tag;need(0<=q<N,'bad profile');return {**{q*n+i:Q(1)for i in range(n)},ci:-Q(worth(q,(1<<n)-1))},Q()
  if tag[0]=='coalition':
   _,q,mask=tag;need(0<=q<N and 0<mask<1<<n,'bad coalition');return {q*n+i:Q(-1)for i in range(n)if mask>>i&1},-Q(worth(q,mask))
  if tag[0]=='monotone':
   _,lo,hi,i=tag;need(0<=lo<N and 0<=hi<N and 0<=i<n,'bad report tag')
   a,b=profiles[lo],profiles[hi];need(a[i]!=b[i] and all(x<=y for x,y in zip(a[i],b[i])) and all(a[j]==b[j]for j in range(n)if j!=i),'invalid actual-owner transition')
   return {lo*n+i:Q(1),hi*n+i:Q(-1)},Q()
  raise ValueError('unknown row tag')
 combo={};rhs=Q()
 for term in d['dual']:
  weight=Q(term['weight']);need(weight>0,'nonpositive weight');r,b=row(term['tag']);rhs+=weight*b
  for j,a in r.items():combo[j]=combo.get(j,Q())+weight*a
 need(combo.get(ci,Q())<0,'missing budget normalization');need(all(a>=0 for j,a in combo.items()if j!=ci),'negative payment coefficient');lower=rhs/combo[ci];need(lower==Q(d['exact_dual_lower']),'false claimed dual lower')
 transitions=0
 if primal:
  pay=list(map(Q,d['primal']));need(len(pay)==ci+1 and all(a>=0 for a in pay),'invalid primal');need(pay[-1]==Q(d['primal_factor']),'factor mismatch')
  for q in range(N):
   need(sum(pay[q*n+i]for i in range(n))<=pay[-1]*worth(q,(1<<n)-1),'budget violation')
   for mask in range(1,1<<n):need(sum(pay[q*n+i]for i in range(n)if mask>>i&1)>=worth(q,mask),'coverage violation')
  for i,dom in enumerate(domains):
   pairs=[(lo,hi)for lo,a in enumerate(dom)for hi,b in enumerate(dom)if lo!=hi and all(x<=y for x,y in zip(a,b))]
   for s in states:
    for lo,hi in pairs:
     if s[i]!=lo:continue
     t=list(s);t[i]=hi;need(pay[ix[s]*n+i]<=pay[ix[tuple(t)]*n+i],'incentive violation');transitions+=1
 return dict(name=d['name'],profiles=N,coalitions=N*((1<<n)-1),all_comparable_own_transitions=transitions,dual_rows=len(d['dual']),exact_factor=str(lower),primal_checked=primal)

def main():
 out=[]
 for p in sorted(ROOT.glob('*.json.gz')):
  d=json.loads(gzip.decompress(p.read_bytes()))
  if 'domains' not in d:continue
  out.append(inspect(d));print(json.dumps(out[-1]),flush=True)
 calibration=json.loads(gzip.decompress((ROOT/'calibration_one_branch.json.gz').read_bytes()))
 bad=[]
 c=copy.deepcopy(calibration);c['exact_dual_lower']='100';bad.append(c)
 c=copy.deepcopy(calibration);c['primal'][-1]='0';c['primal_factor']='0';bad.append(c)
 c=copy.deepcopy(calibration);c['dual'][0]['weight']='-1';bad.append(c)
 c=copy.deepcopy(calibration);c['dual'][0]['tag']=['budget',10**8];bad.append(c)
 for c in bad:
  try:inspect(c)
  except (ValueError,IndexError):pass
  else:raise ValueError('accepted corrupted certificate')
 result=dict(status='EXACT INDEPENDENT PASS',certificates=out,corruption_controls_rejected=len(bad),oracle='Exact enumeration of minimal vertex covers of the physical depth-two graph; no shared value-function implementation.',scope='Finite restrictions only; no all-real-domain upper claim.',sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 (ROOT/'independent_replay.json').write_text(json.dumps(result,indent=2)+'\n');print('All exact certificates passed; corruption controls rejected.')
if __name__=='__main__':main()

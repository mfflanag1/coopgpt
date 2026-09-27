"""Independent exact verification of low-hub-count structural certificates."""
from fractions import Fraction as F
from pathlib import Path
import json
from verify_variable_p import check as check_packing,topology

def require(ok,msg):
 if not ok:raise ValueError(msg)

def main():
 cases=json.loads(Path(__file__).with_name('ONE_HUB_CERTIFICATES.json').read_text());require(len(cases)==10,'case inventory');entries=0;outside=0
 for d in cases:
  entries+=check_packing(d);m=d['m'];P=[tuple(t)for t in d['P']];r=len(P);degree,connected,cycles=topology(d);g=degree.count(3)
  require(connected and cycles==0 and g in (0,1)and g==d['hubs']and all(len(set(t))==3 for t in P),'tree class')
  used={s*m+j for t in P for s,j in enumerate(t)};U=set(range(3*m))-used
  L=[sum(degree[j]==1 and s*m+j in used for j in range(m))for s in range(3)];ell=sum(L);R=ell-3
  require(L==d['leaf_counts']and ell==r+g+2 and 0<=R<=r,'leaf counts')
  alpha={(s,t):F(v)for s,t,v in d['alpha']};delta=list(map(F,d['delta']))
  require(len(d['alpha'])==6 and set(alpha)=={(s,t)for s in range(3)for t in range(3)if s!=t},'alpha indices')
  require(all(v>=0 for v in alpha.values())and len(delta)==3,'scaling format')
  for s in range(3):
   require(sum(L[t]*alpha[s,t]for t in range(3)if t!=s)==1,'sector normalization')
   require(delta[s]==1-sum(alpha[t,s]for t in range(3)if t!=s)and delta[s]>=0,'leaf deficit')
  for(s,t),a in alpha.items():require((R-L[s])*a<=delta[t]<=R*a,'rational scaling inequalities')
  amounts={(i,t):F(0)for i in U for t in P}
  for i,t,v in d['packings']:
   t=tuple(t);s=i//m
   if t in P:amounts[i,t]+=F(v)
   else:require(t[(s+1)%3]==t[(s+2)%3],'same-sector support')
  for i in U:
   s,j=divmod(i,m)
   if degree[j]==2:a=F(0)
   else:a=alpha[s,next(t for t in range(3)if t*m+j in used)]
   require(all(amounts[i,t]==a for t in P),'row P weights')
  h=r+1
  if any(L[s]*(h-2)>(L[s]-g-1)*min(L[s],h-1)+(h-(L[s]-g-1))for s in range(3)):outside+=1
 bad=dict(cases[-1]);bad['packings']=[]
 try:check_packing(bad)
 except ValueError:pass
 else:raise ValueError('empty certificate accepted')
 print(json.dumps(dict(status='PASS',cases=len(cases),rational_entries=entries,outside_old_uniform_condition=outside,negative_controls=1,claim='one-third fixed-obstruction bound; all-size proof in ONE_HUB_THEOREM.md')))
if __name__=='__main__':main()

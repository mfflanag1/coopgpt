"""Exact cut proof and independently checked full-packing attainment."""
from pathlib import Path
from fractions import Fraction as F
import json
from collections import defaultdict
from local_extension_model import system
from verify_variable_p import check,require,topology
from verify_root_mass import verify as verify_equality

def cut(d):
 m,P,types,stride,rows,rhs,eq,erhs,n=system();nr=len(rows);base_eq=len(eq)-30;coeff=[F(0)]*n;bound=F(0);used=set()
 require(d['m']==m and [tuple(t)for t in d['P']]==P,'pattern mismatch')
 # Omit the 30 fixed-weight equations to expose an inequality valid for every new certificate.
 for j,raw in d['multipliers']:
  require(j not in used and 0<=j<len(rows)+len(eq),'bad multiplier index');used.add(j);w=F(raw)
  if j<nr:require(w>=0,'negative inequality multiplier')
  if j>=nr+base_eq:continue
  bound+=w*(rhs+erhs)[j]
  for i,a in (rows+eq)[j].items():coeff[i]+=w*a
 W={}
 old=[(0,1,2),(3,0,4),(5,6,0)];owner={s*7+j:e for e,t in enumerate(old)for s,j in enumerate(t)};lookup={tuple(t):k for k,t in enumerate(types)}
 for j in range(2,7):
  t=next(s for s in range(3)if s*7+j in owner);b=owner[t*7+j]
  for s in range(3):
   if s==t:continue
   k=lookup[b,t,s]
   for e,w in enumerate((5,1,1)):W[k*stride+e]=w
 require(len(W)==30 and sum(W.values())==70,'old weight inventory')
 require(bound==34 and all(a-2*W.get(i,0)>=0 for i,a in enumerate(coeff)),'cut not certified')
 # The full multiplier vector must also contradict the frozen equations.
 full=[F(0)]*n;bb=F(0)
 for j,raw in d['multipliers']:
  w=F(raw);bb+=w*(rhs+erhs)[j]
  for i,a in (rows+eq)[j].items():full[i]+=w*a
 require(bb==-1 and all(v>=0 for v in full),'frozen contradiction')
 return m,P,types,stride,W

def primal(d,meta):
 m,P,types,stride,W=meta;require(d['m']==m and [tuple(e)for e in d['P']]==P,'control pattern');entries=check(d);p=defaultdict(F);diag=defaultdict(F);ex=defaultdict(F)
 for i,e,w in d['packings']:
  e=tuple(e);w=F(w)
  if e in P:p[i,P.index(e)]+=w
  elif len(set(e))==1:diag[i,e[0]]+=w
  else:
   s=i//m;j=e[(s+1)%3];require(e[(s+2)%3]==j,'wrong sector transfer');ex[i,j]+=w
 degree,connected,cycles=topology(d);require(connected and cycles==0,'tree')
 own={s*m+j:e for e,t in enumerate(P)for s,j in enumerate(t)};U=sorted(set(range(3*m))-set(own));values=[]
 hubs=[j for j in range(m)if degree[j]==3]
 for b,t,s in types:
  leaves=[j for j in P[b]if degree[j]==1 and own.get(t*m+j)==b];require(len(leaves)==1,'unique row type');j=leaves[0];i=s*m+j
  vals=[p[i,e]for e in range(5)]
  for e in range(5):
   ls=[a for a in P[e]if degree[a]==1 and own.get(s*m+a)==e]
   vals.append(ex[i,ls[0]]if ls else F(0))
  vals += [ex[i,a]for a in hubs]+[ex[i,j]];values+=vals
  require(m-1-sum(diag[i,a]for a in range(m))-2*sum(p[i,e]for e in range(5))==0,'E=0')
 _,_,_,_,rows,rhs,eq,erhs,n=system()
 require(all(sum(values[j]*a for j,a in row.items())<=b for row,b in zip(rows,rhs)),'marginal inequality')
 require(all(sum(values[j]*a for j,a in row.items())==b for row,b in zip(eq[:-30],erhs[:-30])),'sector balance')
 value=sum(values[j]*w for j,w in W.items());require(value==17,'cut not attained')
 return entries

def run():
 root=Path(__file__).parent;d=json.loads((root/'LOCAL_EXTENSION_DUAL.json').read_text());meta=cut(d);count=primal(json.loads((root/'REBALANCING_SHARP_CERTIFICATE.json').read_text()),meta)
 old=json.loads((root/'HUB_EXTENSION_OLD_CERTIFICATE.json').read_text());old_result=verify_equality(old)
 require(old['m']==7 and [tuple(e)for e in old['P']]==[(0,1,2),(3,0,4),(5,6,0)],'old pattern')
 old_p=defaultdict(F);old_teams=[tuple(t)for t in old['P']]
 for i,e,w in old['packings']:
  if tuple(e)in old_teams:old_p[i,tuple(e)]+=F(w)
 old_used={s*7+j for e in old_teams for s,j in enumerate(e)}
 require(all(old_p[i,e]==F(1,4)for i in set(range(21))-old_used for e in old_teams),'old P weights')
 control=json.loads((root/'HUB_EXTENSION_CONTROL.json').read_text());require(control['P']==d['P'],'equality control pattern');control_result=verify_equality(control)
 bad=dict(d);bad['multipliers']=[]
 try:cut(bad)
 except ValueError:pass
 else:raise ValueError('empty proof accepted')
 print(json.dumps({'status':'PASS','dual_support':len(d['multipliers']),'sharp_cut':'W<=17','old_value':'35/2','control_entries':count,'old_entries':old_result['entries'],'equality_control_entries':control_result['entries'],'negative_controls':1,'scope':'specified sector-balanced E=0 extension model; old-weight preservation impossible'}))
if __name__=='__main__':run()

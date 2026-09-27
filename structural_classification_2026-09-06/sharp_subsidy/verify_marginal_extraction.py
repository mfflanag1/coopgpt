"""Exact extraction/calibration of the same-sector transportation inequalities."""
from pathlib import Path
from fractions import Fraction as F
import json

def require(ok,msg):
 if not ok:raise ValueError(msg)

def check(data):
 m=data['m'];P=[tuple(e)for e in data['P']];owner={s*m+j:e for e,t in enumerate(P)for s,j in enumerate(t)};U=sorted(set(range(3*m))-set(owner));u=len(U)
 p={i:[F(0)]*len(P)for i in U};d={i:[F(0)]*m for i in U};q={i:[F(0)]*m for i in U}
 for i,team,raw in data['packings']:
  team=tuple(team);v=F(raw);require(v>=0 and i in U,'entry')
  if team in P:p[i][P.index(team)]+=v
  else:
   s=i//m;j=team[(s+1)%3];require(team[(s+2)%3]==j,'same-sector block')
   q[i][j]+=v
   if team[s]==j:d[i][j]+=v
 for i in U:
  s,j0=divmod(i,m)
  def load(a,j):return p[i][owner[a*m+j]]if a*m+j in owner else F(0)
  A=[F(0)if j==j0 else 1-load(s,j)for j in range(m)]
  B=[min(1-load(a,j)for a in range(3)if a!=s)for j in range(m)]
  rr=[A[j]-d[i][j]for j in range(m)];cc=[q[i][j]-d[i][j]for j in range(m)];R=sum(rr);C=sum(cc)
  require(all(0<=d[i][j]<=min(A[j],B[j])and d[i][j]<=q[i][j]<=B[j]for j in range(m)),'marginal interval')
  require(C<=R and all(cc[j]<=R-rr[j]for j in range(m)),'transport cuts')
 for e in range(len(P)):require(sum(p[i][e]for i in U)==3,'P total')
 for j in range(m):
  for s in range(3):require(sum(q[i][j]if i//m==s else d[i][j]for i in U)>=u-4,'marginal coverage')
 return len(U)

if __name__=='__main__':
 data=json.loads(Path(__file__).with_name('VARIABLE_P_CERTIFICATES.json').read_text());rows=sum(check(d)for d in data)
 print(json.dumps({'status':'PASS','cases':len(data),'deletion_rows':rows,'exact_transport_and_coverage_checks':True}))

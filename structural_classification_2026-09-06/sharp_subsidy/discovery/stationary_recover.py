"""Exact affine recovery of stationary seed weights, followed by rational flow."""
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from sympy import Matrix,Rational
from cut_transport import flow
from verify_variable_p import check as check_packing

here=Path(__file__).resolve().parent
raw=json.loads((here/'STATIONARY_SEED.json').read_text());m=raw['m'];P=[tuple(t)for t in raw['P']];r=len(P)
U=[row[0]for row in raw['rows']];u=len(U);own={s*m+j:e for e,t in enumerate(P)for s,j in enumerate(t)};degree=[sum(s*m+j in own for s in range(3))for j in range(m)]
adj=[set()for _ in range(m+r)]
for e,t in enumerate(P):
 for j in t:adj[j].add(m+e);adj[m+e].add(j)
pa={}
for i in U:
 root=i%m;parent={root:None};todo=[root]
 for j in todo:
  for v in adj[j]-set(parent):parent[v]=j;todo.append(v)
 pa[i]=parent
old=[F(v)for row in raw['rows']for v in row[1]];n=len(old);equations=[]
def row(coeff,rhs):
 a=[0]*(n+1)
 for j,v in coeff:a[j]+=v
 a[-1]=rhs;equations.append(a)
for s in range(3):
 for e in range(r):row([(k*r+e,1)for k,i in enumerate(U)if i//m==s],1)
for k,i in enumerate(U):
 s=i//m
 row([(k*r+e,sum(degree[j]==1 and a!=s for a,j in enumerate(t)))for e,t in enumerate(P)],1)
 for e in range(r):
  if abs(float(old[k*r+e]))<1e-8:row([(k*r+e,1)],0)
 for j in range(m):
  if j==i%m:continue
  parent=pa[i][j]-m
  for v in adj[j]:
   e=v-m
   if e!=parent and abs(float(old[k*r+e]-old[k*r+parent]))<1e-8:row([(k*r+e,1),(k*r+parent,-1)],0)
M,pivots=Matrix(equations).rref();
if n in pivots:raise ValueError('inconsistent active affine system')
free=[j for j in range(n)if j not in pivots];values=[F(round(v*10**9),10**9)for v in old]
for z,j in enumerate(pivots):
 values[j]=F(M[z,n])-sum(F(M[z,k])*values[k]for k in free)
for a in equations:
 if sum(F(v)*x for v,x in zip(a[:-1],values))!=a[-1]:raise ValueError('affine recovery')
p={i:values[k*r:(k+1)*r]for k,i in enumerate(U)};d={};supply={};capacity={};sources={}
for i in U:
 if any(v<0 or v>1 for v in p[i]):raise ValueError('P bounds')
 d[i]=[F(0)if j==i%m else 1-p[i][pa[i][j]-m]for j in range(m)]
 s=i//m
 def load(a,j):return p[i][own[a*m+j]]if a*m+j in own else F(0)
 for j in range(m):
  if j!=i%m and d[i][j]!=1-max(load(a,j)for a in range(3)):raise ValueError('root monotonicity')
 sources[i]=[F(0)if j==i%m else 1-load(s,j)-d[i][j]for j in range(m)];supply[i]=sum(sources[i])
 for j in range(m):capacity[i,j]=min(1-load(a,j)for a in range(3)if a!=s)-d[i][j]
demand={j:max(F(0),u-4-sum(d[i][j]for i in U))for j in range(m)};allocation={}
for s in range(3):allocation.update(flow([i for i in U if i//m==s],list(range(m)),supply,demand,capacity))
out=defaultdict(F)
for i in U:
 for e,t in enumerate(P):out[i,t]+=p[i][e]
 for j,v in enumerate(d[i]):out[i,(j,j,j)]+=v
 remaining=list(sources[i]);s=i//m
 for j in range(m):
  amount=allocation[i,j]
  if amount and remaining[j]:raise ValueError('overlapping residual supports')
  for a in range(m):
   take=min(amount,remaining[a])
   if take:
    team=[j]*3;team[s]=a;out[i,tuple(team)]+=take;remaining[a]-=take;amount-=take
  if amount:raise ValueError('row realization')
cert=dict(m=m,P=P,parameter='1',packings=[[i,list(t),str(v)]for(i,t),v in sorted(out.items())if v],rows=[[i,[str(v)for v in p[i]],[str(v)for v in d[i]],[str(allocation[i,j])for j in range(m)]]for i in U])
check_packing(cert);(here/'STATIONARY_EXACT_SEED.json').write_text(json.dumps(cert)+'\n')
print(json.dumps(dict(status='PASS',p_variables=n,affine_rank=len(pivots),free_variables=len(free),packing_entries=len(cert['packings']))))

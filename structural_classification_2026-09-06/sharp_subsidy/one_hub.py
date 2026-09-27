"""Exact constant-dimensional scaling for incidence trees with at most one hub."""
from fractions import Fraction as F
from itertools import combinations
from collections import defaultdict
from pathlib import Path
import json

# Affine forms use [constant, x_0, x_1, x_2].
def add(a,b):return [x+y for x,y in zip(a,b)]
def mul(c,a):return [c*x for x in a]
def at(a,x):return a[0]+sum(v*w for v,w in zip(a[1:],x))
def solve(forms):
 a=[[F(v)for v in f[1:]]+[-F(f[0])]for f in forms]
 for j in range(3):
  pivot=next((k for k in range(j,3)if a[k][j]),None)
  if pivot is None:return None
  a[j],a[pivot]=a[pivot],a[j];z=a[j][j];a[j]=[v/z for v in a[j]]
  for k in range(3):
   if k!=j:
    z=a[k][j];a[k]=[v-z*w for v,w in zip(a[k],a[j])]
 return [a[j][3]for j in range(3)]

def scaling(L):
 if len(L)!=3 or any(type(v)is not int or v<1 for v in L)or sum(L)<3:raise ValueError('scaling count domain')
 if L==[1,1,1]:return {(s,t):F(1,2)for s in range(3)for t in range(3)if s!=t},{t:F(0)for t in range(3)},0
 one=[F(1),F(0),F(0),F(0)];zero=[F(0)]*4;alpha={}
 for s in range(3):
  t,v=[a for a in range(3)if a!=s];f=list(zero);f[s+1]=1;alpha[s,t]=f
  alpha[s,v]=mul(F(1,L[v]),add(one,mul(-L[t],f)))
 delta={t:add(one,mul(-1,add(*(alpha[s,t]for s in range(3)if s!=t))))for t in range(3)}
 R=sum(L)-3;constraints=list(alpha.values())+list(delta.values())
 for (s,t),a in alpha.items():
  constraints.append(add(mul(R,a),mul(-1,delta[t])))
  constraints.append(add(delta[t],mul(-(R-L[s]),a)))
 tried=0
 for active in combinations(constraints,3):
  tried+=1;x=solve(active)
  if x is not None and all(at(f,x)>=0 for f in constraints):
   av={key:at(f,x)for key,f in alpha.items()};dv={t:at(f,x)for t,f in delta.items()}
   return av,dv,tried
 raise ValueError('no rational scaling vertex; theorem or implementation failure')

def construct(m,P):
 P=[tuple(t)for t in P];r=len(P);used={s*m+j for t in P for s,j in enumerate(t)}
 if r<1 or m!=2*r+1 or len(used)!=3*r or any(len(set(t))!=3 for t in P):raise ValueError('tree matching domain')
 degree=[sum(s*m+j in used for s in range(3))for j in range(m)]
 adj=[set()for _ in range(m+r)]
 for e,t in enumerate(P):
  for j in t:adj[j].add(m+e);adj[m+e].add(j)
 seen={0};todo=[0]
 for j in todo:
  for v in adj[j]-seen:seen.add(v);todo.append(v)
 if len(seen)!=m+r or degree.count(3)>1:raise ValueError('at most one hub')
 leaves=[[j for j in range(m)if degree[j]==1 and s*m+j in used]for s in range(3)];L=list(map(len,leaves));alpha,delta,tried=scaling(L);R=sum(L)-3
 U=sorted(set(range(3*m))-used);out=defaultdict(F)
 for i in U:
  s,root=divmod(i,m)
  if degree[root]==2:
   for j in range(m):
    if j!=root:out[i,(j,j,j)]+=1
   continue
  t=next(a for a in range(3)if a*m+root in used);a=alpha[s,t]
  for team in P:out[i,team]+=a
  for j in range(m):
   if j!=root:out[i,(j,j,j)]+=1-a
  f=(R*a-delta[t])/L[s];destinations=[(root,delta[t])]+[(j,f)for j in leaves[s]]
  sources=[v%m for v in U if v//m==s and v!=i]
  for j,mass in destinations:
   for v in sources:
    team=[j]*3;team[s]=v;out[i,tuple(team)]+=mass/r
 return dict(m=m,P=P,parameter='1',leaf_counts=L,scaling_trials=tried,alpha=[[s,t,str(v)]for(s,t),v in alpha.items()],delta=[str(delta[t])for t in range(3)],packings=[[i,list(t),str(v)]for(i,t),v in sorted(out.items())if v])

def example(L,hub):
 if hub:m=7;P=[(0,1,2),(3,0,4),(5,6,0)];initial=2
 else:m=3;P=[(0,1,2)];initial=1
 for missing in range(3):
  for _ in range(L[missing]-initial):
   incidence=[[(s,e)for e,t in enumerate(P)for s,j in enumerate(t)if j==v]for v in range(m)]
   root,old=next((v,items[0][0])for v,items in enumerate(incidence)if len(items)==1 and items[0][0]!=missing)
   attach=3-missing-old;t=[None]*3;t[attach]=root
   for s in range(3):
    if s!=attach:t[s]=m;m+=1
   P.append(tuple(t))
 return m,P

if __name__=='__main__':
 cases=[]
 for hub,L in [(0,[1,1,1]),(0,[1,1,2]),(0,[8,1,1]),(0,[3,4,5]),(1,[2,2,2]),(1,[3,3,3]),(1,[10,2,2]),(1,[2,11,3]),(1,[4,3,12]),(1,[7,8,9])]:
  d=construct(*example(L,hub));d['hubs']=hub;cases.append(d)
 Path(__file__).with_name('ONE_HUB_CERTIFICATES.json').write_text(json.dumps(cases)+'\n')
 print(json.dumps(dict(cases=len(cases),entries=sum(len(d['packings'])for d in cases),scaling_trials=[d['scaling_trials']for d in cases])))

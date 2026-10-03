"""Known insufficient ideal-difference relaxation, for paired diagnostics only."""
import argparse,json,time
from fractions import Fraction as Q
from itertools import product,permutations
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


def solve(m,P,seconds=120):
 def pairs(t):a,b,c=t;return [(0,a,b),(1,a,c),(2,b,c)]
 E=sorted({e for t in P+[[j,j,j] for j in range(m)] for e in pairs(t)})
 ix={e:k for k,e in enumerate(E)};X=len(E);H=X+3*m;n=H+3*m
 def add(row,col,v):row[col]=row.get(col,0)+v
 def worth(row,t,coef=1):
  for e in pairs(t):
   if e in ix:add(row,ix[e],coef)
 rows=[];rhs=[]
 def push(row,b=0):rows.append(row);rhs.append(b)
 for t in product(range(m),repeat=3):
  row={};worth(row,t)
  for s,j in enumerate(t):add(row,X+s*m+j,-1)
  push(row)
 U=sorted(set(range(3*m))-{s*m+j for t in P for s,j in enumerate(t)})
 for i in range(3*m):
  row={H+i:1};worth(row,(i%m,)*3,-1);push(row);push({X+i:1,H+i:-1})
 for i in U:
  row={H+i:1}
  for t in P:worth(row,t)
  push(row,1)
 # Every repeated-label completion, including unsupported off-diagonals.
 for s in range(3):
  for a in range(m):
   for b in range(m):
    if a==b:continue
    t=[a]*3;t[s]=b;row={H+s*m+a:1,H+s*m+b:-1};worth(row,t);worth(row,(a,)*3,-1);push(row)
    row={H+s*m+a:1,H+s*m+b:-1}
    for p,(v,z) in enumerate(((0,1),(0,2),(1,2))):
     if s in (v,z):add(row,ix[p,a,a],-1)
    push(row)
 for team in P:
  for s,t,u in permutations(range(3)):
   a,b,c=team[s],team[t],team[u];row={};add(row,H+u*m+b,1);add(row,H+u*m+c,-1)
   worth(row,team);worth(row,(b,)*3,-1)
   for p,(v,z) in enumerate(((0,1),(0,2),(1,2))):
    if s in (v,z):add(row,ix[p,a,a],-1)
   push(row)
 rr=[];cc=[];vv=[]
 for k,row in enumerate(rows):
  for j,v in row.items():
   if v:rr.append(k);cc.append(j);vv.append(v)
 A=coo_matrix((vv,(rr,cc)),shape=(len(rows),n)).tocsr();B=np.zeros((2,n))
 for p in range(3):
  for j in range(m):B[0,ix[p,j,j]]=1
 B[1,X:H]=1;c=np.zeros(n)
 for t in P:
  for e in pairs(t):c[ix[e]]+=3
 for i in U:c[H+i]=1
 start=time.monotonic();res=linprog(-c,A_ub=A,b_ub=rhs,A_eq=B,b_eq=[1,1],bounds=(0,1),options={'time_limit':seconds})
 info={'elapsed_seconds':time.monotonic()-start,'solver_status':res.status,'message':res.message,'variables':n,'rows':len(rows)}
 if not res.success:return {'status':'UNRESOLVED','discovery':info}
 values=None
 for cap in (1000,10000,1000000,100000000):
  z=[Q(float(v)).limit_denominator(cap) for v in res.x]
  if min(z)<0 or max(z)>1:continue
  if sum(z[ix[p,j,j]] for p in range(3) for j in range(m))!=1 or sum(z[X:H])!=1:continue
  if any(sum(v*z[j] for j,v in row.items())>b for row,b in zip(rows,rhs)):continue
  values=z;break
 if values is None:return {'status':'RATIONAL_RECOVERY_FAILED','discovery':info,'raw_primal':res.x.tolist()}
 mats=[[['0']*m for _ in range(m)] for _ in range(3)]
 for (p,a,b),v in zip(E,values):mats[p][a][b]=str(v)
 obj=sum(Q(int(v))*z for v,z in zip(c,values))/3-1
 return {'schema':'ideal-difference-diagnostic-v1','m':m,'P':P,'matrices':mats,'core':list(map(str,values[X:H])),'h':list(map(str,values[H:])),'J_relaxed':str(obj),'discovery':info,'scope':'feasible relaxed vector only, not actual ideals or market subsidy; numerical optimum not an exact upper'}


def check(d):
 # Semantic arithmetic check, independently expressed without the LP row builder.
 def need(ok,msg):
  if not ok:raise ValueError(msg)
 def rational(v):
  need(type(v) in (str,int),'rational format');return Q(v)
 m=d['m'];P=d['P'];need(type(m) is int and m>0,'size');need(all(type(t) is list and len(t)==3 and all(type(j) is int and 0<=j<m for j in t) for t in P),'team indices');need(all(len({t[s] for t in P})==len(P) for s in range(3)),'matching')
 mats=d['matrices'];need(len(mats)==3 and all(len(a)==m and all(len(row)==m for row in a) for a in mats),'matrices');w=[[[rational(v) for v in row] for row in mat] for mat in mats]
 allowed=[set((j,j) for j in range(m)) for _ in range(3)]
 for a,b,c in P:allowed[0].add((a,b));allowed[1].add((a,c));allowed[2].add((b,c))
 for p in range(3):
  for a in range(m):
   for b in range(m):need(w[p][a][b]>=0 and ((a,b) in allowed[p] or w[p][a][b]==0),'support/sign')
 def val(a,b,c):return w[0][a][b]+w[1][a][c]+w[2][b][c]
 diag=[val(j,j,j) for j in range(m)];need(sum(diag)==1,'normalization')
 x=list(map(rational,d['core']));h=list(map(rational,d['h']));need(len(x)==len(h)==3*m and min(x)>=0 and min(h)>=0 and sum(x)==1,'core/ideal format')
 for a,b,c in product(range(m),repeat=3):need(x[a]+x[m+b]+x[2*m+c]>=val(a,b,c),'full team')
 U=sorted(set(range(3*m))-{s*m+j for t in P for s,j in enumerate(t)});wp=sum(val(*t) for t in P)
 for i in range(3*m):need(x[i]<=h[i]<=diag[i%m],'ideal cap/dominance')
 for i in U:need(h[i]<=1-wp,'unmatched cap')
 def budget(s,j):return (w[0][j][j]+w[1][j][j],w[0][j][j]+w[2][j][j],w[1][j][j]+w[2][j][j])[s]
 for s in range(3):
  for a in range(m):
   for b in range(m):
    t=[a]*3;t[s]=b
    need(h[s*m+b]-h[s*m+a]>=val(*t)-diag[a],'completion')
    need(h[s*m+a]-h[s*m+b]<=budget(s,a),'range')
 for team in P:
  for s,t,u in permutations(range(3)):
   a,b,c=team[s],team[t],team[u]
   need(h[u*m+c]-h[u*m+b]>=val(*team)-diag[b]-budget(s,a),'P-induced')
 J=wp+sum(h[i] for i in U)/3-1;need(J==rational(d['J_relaxed']),'objective')
 return {'status':'PASS','J_relaxed':str(J),'above_one_third':J>Q(1,3),'scope':'feasible relaxation point, never an actual subsidy certificate'}


def main():
 ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('output',nargs='?');ap.add_argument('--check',action='store_true');ap.add_argument('--seconds',type=int,default=120);args=ap.parse_args();d=json.loads(Path(args.input).read_text())
 if args.check:print(json.dumps(check(d)));return
 out=solve(d['m'],d['P'],args.seconds);Path(args.output).write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(check(out) if out.get('schema') else out))
if __name__=='__main__':main()

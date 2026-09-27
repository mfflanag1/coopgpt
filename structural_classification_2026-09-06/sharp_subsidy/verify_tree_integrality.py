"""Exact fractional positive control and optional independent binary-weight SMT."""
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
import json,sys
from itertools import product
from uniform_template import construct
from verify_variable_p import check as check_packing

def require(ok,msg):
 if not ok:raise ValueError(msg)

def instance():
 r=5;m=2*r+1;P=[(r+1+j,j,j+1)for j in range(r)]
 own={s*m+j:e for e,t in enumerate(P)for s,j in enumerate(t)};U=sorted(set(range(3*m))-set(own))
 adj=[set()for _ in range(m+r)]
 for e,t in enumerate(P):
  for j in t:adj[j].add(m+e);adj[m+e].add(j)
 parents={}
 for i in U:
  root=i%m;pa={root:None};todo=[root]
  for j in todo:
   for v in adj[j]:
    if v not in pa:pa[v]=j;todo.append(v)
  require(len(pa)==m+r,'connected instance');parents[i]=pa
 return m,P,own,U,parents

def main():
 m,P,own,U,parents=instance();r=len(P);u=len(U);data=construct(m,P);data['parameter']='1';entries=check_packing(data)
 p=defaultdict(F);d=defaultdict(F);q=defaultdict(F);PS=set(P)
 for i,t,v in data['packings']:
  t=tuple(t);v=F(v);s=i//m
  if t in PS:p[i,t]+=v
  else:
   require(t[(s+1)%3]==t[(s+2)%3],'same-sector control');q[i,t[(s+1)%3]]+=v
   if len(set(t))==1:d[i,t[0]]+=v
 for s in range(3):
  for t in P:require(sum(p[i,t]for i in U if i//m==s)==1,'sector-balanced control')
 for i in U:
  for j in range(m):
   if j!=i%m:require(d[i,j]+p[i,P[parents[i][j]-m]]==1,'maximal root-monotone control')
 n2=sum(sum(s*m+j in own for s in range(3))==2 for j in range(m));require(n2==4,'four degree-two labels')
 row_cases=0
 for i in U:
  sector,root=divmod(i,m)
  for bits in product((0,1),repeat=r):
   maxima=[max([bits[e]for e,t in enumerate(P)if j in t],default=0)for j in range(m)]
   if any(maxima[j]!=bits[parents[i][j]-m]for j in range(m)if j!=root):continue
   diagonal=[0 if j==root else 1-maxima[j]for j in range(m)]
   opposite=[1-max([bits[own[a*m+j]]for a in range(3)if a!=sector and a*m+j in own],default=0)for j in range(m)]
   bad=sum(sector*m+j in own and bits[own[sector*m+j]] and any(a!=sector and a*m+j in own and bits[own[a*m+j]]for a in range(3))for j in range(m))
   minimum_loss=max(0,m-1-sum(bits)-sum(opposite))
   require(m-1-sum(diagonal)==2*sum(bits),'binary row root identity')
   require(minimum_loss>=bad,'exhaustive binary row capacity lemma')
   for j in range(m):
    if sector*m+j not in own and sum(a*m+j in own for a in range(3))==2:
     if j==root:require(opposite[j]==0 or sum(bits)==0,'root residual pair has no source or capacity')
     else:require(opposite[j]==diagonal[j],'degree-two pair receives only diagonals')
   row_cases+=1
 out=dict(status='PASS',m=m,degree_two_labels=n2,fractional_control_entries=entries,exhaustive_binary_row_cases=row_cases,optional_smt=[])
 if '--smt' in sys.argv:
  import z3
  def model(binary):
   solver=z3.SolverFor('QF_LRA');solver.set(timeout=45000)
   pz={(i,e):z3.Real(f'p_{binary}_{i}_{e}')for i in U for e in range(r)}
   dz={(i,j):z3.Real(f'd_{binary}_{i}_{j}')for i in U for j in range(m)}
   qz={(i,j):z3.Real(f'q_{binary}_{i}_{j}')for i in U for j in range(m)}
   for v in pz.values():solver.add(z3.Or(v==0,v==1)if binary else z3.And(v>=0,v<=1))
   for i in U:
    s,root=divmod(i,m);ps=sum(pz[i,e]for e in range(r));ds=sum(dz[i,j]for j in range(m));R=m-1-ps-ds
    solver.add(R>=0,sum(qz[i,j]for j in range(m))+ps<=m-1)
    for j in range(m):
     load=pz[i,own[s*m+j]]if s*m+j in own else 0;A=0 if j==root else 1-load
     solver.add(dz[i,j]>=0,dz[i,j]<=A,qz[i,j]>=dz[i,j],qz[i,j]-2*dz[i,j]+A<=R)
     for a in range(3):
      if a!=s:solver.add(qz[i,j]+(pz[i,own[a*m+j]]if a*m+j in own else 0)<=1)
     if j!=root:solver.add(dz[i,j]+pz[i,parents[i][j]-m]==1)
   for s in range(3):
    for e in range(r):solver.add(sum(pz[i,e]for i in U if i//m==s)==1)
   for j in range(m):
    for s in range(3):solver.add(sum(qz[i,j]if i//m==s else dz[i,j]for i in U)>=u-4)
   if not binary:
    def rat(v):return z3.RealVal(v.numerator)/v.denominator
    for i in U:
     for e,t in enumerate(P):solver.add(pz[i,e]==rat(p[i,t]))
     for j in range(m):solver.add(dz[i,j]==rat(d[i,j]),qz[i,j]==rat(q[i,j]))
   return solver.check()
  a=model(False);require(a==z3.sat,'fractional SMT witness');out['optional_smt'].append('fractional witness SAT')
  solver=z3.Solver();solver.set(timeout=10000)
  bits={(i,e):z3.Bool(f'b_{i}_{e}')for i in U for e in range(r)}
  integer=lambda b:z3.If(b,1,0)
  for sector in range(3):
   for e in range(r):solver.add(sum(integer(bits[i,e])for i in U if i//m==sector)==1)
  for i in U:
   for j in range(m):
    if j!=i%m:
     for e,t in enumerate(P):
      if j in t:solver.add(z3.Implies(bits[i,e],bits[i,parents[i][j]-m]))
  bad_terms=[]
  for i in U:
   sector=i//m
   for j in range(m):
    if sector*m+j in own:
     others=[bits[i,own[a*m+j]]for a in range(3)if a!=sector and a*m+j in own]
     if others:bad_terms.append(integer(z3.And(bits[i,own[sector*m+j]],z3.Or(*others))))
  solver.add(sum(bad_terms)<=3)
  for j in range(m):
   edges=[own[a*m+j]for a in range(3)if a*m+j in own]
   if len(edges)!=2:continue
   e,f=edges;root=next(i for i in U if i%m==j)
   overlap=sum(integer(z3.And(bits[i,e],bits[i,f]))for i in U)
   solver.add(overlap+integer(z3.Or(bits[root,e],bits[root,f]))>=3)
  b=solver.check();require(b==z3.unsat,f'binary reduced exclusion unverified: {b}');out['optional_smt'].append('binary reduced constraints UNSAT after exhaustive row-capacity checks')

 print(json.dumps(out))
if __name__=='__main__':main()

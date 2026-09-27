"""Exact verification of a zero-subsidy cyclic family; optional full-core SMT checks."""
from fractions import Fraction as F
from itertools import product
import json,sys

def market(b):
 m=4*b;P=[(j,(j+1)%b,b+j)for j in range(b)]+[(2*b+2*j,2*b+2*j+1,j)for j in range(b)]
 mats=[[[int(j==k)for k in range(m)]for j in range(m)]for _ in range(3)]
 for a,c,d in P:mats[0][a][c]=2;mats[1][a][d]=1;mats[2][c][d]=2
 def worth(t):a,c,d=t;return mats[0][a][c]+mats[1][a][d]+mats[2][c][d]
 used={s*m+j for t in P for s,j in enumerate(t)}
 y=[F(1,3)]*(3*m)
 for i in used:y[i]=F(7,3)
 for j in range(b):y[j]=y[m+j]=F(4,3);y[2*m+j]=F(1,3)
 return m,P,used,y,worth

def require(c,msg):
 if not c:raise ValueError(msg)

def main():
 checks=0;smt=0
 for b in range(2,13):
  m,P,used,y,worth=market(b);T=3*m
  require(sum(y)==T and all(worth((j,j,j))==3 for j in range(m)),'efficiency and diagonal worth')
  require(all(y[i]>=F(1)if i in used and not 2*m<=i<2*m+b else y[i]>=F(1,3)for i in range(3*m)),'floor from proved ideal bounds')
  for t in product(range(m),repeat=3):
   require(sum(y[s*m+j]for s,j in enumerate(t))>=worth(t),'core coverage');checks+=1
  for j in range(b):
   require(worth((j,(j+1)%b,j))==3 and worth((j,(j+1)%b,(j+1)%b))==3,'cycle comparison inequalities')
  require(all(worth(t)==5 for t in P),'special team worths')
  if '--smt' in sys.argv and b<=4:
   import z3
   x=[z3.Real(f'x_{b}_{j}')for j in range(3*m)];solver=z3.SolverFor('QF_LRA');solver.add(*[a>=0 for a in x],sum(x)==T)
   solver.add(*[sum(x[s*m+j]for s,j in enumerate(t))>=worth(t)for t in product(range(m),repeat=3)])
   # One disjunction checks all unmatched coordinates over the entire core.
   solver.push();solver.add(z3.Or(*[x[i]>1 for i in range(3*m)if i not in used or 2*m<=i<2*m+b]));require(solver.check()==z3.unsat,'unmatched ideal bound');solver.pop();smt+=1
   solver.push();solver.add(z3.Or(*[x[i]>3 for i in range(3*m)]));require(solver.check()==z3.unsat,'diagonal ideal bound');solver.pop();smt+=1
   solver.add(*[x[i]==z3.RealVal(y[i].numerator)/y[i].denominator for i in range(3*m)]);require(solver.check()==z3.sat,'witness control');smt+=1
 print(json.dumps({'status':'PASS','parameter_values':11,'triple_checks':checks,'subsidy':'0','optional_smt_queries':smt,'claim':'all-size proof in RING_ZERO_SUBSIDY.md; finite checks corroborate it'}))
if __name__=='__main__':main()

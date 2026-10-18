"""Exact rational checks for analytic adaptive-mixture lemmas; no optimization."""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import json

def polynomial_identity(s):
 # Coefficients of sum_{m=1}^s p(1-p)^(m-1).
 lhs=[Q(0)]*(s+1)
 for m in range(1,s+1):
  for k in range(m):lhs[k+1]+=(-1)**k*comb(m-1,k)
 rhs=[Q(0)]+[Q((-1)**(k+1)*comb(s,k)) for k in range(1,s+1)]
 assert lhs==rhs
 return dict(s=s,harmonic_half=str(sum((Q(1,m) for m in range(1,s+1)),Q(0))/2),polynomial_identity=True)

def single_star(M=200):
 H=Q(1,2);B=Q(2);previous_center=H;rows=[]
 for m in range(2,M+1):
  p=Q(1,m);a=(1-p)**(m-1);c=H/a;d=H-c*p*p;zero=B-c-d
  assert min(c,d,zero)>=0
  assert c+d+zero==B and c*p*p+d==H
  leaf=c*p*(1-p)**(m-1)
  center=d+c*(1-(1-p)**m)
  assert leaf==H/m and center>=previous_center and center>=1
  assert center+m*leaf<=2
  # All old-leaf subsets, including unchanged protected members.
  for k in range(m):assert leaf+k*(leaf-H/(m-1))>=0
  previous_center=center
  if m in [2,3,4,8,16,32,64,128,200]:
   rows.append(dict(m=m,leaf=str(leaf),center_float=float(center),mass=float(c+d)))
 return dict(checked_through=M,all_checks_passed=True,selected_rows=rows)

if __name__=='__main__':
 result=dict(status='PASS',harmonic=[polynomial_identity(s) for s in [1,2,3,4,8,16,32,64]],single_star=single_star())
 Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))

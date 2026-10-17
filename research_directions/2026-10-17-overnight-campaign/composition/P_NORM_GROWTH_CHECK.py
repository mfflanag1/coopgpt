#!/usr/bin/env python3
from fractions import Fraction as F
from pathlib import Path
import json,math
cnt={'embedding_basis_and_diagonal':0,'binomial_and_size_bounds':0,'rational_lower_elimination':0,'growth_parameters':0}
for m in range(2,101):
 h=(m-1).bit_length();p=m*m*h
 # Exponent inequality is exact: (1+1/m²)^(m²)>=2, then raise to h.
 assert 2**h>=m
 if m<=12:assert (1+F(1,m*m))**(m*m)>=2
 S0=(m-2)*m+2;S1=(m-1)*m+1
 assert S0<m*m and S1<m*m
 V0up=2+F(S0,m*m+1);V1up=2+F(S1,m*m+1)
 assert V0up<3 and V1up<3
 assert F(m,1)/(V1up+V0up/2)>F(2*m,9)
 cnt['binomial_and_size_bounds']+=1
 # Exact coordinate power sums for pure and diagonal bundles before m^(-1/p).
 assert sum(abs(1-2*(j==0))**p for j in range(m))==m
 if m<=12:assert sum(abs(m-2)**p for j in range(m))==m*(m-2)**p
 cnt['embedding_basis_and_diagonal']+=1
 # Combining b>=1-(kV0-2)/(2(m-1)), kV1>=(m-1)b.
 # The right side expands exactly to m-kV0/2.
 for kap in [F(1),F(3,2),F(m,3),F(m)]:
  lower=1-(kap*V0up-2)/(2*(m-1))
  assert (m-1)*lower==m-kap*V0up/2
  cnt['rational_lower_elimination']+=1
# For integer p, avoid floating log in the sufficient parameter gate.
for p in range(32,10001):
 h=(p-1).bit_length() # h>=log2 p, conservative explicit finite construction
 m=math.isqrt(p//h)
 if m>=2:
  assert m*m*(m-1).bit_length()<=p
  cnt['growth_parameters']+=1
out={'status':'PASS','arithmetic':'Exact integer/Fraction identities and bounds; no numerical norms',
'counts':cnt,'scope':'Analytic proof covers every real p satisfying p>=m² ceil(log2m); checker supplements finite parameter and coefficient steps.'}
Path(__file__).with_name('P_NORM_GROWTH_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))

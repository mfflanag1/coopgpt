if not __debug__:
    raise RuntimeError('Run without Python -O; assertions are required.')
from fractions import Fraction as Q
import json
num=0
for r in range(2,51):
 for s in range(2,201):
  m=(r-1)*s;n=m+1
  beta=Q(r-1,2)/(Q(r-1,2*(s-1))+Q(m,m-1))
  claimed=Q((s-1)*((r-1)*s-1),2*s*s+(r-3)*s-1)
  assert beta==claimed
  assert Q(r-1,2)*(1-beta/(s-1))==Q(m,m-1)*beta
  assert 1+beta<Q(r+1,2)
  assert (r-2)*s+2+s-1==n
  if r==3:assert beta==Q((s-1)*(2*s-1),2*s*s-1)
  num+=1
print(json.dumps({'status':'PASS','exact_parameter_checks':num,'rank3_sharp_supremum':'2','general_sharp_supremum':'(r+1)/2','finite_rank3_s100':str(1+Q(99*199,19999))}))

if not __debug__:
    raise RuntimeError('Run this exact checker without Python -O; assertions are required.')
from fractions import Fraction as Q
import json
num=0
for r in range(2,41):
 for s in range(2,101):
  m=s+r-2
  a=Q(1,r*s);b=(1-a)/(r-1)
  H=Q(r-2,r-1)+Q(1,r)-Q(r-2,r*(r-1)*s)
  assert s*a+(r-2)*b==H
  B=1+Q(m-1,m)*H
  B1=1+Q(s+r-3,s+r-2)*(Q(r-2,r-1)+Q(1,r)-Q(r-2,r*(r-1)*s))
  assert B==B1
  limit=2-Q(1,r*(r-1));assert B<limit
  if r==2:assert B==Q(3,2)-Q(1,2*s)
  if r==3:assert B==Q(11,6)-Q(1,s+1)
  num+=1
assert Q(11,6)-Q(1,11)==Q(115,66)
assert Q(11,6)-Q(1,101)==Q(1105,606)
print(json.dumps({'status':'PASS','exact_parameter_checks':num,'rank3_limit':'11/6','rank3_owners_5':'19/12','rank3_owners_102':'1105/606'}))

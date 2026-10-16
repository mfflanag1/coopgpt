"""Standalone exact verifier. No scipy, numpy, builder import, or assertions."""
from fractions import Fraction as R
from math import factorial
from pathlib import Path
import json,hashlib

def require(c,s):
 if not c:raise RuntimeError(s)
def taylor_minus(x,n):
 require(x>=0,'Taylor nonnegative argument')
 total=R(1);term=R(1)
 for j in range(1,n+1):
  term*=(-x)/j;total+=term
 return total
root=Path(__file__).resolve().parent
raw=(root/'low_grid_certificate.json').read_bytes();saved=json.loads(raw)
e_low=sum((R(1,factorial(k)) for k in range(7)),R(0));e_high=e_low+R(1,4410)
require(e_low>R(125,46),'c upper')
require(e_high<R(30,11)<R(11,4),'K bounds')
require(R(19,11)**2<3,'K squared')
CB=R(148,125);cc=R(23,125)
require(CB*CB<R(27,16),'power regime comparison')
require(len(saved['intervals'])==128,'interval count')
worst=R(0);last=R(1)
for index,entry in enumerate(saved['intervals']):
 l,h,u=map(R,[entry['lo'],entry['hi'],entry['u']])
 require(l==last and h>l,'complete interval cover');last=h
 require(0<u<1,'dual parameter')
 lower=taylor_minus(1/u-1,25)/2;upper=taylor_minus(1/u-1,24)/2
 require(0<lower<=upper,'q bracket')
 am=1-upper*(1+1/u);ap=1-lower*(1+1/u)
 require(0<am<=ap,'A bracket')
 la=1-lower*(1+1/u-1/l);et=upper/l;mu=3*et*et/(4*am);p=R(7,4)*et
 bn=R(2,5)*taylor_minus(h-1+cc,25)
 require(la>0 and bn>0,'positive multiplier')
 rows=[([1,-1,0,0,0],0),([-CB,1,0,0,0],0),([0,-1,0,0,0],1-l),([-1,1,1,0,0],1),([0,1,1,0,0],R(3,2)),([0,0,1,1,0],1),([R(4,3),0,1,-1,0],R(4,3)),([0,-1,0,1,0],0),([0,-p,0,p,1],0),([0,-mu-ap,0,mu,1],ap*(1-l)),([1,0,0,0,0],1)]
 weights=list(map(R,entry['dual']))
 require(len(weights)==11 and all(y>=0 for y in weights),'nonnegative dual')
 target=[0,0,la-bn,0,1];caps=[1,CB,1,CB,p*CB]
 residual=[max(R(0),target[j]-sum(weights[k]*rows[k][0][j] for k in range(11))) for j in range(5)]
 require(residual==list(map(R,entry['residual'])),'residual replay')
 for j in range(5):require(sum(weights[k]*rows[k][0][j] for k in range(11))+residual[j]>=target[j],'weak dual coefficient')
 bound=1+la*(h-1)+sum(weights[k]*rows[k][1] for k in range(11))+sum(residual[j]*caps[j] for j in range(5))
 require(bound==R(entry['upper']),'saved bound equality')
 require(bound<R(8,5),'strict8/5 target')
 worst=max(worst,bound)
require(last==1+CB,'final endpoint')
require(worst==R(saved['max_upper']),'maximum replay')
result={'status':'PASS','intervals':128,'target':'8/5','max_upper':str(worst),'certificate_sha256':hashlib.sha256(raw).hexdigest(),'scope':'Every interval and exact rational weak-duality implication checked; analytic model reduction remains a separate proof obligation.'}
print(json.dumps(result,indent=2))

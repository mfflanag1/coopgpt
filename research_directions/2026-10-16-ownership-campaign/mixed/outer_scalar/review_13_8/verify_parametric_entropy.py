from fractions import Fraction as Q
from math import factorial
from pathlib import Path
import json

checks=[]
def require(name, ok, **details):
    if not ok: raise RuntimeError(name)
    checks.append({'name':name,'passed':True,**{k:str(v) for k,v in details.items()}})
def exp_bounds(y):
    lo=sum((y**j/Q(factorial(j)) for j in range(19)),Q(0))
    require('positive tail denominator '+str(y),y<20)
    hi=lo+y**19/Q(factorial(19))/(1-y/20)
    return lo,hi
el,eu=exp_bounds(Q(1))
tl,tu=exp_bounds(Q(1,3))
rl,ru=exp_bounds(Q(3,5))
sl,su=exp_bounds(Q(2,3))
cl,cu=1/(2*eu),1/(2*el)
require('positive b and D>A',cu<Q(1,4))
Bupper=Q(1,2)-2*cl+cu*tu/54
require('nonnegative square-bound numerator',Bupper>0)
margin=5*cl/48-Bupper**2
require('square-root charge constant',margin>0,margin=margin)
margin=cl-Q(1,3)/sl-Q(1,96)
require('f(2/3)>1/96',margin>0,margin=margin)
slope_upper=Q(17,32)-cl-Q(7,10)/ru
require('F2 derivative negative at3/5',slope_upper<0,upper=slope_upper)
slope_lower=Q(17,32)-cu-Q(2,3)/sl
require('F2 derivative positive at2/3',slope_lower>0,lower=slope_lower)
tangent_lower=Q(2,5)*cl-Q(29,160)+Q(19,90)/su
require('F2 supporting tangent positive',tangent_lower>0,lower=tangent_lower)
require('polynomial endpoint', (Q(1,2)+Q(1,9)+Q(1,72))*Q(2,3)==Q(5,12))
result={'status':'PASS','checks':checks,'scope':'Exact constants corroborating an analytic continuous-parameter proof.'}
path=Path(__file__).with_name('parametric_entropy_constants.json')
path.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':'PASS','checks':len(checks),'output':str(path)}))


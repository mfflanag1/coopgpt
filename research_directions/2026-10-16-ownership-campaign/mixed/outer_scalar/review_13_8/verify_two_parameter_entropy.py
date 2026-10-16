from fractions import Fraction as Q
from math import factorial
from pathlib import Path
import json
checks=[]
def require(name,ok,**details):
    if not ok: raise RuntimeError(name)
    checks.append({'name':name,'passed':True,**{k:str(v) for k,v in details.items()}})
def exp_bounds(y):
    lo=sum((y**j/Q(factorial(j)) for j in range(19)),Q(0))
    hi=lo+y**19/Q(factorial(19))/(1-y/20)
    require('positive tail '+str(y),y<20)
    return lo,hi
el,eu=exp_bounds(Q(1))
tl,tu=exp_bounds(Q(1,3))
rl,ru=exp_bounds(Q(3,5))
sl,su=exp_bounds(Q(2,3))
cl,cu=1/(2*eu),1/(2*el)
require('1/6<c<1/4',cl>Q(1,6) and cu<Q(1,4))
yl,yu=6*cl-1,6*cu-1
dl=1-3*cu
require('positive logarithm-series domain',yl>0 and yu<1 and dl>0)
bupper=cu-dl*(yl+yl**2/2+yl**3/3)
require('uniform b_t bound',bupper<Q(27,200),upper=bupper)
Bupper=Q(27,200)+cu*tu/54
margin=cl/9-Bupper**2
require('AMGM charge constant',margin>0,margin=margin)
margin=cl-Q(1,3)/sl-Q(1,90)
require('f(2/3)>1/90',margin>0,margin=margin)
slope_upper=cu+Q(101,600)-Q(7,10)/ru
require('negative derivative at3/5',slope_upper<0,upper=slope_upper)
slope_lower=cl+Q(101,600)-Q(2,3)/sl
require('positive derivative at2/3',slope_lower>0,lower=slope_lower)
tangent_lower=-Q(2,5)*cu-Q(17,500)+Q(19,90)/su
require('positive supporting tangent',tangent_lower>0,lower=tangent_lower)
path=Path(__file__).with_name('two_parameter_entropy_constants.json')
path.write_text(json.dumps({'status':'PASS','checks':checks},indent=2)+'\n')
print(json.dumps({'status':'PASS','checks':len(checks),'output':str(path)}))


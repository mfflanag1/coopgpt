from fractions import Fraction as Q
from math import factorial
from pathlib import Path
import json

checks=[]
def require(name, ok, **details):
    if not ok:
        raise RuntimeError(name)
    checks.append({'name':name,'passed':True,**{k:str(v) for k,v in details.items()}})
def exp_bounds(y):
    lo=sum((y**j/Q(factorial(j)) for j in range(19)),Q(0))
    hi=lo+y**19/Q(factorial(19))/(1-y/20)
    require('positive geometric tail denominator '+str(y),y<20)
    return lo,hi
el,eu=exp_bounds(Q(1))
al,au=exp_bounds(Q(3,4))
bl,bu=exp_bounds(Q(5,6))
cl,cu=1/(2*eu),1/(2*el)
require('spill exceeds A',Q(65,64)>Q(1,2)+cu)
require('positive tail derivative',Q(1,2)-2*cu>0)
upper_slope=Q(33,64)-cl-Q(7,8)/au
require('negative derivative at3/4',upper_slope<0,upper=upper_slope)
lower_slope=Q(33,64)-cu-Q(3,4)/bl
require('positive derivative at5/6',lower_slope>0,lower=lower_slope)
lower_tangent=Q(9,8)/eu-Q(29,256)-Q(11,16)/bl
require('positive supporting tangent',lower_tangent>0,lower=lower_tangent)
require('stronger than requested51/50',Q(65,64)<Q(51,50))
result={'status':'PASS','checks':checks,'scope':'Exact scalar constant corroboration, not a formal proof.'}
path=Path(__file__).with_name('entropy_weight_four_constants.json')
path.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':'PASS','checks':len(checks),'output':str(path)}))


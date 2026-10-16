from fractions import Fraction as Q
from math import factorial
from pathlib import Path
import json
lo=sum((Q(1,factorial(j)) for j in range(19)),Q(0))
hi=lo+Q(1,factorial(19))/(1-Q(1,20))
checks=[]
def require(name,ok,**details):
    if not ok: raise RuntimeError(name)
    checks.append({'name':name,'passed':True,**{k:str(v) for k,v in details.items()}})
require('K^2<3',(hi-1)**2<3,upper=(hi-1)**2)
require('e<25/9',hi<Q(25,9),upper=hi)
require('chord slope',(1-Q(4,5))/Q(3,4)==Q(4,15))
path=Path(__file__).with_name('negative_chord_constants.json')
path.write_text(json.dumps({'status':'PASS','checks':checks},indent=2)+'\n')
print(json.dumps({'status':'PASS','checks':len(checks),'output':str(path)}))


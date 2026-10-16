from fractions import Fraction as F
import json
from pathlib import Path

def exp_bounds(x, n=12):
    term = F(1)
    total = term
    for k in range(1, n+1):
        term *= x/k
        total += term
    next_term = term*x/(n+1)
    return total, total + next_term/(1-x/(n+2))

checks=[]
def require(name, condition):
    if not condition:
        raise ArithmeticError(name)
    checks.append(name)

a,b=F(7,20),F(9,25)
alo,ahi=exp_bounds(a)
blo,bhi=exp_bounds(b)
require('root_above_7_20', 2*a*ahi<1)
require('root_below_9_25', 2*b*blo>1)
require('exp_7_20_less_14191_10000', ahi<F(14191,10000))
# f is concave; on [a,b], f <= f(a)+fprime(a)*(b-a), since fprime(a)>0.
# This last expression is (1293/1000)*exp(a)-16/25.
tangent_upper=F(1293,1000)*ahi-F(16,25)
require('sharp_signed_constant_less_239_200', tangent_upper<F(239,200))
require('sharp_signed_constant_less_6_5', tangent_upper<F(6,5))
result={'status':'PASS','checks':checks,'tangent_upper':str(tangent_upper),
        'tangent_upper_display':float(tangent_upper),
        'method':'exact positive exponential Taylor sum and geometric tail; concavity tangent'}
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))

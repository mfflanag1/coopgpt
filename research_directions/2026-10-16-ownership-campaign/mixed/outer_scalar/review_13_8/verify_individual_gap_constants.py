"""Exact rational corroboration for INDIVIDUAL_PAYMENT_GAP_COUPLING.txt."""
from fractions import Fraction as Q
from math import factorial
import json
from pathlib import Path

checks = []

def require(name, condition, **details):
    if not condition:
        raise RuntimeError(name)
    checks.append(dict(name=name, passed=True, **{k: str(v) for k,v in details.items()}))

def exp_bounds(x, n=18):
    lo = sum((x**j/Q(factorial(j)) for j in range(n+1)), Q(0))
    require('tail denominator positive '+str(x), x < n+2)
    hi = lo + x**(n+1)/Q(factorial(n+1))/(1-x/Q(n+2))
    return lo, hi

elo, ehi = exp_bounds(Q(1))
require('8/3 < e < 11/4', elo > Q(8,3) and ehi < Q(11,4), lower=elo, upper=ehi)
require('c < 3/16', 1/(2*elo)<Q(3,16))
require('K < 7/4', ehi-1<Q(7,4))
B=Q(39,64)
def hp(x):
    return B/((1-x)*(2-(2-B)*x))-Q(7,4)
require('tangent derivative', hp(Q(2,3)) == -Q(19,412))
require('derivative positive at7/10', hp(Q(7,10)) > 0, derivative=hp(Q(7,10)))
require('tangent threshold', Q(7,6)+Q(19,12360)==Q(4813,4120))
_, upper = exp_bounds(Q(4813,4120))
require('finite exp threshold', upper<Q(103,32), upper=upper, threshold=Q(103,32))
require('negative v coefficient', Q(6,5)-Q(3,4)*Q(13,3)<0)
x=Q(71,128)
require('funding below8/5', 1+x+x*x/2 > Q(5,3), lower=1+x+x*x/2)
result={'status':'PASS','checks':checks,'scope':'Exact scalar constants, not an exhaustive mathematical proof.'}
output=Path(__file__).with_name('individual_gap_constants.json')
output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':'PASS','checks':len(checks),'output':str(output)}))

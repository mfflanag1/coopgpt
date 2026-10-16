"""Elementary exact constants for SUBSET_HARDWARE_DEFICIT_COUPLING."""
from fractions import Fraction as F
from math import factorial
import json


def require(condition,label):
    if not condition:
        raise RuntimeError(label)
    return label


lo=sum((F(1,factorial(k)) for k in range(15)),F(0))
hi=lo+F(1,factorial(15))/(1-F(1,16))
clo=1/(2*hi)
chi=1/(2*lo)
checks=[
    require(hi<3,"e<3, so c>1/6"),
    require(hi<4,"e<4, so exp(u)<=4u on [1/2,1]"),
    require(lo>2,"K>1, 1-c-q>0 for q<=1/2"),
    require(clo>F(1,6),"1/2+c>=2Kc via Kc=1/2-c"),
    require(chi<F(1,2),"positive coefficient 1-c"),
]
print(json.dumps({"status":"PASS","check_count":len(checks),"checks":checks,
                  "scope":"Uses separately accepted coefficient stability (SD3)."},indent=2))

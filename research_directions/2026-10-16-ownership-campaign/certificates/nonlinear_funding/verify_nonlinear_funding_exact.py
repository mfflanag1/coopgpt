"""Exact arithmetic checks for displayed scalar inequalities, not proof by samples.

General real-variable arguments are in the accompanying theorem notes. This
script replays their finite rational comparisons and expansion identities.
Assertions are deliberately not used; python -O preserves every check.
"""
from fractions import Fraction as F
from math import factorial
import hashlib
import json
from pathlib import Path


def require(value, description):
    if not value:
        raise RuntimeError(description)
    checks.append(description)


checks = []
e_lo = F(1957, 720)
e_hi = e_lo + F(1, 4410)
require(e_lo > F(125, 46), "exponential lower bound for c<23/125")
require(e_hi < F(30, 11), "exponential upper bound for c>11/60")
require(F(19, 11) ** 2 < 3, "K squared below3")
require(e_hi < F(25, 9), "L(3/4)>4/5 sufficient exponential bound")
c_upper = F(23, 125)
require(1-c_upper+c_upper**2/2-c_upper**3/6 > F(83,100),
        "signed Taylor bound exp(-c)>83/100")
require(F(11,60) > F(1,6), "exp(-c)<6/7 sufficient comparison")

small_r_upper = F(17,200)+F(7,64)
require(small_r_upper < F(13,50), "negative-gain cubic on R<=1/2")
r = F(3,4)
a, b = F(17,100), F(7,8)
f0 = a*r+b*r*r*(1-r)
d0 = a+b*(2*r-3*r*r)
q0 = b*(1-3*r)
require(f0 == F(3207,12800), "negative-gain cubic constant coefficient")
require(d0 == F(19,3200), "negative-gain cubic linear coefficient")
require(q0 == -F(35,32), "negative-gain cubic quadratic coefficient")
require(q0+b/4 == -b, "quadratic domination for s>=-1/4")
cubic_upper = f0+d0*d0/(4*b)
require(cubic_upper == F(8979961,35840000), "completed square exact maximum")
require(cubic_upper < F(13,50), "negative-gain cubic on R>=1/2")
funding_upper = F(148,125)+F(49,16)*F(23,125)*F(148,125)/8+F(13,100)
require(funding_upper == F(698699,500000), "small-gap funding arithmetic")
require(funding_upper < F(699,500) < F(71,60)**2,
        "small-gap funding strictly below C squared")

x = F(11,16)
exp_lo = sum((x**j/F(factorial(j)) for j in range(7)), F(0))
exp_hi = exp_lo+x**7/F(factorial(7))/(1-x/8)
require(exp_hi < 2, "exact Taylor-tail proof exp(11/16)<2")
require(F(7,5) < F(71,60)**2, "low-capped-total7/5 below C squared")

x = F(41,100)
require(1+x+x*x/2+x*x*x/6 > F(3,2), "log(3/2)<41/100")
require(F(19,10)*F(141,100) == F(2679,1000), "dual tangent coefficient")
require(F(7,5)-F(33,40) == F(23,40), "dual obstruction x coefficient")
require(F(7,5)+F(17,20)-F(33,40)*F(2679,1000) == F(1593,40000),
        "dual obstruction first branch constant")
require(F(23,40)*F(289,800) > F(81,400), "dual obstruction AM-GM comparison")
require(F(9,10)-F(32407,40000) == F(3593,40000),
        "dual obstruction second branch margin")
require(1+F(11,20)-F(1,8) == F(57,40), "dual obstruction funding arithmetic")
require(F(32,27)**2 < F(57,40), "dual obstruction threshold above C squared")

base = Path(__file__).resolve().parent
names = [
    "POSITIVE_GAP_DUAL_AGGREGATION.txt", "SUBSET_HARDWARE_ROLE_LOWER.txt",
    "AGGREGATE_DUAL_OBSTRUCTION.txt", "SMALL_POSITIVE_GAP_FUNDING.txt",
    "LOW_CAPPED_TOTAL_MANY_POSITIVE.txt", "CAPPED_TOTAL_OVERFLOW_OBSTRUCTION.txt",
    "COMPLEMENT_CAP_TRUNCATION_OBSTRUCTION.txt", Path(__file__).name,
]
result = {
    "status": "PASS",
    "scope": "Exact rational checks of displayed finite inequalities and identities; continuous theorem proofs are in the text notes.",
    "checks": checks,
    "checks_count": len(checks),
    "small_gap_rational_upper": str(funding_upper),
    "low_total_exponential_upper": str(exp_hi),
    "sha256": {name: hashlib.sha256((base/name).read_bytes()).hexdigest() for name in names},
}
print(json.dumps(result, indent=2, sort_keys=True))

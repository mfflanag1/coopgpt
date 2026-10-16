"""Exact constants for DIRECTIONAL_LOCAL_MASS_FUNDING; no asserts/floats."""
from fractions import Fraction as F
from math import factorial
import json


def lower_exp(x, n):
    return sum((x**k / factorial(k) for k in range(n + 1)), F(0))


def require(condition, label):
    if not condition:
        raise RuntimeError(label)
    return label


e_lo = lower_exp(F(1), 14)
e_hi = e_lo + F(1, factorial(15)) / (1 - F(1, 16))
checks = [
    require(e_hi < F(11, 4), "e < 11/4 and K < 7/4"),
    require(lower_exp(F(7, 5), 6) > 4, "log 4 < 7/5"),
    require(F(7, 4)*F(1, 4)*(1+F(7, 5)) == F(21, 20), "negative entropy exponent <21/20"),
    require(F(11, 4)*F(20, 19) == F(55, 19) < 3, "exp(21/20)<3 via geometric tail"),
    require(F(1)/(1-F(7, 400)) == F(400, 393) < F(51, 50), "exp(7/400)<51/50"),
    require(lower_exp(F(25, 102), 3) > F(51, 40), "exp(25/102)>51/40"),
    require(F(51, 100)*F(40, 51) == F(2, 5), "robust funding excess <2/5"),
    require(e_hi < F(87, 32), "e<87/32"),
    require((1+F(16, 87))**2 > F(7, 5), "C^2>7/5"),
    require(F(1, 10)+(1+F(3, 16))/4 < F(1, 2), "example mixed local owners have negative gaps"),
    require(e_lo > F(8, 3), "c<3/16 for example"),
]
print(json.dumps({"status":"PASS", "check_count":len(checks), "checks":checks}, indent=2))

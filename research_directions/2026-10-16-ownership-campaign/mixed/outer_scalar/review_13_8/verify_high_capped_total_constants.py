"""Exact constants for HIGH_CAPPED_TOTAL_FUNDING; independent of optimizers."""
from fractions import Fraction as F
from math import factorial
import json


def exp_lower(x, n=18):
    return sum((x**k / factorial(k) for k in range(n+1)), F(0))


def exp_upper(x, n=18):
    if not 0 <= x < n+2:
        raise ValueError("Taylor geometric tail condition")
    return exp_lower(x,n)+x**(n+1)/factorial(n+1)/(1-x/F(n+2))


def require(condition, label):
    if not condition:
        raise RuntimeError(label)
    return label


checks = [
    require(exp_upper(F(1)) < F(68,25), "e<68/25, so K<43/25"),
    require(exp_upper(F(43,25)) < 6, "exp(K)<6"),
    require(exp_upper(F(1069,825)) < F(11,3), "log(11/3)>1069/825"),
    require(exp_upper(F(1069,825)) < F(183,50) < F(11,3), "displayed rational Taylor bound <183/50<11/3"),
    require(F(56,33)-F(43,25) == -F(19,825), "convex tangent has negative slope"),
    require(F(43,25)-F(14,33) == F(1069,825), "convex tangent endpoint constant"),
    require(exp_lower(F(1)) > F(8,3), "e>8/3"),
    require(F(11,4)/F(8,3)**2 == F(99,256) < F(2,5), "high-S funding excess<2/5"),
    require(exp_upper(F(1)) < F(87,32), "e<87/32"),
    require((1+F(16,87))**2 > F(7,5), "C^2>7/5"),
]
print(json.dumps({"status":"PASS", "check_count":len(checks), "checks":checks,
 "support_margin_lower":str(F(11,3)-exp_upper(F(1069,825)))},indent=2))

"""Exact elementary constants for the independent global-diffuse audit.

The all-profile and asymptotic arguments are analytical, in the audit note.
This checker deliberately uses no floating arithmetic or removable asserts.
"""
from fractions import Fraction as F
from math import factorial
import hashlib
import json
from pathlib import Path


def require(condition, label):
    if not condition:
        raise RuntimeError(label)
    return label


n = 14
e_lo = sum((F(1, factorial(k)) for k in range(n + 1)), F(0))
# All tail ratios after term n+1 are at most 1/(n+2).
e_hi = e_lo + F(1, factorial(n + 1)) / (1 - F(1, n + 2))
checks = [
    require(e_lo > F(8, 3), "e > 8/3"),
    require(e_hi < F(11, 4), "e < 11/4"),
    require(e_lo > F(9, 4), "sqrt(e) > 3/2"),
    require(e_hi < 4, "sqrt(e) < 2; low-S limiting gap is strict"),
    require(2 + 2 / e_lo < F(11, 4), "2+2/e < 11/4"),
    require(F(11, 4) / 3 < 1, "positive-gap restoration coefficient < 1"),
    require(F(9, 4) < e_lo, "negative-gap restoration coefficient < 1"),
    # Independent fallback hardware-restoration charge margin:
    # 1-5/(4sqrt(e)) > 1/(4sqrt(e)) iff sqrt(e)>3/2.
    require(e_lo > F(9, 4), "fallback alpha > 1/(4sqrt(e))"),
]
base = Path(__file__).resolve().parent
target = base.parents[2] / "ownership" / "outer_frontier" / "hardware_bound" / "extension" / "GLOBAL_DIFFUSE_SECOND_ORDER.txt"
result = {
    "status": "PASS",
    "check_count": len(checks),
    "checks": checks,
    "e_lower": str(e_lo),
    "e_upper": str(e_hi),
    "target_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
    "scope": "Exact constants only; proof and uniform asymptotics audited analytically.",
}
print(json.dumps(result, indent=2))

"""Exact affine certificates for the source-comparison boundary example."""
from fractions import Fraction as F
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


# Each coordinate is intercept + slope*t; affine inequalities on [0,1]
# are equivalent to their endpoint inequalities.
coordinates = [(F(0), F(1)), (F(3), F(-2)), (F(3), F(1))]
require(sum(a for a, b in coordinates) == 6, "total intercept")
require(sum(b for a, b in coordinates) == 0, "constant total")
for t in (F(0), F(1)):
    p = [a + b*t for a, b in coordinates]
    require(all(q >= 0 for q in p), "nonnegative endpoint")
    require(all(q >= p[0] for q in p), "first coordinate is minimum")
    require(all(q <= p[2] for q in p), "third coordinate is maximum")
require(coordinates[0][1] > 0, "strictly increasing minimum")
require(coordinates[2][1] > 0, "strictly increasing maximum")
x = [a+b for a,b in coordinates]
z = [a for a,b in coordinates]
rho = sum(abs(a-b) for a,b in zip(x,z))/6
require(x != z and rho == F(2,3), "distinct full selectors")
out = {"status": "PASS", "method": "exact affine endpoint certificates, not sampling",
       "domain": "0 <= t <= 1", "total": 6,
       "leximin": list(map(str,x)), "descending_lex_min": list(map(str,z)),
       "normalized_l1": str(rho)}
Path(__file__).with_name("source_boundary_control.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out))

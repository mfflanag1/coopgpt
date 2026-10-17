from fractions import Fraction as F
import json

def require(condition, message):
    if not condition:
        raise ValueError(message)

L = 2000
delta1 = 665 * F(6, 5) + 666 * 3
require(delta1 == 2796, 'first shift error')
q1_c = (665 * F(2, 5) + F(1, 1000)) / 666
q1_error = (delta1 + 665 * F(2, 5)) / 666
require(q1_c == F(266001, 666000), 'first C coefficient')
require(q1_error == F(1531, 333), 'first error coefficient')
delta2 = 10 * F(4, 5) + 12
require(delta2 == 20, 'second shift error')
lhs_c = 10 * F(4, 5) + 12 * F(5, 4)
lhs_error = 10 * F(8, 5) + 12 * F(5, 4)
require(lhs_c == 23 and lhs_error == 31, 'second upper bound')
A = lhs_c + 2 * q1_c
B = lhs_error + delta2 + 2 * q1_error
require(A == F(2641667, 111000), 'A')
require(B == F(20045, 333), 'B')
d = F(999, 1000)
K = (12 + A/d) / (A/d + B/L)
require(K == F(1588934000, 1058001797), 'final exact fraction')
require(K > F(3, 2), 'strictly exceeds 3/2')
require((1665-665, 666-665) == (1000, 1), 'first retained profile')
require((15-10, 12-10) == (5, 2), 'second retained profile')
require((1665, 666) == (333*5, 333*2), 'first dilation')
require((15, 12) == (3*5, 3*4), 'second dilation')
require(333 == 3**2 * 37 and 1110 == 2*3*5*37, 'prime factors')
print(json.dumps({'status': 'PASS', 'L': L,
 'owners_per_role_symbolic': '12000 * 1110^2003',
 'funding_lower_exact': str(K), 'funding_lower_decimal': float(K),
 'gap_over_three_halves': str(K-F(3,2)),
 'scope': 'exact algebra checks for compressed analytic certificate; not profile enumeration'}, indent=2))

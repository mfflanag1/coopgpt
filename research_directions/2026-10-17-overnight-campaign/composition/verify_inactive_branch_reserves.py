"""Exact product, telescoping, and reserve-coefficient checks; not a proof oracle."""
from fractions import Fraction as Q
from math import comb
import json
from pathlib import Path

checks = 0
for M in range(2, 301):
    p = [None, Q(1)]
    for m in range(2, M + 1):
        p.append(p[-1] * Q(2*m, 2*m-1))
    assert p[M] == Q(4**M, 2*comb(2*M, M))
    assert sum((1 / (2*m*p[m-1]) for m in range(2, M+1)), Q()) == 1-1/p[M]
    # In the recurrence W_m/P_m - W_(m-1)/P_(m-1), all interior coefficients cancel.
    w_coeff = [Q(0)] * (M+1)
    for m in range(2, M+1):
        w_coeff[m] += 1/p[m]
        w_coeff[m-1] -= 1/p[m-1]
        assert (1-Q(1,2*m))/p[m-1] == 1/p[m]
    assert w_coeff[1] == -1 and w_coeff[M] == 1/p[M]
    assert all(x == 0 for x in w_coeff[2:M])
    checks += 1
    for B in range(1, 7):
        eps = Q(1,2*B)
        finite = p[M]*eps/(1+p[M]*eps*eps)
        assert (finite > B) == (p[M] > 4*B*B)
        # Theorem2 specializes to theorem1 when every reserve is zero.
        assert (Q(1,4*B)-B/p[M] > 0) == (p[M] > 4*B*B)
        checks += 1

out = {
    'status': 'PASS', 'exact_fraction_cases': checks,
    'max_M': 300, 'max_B': 6,
    'checks': ['central-binomial product identity', 'reserve weight telescoping',
               'all interior recurrence coefficients cancel',
               'fixed-instance rational threshold equivalence'],
    'limits': 'Algebraic checks only. All-profile mechanism argument is the written proof.'
}
Path(__file__).with_name('INACTIVE_BRANCH_RESERVE_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))

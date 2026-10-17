from fractions import Fraction as Q
from pathlib import Path
import json

A = ((Q(1), Q(1), Q(1, 4)), (Q(1), Q(1, 4), Q(1)))
v = (Q(3, 2), Q(1), Q(1))
cases = [
    ((0, 0), (Q(1), Q(0), Q(0)), (Q(3, 2), Q(0)), Q(3, 2)),
    ((1, 0), (Q(1), Q(0), Q(0)), (Q(3, 2), Q(0)), Q(3, 2)),
    ((0, 1), (Q(1), Q(0), Q(0)), (Q(0), Q(3, 2)), Q(3, 2)),
    ((1, 1), (Q(0), Q(4, 5), Q(4, 5)), (Q(4, 5), Q(4, 5)), Q(8, 5)),
]
values = {}
for caps, z, common_dual, expected in cases:
    c = (Q(1), Q(caps[0]), Q(caps[1]))
    assert all(0 <= z[j] <= c[j] for j in range(3))
    assert all(sum(A[r][j] * z[j] for j in range(3)) <= 1 for r in range(2))
    # An absent private row may have a positive covering price at zero cost.
    private_dual = tuple(max(Q(0), v[j] - sum(A[r][j] * common_dual[r] for r in range(2))) for j in range(3))
    primal = sum(v[j] * z[j] for j in range(3))
    dual = sum(common_dual) + sum(c[j] * private_dual[j] for j in range(3))
    assert primal == dual == expected
    values[caps] = expected
gap = values[(1, 1)] + values[(0, 0)] - values[(1, 0)] - values[(0, 1)]
assert gap == Q(1, 10)
result = {'status': 'PASS', 'exact_primal_dual_profiles': len(cases), 'submodularity_violation': str(gap), 'scope': 'positive fixed linear three-pool sums only'}
Path(__file__).with_name('TWO_COMMON_THREE_POOL_OBSTRUCTION_CHECKS.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))

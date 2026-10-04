"""Exact finite-domain witness check; no LP and no claim for other profiles."""
from fractions import Fraction as F
import json

def worth(c, mask):
    return min(sum(c[i] for i in (0, 1) if mask >> i & 1),
               sum(c[i] for i in (2, 3) if mask >> i & 1))

profiles = [(1, 1, 1, 1)]
payments = [(F(1, 2),) * 4]
ideals = [(F(1),) * 4]
for raised in range(4):
    c = [1] * 4
    c[raised] = 2
    x = [F(3, 4)] * 4
    x[raised] = F(1, 2)
    x[raised ^ 1] = F(1, 4)
    h = [F(1)] * 4
    h[raised] = h[raised ^ 1] = F(0)
    profiles.append(tuple(c))
    payments.append(tuple(x))
    ideals.append(tuple(h))

coalitions = floors = comparisons = 0
ratios = []
for c, x, h in zip(profiles, payments, ideals):
    assert min(x) >= 0
    for mask in range(1, 16):
        assert sum(x[i] for i in range(4) if mask >> i & 1) >= worth(c, mask)
        coalitions += 1
    for xi, hi in zip(x, h):
        assert xi >= hi / 3
        floors += 1
    t = worth(c, 15)
    ratios.append((sum(x) - t) / t)
for j, high in enumerate(profiles):
    for k, low in enumerate(profiles):
        for i in range(4):
            if high[i] > low[i] and all(high[r] == low[r] for r in range(4) if r != i):
                assert payments[j][i] >= payments[k][i]
                comparisons += 1
assert max(ratios) == F(1, 8)
assert (coalitions, floors, comparisons) == (75, 20, 4)
print(json.dumps({"status": "passed", "profiles": len(profiles),
                  "coalition_inequalities": coalitions, "fairness_floors": floors,
                  "distinct_own_report_comparisons": comparisons,
                  "maximum_subsidy_ratio": str(max(ratios)),
                  "scope": "only the five stated capacity profiles"}, indent=2))

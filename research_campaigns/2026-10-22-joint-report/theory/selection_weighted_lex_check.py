"""Exact finite diagnostics for weighted-lex validity and petal barriers.
The proofs are analytic; no floating-point computation enters these checks.
Run with Python standard library only.
"""
from fractions import Fraction as F
from itertools import combinations, permutations, product
import json


def lex_cover(rows, weights):
    n = len(weights)
    x = [None] * n
    remaining = set(range(n))
    while remaining:
        levels = []
        for support, rhs in rows:
            residual = remaining.intersection(support)
            if residual:
                value = rhs - sum(x[i] for i in support if x[i] is not None)
                levels.append((F(value, sum(weights[i] for i in residual)), residual))
        delta = max([F(0)] + [value for value, _ in levels])
        if delta == 0:
            for i in remaining:
                x[i] = F(0)
            break
        frozen = set().union(*(s for value, s in levels if value == delta))
        assert frozen
        for i in frozen:
            x[i] = delta * weights[i]
        remaining.difference_update(frozen)
    assert all(sum(x[i] for i in s) >= rhs for s, rhs in rows)
    return x


stats = {}
formula_cases = 0
weight_monotone_cases = 0
for r, k in [(1, 2), (2, 2), (2, 3), (3, 2)]:
    n = r * k + 1
    petals = [set(range(1 + l*k, 1 + (l+1)*k)) for l in range(r)]
    rows = [({0} | p, F(1)) for p in petals]
    for weights in product((1, 2, 4), repeat=n):
        x = lex_cover(rows, weights)
        m = min(sum(weights[i] for i in p) for p in petals)
        assert sum(x) == F(weights[0] + r*m, weights[0] + m)
        formula_cases += 1
        for i in range(n):
            increased = list(weights)
            increased[i] += 3
            assert lex_cover(rows, increased)[i] >= x[i]
            weight_monotone_cases += 1
stats['petal_formula_cases'] = formula_cases
stats['own_weight_monotonicity_cases'] = weight_monotone_cases

# General non-petal rows: all 0/1 RHS games on three nonempty owner subsets.
supports = [set(s) for size in range(1, 4) for s in combinations(range(3), size)]
rhs_cases = 0
for values in product((0, 1), repeat=len(supports)):
    rows = list(zip(supports, map(F, values)))
    for weights in product((1, 3), repeat=3):
        x = lex_cover(rows, weights)
        for i in range(3):
            changed = list(weights)
            changed[i] += 2
            assert lex_cover(rows, changed)[i] >= x[i]
            new_rows = [(s, rhs + (F(2) if i in s else F(0))) for s, rhs in rows]
            assert lex_cover(new_rows, weights)[i] >= x[i]
            rhs_cases += 1
stats['general_incidence_and_weight_cases'] = rhs_cases

# Complete own-local averaging audit at r=k=2: 5 owners, 6 resources.
# R={0,1}; Q=[2]^2 identified with {2,3,4,5}.
bundles = [{0, 1}, {2, 3}, {4, 5}, {2, 4}, {3, 5}]
assert all(len(b) == 2 for b in bundles)
for coalition_mask in range(1 << 5):
    chosen = {i for i in range(5) if coalition_mask >> i & 1}
    coverage = set().union(*(bundles[i] for i in chosen)) if chosen else set()
    winning = 0 in chosen and ({1, 2} <= chosen or {3, 4} <= chosen)
    assert (len(coverage) == 6) == winning

# Each owner's function is asymmetric in both owner and resource labels.
def local_weight(owner, bundle):
    return 1 + sum(2 ** ((owner + 1) * (resource + 1)) for resource in bundle)

samples = good = 0
strict_max = [[0, 0, 0], [0, 0, 0]]
bad_petals = [0, 0]
for resource_perm in permutations(range(6)):
    moved = [{resource_perm[q] for q in b} for b in bundles]
    for owners in permutations(range(5)):
        w = [local_weight(owners[role], moved[role]) for role in range(5)]
        m = min(w[1]+w[2], w[3]+w[4])
        good += m >= w[0]
        samples += 1
        for ell, roles in enumerate([(0, 1, 2), (0, 3, 4)]):
            vals = [w[i] for i in roles]
            for j in range(3):
                strict_max[ell][j] += all(vals[j] > vals[t] for t in range(3) if t != j)
            bad_petals[ell] += vals[0] > vals[1]+vals[2]
assert samples == 720 * 120
assert good * 3 >= samples
for ell in range(2):
    assert len(set(strict_max[ell])) == 1
    assert bad_petals[ell] * 3 <= samples
stats['local_averaging_profiles'] = samples
stats['local_averaging_good_profiles'] = good
stats['local_strict_max_counts'] = strict_max
stats['local_bad_petal_counts'] = bad_petals
stats['status'] = 'PASS'
print(json.dumps(stats, indent=2))

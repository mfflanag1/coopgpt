"""Exact finite diagnostics for ownership boundaries; no asymptotic claim.

Run with python3 -I, never -O. All decisive comparisons use Fraction.
"""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json
import random

rng = random.Random(202610170703)
counts = dict(profiles=0, coalitions=0, owner_cover_out=0,
              compression_loss_coordinates=0, compression_coalitions=0,
              owner_marginal_equalities=0, activation_cases=0,
              two_pool_out=0, two_pool_coverage=0, min_inequalities=0)

def add(rows, d):
    return [sum((row[j] for row in rows), Q(0)) for j in range(d)]

def value(c):
    return min(c[0], sum((min(c[j], c[j+1])
                         for j in range(1, len(c), 2)), Q(0)))

def transformed_value(c):
    return min(c[0], c[1] + sum((min(c[j], c[j+1])
                                for j in range(2, len(c), 2)), Q(0)))

def compress(row, bundled, split):
    return [row[0], sum((min(row[1+2*j], row[2+2*j])
                        for j in bundled), Q(0))] + [
        row[1+2*j+k] for j in split for k in range(2)]

def covered_payment(rows):
    f = value(add(rows, len(rows[0])))
    return [f if row[0] > 0 else Q(0) for row in rows]

def proportional_pair(rows):
    c = add(rows, 2)
    f = min(c)
    if not f:
        return [Q(0)] * len(rows)
    return [f * (row[0]/c[0] + row[1]/c[1]) for row in rows]

grid = [Q(x, 3) for x in range(10)]
for a, b in product(grid, repeat=2):
    for da in [x for x in grid if x <= a]:
        for db in [x for x in grid if x <= b]:
            assert min(a,b)-min(a-da,b-db) >= min(da,db)
            counts['min_inequalities'] += 1

for n in range(1, 7):
    for trial in range(60):
        m = rng.randint(1, 8)
        d = 1+2*m
        power_eligible = set(rng.sample(range(n), rng.randint(1,n)))
        split = [j for j in range(m) if rng.randrange(3) == 0]
        bundled = [j for j in range(m) if j not in split]
        rows = [[Q(0)]*d for _ in range(n)]
        for i in power_eligible:
            rows[i][0] = Q(rng.randrange(13), 4)
        for j in bundled:
            i = rng.randrange(n)
            rows[i][1+2*j] = Q(rng.randrange(13), 4)
            rows[i][2+2*j] = Q(rng.randrange(13), 4)
        for j in split:
            for i in range(n):
                rows[i][1+2*j] = Q(rng.randrange(5), 4)
                rows[i][2+2*j] = Q(rng.randrange(5), 4)
        tr = [compress(row,bundled,split) for row in rows]
        td = len(tr[0])
        f = value(add(rows,d))
        assert transformed_value(add(tr,td)) == f
        pay = covered_payment(rows)
        assert sum(pay) <= len(power_eligible)*f
        assert all(pay[i] == 0 for i in range(n) if rows[i][0] == 0)
        counts['profiles'] += 1
        for i in range(n):
            original_marginal = f-value(add([r for j,r in enumerate(rows)
                                             if j != i],d))
            transformed_marginal = f-transformed_value(add(
                [r for j,r in enumerate(tr) if j != i],td))
            assert original_marginal == transformed_marginal
            counts['owner_marginal_equalities'] += 1
        for mask in range(1<<n):
            coalition = [i for i in range(n) if mask & (1<<i)]
            worth = value(add([rows[i] for i in coalition],d))
            assert worth == transformed_value(add([tr[i] for i in coalition],td))
            assert sum(pay[i] for i in coalition) >= worth
            counts['coalitions'] += 1
            counts['compression_coalitions'] += 1
            low = [row[:] for row in rows]
            for i in coalition:
                for j in range(d):
                    low[i][j] *= Q(rng.randrange(5),4)
            wd = [[rows[i][j]-low[i][j] for j in range(d)] for i in range(n)]
            low_pay = covered_payment(low)
            assert sum(pay[i]-low_pay[i] for i in coalition) >= value(add(wd,d))
            counts['owner_cover_out'] += 1
            counts['activation_cases'] += sum(
                rows[i][0] > 0 and low[i][0] == 0 for i in coalition)
            tr_low = [compress(row,bundled,split) for row in low]
            tr_wd = [compress(row,bundled,split) for row in wd]
            delta = [[tr[i][j]-tr_low[i][j] for j in range(td)] for i in range(n)]
            for i,j in product(range(n),range(td)):
                assert delta[i][j] >= tr_wd[i][j]
                counts['compression_loss_coordinates'] += 1
            assert transformed_value(add(delta,td)) >= value(add(wd,d))
            if not split:
                pp = proportional_pair(tr)
                pl = proportional_pair(tr_low)
                assert sum(pp[i] for i in coalition) >= worth
                assert sum(pp[i]-pl[i] for i in coalition) >= value(add(wd,d))
                assert sum(pp) <= 2*f
                counts['two_pool_coverage'] += 1
                counts['two_pool_out'] += 1

# Exact invalidity witness: branch split between two owners cannot be replaced
# by a sum of their individual min capacities, even at a single report profile.
split_rows = [[Q(0),Q(1),Q(0)], [Q(1),Q(0),Q(1)]]
assert value(add(split_rows,3)) == 1
assert sum(min(r[1],r[2]) for r in split_rows) == 0

# One power owner may collect every dollar while a hardware owner's full-owner
# marginal is positive. The efficient owner-cover rule has no such floor.
floor_rows = [[Q(1),Q(0),Q(0)], [Q(0),Q(1),Q(1)]]
assert covered_payment(floor_rows) == [1,0]
assert value(add(floor_rows,3))-value(floor_rows[0]) == 1

result = {'status':'PASS', 'arithmetic':'exact fractions', **counts,
          'split_branch_invalid_compression_witness':True,
          'owner_cover_fairness_floor_counterexample':True}
Path(__file__).with_name('ai_ownership_boundary_checks.json').write_text(
    json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))

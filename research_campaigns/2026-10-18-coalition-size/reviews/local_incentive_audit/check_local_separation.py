#!/usr/bin/env python3
"""Independent finite audit: sorting/assignment tests versus direct direction LPs.

Every numerical optimum is reconstructed as rational primal and dual solutions
and checked exactly. No implementation from the root note is imported.
"""
from fractions import Fraction as Q
from itertools import combinations, product
from pathlib import Path
from collections import Counter
import hashlib
import json
import random
from datetime import datetime, timezone
import numpy as np
from scipy.optimize import linprog


def rational(x):
    return Q(float(x)).limit_denominator(1000000)


def neg(values, k):
    return sum(sorted(x for x in values if x < 0)[:max(0, k)])


def coalitions(n, s):
    return [c for t in range(1, min(n, s) + 1)
            for c in combinations(range(n), t)]


def sorting_test(n, s, J, jac):
    vals = []
    for col, (owner, _) in enumerate(J):
        z = [jac[i][col] for i in range(n)]
        vals.append(z[owner] + neg([z[i] for i in range(n) if i != owner], s-1))
    return all(v >= 0 for v in vals), min(vals, default=0)


def assignment_test(n, s, rows, activities, profits, J, jac):
    by_row = [[k for k, (_, a) in enumerate(J) if a == row]
              for row in range(rows)]
    margins = []
    for activity, profit in zip(activities, profits):
        if profit <= 0:
            continue
        support = [a for a in range(rows) if activity[a] > 0]
        for assigned_cols in product(*(by_row[a] for a in support)):
            owners = {J[k][0] for k in assigned_cols}
            if len(owners) > s:
                continue
            z = [sum(activity[a] * jac[i][col]
                     for a, col in zip(support, assigned_cols))
                 for i in range(n)]
            score = sum(z[i] for i in owners)
            score += neg([z[i] for i in range(n) if i not in owners], s-len(owners))
            margins.append(score-profit)
    return all(v >= 0 for v in margins), min(margins, default=0), len(margins)


def direct_direction_lp(n, rows, activities, profits, J, jac, coalition):
    """Max pi*x - sum_i-in-C jac[i]*d under Ax<=sum d, sum d<=1.

    This independently searches all distributed directions, including mixtures
    of activities and the unproductive directions that detect TCWM failure.
    """
    cols = [k for k, (j, _) in enumerate(J) if j in coalition]
    m = len(activities)
    if not cols:
        return Q(0), None
    objective = list(profits) + [-sum(jac[i][k] for i in coalition) for k in cols]
    A = [[activities[e][a] for e in range(m)] +
         [-int(J[k][1] == a) for k in cols] for a in range(rows)]
    A.append([0]*m + [1]*len(cols))
    b = [0]*rows + [1]
    result = linprog(-np.array(objective, dtype=float),
                     A_ub=np.array(A, dtype=float), b_ub=np.array(b, dtype=float),
                     bounds=(0, None), method='highs')
    assert result.success, result.message
    x = [rational(z) for z in result.x]
    dual = [rational(-z) for z in result.ineqlin.marginals]
    assert all(v >= 0 for v in x)
    assert all(v >= 0 for v in dual)
    assert all(sum(a*v for a, v in zip(row, x)) <= rhs for row, rhs in zip(A, b))
    assert all(sum(dual[i]*A[i][k] for i in range(len(b))) >= objective[k]
               for k in range(len(objective)))
    primal_value = sum(v*c for v, c in zip(x, objective))
    dual_value = sum(v*c for v, c in zip(dual, b))
    assert primal_value == dual_value
    if primal_value > 0:
        witness = {'coalition': list(coalition), 'value': str(primal_value),
                   'directions': {str(J[k]): str(x[m+j]) for j,k in enumerate(cols)
                                  if x[m+j]},
                   'activities': [str(v) for v in x[:m]],
                   'resource_dual': [str(v) for v in dual]}
    else:
        witness = None
    return primal_value, witness


def main():
    rng = random.Random(20261018)
    count = Counter()
    examples = {}
    for case in range(240):
        n = rng.choice([3, 4, 5])
        rows = rng.choice([2, 3, 4])
        s = 1 + case % n
        if case % 19 == 0:
            s = n + 2  # Verify the at-most convention and capped order statistic.
        r = min(rows, 1 + case % 3)
        m = rng.randint(1, 4)
        activities = []
        for _ in range(m):
            support = rng.sample(range(rows), rng.randint(1, r))
            activities.append([rng.randint(1, 3) if a in support else 0
                               for a in range(rows)])
        profits = [rng.randint(0, 7) for _ in range(m)]
        # Every fourth case deliberately retains a wholly inactive owner.
        active_owner_count = n-1 if case % 4 == 0 else n
        J = [(j, a) for j in range(active_owner_count) for a in range(rows)
             if rng.random() < .65]
        if not J:
            J = [(0, 0)]
        jac = [[rng.randint(-3, 3) for _ in J] for _ in range(n)]
        family = case % 3
        if family >= 1:
            for col, (owner, a) in enumerate(J):
                rest = [jac[i][col] for i in range(n) if i != owner]
                jac[owner][col] = -neg(rest, s-1) + rng.randint(0, 2)
                if family == 2:
                    # The extra diagonal rate is a valid resource dual cover.
                    jac[owner][col] += max(profits, default=0)
        tcwm, tmargin = sorting_test(n, s, J, jac)
        brute_tcwm = all(sum(jac[i][k] for i in c) >= 0
                         for c in coalitions(n, s)
                         for k, (j, a) in enumerate(J) if j in c)
        assert tcwm == brute_tcwm
        assignment, omargin, tests = assignment_test(n, s, rows, activities, profits, J, jac)
        oracle = tcwm and assignment
        max_violation = Q(0)
        first_witness = None
        for c in coalitions(n, s):
            value, witness = direct_direction_lp(n, rows, activities, profits, J, jac, c)
            count['coalition_direction_problems_exactly_certified'] += 1
            if any(j in c for j, a in J):
                count['LP_optima_with_exact_primal_dual_certificates'] += 1
            else:
                count['trivial_zero_direction_problems'] += 1
            max_violation = max(max_violation, value)
            if first_witness is None and witness is not None:
                first_witness = witness
        assert oracle == (max_violation == 0), (case, oracle, max_violation)
        assert family != 1 or tcwm
        assert family != 2 or oracle
        category = 'OUT_pass' if oracle else ('TCWM_pass_OUT_fail' if tcwm else 'TCWM_fail')
        count[category] += 1
        count['cases'] += 1
        count['activity_owner_assignment_tests'] += tests
        count['coordinate_tests'] += len(J)
        count['cases_with_wholly_inactive_owner'] += int(active_owner_count < n)
        if category not in examples:
            examples[category] = {'case':case, 'n':n, 'rows':rows, 's':s,
                                  'activities':activities, 'profits':profits,
                                  'J':J, 'jacobian':jac,
                                  'TCWM_margin':tmargin, 'assignment_margin':omargin,
                                  'max_violation':str(max_violation),
                                  'first_LP_witness':first_witness}

    # Exact independent admission counterexample verification.
    grid = [Q(k,4) for k in range(5)]
    for b1, b2 in product(grid, repeat=2):
        y = [b1 if b1 > 0 else b2, b2]
        assert all(v >= 0 for v in y)
        assert y[0] >= b1 and y[1] >= b2 and sum(y) >= b1+b2
        assert sum(y) <= 2*(b1+b2)
        for c in coalitions(2,2):
            for owner, amount in enumerate([b1,b2]):
                if amount == 0 or owner not in c:
                    continue
                derivative = ([1,0] if owner == 0 else ([0,1] if b1>0 else [1,1]))
                assert sum(derivative[i] for i in c) >= 1
                count['counterexample_face_OUT_coordinate_checks'] += 1
        count['counterexample_profiles'] += 1
    eps = Q(1,4)
    assert eps < 1
    counterexample = {'old_profile':['0','1'], 'new_profile':[str(eps),'1'],
                      'old_y1':'1', 'new_y1':str(eps),
                      'within_face_OUT':'PASS for all active-coordinate directions',
                      'admission_right_limit_y1':'0', 'admission_violation':'1 > 0'}

    source = Path(__file__).resolve().parents[2] / 'root/LOCAL_INCENTIVE_SEPARATION.txt'
    result = {'status':'PASS', 'timestamp_utc':datetime.now(timezone.utc).isoformat(),
              'source':str(source), 'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
              'checks':dict(count), 'examples':examples, 'admission_counterexample':counterexample,
              'scope':'Exact finite checks supplement the independent proof audit; no global or funding bound is inferred.'}
    out = Path(__file__).with_suffix('.json')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'status':'PASS', 'checks':dict(count), 'output':str(out)}))


if __name__ == '__main__':
    main()

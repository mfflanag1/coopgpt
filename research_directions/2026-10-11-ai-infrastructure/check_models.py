"""Exact, bounded calibration checks; not a proof of the universal LP theorem."""
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations, product
import json


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def solve(matrix, rhs):
    n = len(rhs)
    a = [[Q(x) for x in row] + [Q(b)] for row, b in zip(matrix, rhs)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if a[i][j]), None)
        if pivot is None:
            return None
        a[j], a[pivot] = a[pivot], a[j]
        divisor = a[j][j]
        a[j] = [x / divisor for x in a[j]]
        for i in range(n):
            if i != j:
                factor = a[i][j]
                a[i] = [x - factor*y for x, y in zip(a[i], a[j])]
    return tuple(row[-1] for row in a)


def dot(a, b):
    return sum((x*y for x, y in zip(a, b)), Q(0))


def vertices(rows, rhs, dimension):
    result = []
    for active in combinations(range(len(rows)), dimension):
        x = solve([rows[i] for i in active], [rhs[i] for i in active])
        if x is not None and all(dot(row, x) <= b for row, b in zip(rows, rhs)):
            result.append(x)
    return result


def oracle(matrix, prices):
    d, m = len(matrix), len(prices)
    # Dual: -A^T w <= -p, -w <= 0. Independent dual value check.
    dual_rows = [tuple(-matrix[e][j] for e in range(d)) for j in range(m)]
    dual_rows += [tuple(-int(e == k) for e in range(d)) for k in range(d)]
    dual_rhs = tuple(-x for x in prices) + (0,)*d
    dual_points = vertices(dual_rows, dual_rhs, d)
    check(bool(dual_points), 'Missing dual vertices')

    @lru_cache(None)
    def value(capacity):
        rows = list(matrix) + [tuple(-int(j == k) for j in range(m)) for k in range(m)]
        rhs = tuple(capacity) + (0,)*m
        points = vertices(rows, rhs, m)
        check(bool(points), 'Missing primal vertices')
        answer = max(dot(prices, x) for x in points)
        dual_answer = min(dot(capacity, w) for w in dual_points)
        check(answer == dual_answer, 'Primal-dual mismatch')
        return answer
    return value


def aggregate(bundles, members=None):
    if members is None:
        members = range(len(bundles))
    members = tuple(members)
    return tuple(sum(bundles[i][e] for i in members) for e in range(len(bundles[0])))


def marginals(value, bundles):
    c = aggregate(bundles)
    t = value(c)
    return tuple(t-value(tuple(c[e]-b[e] for e in range(len(c)))) for b in bundles)


def run():
    records = []
    for name, matrix, prices in [
        ('two_overlapping_activities', ((1,0),(1,1),(0,1)), (2,1)),
        ('weighted_triangle', ((1,0,1),(1,1,0),(0,1,1)), (3,2,1)),
    ]:
        value = oracle(matrix, prices)
        d, n = len(matrix), 3
        r = max(sum(row[j] > 0 for row in matrix) for j in range(len(prices)))
        profiles = coalitions = unilateral_pairs = 0
        for flat in product((0,1), repeat=n*d):
            bundles = tuple(tuple(flat[i*d:(i+1)*d]) for i in range(n))
            t = value(aggregate(bundles)); u = marginals(value, bundles)
            check(all(x >= 0 for x in u), 'Negative payment')
            check(sum(u) <= min(n,r)*t, 'Sparse budget bound failed')
            for mask in range(1 << n):
                members = tuple(i for i in range(n) if mask >> i & 1)
                check(sum(u[i] for i in members) >= value(aggregate(bundles,members)), 'Coverage failed')
                coalitions += 1
            for i, own in enumerate(bundles):
                for low in product(*(range(x+1) for x in own)):
                    if low == own:
                        continue
                    changed = bundles[:i] + (low,) + bundles[i+1:]
                    check(marginals(value, changed)[i] <= u[i], 'Individual monotonicity failed')
                    unilateral_pairs += 1
            profiles += 1
        records.append(dict(model=name,profiles=profiles,coalition_checks=coalitions,
                            unilateral_report_pairs=unilateral_pairs,arity=r,
                            primal_dual_values=value.cache_info().currsize))

    # Mechanism-specific dual-price failure, away from ties.
    def production(rows):
        return min(aggregate(rows))
    def dual_payment(rows):
        totals=aggregate(rows); chosen=0 if totals[0] <= totals[1] else 1
        return tuple(row[chosen] for row in rows)
    truthful=((Q(2),Q(0)),(Q(1),Q(0)),(Q(0),Q(2)))
    withheld=((Q(1,2),Q(0)),truthful[1],truthful[2])
    for rows in (truthful,withheld):
        pay=dual_payment(rows)
        check(sum(pay)==production(rows),'Dual allocation not efficient')
        for mask in range(8):
            members=tuple(i for i in range(3) if mask >> i & 1)
            check(sum(pay[i] for i in members)>=min(aggregate(rows,members)),'Dual coverage failed')
    check(dual_payment(withheld)[0]-dual_payment(truthful)[0]==Q(1,2),'Wrong withholding gain')
    records.append(dict(model='dual_price_withholding',true_output='2',withheld_output='3/2',owner_gain='1/2'))

    # Coordinated withholding can improve a coalition although own monotonicity holds.
    value=lambda c: min(c)
    bundles=((1,0),(1,0),(0,1)); hidden=((0,0),bundles[1],bundles[2])
    check(marginals(value,bundles)==(0,0,1),'Wrong true marginal vector')
    check(marginals(value,hidden)==(0,1,1),'Wrong coalition-deviation vector')
    records.append(dict(model='group_withholding',true_payments=[0,0,1],deviation_payments=[0,1,1]))

    # This rule attains rT, but that is NOT an optimal-mechanism lower bound.
    for r in range(1,8):
        owners=tuple(tuple(int(i==e) for e in range(r)) for i in range(r))
        check(sum(marginals(value,owners))==r,'Rule-specific sharpness failed')
    records.append(dict(model='rule_specific_sharpness',arities=list(range(1,8))))

    # Shared unowned cap is a different coalition game and destroys the guarantee.
    for n in range(2,9):
        grand=Q(1); u=(Q(0),)*n
        check(sum(u)<grand and u[0]<1,'Expected invalid-model coverage failure absent')
        check(n*Q(1)==n*grand,'Shared-cap static factor incorrect')
    records.append(dict(model='shared_public_cap_obstruction',owner_counts=list(range(2,9))))
    print(json.dumps(dict(status='pass',scope='Exact bounded examples; universal claims use the written proof.',records=records),indent=2))

if __name__=='__main__':
    run()

"""Exact finite falsification probe; not a continuum proof.

Candidate y_i=(F(2*c_i+c_-i)-F(c_-i))/2 for unit bipartite production.
Integer min-cut enumeration makes every reported discrepancy exact.
"""
import json
import random
from pathlib import Path


def value(capacities, left, edges):
    best = sum(capacities[:left])
    for selected in range(1 << left):
        neighbors = {v for u, v in edges if selected >> u & 1}
        cut = sum(capacities[u] for u in range(left) if not selected >> u & 1)
        cut += sum(capacities[v] for v in neighbors)
        best = min(best, cut)
    return best


def main():
    rng = random.Random(1162026)
    worst = (0, 1)
    checked = 0
    for trial in range(20000):
        left, right, owners = rng.randint(1, 5), rng.randint(1, 5), rng.randint(2, 6)
        size = left + right
        edges = [(u, left+v) for u in range(left) for v in range(right) if rng.random() < 0.4]
        rows = [[rng.choice([0, 0, 0, 1, 2, 3]) for _ in range(size)] for _ in range(owners)]
        full = [sum(row[j] for row in rows) for j in range(size)]
        f = value(full, left, edges)
        if not f:
            continue
        y2 = []
        for row in rows:
            others = [full[j]-row[j] for j in range(size)]
            increased = [full[j]+row[j] for j in range(size)]
            y2.append(value(increased, left, edges)-value(others, left, edges))
        if sum(y2)*worst[1] > worst[0]*2*f:
            worst = (sum(y2), 2*f)
        for subset in range(1, 1 << owners):
            aggregate = [sum(rows[i][j] for i in range(owners) if subset >> i & 1) for j in range(size)]
            rhs2 = 2*value(aggregate, left, edges)
            lhs2 = sum(y2[i] for i in range(owners) if subset >> i & 1)
            checked += 1
            if lhs2 < rhs2:
                result = dict(status="COVERAGE_COUNTEREXAMPLE", trial=trial, left=left,
                              edges=edges, owners=rows, payment_numerators=y2,
                              payment_denominator=2, coalition=subset,
                              coalition_payment_numerator=lhs2, coalition_value_numerator=rhs2,
                              full_value=f, checked=checked)
                Path(__file__).with_suffix('.json').write_text(json.dumps(result, indent=2)+'\n')
                print(json.dumps(result))
                return
    result = dict(status="NO_COUNTEREXAMPLE_IN_FINITE_PROBE", checked=checked,
                  worst_ratio_numerator=worst[0], worst_ratio_denominator=worst[1])
    Path(__file__).with_suffix('.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

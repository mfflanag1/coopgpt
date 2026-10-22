#!/usr/bin/env python3
"""Exact diagnostics for the all-real threshold theorem; no external packages."""
from fractions import Fraction as Q
from itertools import combinations, product
from pathlib import Path
import json


def output(totals, rows):
    return min(sum(totals[r] for r in row) for row in rows)


def payments(profile, rows):
    d = len(profile[0])
    totals = [sum(owner[r] for owner in profile) for r in range(d)]
    tau = min(max(totals[r] for r in row) for row in rows)
    paid = tuple(sum(min(Q(owner[r]), tau * Q(owner[r], totals[r]))
                     if totals[r] else Q(0) for r in range(d))
                 for owner in profile)
    return paid, totals, tau


def run_grid(name, n, d, rows, levels):
    rows = tuple(tuple(row) for row in rows)
    beta = d - min(map(len, rows)) + 1
    cache = {}
    stats = dict(name=name, owners=n, resources=d, rows=len(rows),
                 profiles=0, coalitions=0, own_edges=0, factor=beta,
                 max_rule_ratio=Q(0))
    for flat in product(levels, repeat=n*d):
        profile = [flat[i*d:(i+1)*d] for i in range(n)]
        paid, totals, tau = payments(profile, rows)
        full = output(totals, rows)
        assert all(x >= 0 for x in paid)
        assert sum(paid) == sum(min(x, tau) for x in totals)
        assert tau <= full
        assert sum(paid) <= beta * full
        assert bool(tau) == bool(full)
        if full:
            stats['max_rule_ratio'] = max(stats['max_rule_ratio'], sum(paid)/full)
        for mask in range(1 << n):
            sub = [sum(profile[i][r] for i in range(n) if mask >> i & 1)
                   for r in range(d)]
            assert sum(paid[i] for i in range(n) if mask >> i & 1) >= output(sub, rows)
            stats['coalitions'] += 1
        cache[flat] = paid
        stats['profiles'] += 1
    level_next = dict(zip(levels, levels[1:]))
    for flat, paid in cache.items():
        for coordinate, value in enumerate(flat):
            if value in level_next:
                high = list(flat)
                high[coordinate] = level_next[value]
                assert cache[tuple(high)][coordinate // d] >= paid[coordinate // d]
                stats['own_edges'] += 1
    stats['max_rule_ratio'] = str(stats['max_rule_ratio'])
    return stats


def main():
    cases = [
        run_grid('uniform_2_of_3', 2, 3, combinations(range(3), 2), (0, 1, 2)),
        run_grid('uniform_3_of_4', 3, 4, combinations(range(4), 3), (0, 1)),
        run_grid('nonmatroid_two_pools', 3, 4, ((0, 1), (2, 3)), (0, 1)),
        run_grid('unequal_row_sizes', 2, 4, ((0,), (1, 2, 3)), (0, 1, 2)),
    ]
    totals = [Q(1), Q(1), Q(0), Q(3, 2)]
    rows = ((0, 1), (2, 3))
    assert min(rows, key=lambda row: max(totals[r] for r in row)) == rows[0]
    assert min(rows, key=lambda row: sum(totals[r] for r in row)) == rows[1]
    sharp = []
    for d in range(1, 13):
        for k in range(1, d+1):
            # Each resource has a different actual owner in this diagnostic.
            totals = [0]*(k-1) + [1]*(d-k+1)
            profile = [tuple(totals[i] if i == r else 0 for r in range(d))
                       for i in range(d)]
            rows = tuple(combinations(range(d), k))
            paid, _, tau = payments(profile, rows)
            assert tau == output(totals, rows) == 1
            assert sum(paid) == d-k+1
            sharp.append((d, k))
    result = {'status': 'PASS', 'arithmetic': 'stdlib Fraction', 'cases': cases,
              'different_bottleneck_and_sum_rows': True,
              'sharp_rule_examples': len(sharp),
              'scope': 'Finite diagnostics; the independent all-real proof is in composition_threshold_mechanism.txt.'}
    destination = Path(__file__).with_name('composition_threshold_check_results.json')
    destination.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

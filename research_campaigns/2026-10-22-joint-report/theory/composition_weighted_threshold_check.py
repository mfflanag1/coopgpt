#!/usr/bin/env python3
"""Fraction checks for weighted caps, grand-marginal comparison and group monotonicity."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json


def value(x, rows):
    return min(sum(a*b for a, b in zip(row, x)) for row in rows)


def evaluate(profile, rows):
    d = len(rows[0])
    B = tuple(sum(owner[r] for owner in profile) for r in range(d))
    w = tuple(max(row[r] for row in rows) for r in range(d))
    T = value(B, rows)
    tau = min(max(a*b for a, b in zip(row, B)) for row in rows)
    def capped(threshold):
        return tuple(sum(min(w[r]*owner[r], threshold*Q(owner[r], B[r]))
                         if B[r] else Q(0) for r in range(d)) for owner in profile)
    X, Y = capped(tau), capped(T)
    U = tuple(T-value(tuple(B[r]-owner[r] for r in range(d)), rows)
              for owner in profile)
    effective = sum(z > 0 for z in w)
    kappa = min(sum(a/z for a, z in zip(row, w) if z) for row in rows)
    beta = min(Q(effective), 1+effective-kappa)
    return X, Y, U, B, T, tau, w, beta, kappa


def grid(name, n, d, rows, levels):
    rows = tuple(tuple(map(Q, row)) for row in rows)
    cache = {}
    stats = dict(name=name, profiles=0, coalition_checks=0,
                 own_edges=0, group_coordinate_edges=0,
                 max_X_ratio=Q(0), max_Y_ratio=Q(0), max_U_ratio=Q(0))
    for flat in product(levels, repeat=n*d):
        profile = tuple(flat[i*d:(i+1)*d] for i in range(n))
        X, Y, U, B, T, tau, w, beta, kappa = evaluate(profile, rows)
        assert tau <= T
        assert sum(X) == sum(min(z*b, tau) for z,b in zip(w,B))
        assert sum(Y) == sum(min(z*b, T) for z,b in zip(w,B))
        assert all(0 <= x <= y and 0 <= u <= y for x,y,u in zip(X,Y,U))
        assert max(sum(X),sum(Y),sum(U)) <= beta*T
        for mask in range(1 << n):
            coalition = tuple(i for i in range(n) if mask >> i & 1)
            sub = tuple(sum(profile[i][r] for i in coalition) for r in range(d))
            required = value(sub, rows)
            for paid in (X,Y,U):
                assert sum(paid[i] for i in coalition) >= required
                stats['coalition_checks'] += 1
            # Exact coalition aggregation identity (including empty coalition).
            for paid, threshold in ((X,tau),(Y,T)):
                aggregated = sum(min(w[r]*sub[r],threshold*Q(sub[r],B[r]))
                                 if B[r] else Q(0) for r in range(d))
                assert sum(paid[i] for i in coalition) == aggregated
        if T:
            for label,paid in (('X',X),('Y',Y),('U',U)):
                key = 'max_'+label+'_ratio'
                stats[key] = max(stats[key],sum(paid)/T)
        cache[flat] = (X,Y,U)
        stats['profiles'] += 1
    successor = dict(zip(levels,levels[1:]))
    for flat, lower in cache.items():
        for r, z in enumerate(flat):
            if z not in successor:
                continue
            higher_flat = list(flat)
            higher_flat[r] = successor[z]
            higher = cache[tuple(higher_flat)]
            owner = r//d
            for low,high in zip(lower,higher):
                assert low[owner] <= high[owner]
                stats['own_edges'] += 1
            for mask in range(1 << n):
                if mask >> owner & 1:
                    for low,high in zip(lower[:2],higher[:2]):
                        assert sum(low[i] for i in range(n) if mask >> i & 1) <= sum(high[i] for i in range(n) if mask >> i & 1)
                        stats['group_coordinate_edges'] += 1
    stats['beta'],stats['kappa'] = str(beta),str(kappa)
    for key in ('max_X_ratio','max_Y_ratio','max_U_ratio'):
        stats[key] = str(stats[key])
    return stats


def main():
    cases = [
        grid('unequal_positive',2,3,((1,Q(1,2),2),(Q(1,3),1,2),(1,1,Q(3,2))),(0,1,2)),
        grid('zero_entries',2,3,((1,0,2),(0,3,Q(1,2)),(Q(1,2),1,0)),(0,1,2)),
        grid('irrelevant_resource',2,4,((1,0,2,0),(0,3,1,0)),(0,1)),
        grid('dense_weighted',3,3,((1,1,Q(3,4)),(1,Q(3,4),1),(Q(3,4),1,1)),(0,1)),
    ]
    rows = ((Q(1),Q(0)),(Q(0),Q(1)))
    low = evaluate(((2,0),(0,1)),rows)
    high = evaluate(((2,0),(1,1)),rows)
    assert low[4] == high[4] == 1
    assert sum(low[2]) == 2 and sum(high[2]) == 1
    assert sum(low[0]) == sum(high[0]) == 2
    # Neither the bottleneck rule nor grand marginals dominate the other.
    rows = tuple(tuple(map(Q,row)) for row in ((1,1,0,0),(0,0,1,1)))
    p = ((1,0,0,0),(0,1,0,0),(0,0,0,0),(0,0,0,Q(3,2)))
    X,_,U,*_ = evaluate(p,rows)
    assert X == (1,1,0,1) and U == (Q(1,2),Q(1,2),0,Q(3,2))
    result = {'status':'PASS','arithmetic':'stdlib Fraction','cases':cases,
              'grand_marginal_group_monotonicity_counterexample':True,
              'bottleneck_and_grand_marginal_incomparable':True,
              'scope':'Complete finite diagnostics; all-real statements proved separately.'}
    Path(__file__).with_name('composition_weighted_threshold_check_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()

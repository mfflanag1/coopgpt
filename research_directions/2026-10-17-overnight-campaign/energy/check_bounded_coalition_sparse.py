"""Exact Fraction checks for bounded-coalition sparse-production payments."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import json
import random


def coalition_values(bundles, production):
    n, d = len(bundles), len(bundles[0])
    capacity = [[Q(0)] * d for _ in range(1 << n)]
    values = [Q(0)] * (1 << n)
    for mask in range(1, 1 << n):
        bit = mask & -mask
        owner = bit.bit_length() - 1
        previous = mask ^ bit
        capacity[mask] = [capacity[previous][j] + bundles[owner][j] for j in range(d)]
        values[mask] = production(capacity[mask])
    return values


def marginal_payments(values, n, p):
    if p == 1:
        return [values[-1] - values[((1 << n) - 1) ^ (1 << i)] for i in range(n)]
    weights = [p ** k * (1 - p) ** (n - 1 - k) for k in range(n)]
    return [sum((weights[mask.bit_count()] * (values[mask | (1 << i)] - values[mask])
                 for mask in range(1 << n) if not mask & (1 << i)), Q(0))
            for i in range(n)]


def coefficient(mask, coalition, n, p):
    size = coalition.bit_count()
    if mask == 0:
        return -size * (1 - p) ** (n - 1)
    if mask == (1 << n) - 1:
        return size * p ** (n - 1)
    k = mask.bit_count()
    return p ** (k - 1) * (1 - p) ** (n - k - 1) * ((mask & coalition).bit_count() - p * size)


def payment_sum(payments, coalition):
    return sum((x for i, x in enumerate(payments) if coalition & (1 << i)), Q(0))


def main():
    rng = random.Random(20261017)
    catalog = [
        ("linear", 3, 1, lambda c: c[0] + 2*c[1] + 3*c[2]),
        ("single_triple", 3, 3, lambda c: min(c)),
        ("common_cap", 5, 3, lambda c: min(c[0], min(c[1],c[2]) + min(c[3],c[4]))),
        ("weighted_common_cap", 5, 3, lambda c: min(c[0], 2*min(c[1],c[2]) + 3*min(c[3],c[4]))),
        ("path_four", 4, 2, lambda c: min(c[0]+c[2], c[1]+c[2], c[1]+c[3])),
    ]
    profiles = coverage = outside = coefficient_checks = thinning = boundary = 0
    for name, dimension, arity, production in catalog:
        for trial in range(36):
            n = 1 + trial % 6
            b = [[Q(rng.randrange(5), rng.randrange(1,4)) for _ in range(dimension)] for _ in range(n)]
            if trial % 9 == 0:
                b = [[Q(0)] * dimension for _ in range(n)]
            elif trial % 9 == 1:
                for row in b:
                    row[0] = 0
            values = coalition_values(b, production)
            all_owners = (1 << n) - 1
            for s in range(1, 5):
                p = Q(1, s)
                unscaled = marginal_payments(values, n, p)
                payments = [x * p ** (1 - arity) for x in unscaled]
                assert all(x >= 0 for x in payments)
                assert sum(payments) <= arity * s ** (arity - 1) * values[-1]
                for coalition in range(1 << n):
                    assert payment_sum(payments, coalition) >= values[coalition]
                    coverage += 1
                    # Every coalition's p-thinning value dominates p^r times worth.
                    submask = coalition
                    expectation = Q(0)
                    while True:
                        expectation += (p ** submask.bit_count() *
                                        (1-p) ** (coalition.bit_count()-submask.bit_count()) * values[submask])
                        if not submask:
                            break
                        submask = (submask - 1) & coalition
                    assert expectation >= p ** arity * values[coalition]
                    thinning += 1
                    if s >= 2:
                        expanded = sum((coefficient(mask, coalition, n, p) * values[mask]
                                        for mask in range(1 << n)), Q(0))
                        assert expanded == payment_sum(unscaled, coalition)
                        if coalition.bit_count() <= s:
                            for mask in range(1 << n):
                                if mask & coalition:
                                    assert coefficient(mask, coalition, n, p) >= 0
                                    coefficient_checks += 1
                allowed = [mask for mask in range(1, 1 << n) if mask.bit_count() <= s]
                selected = allowed if len(allowed) <= 4 else rng.sample(allowed, 4)
                for coalition in selected:
                    withheld = [[b[i][j] * Q(rng.randrange(5), 4) if coalition & (1 << i) else Q(0)
                                 for j in range(dimension)] for i in range(n)]
                    low = [[b[i][j]-withheld[i][j] for j in range(dimension)] for i in range(n)]
                    low_values = coalition_values(low, production)
                    low_payments = [x*p**(1-arity) for x in marginal_payments(low_values,n,p)]
                    outside_worth = production([sum(withheld[i][j] for i in range(n)) for j in range(dimension)])
                    assert payment_sum(payments,coalition)-payment_sum(low_payments,coalition) >= outside_worth
                    outside += 1
                    if values[-1] == 0 or low_values[-1] == 0:
                        boundary += 1
                profiles += 1

    # Exact failure when the binomial parameter exceeds the coalition threshold.
    thresholds = []
    for s in range(2, 9):
        n = s + 1
        p = (Q(1,s) + 1)/2
        high = [Q(0)] * (1 << n)
        low = [Q(0)] * (1 << n)
        for mask in range(1 << n):
            center = bool(mask & 1)
            leaves = (mask >> 1).bit_count()
            high[mask] = Q(center and leaves > 0)
            low[mask] = Q(center and ((mask >> 2).bit_count() > 0))
        S = ((1 << n)-1) ^ 1
        diff = payment_sum(marginal_payments(high,n,p),S)-payment_sum(marginal_payments(low,n,p),S)
        exact = p*(1-p)**(s-2)*(1-s*p)
        assert diff == exact < 0
        thresholds.append({"s":s,"p":str(p),"payment_change":str(diff)})

    result = {"status":"PASS","arithmetic":"fractions.Fraction, exact",
              "profile_parameter_pairs":profiles,"coalition_coverage_checks":coverage,
              "thinning_checks":thinning,"affected_coefficient_nonnegativity":coefficient_checks,
              "full_outside_deviations":outside,"zero_production_boundaries":boundary,
              "sharp_binomial_threshold_counterexamples":thresholds,
              "scope":"Finite checks corroborate the general analytic proof; they do not establish novelty or optimal funding."}
    Path(__file__).with_name("bounded_coalition_sparse_checks.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Exact checks of the star reduction, separate from the analytic proof."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json
import random

from waterfill_rule import rule


def require(ok, message):
    if not ok:
        raise ArithmeticError(message)


def production(profile, values, energy, subset):
    """Independent greedy fractional-knapsack evaluation, without layer sums."""
    q = sum((profile[i][-1] for i in subset), Q())
    result = Q()
    for j in sorted(range(len(values)), key=lambda j: values[j] / energy[j], reverse=True):
        capacity = sum((profile[i][j] for i in subset), Q())
        units = min(capacity, q / energy[j])
        result += values[j] * units
        q -= energy[j] * units
    return result


def mechanism(profile, values, energy):
    order = sorted(range(len(values)), key=lambda j: values[j] / energy[j], reverse=True)
    ratios = [values[j] / energy[j] for j in order] + [Q()]
    prefix = [Q() for _ in profile]
    payments = [Q() for _ in profile]
    for k, j in enumerate(order):
        for i in range(len(profile)):
            prefix[i] += energy[j] * profile[i][j]
        component = rule([(prefix[i], profile[i][-1]) for i in range(len(profile))])
        for i in range(len(profile)):
            payments[i] += (ratios[k] - ratios[k + 1]) * component[i]
    return payments


def layer_value(profile, values, energy, subset):
    order = sorted(range(len(values)), key=lambda j: values[j] / energy[j], reverse=True)
    ratios = [values[j] / energy[j] for j in order] + [Q()]
    q = sum((profile[i][-1] for i in subset), Q())
    prefix = Q()
    value = Q()
    for k, j in enumerate(order):
        prefix += energy[j] * sum((profile[i][j] for i in subset), Q())
        value += (ratios[k] - ratios[k + 1]) * min(q, prefix)
    return value


def main():
    rng = random.Random(202610163127)
    counts = dict(profiles=0, coalition_checks=0, coordinate_increases=0, bundle_increases=0)
    max_ratio = Q(1)
    for trial in range(420):
        n, m = 1 + trial % 6, 1 + trial % 7
        energy = [Q(rng.randint(1, 8), rng.randint(1, 5)) for _ in range(m)]
        # Repeated values/energy ratios deliberately include public ties.
        ratios = [Q(rng.randint(1, 5), rng.randint(1, 3)) for _ in range(m)]
        values = [e * a for e, a in zip(energy, ratios)]
        profile = [[Q(rng.randint(0, 8), rng.randint(1, 5)) for _ in range(m + 1)] for _ in range(n)]
        if trial % 19 == 0:
            for row in profile:
                row[-1] = Q()
        if trial % 23 == 0:
            for row in profile:
                for j in range(m):
                    row[j] = Q()
        payments = mechanism(profile, values, energy)
        full = production(profile, values, energy, range(n))
        require(all(y >= 0 for y in payments), 'negative payment')
        require(sum(payments) <= Q(31, 27) * full, 'budget violation')
        if full:
            max_ratio = max(max_ratio, sum(payments) / full)
        for flags in product((0, 1), repeat=n):
            subset = [i for i, flag in enumerate(flags) if flag]
            actual = production(profile, values, energy, subset)
            require(actual == layer_value(profile, values, energy, subset), 'decomposition identity failed')
            require(sum(payments[i] for i in subset) >= actual, 'coalition violation')
            counts['coalition_checks'] += 1
        for i in range(n):
            for j in range(m + 1):
                changed = [list(row) for row in profile]
                changed[i][j] += Q(rng.randint(1, 5), rng.randint(1, 7))
                require(mechanism(changed, values, energy)[i] >= payments[i], 'coordinate monotonicity failed')
                counts['coordinate_increases'] += 1
            changed = [list(row) for row in profile]
            for j in range(m + 1):
                changed[i][j] += Q(rng.randint(0, 5), rng.randint(1, 7))
            require(mechanism(changed, values, energy)[i] >= payments[i], 'bundle monotonicity failed')
            counts['bundle_increases'] += 1
        counts['profiles'] += 1
    # Unit star embeds the exact component extremizer.
    sharp = [[Q(1), Q(0)], [Q(0), Q(1)], [Q(0), Q(1)]]
    require(sum(mechanism(sharp, [Q(1)], [Q(1)])) == Q(31, 27), 'sharp component embedding failed')
    out = dict(status='EXACT PASS', **counts, stress_max_ratio=str(max_ratio),
               embedded_sharp_ratio='31/27',
               scope='Finite corroboration of reduction and implementation; continuous theorem uses the analytic proof.')
    Path(__file__).with_name('heterogeneous_star_verification.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out))


if __name__ == '__main__':
    main()

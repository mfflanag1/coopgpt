#!/usr/bin/env python3
"""Exact rational finite-rule checks, independent of the continuous constant."""
from fractions import Fraction as Q
import json
import random
from pathlib import Path


def rule(tau, count):
    gamma = 1 / (1 + tau)
    nodes = [tau * j / count for j in range(1, count + 1)]
    weights = [gamma * tau / count / (1 - u) for u in nodes]
    total = sum(weights, Q())
    moment = sum((w * u for w, u in zip(weights, nodes)), Q())
    assert total >= 1
    assert moment == gamma + total - 1
    return nodes, weights, total, moment


def value(rows, x):
    return min(sum((a * b for a, b in zip(row, x)), Q()) for row in rows)


def prices(rows, x, nodes, weights):
    out = []
    for j, amount in enumerate(x):
        if not amount:
            out.append(Q())
            continue
        h = sum((w * value(rows, [z if k == j else u * z for k, z in enumerate(x)])
                 for u, w in zip(nodes, weights)), Q())
        out.append(h / amount)
    return out


def dot(a, b):
    return sum((x * y for x, y in zip(a, b)), Q())


def main():
    examples = []
    for tau, count in [(Q(421, 500), 100), (Q(84141, 100000), 1000),
                       (Q(9, 10), 10), (Q(7, 8), 20)]:
        nodes, weights, total, moment = rule(tau, count)
        examples.append(dict(tau=str(tau), nodes=count, exact_W_ge_1=True,
                             display_W=float(total), display_M=float(moment),
                             W_numerator_bits=total.numerator.bit_length(),
                             W_denominator_bits=total.denominator.bit_length()))
    nodes, weights, total, moment = rule(Q(7, 8), 20)
    rng = random.Random(771525)
    counts = dict(profiles=0, finite_deviations=0, floors=0, boundaries=0,
                  rational_scalar_hinges=0)
    for _ in range(240):
        dim = rng.randint(2, 5)
        rows = [[Q(rng.choice([0, 0, 1, 2, 4])) for _ in range(dim)]
                for _ in range(rng.randint(1, 5))]
        owners = [[Q(rng.choice([0, 0, 1, 2, 3])) for _ in range(dim)]
                  for _ in range(rng.randint(2, 6))]
        high = [sum((b[j] for b in owners), Q()) for j in range(dim)]
        ph = prices(rows, high, nodes, weights)
        active = sum(z > 0 for z in high)
        budget = (total + moment * (active - 1)) * value(rows, high) if active else Q()
        assert dot(high, ph) <= budget
        for owner in owners:
            marginal = value(rows, high) - value(rows, [a - b for a, b in zip(high, owner)])
            assert dot(owner, ph) >= moment * marginal
            counts['floors'] += 1
        for _ in range(3):
            selected = [i for i in range(len(owners)) if rng.randrange(2)]
            held = [sum((owners[i][j] for i in selected), Q()) for j in range(dim)]
            removed = [sum((owners[i][j] * rng.choice([Q(), Q(1, 2), Q(1)])
                            for i in selected), Q()) for j in range(dim)]
            low = [a - b for a, b in zip(high, removed)]
            retained = [a - b for a, b in zip(held, removed)]
            pl = prices(rows, low, nodes, weights)
            assert dot(held, ph) >= dot(retained, pl) + value(rows, removed)
            assert dot(held, ph) >= value(rows, held)
            counts['finite_deviations'] += 1
            counts['boundaries'] += int(any(z == 0 for z in high + low))
        counts['profiles'] += 1
    tau = Q(7, 8)
    for ti in range(1, 101):
        t = tau * ti / 100
        for si in range(1, 101):
            s = Q(si, 100)
            integral = s * max(tau - s, Q())
            assert integral + t * s >= tau * min(t, s)
            counts['rational_scalar_hinges'] += 1
    result = dict(status='PASS', arithmetic='exact fractions throughout all assertions',
                  counts=counts, examples=examples)
    Path(__file__).with_name('finite_logarithmic_face_checks.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

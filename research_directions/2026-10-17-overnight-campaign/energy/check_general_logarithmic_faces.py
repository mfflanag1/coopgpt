#!/usr/bin/env python3
"""Floating challenge checks; analytic segment integrals, no quadrature.

F(x)=min_r row_r.x. Break every face at every affine-row crossing. The
minimum row is then fixed within each segment. Tests use actual owner
bundles and arbitrary withholding, plus every derivative holding corner.
This is a diagnostic, not an exact proof of transcendental statements.
"""
import itertools
import json
import math
import random
from pathlib import Path


def constant():
    lo, hi = 0.5, 1.0
    for _ in range(90):
        mid = (lo + hi) / 2
        if mid * (2 - math.exp(-1 / mid)) < 1:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


C = constant()
T0 = 1 / C - 1


def value(rows, x):
    return min(sum(a * b for a, b in zip(row, x)) for row in rows)


def face(rows, x, j, direction=None):
    lines = [(row[j] * x[j], sum(row[k] * x[k] for k in range(len(x)) if k != j))
             for row in rows]
    cuts = [0.0, T0]
    for (a, b), (aa, bb) in itertools.combinations(lines, 2):
        if b != bb:
            root = (aa - a) / (b - bb)
            if 0 < root < T0:
                cuts.append(root)
    cuts = sorted(set(cuts))
    total = derivative = 0.0
    for lo, hi in zip(cuts, cuts[1:]):
        mid = (lo + hi) / 2
        active = min(range(len(rows)), key=lambda r: lines[r][0] + mid * lines[r][1])
        a, b = lines[active]
        mass = C * math.log((1 - lo) / (1 - hi))
        first = mass - C * (hi - lo)
        total += a * mass + b * first
        if direction is not None:
            row = rows[active]
            derivative += row[j] * direction[j] * mass
            derivative += sum(row[k] * direction[k] for k in range(len(x)) if k != j) * first
    return total, derivative


def prices(rows, x):
    return [face(rows, x, j)[0] / z if z > 0 else 0.0 for j, z in enumerate(x)]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def main():
    rng = random.Random(527011)
    counts = dict(profiles=0, derivative_corners=0, finite_deviations=0,
                  scalar_hinges=0, boundary_profiles=0)
    worst = dict(funding_gap=0.0, derivative_gap=0.0, finite_gap=0.0,
                 scalar_gap=0.0, coverage_gap=0.0)
    technologies = [
        [[1, 0], [0, 1]],
        [[1, 0, 1, 0], [0, 1, 0, 1], [0, 1, 1, 0]],
        [[1, 1, 0, 0], [1, 0, 1, 0], [0, 1, 1, 1], [.5, .5, .5, .5]],
        [[1, 2, 3, 4]],
        [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        [[0, 0], [1, 1]],
    ]
    for _ in range(140):
        dim = rng.randint(2, 7)
        technologies.append([[rng.choice([0, 0, .125, .5, 1, 2, 8])
                              for _ in range(dim)] for _ in range(rng.randint(1, 9))])
    for rows in technologies:
        dim = len(rows[0])
        for trial in range(16):
            x = [10 ** rng.uniform(-1.5, 1.5) for _ in range(dim)]
            direction = [10 ** rng.uniform(-1.5, 1.5) for _ in range(dim)]
            hv = [face(rows, x, j, direction) for j in range(dim)]
            av = [hv[j][0] * direction[j] / x[j] for j in range(dim)]
            bv = [item[1] for item in hv]
            fd = value(rows, direction)
            scale = max(1.0, fd, sum(av), sum(bv))
            for bits in itertools.product((0, 1), repeat=dim):
                gap = sum(bv[j] if bits[j] else av[j] for j in range(dim)) - fd
                worst['derivative_gap'] = min(worst['derivative_gap'], gap / scale)
                assert gap >= -1e-10 * scale, (rows, x, direction, bits, gap)
                counts['derivative_corners'] += 1
            fx = value(rows, x)
            funding_gap = (1 + C * (dim - 1)) * fx - sum(h for h, _ in hv)
            worst['funding_gap'] = min(worst['funding_gap'], funding_gap / max(1, fx))
            assert funding_gap >= -1e-10 * max(1, fx)
            counts['profiles'] += 1
            for _ in range(4):
                owners = [[rng.choice([0, 0, 1, 2, 4, 8]) for _ in range(dim)]
                          for _ in range(rng.randint(2, 7))]
                coalition = [i for i in range(len(owners)) if rng.randrange(2)]
                high = [sum(b[j] for b in owners) for j in range(dim)]
                held = [sum(owners[i][j] for i in coalition) for j in range(dim)]
                withheld = [sum(owners[i][j] * rng.choice([0, .25, .5, 1])
                                for i in coalition) for j in range(dim)]
                low = [a - b for a, b in zip(high, withheld)]
                retained = [a - b for a, b in zip(held, withheld)]
                ph, pl = prices(rows, high), prices(rows, low)
                yy, zz = dot(held, ph), dot(retained, pl)
                outside = value(rows, withheld)
                gap = yy - zz - outside
                scale = max(1, yy, zz, outside)
                worst['finite_gap'] = min(worst['finite_gap'], gap / scale)
                assert gap >= -1e-10 * scale, (rows, owners, coalition, withheld, gap)
                covergap = yy - value(rows, held)
                worst['coverage_gap'] = min(worst['coverage_gap'], covergap / scale)
                assert covergap >= -1e-10 * scale
                active = sum(z > 0 for z in high)
                bound = (1 + C * (active - 1)) * value(rows, high) if active else 0
                assert dot(high, ph) <= bound + 1e-10 * max(1, bound)
                counts['finite_deviations'] += 1
                counts['boundary_profiles'] += int(any(z == 0 for z in high + low))
    for _ in range(30000):
        t = rng.random() * T0
        s = rng.random()
        residual = s * max(T0 - s, 0) + t * s - T0 * min(t, s)
        worst['scalar_gap'] = min(worst['scalar_gap'], residual)
        assert residual >= -1e-14
        counts['scalar_hinges'] += 1
    result = dict(status='PASS', arithmetic='floating analytic-piece integration; not a proof',
                  c=C, t0=T0, counts=counts, worst_normalized_gaps=worst)
    Path(__file__).with_name('general_logarithmic_face_checks.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

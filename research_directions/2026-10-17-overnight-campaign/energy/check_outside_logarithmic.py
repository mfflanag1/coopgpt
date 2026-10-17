"""Floating diagnostics for an analytically proved all-real mechanism.

These are not interval certificates and do not prove the transcendental root.
"""
import json
import math
import random
from pathlib import Path


def demand(condition, message):
    if not condition:
        raise RuntimeError(message)


lo, hi = .5, 1.
for _ in range(100):
    mid = (lo + hi) / 2
    if mid * (2 - math.exp(-1 / mid)) < 1:
        lo = mid
    else:
        hi = mid
C = (lo + hi) / 2
T0 = 1 - math.exp(-1 / C)


def prices(t):
    if t <= 0:
        return 0., 1., C, -C / 2
    if t >= T0:
        return C * t, C / t, C, -C / (t * t)
    if t < 1e-4:
        q = 1 - C * sum(t ** k / (k * (k + 1)) for k in range(1, 12))
        qp = -C * sum(t ** (k - 1) / (k + 1) for k in range(1, 12))
    else:
        l = math.log1p(-t)
        q = 1 - C - C * (1 - t) * l / t
        qp = C * (l + t) / (t * t)
    return C * t, q, C, qp


def payments(xs):
    a, b = map(sum, zip(*xs))
    if min(a, b) <= 0:
        return [0.] * len(xs)
    if a >= b:
        p, q, _, _ = prices(b / a)
    else:
        q, p, _, _ = prices(a / b)
    return [p * x + q * y for x, y in xs]


def main():
    rng = random.Random(20261017)
    corner_checks = 0
    worst_corner = 1.
    for t in [10 ** (-k) for k in range(1, 14)] + [T0, 1.] + [rng.random() for _ in range(10000)]:
        p, q, pp, qp = prices(t)
        demand(min(p, q) >= 0, "nonnegative prices")
        demand(p + q >= 1 - 1e-12, "coverage prices")
        demand(p / t + q <= 1 + C + 1e-12, "funding")
        for alpha in (0., 1.):
            for beta in (0., 1.):
                ga = p - alpha * t * pp - beta * t * t * qp
                gb = q + alpha * pp + beta * t * qp
                demand(min(ga, gb) >= -1e-10, "coordinate derivative")
                demand(ga + gb >= 1 - 1e-10, "balanced outside derivative")
                worst_corner = min(worst_corner, ga + gb)
                corner_checks += 1
    profiles = coalition_checks = outside_checks = floor_checks = 0
    min_outside_slack = math.inf
    for _ in range(7000):
        n = rng.randint(2, 8)
        xs = []
        for i in range(n):
            pair = [0. if rng.random() < .25 else 10 ** rng.uniform(-3, 3) for _ in range(2)]
            xs.append(tuple(pair))
        a, b = map(sum, zip(*xs))
        ys = payments(xs)
        scale = max(1., a, b)
        demand(sum(ys) <= (1 + C) * min(a, b) + 1e-10 * scale, "profile budget")
        for i, (ei, hi) in enumerate(xs):
            marginal = min(a, b) - min(a - ei, b - hi)
            demand(ys[i] >= C * marginal - 1e-10 * scale, "fractional full-owner floor")
            floor_checks += 1
        for _ in range(12):
            mask = rng.randrange(1, 1 << n)
            indices = [i for i in range(n) if mask >> i & 1]
            sa = sum(xs[i][0] for i in indices)
            sb = sum(xs[i][1] for i in indices)
            full_pay = sum(ys[i] for i in indices)
            demand(full_pay >= min(sa, sb) - 1e-10 * scale, "coalition coverage")
            coalition_checks += 1
            reduced = list(xs)
            da = db = 0.
            for i in indices:
                u, v = xs[i]
                ru = u * rng.choice([0., 1., rng.random()])
                rv = v * rng.choice([0., 1., rng.random()])
                da += u - ru
                db += v - rv
                reduced[i] = (ru, rv)
            under_ys = payments(reduced)
            slack = full_pay - sum(under_ys[i] for i in indices) - min(da, db)
            demand(slack >= -1e-10 * scale, "coalition outside-production deviation")
            min_outside_slack = min(min_outside_slack, slack)
            outside_checks += 1
        profiles += 1
    result = {
        "status": "PASS",
        "arithmetic": "floating numerical diagnostics, not exact or interval certificates",
        "c": C,
        "funding_factor": 1 + C,
        "switch_ratio": T0,
        "derivative_corner_checks": corner_checks,
        "profiles": profiles,
        "coalition_coverage_checks": coalition_checks,
        "coalition_outside_deviations": outside_checks,
        "fractional_full_owner_floor_checks": floor_checks,
        "minimum_derivative_sum": worst_corner,
        "minimum_outside_slack": min_outside_slack,
        "scope": "Analytic theorem and architecture lower are in OUTSIDE_LOGARITHMIC_PRICE_THEOREM.txt."
    }
    Path(__file__).with_name("outside_logarithmic_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Exact corroboration of the analytic concentration theorem; no tolerances."""
from fractions import Fraction as Q
from pathlib import Path
from math import ceil
import json
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from waterfill_rule import rule
from verify_heterogeneous_star import mechanism, production


def require(ok, message):
    if not ok:
        raise ArithmeticError(message)


def g(s):
    require(0 < s <= 1, 'invalid concentration')
    return Q(1, 8) if s <= Q(1, 2) else (1 + s) ** 3 / (54 * s)


def main():
    concentrations = sorted({Q(p, q) for q in range(1, 65) for p in range(1, q + 1)})
    counts = dict(extremizers=0, scalar_checks=0, random_profiles=0, no_majority_profiles=0,
                  heterogeneous_extremizers=0)
    for s in concentrations:
        n = ceil(1 / s)
        xs = [s] * (n - 1) + [1 - (n - 1) * s]
        if len(xs) < 2:
            xs.append(Q())
        require(sum(xs) == 1 and max(xs) == s, 'short construction failed')
        profile = [(x, Q(1) if i < 2 else Q()) for i, x in enumerate(xs)]
        payments, info = rule(profile, details=True)
        require(sum(payments) == 1 + g(s), 'sharp profile failed')
        require(info['p'] == g(s), 'sharp coefficient failed')
        require(info['level'] == (Q(1, 2) if s <= Q(1, 2) else (1 + s) / 3), 'sharp level failed')
        penalty = max(Q(), 2*s - 1)**2 * (s + 4) / (216*s)
        require(g(s) == Q(1, 8) + penalty, 'penalty factorization failed')
        counts['extremizers'] += 1
        for k in range(41):
            upper = min(s, (1 + s) / (k + 1))
            critical = s / 2 if k == 0 else (k + s) / (k + 2)
            for level in {Q(), upper, upper/2, min(upper, critical)}:
                excess = level**(k + 1) * (k + s - (k + 1)*level) / (2*s)
                require(excess <= g(s), 'dummy-active scalar bound failed')
                counts['scalar_checks'] += 1
            if k and s <= Q(1, k):
                upper = Q(1, k)
                critical = Q(k, k + 1)
                for level in {s, upper, max(s, min(upper, critical))}:
                    excess = Q(k, 2) * level**k * (1-level)
                    require(excess <= g(s), 'dummy-inactive scalar bound failed')
                    counts['scalar_checks'] += 1
    rng = random.Random(20261016)
    for t in range(2400):
        n = 1 + t % 19
        profile = [(Q(rng.randint(0, 12), rng.randint(1, 8)),
                    Q(rng.randint(0, 12), rng.randint(1, 8))) for _ in range(n)]
        ys, info = rule(profile, details=True)
        if info['A']:
            s = info['M'] / info['A']
            require(sum(ys) <= info['A']*(1 + g(s)), 'profilewise bound failed')
            if s <= Q(1, 2):
                require(sum(ys) <= Q(9, 8)*info['A'], 'no-majority bound failed')
                counts['no_majority_profiles'] += 1
        else:
            require(sum(ys) == 0, 'zero-output payment failed')
        counts['random_profiles'] += 1
    star = [[Q(1), Q(1), Q()], [Q(), Q(2), Q(1)], [Q(), Q(), Q(1)]]
    for theta in sorted({Q(p, q) for q in range(2, 17) for p in range(1, q)}):
        values, energy = [1+theta, 1-theta], [Q(1), Q(1)]
        require(production(star, values, energy, range(3)) == 2, 'star output failed')
        total = sum(mechanism(star, values, energy))
        require(total == 2*(Q(9, 8)+Q(5, 216)*theta), 'value-share sharpness failed')
        counts['heterogeneous_extremizers'] += 1
    out = dict(status='EXACT PASS', **counts,
               scope='Finite exact checks of concentration bounds and extremizers; all-real proof is CONCENTRATION_THEOREM.txt.')
    Path(__file__).with_name('concentration_verification.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(out))


if __name__ == '__main__':
    main()

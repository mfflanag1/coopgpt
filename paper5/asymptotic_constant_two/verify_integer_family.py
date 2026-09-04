"""Exact full-coalition checks for the three-generator extension of PXC151."""
from fractions import Fraction as F
from pathlib import Path
import json
import z3


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def zq(value):
    value = F(value)
    return z3.Q(value.numerator, value.denominator)


def generators(m, k, r):
    q = (k + 1) * m - k + 2
    a = k * m - k + 1
    y = r * (q - 1) - a
    total = r * q + m + 1
    x = [1] * m + [m - 1] * k + [y, 1] + [1] * r + [1]
    b = [0] * (m + k + 2) + [q] * r + [m + 1]
    c = [0] * m + [m + 1] * k + [total - k * (m + 1), 0] + [0] * r + [0]
    return x, b, c, q, y, total


def check(m, k, r):
    require(k >= 1 and m >= max(2, 2 * k - 2) and r >= 3, 'invalid domain')
    x, b, c, q, y, total = generators(m, k, r)
    n = len(x)
    lam = F(q, y + q - 1)
    z = [lam * xi + (1 - lam) * bi for xi, bi in zip(x, b)]
    require(sum(x) == sum(b) == sum(c) == total, 'efficiency failed')
    require(min(x) >= 1 and min(b + c) >= 0, 'generator positivity failed')
    require(all(min(column) == 0 for column in zip(x, b, c)), 'singleton normalization failed')
    require(max(z) == lam * y, 'ceiling formula failed')
    require(sum(min(F(xi), zi) for xi, zi in zip(x, z)) == q + r + 1, 'overlap failed')
    w = z3.Reals(' '.join(f'w{i}' for i in range(n)))
    solver = z3.Solver()
    solver.set(timeout=120000)
    solver.add(z3.Sum(w) == total)
    for mask in range(1, 2 ** n - 1):
        ids = [j for j in range(n) if mask >> j & 1]
        value = min(sum(row[j] for j in ids) for row in (x, b, c))
        solver.add(z3.Sum([w[j] for j in ids]) >= value)
    verdicts = {}

    def exclude(name, conditions):
        solver.push()
        solver.add(*conditions)
        verdict = solver.check()
        require(verdict == z3.unsat, f'{(m, k, r)} {name}: {verdict}')
        verdicts[name] = str(verdict)
        solver.pop()

    exclude('floor_above_one', [wi > 1 for wi in w])
    exclude('floor_face_nonunique', [wi >= 1 for wi in w] + [z3.Or(*[wi != xi for wi, xi in zip(w, x)])])
    exclude('ceiling_below_formula', [wi < zq(lam * y) for wi in w])
    exclude('ceiling_face_nonunique', [wi <= zq(lam * y) for wi in w] + [z3.Or(*[wi != zq(zi) for wi, zi in zip(w, z)])])
    result = dict(m=m, k=k, r=r, n=n, q=q, T=total, lambda_exact=str(lam), M=str(lam*y), overlap=q+r+1, full_coalitions=2**n-2, verdicts=verdicts)
    print('PASS', m, k, r, flush=True)
    return result


def negative_control():
    # This tuple violates the theorem's m >= 2k-2 condition.
    m, k, r = 3, 3, 3
    x, b, c, q, y, total = generators(m, k, r)
    witness = x.copy()
    witness[m+k] -= 1
    witness[m+k+2] += 1
    require(sum(witness) == total and min(witness) >= 0, 'invalid witness')
    for mask in range(1, 2 ** len(x) - 1):
        ids = [i for i in range(len(x)) if mask >> i & 1]
        value = min(sum(row[i] for i in ids) for row in (x, b, c))
        require(sum(witness[i] for i in ids) >= value, 'negative witness outside core')
    require(sorted(witness) > sorted(x), 'negative control did not improve leximin')
    print('PASS out-of-domain negative control', flush=True)
    return dict(m=m, k=k, r=r, claimed_Lmin=x, improved_core_point=witness, full_coalitions=2**len(x)-2)


if __name__ == '__main__':
    payload = {
        'evidence': 'Exact finite calibration; all-parameter proof separate',
        'cases': [check(*p) for p in ((2,1,3), (2,2,3), (3,2,4), (4,3,3))],
        'negative_control': negative_control(),
    }
    Path(__file__).with_name('integer_family_calibration.json').write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')

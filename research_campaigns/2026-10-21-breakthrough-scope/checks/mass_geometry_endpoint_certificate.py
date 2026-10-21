"""Exact certificate of a normalized deletion-endpoint obstruction.

Discovery uses a floating-point convex QP only to guess support. Verification
uses Python Fraction and covers every incident-row deletion choice directly.
Run --verify FILE independently without importing numpy or scipy.
"""
from fractions import Fraction as F
from pathlib import Path
import argparse
import json


def solve(a, b):
    n = len(b)
    aug = [[F(x) for x in row] + [F(y)] for row, y in zip(a, b)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if aug[r][col]), None)
        if pivot is None:
            raise ValueError('singular support')
        aug[col], aug[pivot] = aug[pivot], aug[col]
        divisor = aug[col][col]
        aug[col] = [x / divisor for x in aug[col]]
        for r in range(n):
            if r != col:
                factor = aug[r][col]
                aug[r] = [x - factor*y for x, y in zip(aug[r], aug[col])]
    return [row[-1] for row in aug]


def dot(a, b):
    return sum((x*y for x, y in zip(a, b)), F(0))


def fixture():
    n = 15
    seed = [0, 1, 2, 3, 4, 5, 7, 8]
    sets = sorted({tuple(sorted((j+s) % n for j in seed)) for s in range(n)})
    return [[int(j in row) for j in range(n)] for row in sets]


def verify_piecewise(a):
    """Exact affine KKT checks at endpoints imply them on each whole interval."""
    retained = [r for r in range(15) if r not in [0,4]]
    g = [[dot(x,y) for y in a] for x in a]
    left, peak = F(32545,33981), F(18923,19364)
    cells = [(left,peak,[r for r in retained if r != 13],
              [F(6401,272789),F(29518,272789),F(58062,272789),F(5744,272789)]),
             (peak,F(1),retained,
              [F(6537,38794),F(-1560,38794),F(8043,38794),F(1036,38794)])]
    lowest_lambda = None
    for lo,hi,support,expected in cells:
        mat = [[g[r][s] for s in support] for r in support]
        l0 = solve(mat,[int(r != 1) for r in support])
        l1 = solve(mat,[int(r == 1) for r in support])
        q0 = sum(x for r,x in zip(support,l0) if r < 8)
        q1 = sum(x for r,x in zip(support,l1) if r < 8)
        assert [q0,q1,sum(l0),sum(l1)] == expected
        for s in [lo,hi]:
            lam = [F(0)]*15
            for r,x,y in zip(support,l0,l1):
                lam[r] = x+s*y
            assert all(x >= 0 for x in lam)
            q = [sum(lam[r]*a[r][j] for r in range(15)) for j in range(15)]
            rhs = [F(0) if r in [0,4] else s if r == 1 else F(1) for r in range(15)]
            potentials = [dot(row,q) for row in a]
            assert all(x>=b for x,b in zip(potentials,rhs))
            assert all(x==b for r,(x,b) in enumerate(zip(potentials,rhs)) if lam[r])
            if s == left:
                lowest_lambda = lam
        derivative = q1*sum(l0)-q0*sum(l1)
        assert derivative > 0 if lo == left else derivative < 0
    assert lowest_lambda is not None and lowest_lambda[1] == 0
    # At and below left, row1's inactive demand only decreases; every other
    # KKT relation is unchanged, so the same projection certifies [0,left].
    return True


def verify(data):
    a = data['A']
    assert a == fixture()
    n = len(a[0])
    own = [r for r, row in enumerate(a) if row[0]]
    off = [r for r, row in enumerate(a) if not row[0]]
    assert len(own) == 8
    assert len(data['endpoints']) == 2**len(own)
    assert {entry['mask'] for entry in data['endpoints']} == set(range(2**len(own)))
    maximum = F(0)
    maximizers = []
    for entry in data['endpoints']:
        mask = entry['mask']
        retained = set(off + [r for bit, r in enumerate(own) if mask >> bit & 1])
        lam = [F(x) for x in entry['lambda']]
        assert len(lam) == len(a)
        assert all(x >= 0 for x in lam)
        assert all(not lam[r] for r in range(len(a)) if r not in retained)
        q = [sum((lam[r]*a[r][j] for r in range(len(a))), F(0)) for j in range(n)]
        potentials = [dot(row, q) for row in a]
        assert all(potentials[r] >= 1 for r in retained)
        assert all(potentials[r] == 1 for r in range(len(a)) if lam[r])
        mass = sum(lam)
        assert mass > 0 and mass == dot(q, q)
        theta = q[0] / mass
        assert theta == F(entry['theta'])
        if theta > maximum:
            maximum, maximizers = theta, [mask]
        elif theta == maximum:
            maximizers.append(mask)
    alpha = [F(x) for x in data['continuous']['alpha']]
    t = F(data['continuous']['t'])
    assert len(alpha) == len(a) and sum(alpha) == 1 and all(x >= 0 for x in alpha)
    v = [sum((alpha[r]*a[r][j] for r in range(len(a))), F(0)) for j in range(n)]
    potentials = [dot(row, v) for row in a]
    assert all(potentials[r] >= t for r in off)
    assert all(potentials[r] <= t for r in own if alpha[r])
    assert all(potentials[r] == t for r in off if alpha[r])
    theta = v[0]
    assert theta == F('1251/2260')
    assert maximum == F('711/1297')
    assert theta > maximum
    assert verify_piecewise(a)
    return {'certified': True, 'endpoint_count': len(data['endpoints']),
            'endpoint_max_theta': str(maximum), 'maximizing_masks': maximizers,
            'continuous_theta': str(theta), 'strict_gap': str(theta-maximum),
            'continuous_norm2': str(dot(v,v)/t**2), 'continuous_L': str(1/t),
            'continuous_H': str(F(225,64)*theta**2),
            'endpoint_H': str(F(225,64)*maximum**2),
            'piecewise_affine_KKT_certified': True,
            'scope': 'Exact finite obstruction to normalized deletion-endpoint reduction; not H>2 or a diagonal counterexample.'}


def discover():
    import numpy as np
    from scipy.optimize import minimize
    a = fixture()
    an = np.array(a, dtype=float)
    own = [r for r, row in enumerate(a) if row[0]]
    off = [r for r, row in enumerate(a) if not row[0]]
    g = [[dot(x,y) for y in a] for x in a]
    endpoints = []
    for mask in range(2**len(own)):
        retained = off + [r for bit, r in enumerate(own) if mask >> bit & 1]
        b = an[retained]
        gram = b @ b.T
        result = minimize(lambda x: (0.5*x @ gram @ x - x.sum(), gram @ x - 1),
                          np.full(len(retained), 1/64), jac=True,
                          method='SLSQP', bounds=[(0,None)]*len(retained),
                          options={'ftol': 1e-13, 'maxiter': 2000})
        support = [r for r,x in zip(retained,result.x) if x > 1e-7]
        exact = solve([[g[r][s] for s in support] for r in support], [1]*len(support))
        lam = [F(0)]*len(a)
        for r,x in zip(support,exact):
            lam[r] = x
        q0 = sum(lam[r] for r in own)
        endpoints.append({'mask': mask, 'lambda': [str(x) for x in lam],
                          'theta': str(q0/sum(lam))})
    return {'A': a, 'owner': 0, 'own_rows': own, 'off_rows': off,
            'row_order': 'lexicographic sorted owner subsets', 'endpoints': endpoints,
            'continuous': {'alpha': ['0','47/1130','429/4520','629/4520','0',
                '489/4520','33/452','437/4520','393/4520','129/4520','381/4520',
                '489/4520','311/4520','0','63/904'], 't': '4841/1130'}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.verify:
        data = json.loads(args.verify.read_text())
        print(json.dumps(verify(data), indent=2))
    else:
        data = discover()
        data['verified_summary'] = verify(data)
        destination = args.output or Path(__file__).with_suffix('.json')
        destination.write_text(json.dumps(data,indent=2)+'\n')
        print(json.dumps(data['verified_summary'],indent=2))

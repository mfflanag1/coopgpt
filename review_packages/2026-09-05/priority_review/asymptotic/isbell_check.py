"""Independent exact checks of the old Fibonacci-Isbell donor construction.

No package modules are imported. Finite checks corroborate the source theorem;
they do not substitute for its all-p proof. Run with Python containing Z3.
"""
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import platform

HERE = Path(__file__).resolve().parent


def fib(k):
    a, b = 0, 1
    for _ in range(k):
        a, b = b, a + b
    return a


def determinant(matrix):
    a = [[Q(x) for x in row] for row in matrix]
    d = Q(1)
    for j in range(len(a)):
        k = next((k for k in range(j, len(a)) if a[k][j]), None)
        if k is None:
            return Q(0)
        if k != j:
            a[j], a[k] = a[k], a[j]
            d = -d
        pivot = a[j][j]
        d *= pivot
        for k in range(j + 1, len(a)):
            ratio = a[k][j] / pivot
            for l in range(j + 1, len(a)):
                a[k][l] -= ratio * a[j][l]
            a[k][j] = Q(0)
    return d


def gadget(p):
    q = fib(p)
    w = [fib(i) for i in range(1, p - 1)] + [fib(p - 2), fib(p - 1)]
    sums = [0] * (1 << p)
    masks = []
    minimal_winning = []
    for s in range(1, 1 << p):
        low = s & -s
        sums[s] = sums[s ^ low] + w[low.bit_length() - 1]
        if sums[s] == q:
            masks.append(s)
        if sums[s] >= q and all(sums[s] - w[i] < q for i in range(p) if s >> i & 1):
            minimal_winning.append(s)
    if masks != minimal_winning or len(masks) != p:
        raise RuntimeError(('homogeneity/parsimony failure', p))
    a = [[int(s >> i & 1) for i in range(p)] for s in masks]
    det = determinant(a)
    d = [Q(wi, q) for wi in w]
    checks = [abs(det) == q, all(x > 0 for x in d), max(d) <= 1,
              min(d) == Q(1, q), sum(d) == 2 - Q(1, q),
              all(sum(aij * dj for aij, dj in zip(row, d)) == 1 for row in a)]
    if not all(checks):
        raise RuntimeError(('gadget failure', p, checks))
    return {'p': p, 'q': q, 'weights': w, 'quota_coalition_masks': masks,
            'minimal_winning_count': len(minimal_winning), 'determinant': str(det),
            'min_d': str(min(d)), 'sum_d': str(sum(d)), 'passed': True}


def zr(x):
    x = Q(x)
    return z3.RealVal(f'{x.numerator}/{x.denominator}')


def raw_core(p, r):
    q = fib(p)
    d = [Q(fib(i), q) for i in range(1, p - 1)] + [Q(fib(p - 2), q), Q(fib(p - 1), q)]
    h = r - sum(d)
    if h < 1:
        raise RuntimeError('inadmissible H')
    u = [h] + d + [Q(0)] * r
    v = [Q(0)] * (p + 1) + [Q(1)] * r
    n = len(u)
    x = [z3.Real(f'x_{p}_{r}_{i}') for i in range(n)]
    core = [z3.Sum(x) == r]
    for s in range(1 << n):
        us = sum(u[i] for i in range(n) if s >> i & 1)
        vs = sum(v[i] for i in range(n) if s >> i & 1)
        core.append(z3.Sum([x[i] for i in range(n) if s >> i & 1]) >= zr(min(us, vs)))
    t = 1 - x[-1]
    off_segment = z3.Or(t < 0, t > 1, *[x[i] != zr(u[i]) * t + zr(v[i]) * (1-t) for i in range(n)])
    t_min = Q(q, q+1)
    t_max = 1 / (1+h)
    point_min = [t_min * ui + (1-t_min) * vi for ui, vi in zip(u,v)]
    point_max = [t_max * ui + (1-t_max) * vi for ui, vi in zip(u,v)]
    queries = {
        'core_point_off_segment': off_segment,
        'distinct_maximin_point': z3.And(*[xi >= zr(min(point_min)) for xi in x], z3.Or(*[xi != zr(pi) for xi, pi in zip(x, point_min)])),
        'distinct_minimax_point': z3.And(*[xi <= zr(max(point_max)) for xi in x], z3.Or(*[xi != zr(pi) for xi, pi in zip(x, point_max)])),
    }
    outcomes = {}
    for name, query in queries.items():
        solver = z3.Solver()
        solver.add(*core, query)
        outcomes[name] = str(solver.check())
        if outcomes[name] != 'unsat':
            raise RuntimeError((p,r,name,outcomes[name]))
    deficit = 2 - sum(abs(a-b) for a,b in zip(point_min,point_max))/r
    formula = Q(2,q+1) + 2/(r-1+Q(1,q))
    if deficit != formula:
        raise RuntimeError('selector formula failure')
    return {'p':p, 'r':r, 'n':n, 'q':q, 'H':str(h), 't_min':str(t_min),
            't_max':str(t_max), 'deficit':str(deficit), 'raw_coalitions':1<<n, 'queries':outcomes}


def all_n_parameters(n):
    p = 4
    while fib(p) < n*n:
        p += 1
    q = fib(p)
    r = n-p-1
    h = r - 2 + Q(1,q)
    deficit = Q(2,q+1) + 2/(1+h)
    L = (n-1).bit_length()
    bound = Q(2,n-4*L-3) + Q(2,n*n+1)
    conditions = [p <= 4*L+1, h >= 1, q < 2*n*n, r*q < 2*n**3, deficit <= bound]
    if not all(conditions):
        raise RuntimeError(('parameter failure',n,conditions))
    return {'n':n,'p':p,'q':q,'r':r,'H':str(h),'integer_total':r*q,
            'deficit':str(deficit),'n_times_deficit':str(n*deficit),'bound':str(bound)}


if __name__ == '__main__':
    result = {'date':'2026-09-05','python':platform.python_version(),
              'status':'RUNNING','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    path = HERE / 'isbell_check.json'
    path.write_text(json.dumps(result,indent=2)+'\n')
    try:
        import z3
        result['z3'] = z3.get_version_string()
        result['gadgets'] = [gadget(p) for p in range(3,19)]
        result['raw_core_checks'] = [raw_core(p,r) for p,r in [(3,3),(4,3),(5,3),(6,4)]]
        for n in range(128,10001):
            all_n_parameters(n)
        result['parameter_interval'] = [128,10000]
        result['parameter_samples'] = [all_n_parameters(n) for n in [128,256,1000,10000,10**6,10**12]]
        result['status'] = 'PASS'
    except Exception as exc:
        result.update(status='FAIL',error=repr(exc))
        raise
    finally:
        path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','parameter_interval','raw_core_checks']},indent=2))

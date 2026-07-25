"""Fast FLOAT screening for vNM core-stability, exact certification of hits.

dominated_via_float(y,S): does a core point tight on S strictly dominate y on S?
  LP (HiGHS): max t s.t. x(T)>=v(T) all proper T, x(N)=v(N), x(S)<=v(S),
              x_i - y_i >= t (i in S).  t>1e-7 => dominated via S.
find_escape_float: sample imputations, return one that is outside the core and
  undominated (float). Certify exactly with core_stability.certify_undominated.
"""
import random
import numpy as np
from scipy.optimize import linprog

TOL = 1e-7


def _core_rows(vf, n, N):
    A_ub, b_ub = [], []
    for T in range(1, N):
        A_ub.append([-1.0 if T >> i & 1 else 0.0 for i in range(n)])
        b_ub.append(-vf[T])
    return A_ub, b_ub


def in_core_float(vf, n, N, y):
    if abs(sum(y) - vf[N]) > 1e-6:
        return False
    for S in range(1, N):
        if sum(y[i] for i in range(n) if S >> i & 1) < vf[S] - 1e-7:
            return False
    return True


def dominated_via_float(vf, n, N, y, S, base_rows):
    mem = [i for i in range(n) if S >> i & 1]
    A_ub = [row + [0.0] for row in base_rows[0]]
    b_ub = list(base_rows[1])
    # x(S) <= v(S)
    A_ub.append([1.0 if S >> i & 1 else 0.0 for i in range(n)] + [0.0]); b_ub.append(vf[S])
    for i in mem:
        row = [0.0] * (n + 1); row[i] = -1.0; row[n] = 1.0
        A_ub.append(row); b_ub.append(-y[i])
    A_eq = [[1.0] * n + [0.0]]; b_eq = [vf[N]]
    c = [0.0] * n + [-1.0]
    r = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                bounds=[(None, None)] * n + [(None, None)], method="highs")
    if not r.success:
        return False
    return (-r.fun) > TOL


def is_dominated_float(vf, n, N, y, base_rows):
    for S in range(1, N):
        yS = sum(y[i] for i in range(n) if S >> i & 1)
        if vf[S] - yS > 1e-9:
            if dominated_via_float(vf, n, N, y, S, base_rows):
                return True
    return False


def find_escape_float(vf, n, N, tries=200000, seed=0, grid=None):
    """Return a float imputation outside the core, undominated, or None."""
    rng = random.Random(seed)
    lo = [vf[1 << i] for i in range(n)]
    slack = vf[N] - sum(lo)
    base_rows = _core_rows(vf, n, N)
    for _ in range(tries):
        cuts = sorted(rng.random() for _ in range(n - 1))
        prev = 0.0; parts = []
        for cpt in list(cuts) + [1.0]:
            parts.append((cpt - prev) * slack); prev = cpt
        y = [lo[i] + parts[i] for i in range(n)]
        if in_core_float(vf, n, N, y):
            continue
        if not is_dominated_float(vf, n, N, y, base_rows):
            return y
    return None

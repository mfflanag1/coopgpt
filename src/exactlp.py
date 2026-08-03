"""Exact rational LP solver: two-phase primal simplex with Bland's rule.

min c.x  s.t.  A_ub x <= b_ub,  A_eq x = b_eq,  x free.

Free variables handled by the split x = xp - xm. All arithmetic in Fractions.
Returns (status, opt, x) with status in {'optimal','infeasible','unbounded'}.

Written from scratch because sympy 1.14's exact simplex returned infeasible
"optima" on a 3-variable test LP. Cross-validated against scipy HiGHS.
"""
from fractions import Fraction


def _exact(value):
    """Convert an exact scalar while rejecting accidental binary floats."""
    if isinstance(value, float):
        raise TypeError("exact_linprog rejects float input; use Fraction or integer")
    return Fraction(value)

def _simplex_core(T, basis, m, ncols):
    """Simplex on tableau T (m constraint rows + 1 objective row, ncols cols incl RHS).
    Objective row is T[m], minimization, reduced costs in T[m][:ncols-1], obj value = T[m][-1].
    Bland's rule. Returns 'optimal' or 'unbounded'."""
    while True:
        # entering: smallest index with negative reduced cost (Bland)
        enter = -1
        for j in range(ncols - 1):
            if T[m][j] < 0:
                enter = j
                break
        if enter == -1:
            return 'optimal'
        # ratio test, Bland tie-break on smallest basis var index
        leave, best = -1, None
        for i in range(m):
            if T[i][enter] > 0:
                ratio = T[i][-1] / T[i][enter]
                if best is None or ratio < best or (ratio == best and basis[i] < basis[leave]):
                    best, leave = ratio, i
        if leave == -1:
            return 'unbounded'
        # pivot
        piv = T[leave][enter]
        T[leave] = [a / piv for a in T[leave]]
        for i in range(m + 1):
            if i != leave and T[i][enter] != 0:
                f = T[i][enter]
                T[i] = [a - f * b for a, b in zip(T[i], T[leave])]
        basis[leave] = enter

def exact_linprog(c, A_ub=None, b_ub=None, A_eq=None, b_eq=None):
    F = Fraction
    c = [_exact(x) for x in c]
    nv = len(c)
    rows = []   # (coeffs, rhs, is_eq)
    if A_ub:
        for r, b in zip(A_ub, b_ub):
            rows.append(([_exact(x) for x in r], _exact(b), False))
    if A_eq:
        for r, b in zip(A_eq, b_eq):
            rows.append(([_exact(x) for x in r], _exact(b), True))
    m = len(rows)
    nslack = sum(0 if eq else 1 for _, _, eq in rows)
    # columns: xp(nv) xm(nv) slacks(nslack) artificials(m) | rhs
    ncols = 2 * nv + nslack + m + 1
    T = []
    si = 0
    for idx, (r, b, eq) in enumerate(rows):
        row = [F(0)] * ncols
        for j in range(nv):
            row[j] = r[j]
            row[nv + j] = -r[j]
        if not eq:
            row[2 * nv + si] = F(1)
            si += 1
        row[-1] = b
        if b < 0:
            row = [-a for a in row]
        row[2 * nv + nslack + idx] = F(1)
        T.append(row)
    basis = [2 * nv + nslack + i for i in range(m)]
    # phase 1: min sum of artificials
    obj = [F(0)] * ncols
    for i in range(m):
        obj = [o - a for o, a in zip(obj, T[i])]
    for i in range(m):
        obj[2 * nv + nslack + i] = F(0)
    T.append(obj)
    st = _simplex_core(T, basis, m, ncols)
    if -T[m][-1] != 0:      # phase-1 optimum > 0
        return 'infeasible', None, None
    # drive artificials out of basis if possible; then drop artificial columns
    for i in range(m):
        if basis[i] >= 2 * nv + nslack:
            for j in range(2 * nv + nslack):
                if T[i][j] != 0:
                    piv = T[i][j]
                    T[i] = [a / piv for a in T[i]]
                    for k in range(m + 1):
                        if k != i and T[k][j] != 0:
                            f = T[k][j]
                            T[k] = [a - f * b for a, b in zip(T[k], T[i])]
                    basis[i] = j
                    break
    keep = list(range(2 * nv + nslack)) + [ncols - 1]
    T = [[row[j] for j in keep] for row in T[:m]]
    ncols2 = len(keep)
    # rows whose basis var is still artificial are redundant (all-zero); drop them
    live = [i for i in range(m) if basis[i] < 2 * nv + nslack]
    T = [T[i] for i in live]
    basis = [basis[i] for i in live]
    m2 = len(T)
    # phase 2 objective
    obj = [F(0)] * ncols2
    for j in range(nv):
        obj[j] = c[j]
        obj[nv + j] = -c[j]
    # reduce over basis
    for i in range(m2):
        bj = basis[i]
        if obj[bj] != 0:
            f = obj[bj]
            obj = [o - f * t for o, t in zip(obj, T[i])]
    T.append(obj)
    st = _simplex_core(T, basis, m2, ncols2)
    if st == 'unbounded':
        return 'unbounded', None, None
    xfull = [F(0)] * (ncols2 - 1)
    for i in range(m2):
        xfull[basis[i]] = T[i][-1]
    x = [xfull[j] - xfull[nv + j] for j in range(nv)]
    opt = sum(ci * xi for ci, xi in zip(c, x))
    return 'optimal', opt, x

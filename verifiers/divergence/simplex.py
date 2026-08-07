"""Exact-rational two-phase simplex with Bland's rule (no cycling, no floats).

Solves:  max c.y  subject to  A y <= b,  y >= 0.
Returns (optimum, y) or ('infeasible', None) or ('unbounded', None).
Written from scratch so it shares no code with z3 or sympy.
"""
from fractions import Fraction as F


def _pivot(T, basis, r, c):
    pv = T[r][c]
    T[r] = [q / pv for q in T[r]]
    for i in range(len(T)):
        if i != r and T[i][c] != 0:
            f = T[i][c]
            T[i] = [T[i][j] - f * T[r][j] for j in range(len(T[0]))]
    basis[r] = c


def _run(T, basis, ncols, maxiter):
    """Primal simplex on tableau T (last row = objective, last col = rhs).
    Bland's rule -> terminates.  Returns True on optimal, False on unbounded."""
    it = 0
    while it < maxiter:
        it += 1
        # entering: smallest index with negative reduced cost (row -1 holds -z)
        c = None
        for j in range(ncols):
            if T[-1][j] < 0:
                c = j
                break
        if c is None:
            return True
        # ratio test, Bland tie-break on smallest basis index
        r, best = None, None
        for i in range(len(T) - 1):
            if T[i][c] > 0:
                ratio = T[i][-1] / T[i][c]
                if best is None or ratio < best or (ratio == best and basis[i] < basis[r]):
                    best, r = ratio, i
        if r is None:
            return False  # unbounded
        _pivot(T, basis, r, c)
    raise RuntimeError("simplex iteration cap hit")


def lp_max(c, A, b, maxiter=200000):
    """max c.y s.t. A y <= b, y >= 0.  All entries Fractions/ints."""
    m, n = len(A), len(c)
    c = [F(q) for q in c]
    A = [[F(q) for q in row] for row in A]
    b = [F(q) for q in b]
    # make rhs nonnegative by negating rows (introduces need for phase 1)
    # standard: add slacks; rows with b<0 also get an artificial variable.
    rows = []
    for i in range(m):
        if b[i] < 0:
            rows.append(([-q for q in A[i]], -b[i], True))
        else:
            rows.append((A[i][:], b[i], False))
    # column layout: y (n) | slack (m) | artificial (na)
    art_rows = [i for i, (_, _, neg) in enumerate(rows) if neg]
    na = len(art_rows)
    ncols = n + m + na
    T = []
    basis = []
    art_cols = {}
    k = 0
    for i, (row, rhs, neg) in enumerate(rows):
        r = row + [F(0)] * (m + na) + [rhs]
        # slack column i: original row was A y + s = b ; if negated, -A y - s + a = -b
        r[n + i] = F(-1) if neg else F(1)
        if neg:
            col = n + m + k
            art_cols[i] = col
            r[col] = F(1)
            basis.append(col)
            k += 1
        else:
            basis.append(n + i)
        T.append(r)
    if na:
        # phase 1: minimize sum of artificials  ->  max -sum
        obj = [F(0)] * (ncols + 1)
        for i in art_rows:
            for j in range(ncols + 1):
                obj[j] += T[i][j]
        # reduced-cost row = -(sum of artificial rows) restricted to non-artificial cols
        z = [-obj[j] for j in range(ncols)] + [-obj[ncols]]
        for i in art_rows:
            z[art_cols[i]] = F(0)
        T.append(z)
        if not _run(T, basis, n + m, maxiter):
            return ("unbounded_phase1", None)
        if -T[-1][-1] != 0:
            return ("infeasible", None)
        # drive artificials out of the basis
        for i in range(len(T) - 1):
            if basis[i] >= n + m:
                piv = None
                for j in range(n + m):
                    if T[i][j] != 0:
                        piv = j
                        break
                if piv is not None:
                    _pivot(T, basis, i, piv)
        T.pop()
        # zero out artificial columns
        for row in T:
            for j in range(n + m, ncols):
                row[j] = F(0)
    # phase 2
    z = [F(0)] * (ncols + 1)
    for j in range(n):
        z[j] = -c[j]
    T.append(z)
    for i in range(len(T) - 1):
        if basis[i] < ncols and z[basis[i]] != 0:
            pass
    # restore canonical form: eliminate basic columns from objective row
    for i in range(len(T) - 1):
        j = basis[i]
        if T[-1][j] != 0:
            f = T[-1][j]
            T[-1] = [T[-1][q] - f * T[i][q] for q in range(ncols + 1)]
    if not _run(T, basis, n + m, maxiter):
        return ("unbounded", None)
    y = [F(0)] * n
    for i in range(len(T) - 1):
        if basis[i] < n:
            y[basis[i]] = T[i][-1]
    return (T[-1][-1], y)


def lp_min(c, A, b, **kw):
    val, y = lp_max([-q for q in c], A, b, **kw)
    if isinstance(val, str):
        return (val, None)
    return (-val, y)

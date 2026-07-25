"""DETERMINISTIC (full basis enumeration) largeness test, exact certification.

Core is LARGE (Sharkey) iff every y with y(S) >= v(S) for all nonempty S has a
core point x <= y. The minimal such y are vertices of U = {y : y(S)>=v(S) all
nonempty S}: n tight independent constraints. Enumerate ALL bases (deterministic),
find vertices of U, test core-domination. A vertex with no core x<=y => NON-large.
"""
import itertools
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F
from tugame import Game, exact_lp_min


def core_dominates_float(vf, n, N, y):
    A_ub, b_ub = [], []
    for S in range(1, N):
        A_ub.append([-1.0 if S >> i & 1 else 0.0 for i in range(n)]); b_ub.append(-vf[S])
    for i in range(n):
        row = [0.0] * n; row[i] = 1.0; A_ub.append(row); b_ub.append(y[i])
    A_eq = [[1.0] * n]; b_eq = [vf[N]]
    r = linprog([0.0] * n, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                bounds=[(None, None)] * n, method="highs")
    return r.success


def core_dominates_exact(v, n, N, y):
    A_ub, b_ub = [], []
    for S in range(1, N):
        A_ub.append([-1 if S >> i & 1 else 0 for i in range(n)]); b_ub.append(-v[S])
    for i in range(n):
        row = [0] * n; row[i] = 1; A_ub.append(row); b_ub.append(y[i])
    A_eq = [[1] * n]; b_eq = [v[N]]
    opt, x = exact_lp_min([0] * n, A_ub, b_ub, A_eq, b_eq)
    return opt is not None and opt != 'unbounded'


def enumerate_largeness(v, n, verbose=True):
    """Return list of exact non-large vertices y (each certifies non-largeness)."""
    N = (1 << n) - 1
    vf = [float(x) for x in v]
    coalitions = list(range(1, N + 1))
    incid = {S: np.array([1.0 if S >> i & 1 else 0.0 for i in range(n)]) for S in coalitions}
    witnesses = []
    checked = 0
    for B in itertools.combinations(coalitions, n):
        M = np.array([incid[S] for S in B])
        d = np.linalg.det(M)
        if abs(d) < 1e-9:
            continue
        b = np.array([vf[S] for S in B])
        try:
            y = np.linalg.solve(M, b)
        except np.linalg.LinAlgError:
            continue
        # y in U?  y(S) >= v(S) for all nonempty S
        if any(float(incid[S] @ y) < vf[S] - 1e-7 for S in coalitions):
            continue
        checked += 1
        if not core_dominates_float(vf, n, N, list(y)):
            # exact recompute of the vertex and certify
            Me = [[F(1) if S >> i & 1 else F(0) for i in range(n)] for S in B]
            be = [F(v[S]) for S in B]
            ye = exact_solve(Me, be, n)
            if ye is None:
                continue
            if any(sum(ye[i] for i in range(n) if S >> i & 1) < F(v[S]) for S in coalitions):
                continue
            if not core_dominates_exact([F(x) for x in v], n, N, ye):
                witnesses.append((B, ye))
                if verbose:
                    print(f"  NON-LARGE vertex: basis={B} y={[str(a) for a in ye]}", flush=True)
                    return witnesses  # one certificate suffices
    if verbose:
        print(f"  enumerated, U-vertices checked={checked}, non-large witnesses={len(witnesses)}", flush=True)
    return witnesses


def exact_solve(M, b, n):
    """Solve n x n exact linear system via Gaussian elimination (Fractions)."""
    A = [row[:] + [b[i]] for i, row in enumerate(M)]
    for col in range(n):
        piv = next((r for r in range(col, n) if A[r][col] != 0), None)
        if piv is None:
            return None
        A[col], A[piv] = A[piv], A[col]
        pv = A[col][col]
        A[col] = [a / pv for a in A[col]]
        for r in range(n):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                A[r] = [A[r][k] - f * A[col][k] for k in range(n + 1)]
    return [A[i][n] for i in range(n)]


if __name__ == "__main__":
    WIT_VN4 = [0,0,0,0,0,1,1,1,1,1,1,1,2,2,2,2,0,1,1,2,0,1,1,2,2,3,3,3,2,3,3,4]
    BASE_VN6 = [0,0,0,0,3,3,3,3,0,0,0,0,4,4,4,4,0,0,0,0,4,5,5,5,0,0,0,0,4,5,5,6]
    for tag, v in [("vN4", WIT_VN4), ("vN6", BASE_VN6)]:
        print(f"=== {tag} largeness (deterministic) ===", flush=True)
        w = enumerate_largeness([F(x) for x in v], 5)
        print(f"  {tag}: {'NON-LARGE (certified)' if w else 'LARGE (no non-large vertex found)'}", flush=True)

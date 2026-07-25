"""Randomized non-largeness detector (float) for TU games.

Core is LARGE (Sharkey) iff every y with y(S) >= v(S) for all nonempty S dominates
some core point from above (exists core x <= y). The minimal such y are vertices of
U = {y : y(S) >= v(S)}: each fixed by n coalitions S_1..S_n whose incidence vectors are
independent (y(S_j) = v(S_j)). At such a vertex, non-largeness is certified if no core
point x <= y exists (LP infeasible). We SAMPLE bases -> a hit certifies non-large;
absence over many samples is strong (not proof) evidence of large.

Large core => egalitarian stable (Dietzenbacher 2021). So a non-ES exact game must be
found among NON-large exact games. This module locates them.
"""
import random, itertools
import numpy as np
from scipy.optimize import linprog


def core_dominates(vf, n, N, y):
    """Does some core point x <= y exist? x(S)>=v(S) proper, x(N)=v(N), x<=y."""
    A_ub, b_ub = [], []
    for S in range(1, N):
        A_ub.append([-1.0 if S >> i & 1 else 0.0 for i in range(n)])
        b_ub.append(-vf[S])
    for i in range(n):                       # x_i <= y_i
        row = [0.0] * n; row[i] = 1.0
        A_ub.append(row); b_ub.append(y[i])
    A_eq = [[1.0] * n]; b_eq = [vf[N]]
    r = linprog([0.0] * n, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                bounds=[(None, None)] * n, method="highs")
    return r.success


def non_large_witness(vf, n, N, samples=4000, seed=0):
    """Return a violating vertex y (list) certifying non-largeness, or None."""
    rng = random.Random(seed)
    coalitions = list(range(1, N + 1))
    incidence = {S: np.array([1.0 if S >> i & 1 else 0.0 for i in range(n)])
                 for S in coalitions}
    vals = {S: vf[S] for S in coalitions}
    for _ in range(samples):
        B = rng.sample(coalitions, n)
        M = np.array([incidence[S] for S in B])
        if abs(np.linalg.det(M)) < 1e-9:
            continue
        b = np.array([vals[S] for S in B])
        try:
            y = np.linalg.solve(M, b)
        except np.linalg.LinAlgError:
            continue
        # y in U?  y(S) >= v(S) for all nonempty S (tol)
        ok = True
        for S in coalitions:
            if float(incidence[S] @ y) < vals[S] - 1e-7:
                ok = False; break
        if not ok:
            continue
        if not core_dominates(vf, n, N, list(y)):
            return list(y)
    return None

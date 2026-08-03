"""DETERMINISTIC (full basis enumeration) largeness test, exact certification.

Core is LARGE (Sharkey) iff every y with y(S) >= v(S) for all nonempty S has a
core point x <= y. The minimal such y are vertices of U = {y : y(S)>=v(S) all
nonempty S}: n tight independent constraints. Enumerate ALL bases (deterministic),
find vertices of U, test core-domination. A vertex with no core x<=y => NON-large.
"""
import itertools
import math
import numpy as np
import sys
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


def exact_solve_many(M, right_hand_sides, n):
    """Solve one exact square system against several right-hand sides."""
    width = len(right_hand_sides)
    augmented = [
        list(M[row]) + [right_hand_sides[column][row] for column in range(width)]
        for row in range(n)
    ]
    for column in range(n):
        pivot = next(
            (row for row in range(column, n) if augmented[row][column] != 0),
            None,
        )
        if pivot is None:
            return None
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_value = augmented[column][column]
        augmented[column] = [value / pivot_value for value in augmented[column]]
        for row in range(n):
            if row == column or augmented[row][column] == 0:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                value - factor * pivot_row_value
                for value, pivot_row_value in zip(
                    augmented[row], augmented[column]
                )
            ]
    return [
        [augmented[row][n + column] for row in range(n)]
        for column in range(width)
    ]


def verify_large_cores_exact(games, n, progress=False):
    """Completely verify Sharkey largeness for several games at once.

    The acceptable-payoff polyhedron is upward comprehensive and pointed.
    Its vertices are obtained by every independent set of ``n`` tight
    coalition inequalities.  If every vertex dominates a core allocation,
    convexity and the nonnegative recession cone give the property for the
    whole polyhedron.  All basis solves, feasibility tests, and domination LPs
    use exact rational arithmetic.
    """
    values_by_game = [[F(value) for value in values] for values in games]
    full = (1 << n) - 1
    coalitions = list(range(1, full + 1))
    incidence = {
        coalition: [
            F(1) if coalition >> player & 1 else F(0)
            for player in range(n)
        ]
        for coalition in coalitions
    }
    vertices = [set() for _ in games]
    feasible_basis_counts = [0 for _ in games]
    independent_basis_count = 0
    total_bases = math.comb(len(coalitions), n)
    for basis_index, basis in enumerate(
        itertools.combinations(coalitions, n),
        start=1,
    ):
        matrix = [incidence[coalition] for coalition in basis]
        right_hand_sides = [
            [values[coalition] for coalition in basis]
            for values in values_by_game
        ]
        solutions = exact_solve_many(matrix, right_hand_sides, n)
        if progress and basis_index % 20000 == 0:
            print(
                f"large-core bases {basis_index}/{total_bases}",
                file=sys.stderr,
                flush=True,
            )
        if solutions is None:
            continue
        independent_basis_count += 1
        for game_index, (values, candidate) in enumerate(
            zip(values_by_game, solutions)
        ):
            if all(
                sum(
                    candidate[player]
                    for player in range(n)
                    if coalition >> player & 1
                ) >= values[coalition]
                for coalition in coalitions
            ):
                feasible_basis_counts[game_index] += 1
                vertices[game_index].add(tuple(candidate))
    reports = []
    for values, game_vertices, feasible_count in zip(
        values_by_game,
        vertices,
        feasible_basis_counts,
    ):
        ordered_vertices = sorted(game_vertices)
        for vertex in ordered_vertices:
            if not core_dominates_exact(values, n, full, vertex):
                raise RuntimeError(
                    "acceptable-payoff vertex does not dominate any core point: "
                    f"{vertex}"
                )
        reports.append({
            "coalition_bases_enumerated": total_bases,
            "independent_bases": independent_basis_count,
            "feasible_vertex_bases": feasible_count,
            "distinct_acceptable_vertices": len(ordered_vertices),
            "vertices_core_dominated": len(ordered_vertices),
            "large_core": True,
        })
    return reports


if __name__ == "__main__":
    WIT_VN4 = [0,0,0,0,0,1,1,1,1,1,1,1,2,2,2,2,0,1,1,2,0,1,1,2,2,3,3,3,2,3,3,4]
    BASE_VN6 = [0,0,0,0,3,3,3,3,0,0,0,0,4,4,4,4,0,0,0,0,4,5,5,5,0,0,0,0,4,5,5,6]
    for tag, v in [("vN4", WIT_VN4), ("vN6", BASE_VN6)]:
        print(f"=== {tag} largeness (deterministic) ===", flush=True)
        w = enumerate_largeness([F(x) for x in v], 5)
        print(f"  {tag}: {'NON-LARGE (certified)' if w else 'LARGE (no non-large vertex found)'}", flush=True)

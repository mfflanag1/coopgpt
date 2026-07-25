"""Family-infeasibility engine for the coalitional-monotonicity impossibility hunt.

A single-valued core selection sigma assigns sigma(v) in core(v) to each game v.
Coalitional monotonicity: if v'(S) = v(S)+d (d>0) and v'=v elsewhere, then
sigma_i(v') >= sigma_i(v) for all i in S.

Given a finite family of games {v^1..v^m} and a set of BUMP EDGES (k,l,S) meaning
v^l = v^k except v^l(S) = v^k(S)+d for one proper coalition S, any coalitionally
monotonic core selection must produce points x^1..x^m with:
  (efficiency)   sum_i x^k_i = v^k(N)                     for all k
  (core)         sum_{i in T} x^k_i >= v^k(T)             for all k, proper T
  (monotone)     x^k_i <= x^l_i                           for edge (k,l,S), i in S
This is one exact LP feasibility problem in n*m variables. INFEASIBLE => no
coalitionally monotonic core selection exists on any class containing the family.

Certification of an infeasible hit is via an exact Farkas certificate: nonnegative
multipliers on the (>=/<=) inequality rows and free multipliers on the equalities
whose weighted sum is the contradiction 0 <= (negative). The certificate is verified
by direct exact-rational arithmetic, independent of the simplex solver.
"""
from fractions import Fraction as F
from tugame import Game, exact_lp_min
from exactlp import exact_linprog


def build_constraints(games, edges):
    """Return (nvars, A_ub, b_ub, A_eq, b_eq, rowmeta) for the family LP.

    games : list of Game (all same n).
    edges : list of (k, l, S) bump edges; v^l(S) = v^k(S)+d, else equal.
    Variable index of x^k_i is k*n + i.
    rowmeta lists a human tag per A_ub row (for debugging / certificate reading).
    """
    n = games[0].n
    m = len(games)
    nv = n * m
    A_ub, b_ub, rowmeta = [], [], []
    A_eq, b_eq = [], []
    # efficiency (equalities)
    for k, g in enumerate(games):
        row = [0] * nv
        for i in range(n):
            row[k * n + i] = 1
        A_eq.append(row); b_eq.append(g.v[g.N])
    # core: x^k(T) >= v^k(T)  ->  -x^k(T) <= -v^k(T)
    for k, g in enumerate(games):
        for T in range(1, g.N):
            row = [0] * nv
            for i in range(n):
                if T >> i & 1:
                    row[k * n + i] = -1
            A_ub.append(row); b_ub.append(-g.v[T])
            rowmeta.append(("core", k, T))
    # monotonicity: x^k_i - x^l_i <= 0 for i in S
    for (k, l, S) in edges:
        for i in range(n):
            if S >> i & 1:
                row = [0] * nv
                row[k * n + i] = 1
                row[l * n + i] = -1
                A_ub.append(row); b_ub.append(0)
                rowmeta.append(("mono", k, l, i, S))
    return nv, A_ub, b_ub, A_eq, b_eq, rowmeta


def is_family_feasible(games, edges):
    """Return (feasible: bool, witness: list[list[Fraction]] or None)."""
    nv, A_ub, b_ub, A_eq, b_eq, _ = build_constraints(games, edges)
    n, m = games[0].n, len(games)
    opt, z = exact_lp_min([0] * nv, A_ub, b_ub, A_eq, b_eq)
    if opt is None:            # infeasible
        return False, None
    # reshape witness
    x = [[z[k * n + i] for i in range(n)] for k in range(m)]
    return True, x


def verify_witness(games, edges, x):
    """Exactly verify x^k in core(v^k) and monotonicity across edges."""
    n = games[0].n
    for k, g in enumerate(games):
        if sum(x[k]) != g.v[g.N]:
            return False, ("efficiency", k)
        for T in range(1, g.N):
            if sum(x[k][i] for i in range(n) if T >> i & 1) < g.v[T]:
                return False, ("core", k, T)
    for (k, l, S) in edges:
        for i in range(n):
            if S >> i & 1 and x[k][i] > x[l][i]:
                return False, ("mono", k, l, i)
    return True, None


def farkas_certificate(games, edges):
    """Find and exactly verify a Farkas infeasibility certificate.

    System: A_ub z <= b_ub, A_eq z = b_eq. Infeasible iff exists y_ub >= 0 and
    y_eq free with  y_ub^T A_ub + y_eq^T A_eq = 0  and  y_ub^T b_ub + y_eq^T b_eq < 0.
    We solve for such (y_ub, y_eq) via an LP, then verify the two conditions by
    exact arithmetic. Returns dict or None (None => no certificate found).
    """
    nv, A_ub, b_ub, A_eq, b_eq, rowmeta = build_constraints(games, edges)
    p = len(A_ub)     # inequality rows, y_ub_j >= 0
    q = len(A_eq)     # equality rows,  y_eq free -> split into two nonneg? keep free via LP var split
    # Variables of the certificate LP: y_ub (p, >=0), y_eq (q, free).
    # Constraints (exact equalities): for each column c in 0..nv-1:
    #   sum_j y_ub_j A_ub[j][c] + sum_r y_eq_r A_eq[r][c] = 0.
    # Normalization: sum over rows of (b) contribution = -1, i.e.
    #   sum_j y_ub_j b_ub[j] + sum_r y_eq_r b_eq[r] = -1.
    # y_ub >= 0 enforced by sign constraints; y_eq free (exact_linprog treats all vars free,
    # so add explicit y_ub_j >= 0 rows).
    ncert = p + q
    cA_eq, cb_eq = [], []
    for c in range(nv):
        row = [F(A_ub[j][c]) for j in range(p)] + [F(A_eq[r][c]) for r in range(q)]
        cA_eq.append(row); cb_eq.append(F(0))
    normrow = [F(b_ub[j]) for j in range(p)] + [F(b_eq[r]) for r in range(q)]
    cA_eq.append(normrow); cb_eq.append(F(-1))
    cA_ub, cb_ub = [], []
    for j in range(p):         # -y_ub_j <= 0
        r = [F(0)] * ncert; r[j] = F(-1)
        cA_ub.append(r); cb_ub.append(F(0))
    status, opt, y = exact_linprog([0] * ncert, cA_ub, cb_ub, cA_eq, cb_eq)
    if status == 'infeasible':
        return None
    y_ub = y[:p]; y_eq = y[p:]
    # exact verification, independent of solver internals
    # (1) y_ub >= 0
    if any(v < 0 for v in y_ub):
        return None
    # (2) combination of columns is exactly zero
    for c in range(nv):
        s = sum(y_ub[j] * A_ub[j][c] for j in range(p)) + sum(y_eq[r] * A_eq[r][c] for r in range(q))
        if s != 0:
            return None
    # (3) rhs combination is strictly negative
    rhs = sum(y_ub[j] * b_ub[j] for j in range(p)) + sum(y_eq[r] * b_eq[r] for r in range(q))
    if rhs >= 0:
        return None
    active = [(rowmeta[j], y_ub[j]) for j in range(p) if y_ub[j] != 0]
    active_eq = [(("eff", r), y_eq[r]) for r in range(q) if y_eq[r] != 0]
    return {"y_ub": y_ub, "y_eq": y_eq, "rhs": rhs,
            "active_ineq": active, "active_eq": active_eq}


def certify_infeasible(games, edges):
    """Full certification of an infeasible family:
    - re-run feasibility with constraint rows shuffled (order-independence),
    - exact Farkas certificate.
    Returns dict with 'infeasible' bool and 'farkas' payload, or reason it failed."""
    import random
    feas, _ = is_family_feasible(games, edges)
    if feas:
        return {"infeasible": False, "reason": "LP feasible"}
    # re-solve with permuted row order (independent code path stress)
    nv, A_ub, b_ub, A_eq, b_eq, _ = build_constraints(games, edges)
    rng = random.Random(12345)
    for _ in range(3):
        perm = list(range(len(A_ub))); rng.shuffle(perm)
        A2 = [A_ub[i] for i in perm]; b2 = [b_ub[i] for i in perm]
        eperm = list(range(len(A_eq))); rng.shuffle(eperm)
        Ae2 = [A_eq[i] for i in eperm]; be2 = [b_eq[i] for i in eperm]
        opt, _z = exact_lp_min([0] * nv, A2, b2, Ae2, be2)
        if opt is not None:
            return {"infeasible": False, "reason": "order-dependent feasibility (solver bug!)"}
    fk = farkas_certificate(games, edges)
    if fk is None:
        return {"infeasible": True, "farkas": None, "reason": "infeasible but no verified Farkas cert"}
    return {"infeasible": True, "farkas": fk}

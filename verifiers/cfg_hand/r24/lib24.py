"""Exact-Fraction machinery for round 24 on inequality (R).

No solver process is used anywhere: a hand-rolled exact rational simplex
(Bland's rule, guaranteed termination) does every LP.

CONVENTIONS (re-read before writing any code):
  n = 5, coalitions are bitmasks 1..31, FULL = 31.
  v singleton-normalized: v({i}) = 0.  T = v(N).
  f(S) = T - v(N\\S).
  lambda = min over ALL nonempty S INCLUDING N of f(S)/|S|
         = min(lambda_proper, T/5)   since f(N) = T.
  Core(v) = {y : y(N) = T, y(S) <= f(S) for all proper nonempty S}
            (this already forces y >= 0, via S = N\\{i}).

EXACT GAMES = CAP CLOSURES.  For a finite set G of nonnegative vectors with
common total T, envelope(G) has v(S) = min_g g(S) and is exact, with
f(S) = max_g g(S).  Conversely every exact game is the envelope of its core
vertices.  So the generator is complete in principle; its REACHABLE SHAPES are
limited by the number of rows and the size of the integers drawn.
"""
from __future__ import annotations

from fractions import Fraction as F

N_PLAYERS = 5
FULL = (1 << N_PLAYERS) - 1
PROPER = list(range(1, FULL))
ALLNE = list(range(1, FULL + 1))
LETTERS = "abcde"


def nm(mask):
    return "".join(LETTERS[i] for i in range(N_PLAYERS) if mask >> i & 1) or "0"


def bits(mask):
    return [i for i in range(N_PLAYERS) if mask >> i & 1]


def card(mask):
    return bin(mask).count("1")


# --------------------------------------------------------------- exact simplex

class LPError(Exception):
    pass


def simplex_min(A, b, c):
    """min c.x  s.t.  A x = b, x >= 0.   Exact Fractions.

    Returns (value, x, duals).  duals = c_B B^{-1} for the ORIGINAL row order
    and orientation (so duals[i] is the multiplier of row i as supplied).
    Raises LPError('infeasible') or LPError('unbounded').
    """
    m = len(A)
    ncol = len(A[0])
    A = [[F(t) for t in row] for row in A]
    b = [F(t) for t in b]
    c = [F(t) for t in c]
    sign = [1] * m
    for i in range(m):
        if b[i] < 0:
            A[i] = [-t for t in A[i]]
            b[i] = -b[i]
            sign[i] = -1

    ntot = ncol + m                      # artificials appended
    tab = [A[i] + [F(1) if j == i else F(0) for j in range(m)] + [b[i]]
           for i in range(m)]
    basis = [ncol + i for i in range(m)]

    def cost_row(cost):
        r = [cost[j] - sum(cost[basis[i]] * tab[i][j] for i in range(m))
             for j in range(ntot)]
        z = sum(cost[basis[i]] * tab[i][ntot] for i in range(m))
        return r, z

    def run(cost, allowed):
        it = 0
        while True:
            it += 1
            if it > 20000:
                raise LPError("cycling")
            r, _ = cost_row(cost)
            enter = -1
            for j in allowed:
                if r[j] < 0:
                    enter = j
                    break
            if enter < 0:
                return
            leave, best = -1, None
            for i in range(m):
                if tab[i][enter] > 0:
                    ratio = tab[i][ntot] / tab[i][enter]
                    if best is None or ratio < best or (
                            ratio == best and basis[i] < basis[leave]):
                        best, leave = ratio, i
            if leave < 0:
                raise LPError("unbounded")
            piv = tab[leave][enter]
            tab[leave] = [t / piv for t in tab[leave]]
            for i in range(m):
                if i != leave and tab[i][enter] != 0:
                    fac = tab[i][enter]
                    tab[i] = [tab[i][j] - fac * tab[leave][j]
                              for j in range(ntot + 1)]
            basis[leave] = enter

    c1 = [F(0)] * ncol + [F(1)] * m
    run(c1, range(ncol))                       # artificials never re-enter
    _, z1 = cost_row(c1)
    if z1 > 0:
        raise LPError("infeasible")
    # drive artificials out of the basis where possible
    for i in range(m):
        if basis[i] >= ncol:
            piv_j = next((j for j in range(ncol) if tab[i][j] != 0), None)
            if piv_j is None:
                continue                        # redundant row, leave it
            piv = tab[i][piv_j]
            tab[i] = [t / piv for t in tab[i]]
            for k in range(m):
                if k != i and tab[k][piv_j] != 0:
                    fac = tab[k][piv_j]
                    tab[k] = [tab[k][j] - fac * tab[i][j]
                              for j in range(ntot + 1)]
            basis[i] = piv_j

    c2 = c + [F(0)] * m
    run(c2, range(ncol))
    x = [F(0)] * ncol
    for i in range(m):
        if basis[i] < ncol:
            x[basis[i]] = tab[i][ntot]
    val = sum(c[j] * x[j] for j in range(ncol))
    duals = [sign[i] * sum(c2[basis[k]] * tab[k][ncol + i] for k in range(m))
             for i in range(m)]
    return val, x, duals


# ------------------------------------------------- core LPs via the small dual

def core_max(f, T, w, eqs=()):
    """max sum_k w_k y_k over {y : y(N)=T, y(S) <= f(S) proper S} intersected
    with the equalities  y(E) = rhs  for (E, rhs) in eqs.

    Solved on the DUAL (5 rows only):
        min eta*T + sum_S gamma_S f(S) + sum_E theta_E rhs_E
        s.t. eta + sum_{S ni k} gamma_S + sum_{E ni k} theta_E >= w_k,
             gamma >= 0, eta and theta free.
    Returns (value, y, eta, gamma_dict, theta_list).
    y is the primal optimum, read off as the simplex multipliers; it is
    verified to be primal feasible and to attain the value.
    """
    cols = []          # (kind, key, cost, coeff vector over players)
    for S in PROPER:
        cols.append(("g", S, F(f[S]), [F(1) if S >> k & 1 else F(0)
                                       for k in range(N_PLAYERS)]))
    for sgn in (1, -1):
        cols.append(("eta", sgn, sgn * F(T), [F(sgn)] * N_PLAYERS))
    for idx, (E, rhs) in enumerate(eqs):
        for sgn in (1, -1):
            cols.append(("th", (idx, sgn), sgn * F(rhs),
                         [F(sgn) if E >> k & 1 else F(0)
                          for k in range(N_PLAYERS)]))
    # surplus variables for the >= constraints
    A, cst = [], []
    ncols = len(cols)
    for k in range(N_PLAYERS):
        A.append([cols[j][3][k] for j in range(ncols)]
                 + [F(-1) if i == k else F(0) for i in range(N_PLAYERS)])
    cst = [cols[j][2] for j in range(ncols)] + [F(0)] * N_PLAYERS
    b = [F(w[k]) for k in range(N_PLAYERS)]
    val, x, duals = simplex_min(A, b, cst)
    y = duals[:]                       # primal optimum
    eta = F(0)
    gamma = {}
    theta = [F(0)] * len(eqs)
    for j, (kind, key, _, _) in enumerate(cols):
        if x[j] == 0:
            continue
        if kind == "g":
            gamma[key] = gamma.get(key, F(0)) + x[j]
        elif kind == "eta":
            eta += key * x[j]
        else:
            theta[key[0]] += key[1] * x[j]
    # ---- guards: primal feasibility and complementary value
    assert sum(y) == F(T), "dual multipliers violate efficiency"
    for S in PROPER:
        assert sum(y[k] for k in bits(S)) <= F(f[S]) + 0, f"cap {nm(S)} violated"
    for (E, rhs) in eqs:
        assert sum(y[k] for k in bits(E)) == F(rhs), "equality violated"
    assert sum(F(w[k]) * y[k] for k in range(N_PLAYERS)) == val, "duality gap"
    return val, y, eta, gamma, theta


def core_feasible(f, T, lows):
    """Is there y in Core with y_k >= lows[k] for every k?  Exact phase-1.

    Substitute u = y - lows >= 0; then u(N) = T - sum(lows) and
    u(S) <= f(S) - lows(S) with slacks.  Feasible iff the equality system has a
    nonnegative solution.
    """
    shift = [F(t) for t in lows]
    npro = len(PROPER)
    rows, rhs = [], []
    rows.append([F(1)] * N_PLAYERS + [F(0)] * npro)
    rhs.append(F(T) - sum(shift))
    for i, S in enumerate(PROPER):
        row = [F(1) if S >> k & 1 else F(0) for k in range(N_PLAYERS)]
        row += [F(1) if j == i else F(0) for j in range(npro)]
        rows.append(row)
        rhs.append(F(f[S]) - sum(shift[k] for k in bits(S)))
    if any(r < 0 for r in rhs):
        return False
    try:
        simplex_min(rows, rhs, [F(0)] * (N_PLAYERS + npro))
        return True
    except LPError as e:
        if str(e) == "infeasible":
            return False
        raise


# ------------------------------------------------------------------- games

def envelope(gens):
    """Lower envelope of common-total allocations: an exact game."""
    total = sum(gens[0])
    for g in gens:
        assert sum(g) == total
    v = [F(0)] * (FULL + 1)
    for S in PROPER:
        v[S] = min(sum(g[k] for k in bits(S)) for g in gens)
    v[FULL] = F(total)
    return v


def fvec(v):
    T = v[FULL]
    return [T - v[FULL ^ S] for S in range(FULL + 1)], T


def lam_of(f, T):
    """lambda over ALL nonempty S INCLUDING N."""
    return min(F(f[S], 1) / card(S) for S in ALLNE)


def lam_proper(f, T):
    return min(F(f[S], 1) / card(S) for S in PROPER)

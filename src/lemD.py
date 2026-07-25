"""Lemma D toolkit — exact-rational cone/star analysis at the leximin point.

All certificates exact (Fraction). Never imports validate.py; uses exactlp.
"""
from fractions import Fraction as F
from itertools import combinations
from tugame import Game, exact_lp_min
from leximin import leximin_core_exact


def xS(x, S, n):
    return sum(x[i] for i in range(n) if S >> i & 1)


def tight_coalitions(g, x):
    """Proper coalitions T (1..N-1) with x(T)==v(T)."""
    return [T for T in range(1, g.N) if xS(x, T, g.n) == g.v[T]]


def core_min_xT(g, T):
    """min_{core} x(T), exact."""
    n, N, v = g.n, g.N, g.v
    A_ub, b_ub = [], []
    for S in range(1, N):
        A_ub.append([-1 if S >> i & 1 else 0 for i in range(n)]); b_ub.append(-v[S])
    A_eq = [[1] * n]; b_eq = [v[N]]
    c = [1 if T >> i & 1 else 0 for i in range(n)]
    opt, _ = exact_lp_min(c, A_ub, b_ub, A_eq, b_eq)
    return opt


def core_max_xS(g, S):
    """max_{core} x(S) = v(N) - min_{core} x(N\\S), exact."""
    return g.v[g.N] - core_min_xT(g, g.N ^ S)


def is_exact_game(g):
    for T in range(1, g.N):
        if core_min_xT(g, T) != g.v[T]:
            return False
    return True


def binding_bumpable(g, x, S):
    """S proper non-singleton with max_core x(S) > phi(S)."""
    if bin(S).count("1") < 2 or S == g.N:
        return False
    return core_max_xS(g, S) > xS(x, S, g.n)


def star_holds(g, x, S):
    """(star_S) via Pareto form (R1): exists core y with y_i>=x_i (i in S), y(S)>x(S).
    Returns (holds: bool, value, y). value = max{y(S): y core, y_i>=x_i i in S}."""
    n, N, v = g.n, g.N, g.v
    A_ub, b_ub = [], []
    for T in range(1, N):
        A_ub.append([-1 if T >> i & 1 else 0 for i in range(n)]); b_ub.append(-v[T])
    for i in range(n):                       # y_i >= x_i for i in S  ->  -y_i <= -x_i
        if S >> i & 1:
            row = [0] * n; row[i] = -1
            A_ub.append(row); b_ub.append(-x[i])
    A_eq = [[1] * n]; b_eq = [v[N]]
    c = [-1 if S >> i & 1 else 0 for i in range(n)]   # maximize y(S)
    opt, y = exact_lp_min(c, A_ub, b_ub, A_eq, b_eq)
    if opt is None or opt == "unbounded":
        return None, None, None
    val = -opt
    return val > xS(x, S, n), val, y


def star_direction(g, x, S):
    """Direct (star_S) feasibility LP: max e(S) s.t. e(N)=0, e_i>=0 (i in S),
    e(T)>=0 tight T, box -1<=e<=1. Returns (holds, e). Cone form."""
    n, N = g.n, g.N
    tights = tight_coalitions(g, x)
    A_ub, b_ub = [], []
    for T in tights:                          # e(T) >= 0 -> -e(T) <= 0
        A_ub.append([-1 if T >> i & 1 else 0 for i in range(n)]); b_ub.append(0)
    for i in range(n):                        # e_i >= 0 for i in S
        if S >> i & 1:
            row = [0] * n; row[i] = -1; A_ub.append(row); b_ub.append(0)
    for i in range(n):                        # box
        r1 = [0] * n; r1[i] = 1; A_ub.append(r1); b_ub.append(1)
        r2 = [0] * n; r2[i] = -1; A_ub.append(r2); b_ub.append(1)
    A_eq = [[1] * n]; b_eq = [0]
    c = [-1 if S >> i & 1 else 0 for i in range(n)]
    opt, e = exact_lp_min(c, A_ub, b_ub, A_eq, b_eq)
    if opt is None or opt == "unbounded":
        return None, None
    return (-opt > 0), e


def residual_cover(g, x, S):
    """When (star_S) fails: find lambda_T>=0 (tight T), mu, r_k>=1 (k in S) with
    mu - sum_{T ni k} lambda_T = r_k (k in S), = 0 (j not in S).
    Returns dict {tights, lambda, mu, r} or None if not found (i.e. star holds)."""
    n, N = g.n, g.N
    tights = tight_coalitions(g, x)
    m = len(tights)
    # vars: lambda_0..lambda_{m-1} (>=0), mu (free -> split), r_k for k in S (>=1)
    Sm = [k for k in range(n) if S >> k & 1]
    # Build equalities: for each player i:
    #   mu - sum_{T ni i} lambda_T - r_i*[i in S] = 0    (r_i defined only i in S)
    # unknowns ordering: [lambda(m)] [mu] [r(len Sm)]
    nl = m; nvars = nl + 1 + len(Sm)
    ridx = {k: nl + 1 + t for t, k in enumerate(Sm)}
    A_eq, b_eq = [], []
    for i in range(n):
        row = [0] * nvars
        for t, T in enumerate(tights):
            if T >> i & 1:
                row[t] = -1
        row[nl] = 1                      # mu
        if S >> i & 1:
            row[ridx[i]] = -1
        A_eq.append(row); b_eq.append(0)
    # bounds: lambda>=0, r>=1, mu free. Encode via A_ub with x free (exact_lp splits).
    A_ub, b_ub = [], []
    for t in range(nl):                  # -lambda_t <= 0
        row = [0] * nvars; row[t] = -1; A_ub.append(row); b_ub.append(0)
    for k in Sm:                         # -r_k <= -1
        row = [0] * nvars; row[ridx[k]] = -1; A_ub.append(row); b_ub.append(-1)
    c = [0] * nvars                      # feasibility
    opt, sol = exact_lp_min(c, A_ub, b_ub, A_eq, b_eq)
    if opt is None or opt == "unbounded":
        return None
    lam = {tights[t]: sol[t] for t in range(nl) if sol[t] != 0}
    mu = sol[nl]
    r = {k: sol[ridx[k]] for k in Sm}
    return {"tights": tights, "lambda": lam, "mu": mu, "r": r}


def max_exact_bump(g, S):
    """Largest d>=0 such that v+d*1_S stays exact.
    d*_T = max{x(S): x in core, x(T)=v(T)} - v(S) for each proper T!=S; d* = min_T d*_T.
    (Also bounded by max_core x(S)-v(S), which is the T=singletons/efficiency envelope.)"""
    n, N, v = g.n, g.N, g.v
    dstar = None
    for T in range(1, N):
        if T == S:
            continue
        # max x(S) s.t. core and x(T)=v(T)
        A_ub, b_ub = [], []
        for U in range(1, N):
            A_ub.append([-1 if U >> i & 1 else 0 for i in range(n)]); b_ub.append(-v[U])
        A_eq = [[1] * n, [1 if T >> i & 1 else 0 for i in range(n)]]
        b_eq = [v[N], v[T]]
        c = [-1 if S >> i & 1 else 0 for i in range(n)]
        opt, _ = exact_lp_min(c, A_ub, b_ub, A_eq, b_eq)
        if opt is None or opt == "unbounded":
            continue
        dT = (-opt) - v[S]
        if dstar is None or dT < dstar:
            dstar = dT
    return dstar


def exact_bumpable(g, S):
    """True iff max_exact_bump(g,S) > 0, with early exit (stop at first T giving d*_T=0)."""
    n, N, v = g.n, g.N, g.v
    for T in range(1, N):
        if T == S:
            continue
        A_ub, b_ub = [], []
        for U in range(1, N):
            A_ub.append([-1 if U >> i & 1 else 0 for i in range(n)]); b_ub.append(-v[U])
        A_eq = [[1] * n, [1 if T >> i & 1 else 0 for i in range(n)]]
        b_eq = [v[N], v[T]]
        c = [-1 if S >> i & 1 else 0 for i in range(n)]
        opt, _ = exact_lp_min(c, A_ub, b_ub, A_eq, b_eq)
        if opt is None or opt == "unbounded":
            continue
        if (-opt) - v[S] <= 0:
            return False
    return True


def round1_dual(g):
    """Exact dual of the leximin round-1 LP (free=N):
    min -sum lambda_U v(U) + sigma v(N) - sum pi_i m_i
    s.t. sigma - sum_{U ni i} lambda_U - pi_i = 0 (all i), sum pi_i = 1, lambda,pi>=0, sigma free.
    Returns (pi, lambda_dict, sigma). pi supported on lowest stratum B_1."""
    n, N, v = g.n, g.N, g.v
    props = list(range(1, N))
    m = len(props)
    # vars: lambda(m) >=0, pi(n) >=0, sigma free
    nl = m; npi = n; nvars = nl + npi + 1; si = nl + npi
    A_eq, b_eq = [], []
    for i in range(n):                       # sigma - sum_{U ni i} lambda - pi_i = 0
        row = [0] * nvars
        for t, U in enumerate(props):
            if U >> i & 1:
                row[t] = -1
        row[nl + i] = -1; row[si] = 1
        A_eq.append(row); b_eq.append(0)
    A_eq.append([0]*nl + [1]*npi + [0]); b_eq.append(1)   # sum pi = 1
    A_ub, b_ub = [], []
    for t in range(nl):
        row = [0]*nvars; row[t] = -1; A_ub.append(row); b_ub.append(0)
    for i in range(npi):
        row = [0]*nvars; row[nl+i] = -1; A_ub.append(row); b_ub.append(0)
    mvec = [v[1 << i] for i in range(n)]
    c = [-v[U] for U in props] + [-mvec[i] for i in range(n)] + [v[N]]
    opt, sol = exact_lp_min(c, A_ub, b_ub, A_eq, b_eq)
    if opt is None or opt == "unbounded":
        return None, None, None
    lam = {props[t]: sol[t] for t in range(nl) if sol[t] != 0}
    pi = [sol[nl + i] for i in range(n)]
    sigma = sol[si]
    return pi, lam, sigma

"""Exact vNM core-stability test for TU games.

Core is always INTERNALLY stable (core elements are mutually undominated), so
core is a vNM-stable set  <=>  it is EXTERNALLY stable: every imputation y not
in the core is dominated by some core element.

Domination (x dom y via S): x_i > y_i for all i in S and x(S) <= v(S). For a
CORE element x we always have x(S) >= v(S), so domination via S forces
x(S) = v(S) (x tight on S). Hence:

  y is dominated by the core  <=>  exists coalition S and core element x with
      x(S) = v(S)  and  x_i > y_i for all i in S.

is_dominated_by_core(y): for each proper S with v(S) > y(S), solve the exact LP
    maximize t  s.t.  x in core (x(T)>=v(T) all proper T, x(N)=v(N)),
                       x(S) <= v(S)  [=> x(S)=v(S)],  x_i - y_i >= t  (i in S).
  t>0 feasible  <=>  y dominated via S.

A certified NEGATIVE (core NOT stable): an imputation y, not in the core, that
is undominated by the core (all these LPs give t<=0).
"""
from fractions import Fraction as F
from tugame import Game, exact_lp_min, members


def is_imputation(game, y):
    if sum(y) != game.v[game.N]:
        return False
    return all(y[i] >= game.v[1 << i] for i in range(game.n))


def dominated_via(game, y, S):
    """Return (True, mingap) if the core dominates y via coalition S, else (False, opt).
    Solves: max t s.t. x in core, x(S)<=v(S), x_i-y_i>=t for i in S."""
    n, N, v = game.n, game.N, game.v
    mem = members(S, n)
    # variables: x_0..x_{n-1}, t   (index n = t)
    A_ub, b_ub = [], []
    # core: x(T) >= v(T)  ->  -x(T) <= -v(T)  for all proper nonempty T
    for T in range(1, N):
        row = [-1 if T >> i & 1 else 0 for i in range(n)] + [0]
        A_ub.append(row); b_ub.append(-v[T])
    # x(S) <= v(S)
    row = [1 if S >> i & 1 else 0 for i in range(n)] + [0]
    A_ub.append(row); b_ub.append(v[S])
    # x_i - y_i >= t  ->  -x_i + t <= -y_i
    for i in mem:
        row = [0] * (n + 1)
        row[i] = -1; row[n] = 1
        A_ub.append(row); b_ub.append(-y[i])
    # efficiency x(N)=v(N)
    A_eq = [[1] * n + [0]]; b_eq = [v[N]]
    # maximize t == minimize -t
    c = [0] * n + [-1]
    opt, sol = exact_lp_min(c, A_ub, b_ub, A_eq, b_eq)
    if opt is None or opt == 'unbounded':
        return False, None
    t = -opt
    return (t > 0), t


def is_dominated_by_core(game, y):
    """Return (True, S) if some coalition lets the core dominate y, else (False, None)."""
    n, N, v = game.n, game.N, game.v
    for S in range(1, N):
        yS = sum(y[i] for i in range(n) if S >> i & 1)
        if v[S] - yS > 0:                    # only such S can dominate y
            dom, _ = dominated_via(game, y, S)
            if dom:
                return True, S
    return False, None


def in_core(game, y):
    n, N, v = game.n, game.N, game.v
    if sum(y) != v[N]:
        return False
    return all(sum(y[i] for i in range(n) if S >> i & 1) >= v[S] for S in range(1, N))


def certify_undominated(game, y):
    """Full certificate that y is an imputation, outside the core, and undominated
    by the core (=> core is NOT vNM-stable). Returns dict or None if y fails."""
    n, N, v = game.n, game.N, game.v
    if not is_imputation(game, y):
        return None
    if in_core(game, y):
        return None
    # blocking coalitions (witness that y is outside the core)
    blocking = [S for S in range(1, N)
                if sum(y[i] for i in range(n) if S >> i & 1) < v[S]]
    # verify undominated: every proper S gives t<=0
    for S in range(1, N):
        dom, t = dominated_via(game, y, S)
        if dom:
            return None  # actually dominated
    return {
        "y": [str(a) for a in y],
        "is_imputation": True,
        "in_core": False,
        "blocking_coalitions": blocking,
        "undominated": True,
        "conclusion": "core is NOT vNM-stable",
    }

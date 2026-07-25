"""EXACT, FAST vNM core-stability check for BIG BOSS games, exploiting the box core
Core(v) = { x : x(N)=v(N), 0<=x_i<=M_i for non-boss i }  (MNPT parallelotope).

Domination of imputation y by the core: needs coalition S with boss in S and
S disjoint from the over-box set K={non-boss i: y_i>M_i} (a player i with x_i<=M_i<y_i
can't be beaten; and boss must be in S since v(S)=0 otherwise). Then check the box LP:
   exists x: 0<=x_j<=M_j (non-boss), sum x=v(N), x(S)=v(S), x_i>y_i for i in S.
We solve max t s.t. ... x_i-y_i>=t; dominated via S iff t>0.  Only n box bounds +
efficiency + |S| rows => tiny exact LP.

Stability decision: enumerate over-box sets K (nonempty subsets of non-boss). For each K,
solve for an imputation y with y_i>=M_i (i in K, at least one strict), y_j>=0, sum=v(N),
that is UNDOMINATED (for every admissible S, not dominated). We test the canonical
'hardest' y for K by an LP that pushes weight onto K and the low-marginal players and
strips the boss; then exact-certify undomination. A certified undominated y => NOT stable.
"""
from fractions import Fraction as F
from itertools import combinations
from tugame import Game, exact_lp_min, members
from bigboss import marginals, is_big_boss


def box_dominated_via(g, M, boss, y, S):
    """Exact: does a box (core) element tight on S strictly dominate y on S?"""
    n, N, v = g.n, g.N, g.v
    mem = members(S, n)
    # vars x_0..x_{n-1}, t
    A_ub, b_ub = [], []
    # box: x_j <= M_j and -x_j <= 0 for non-boss; boss free (0<=x_boss handled by efficiency+others)
    for j in range(n):
        if j != boss:
            row = [0] * (n + 1); row[j] = 1; A_ub.append(row); b_ub.append(M[j])   # x_j<=M_j
            row = [0] * (n + 1); row[j] = -1; A_ub.append(row); b_ub.append(0)      # x_j>=0
    # x_boss >= 0 (imputation floor v({boss}) could be >0; use v({boss}))
    rowb = [0] * (n + 1); rowb[boss] = -1; A_ub.append(rowb); b_ub.append(-v[1 << boss])
    # x(S) <= v(S)
    row = [1 if S >> i & 1 else 0 for i in range(n)] + [0]; A_ub.append(row); b_ub.append(v[S])
    # x_i - y_i >= t
    for i in mem:
        row = [0] * (n + 1); row[i] = -1; row[n] = 1; A_ub.append(row); b_ub.append(-y[i])
    A_eq = [[1] * n + [0]]; b_eq = [v[N]]
    c = [0] * n + [-1]
    opt, sol = exact_lp_min(c, A_ub, b_ub, A_eq, b_eq)
    if opt is None or opt == 'unbounded':
        return False
    return (-opt) > 0


def is_dominated_bigboss(g, M, boss, y):
    """Exact domination test using only admissible coalitions (boss in S, S disjoint K)."""
    n, N = g.n, g.N
    K = [i for i in range(n) if i != boss and y[i] > M[i]]
    Kmask = 0
    for i in K:
        Kmask |= 1 << i
    for S in range(1, N + 1):
        if not (S >> boss & 1):
            continue
        if S & Kmask:
            continue
        # need v(S)>y(S) for any chance
        yS = sum(y[i] for i in range(n) if S >> i & 1)
        if g.v[S] - yS <= 0:
            continue
        if box_dominated_via(g, M, boss, y, S):
            return True, S
    return False, None


def in_box(g, M, boss, y):
    n = g.n
    if sum(y) != g.v[g.N]:
        return False
    for j in range(n):
        if j != boss and (y[j] < 0 or y[j] > M[j]):
            return False
    return y[boss] >= g.v[1 << boss]


def find_escape_bigboss(g, boss=None):
    """Search for an undominated imputation outside the box (=> core not stable).
    Enumerate over-box sets K; for each, LP-construct a candidate then exact-test."""
    n, N, v = g.n, g.N, g.v
    if boss is None:
        boss = n - 1
    M = marginals(g)
    nonboss = [i for i in range(n) if i != boss]
    # candidate family: give players in K their box max + epsilon by stripping the boss.
    # We try, for each nonempty K, the point y_i = M_i + s_i (i in K), y_j = a_j (j not in K),
    # boss gets residual. Concretely we sweep a few canonical distributions.
    for r in range(1, len(nonboss) + 1):
        for K in combinations(nonboss, r):
            # canonical: put as much as possible on K (over box) + low-M players, strip boss
            # try y_i = M_i + delta for i in K; distribute the boss's core-min c across K
            c = v[N] - sum(M[i] for i in nonboss)      # boss core-min (>=0)
            if c <= 0:
                continue
            # strip the boss down to y_boss = v({boss}); give freed value c - v({boss}) to K
            free = c - v[1 << boss]
            if free <= 0:
                continue
            add = F(free, len(K))
            y = [F(0)] * n
            for j in nonboss:
                y[j] = F(M[j]) if j in K else F(0)
            for i in K:
                y[i] = F(M[i]) + add
            y[boss] = v[1 << boss]
            # fix efficiency exactly
            s = sum(y)
            if s != v[N]:
                y[boss] += v[N] - s
            if y[boss] < v[1 << boss]:
                continue
            # must be outside box
            if in_box(g, M, boss, y):
                continue
            if not all(y[i] >= 0 for i in range(n)):
                continue
            dom, _ = is_dominated_bigboss(g, M, boss, y)
            if not dom:
                return y, K
    return None, None

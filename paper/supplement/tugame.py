"""TU cooperative game toolkit — exact rational arithmetic.

Games on n players (n <= 8), coalitions as bitmasks 0..2^n-1.
v is a list of Fractions of length 2^n with v[0] == 0.
"""
from fractions import Fraction
from itertools import combinations

def popcount(m): return bin(m).count("1")

def members(S, n):
    return [i for i in range(n) if S >> i & 1]

class Game:
    def __init__(self, n, v):
        assert len(v) == 1 << n and v[0] == 0
        self.n = n
        self.v = [Fraction(x) for x in v]
        self.N = (1 << n) - 1

    def xS(self, x, S):
        return sum(x[i] for i in range(self.n) if S >> i & 1)

    def excess(self, x, S):
        return self.v[S] - self.xS(x, S)

    # ---------- properties (all exact) ----------
    def is_superadditive(self):
        for S in range(1, self.N + 1):
            T = (self.N ^ S)
            sub = T
            while sub:
                if self.v[S | sub] < self.v[S] + self.v[sub]:
                    return False
                sub = (sub - 1) & T
        return True

    def is_convex(self):
        # supermodular <=> local condition: for all S, i<j not in S:
        # v(S+i+j) + v(S) >= v(S+i) + v(S+j)
        n, v = self.n, self.v
        for S in range(self.N + 1):
            out = [i for i in range(n) if not (S >> i & 1)]
            for a in range(len(out)):
                for b in range(a + 1, len(out)):
                    i, j = 1 << out[a], 1 << out[b]
                    if v[S | i | j] + v[S] < v[S | i] + v[S | j]:
                        return False
        return True

    def is_monotone_game(self):
        # v(S) <= v(T) for S subset T -- check one-element extensions
        for S in range(self.N + 1):
            for i in range(self.n):
                if not (S >> i & 1) and self.v[S | (1 << i)] < self.v[S]:
                    return False
        return True

    def is_zero_normalized(self):
        return all(self.v[1 << i] == 0 for i in range(self.n))

    def in_core(self, x):
        if sum(x) != self.v[self.N]:
            return False
        return all(self.xS(x, S) >= self.v[S] for S in range(1, self.N))

    def core_violations(self, x):
        return [S for S in range(1, self.N) if self.xS(x, S) < self.v[S]]

    def subgame(self, T):
        """Restriction of v to player set T (bitmask). Returns Game on |T| players
        plus the list mapping new index -> old player."""
        mem = members(T, self.n)
        k = len(mem)
        v2 = [Fraction(0)] * (1 << k)
        for S2 in range(1, 1 << k):
            S = 0
            for j in range(k):
                if S2 >> j & 1:
                    S |= 1 << mem[j]
            v2[S2] = self.v[S]
        return Game(k, v2), mem

def exact_lp_min(c, A_ub=None, b_ub=None, A_eq=None, b_eq=None):
    """Exact rational LP: min c.x s.t. A_ub x <= b_ub, A_eq x = b_eq, x free.
    Returns (opt_value, x) as Fractions, or (None, None) if infeasible,
    ('unbounded', None) if unbounded."""
    from exactlp import exact_linprog
    status, opt, x = exact_linprog(c, A_ub, b_ub, A_eq, b_eq)
    if status == 'infeasible':
        return None, None
    if status == 'unbounded':
        return 'unbounded', None
    return opt, x

def is_balanced_game(game):
    """Core nonempty? Exact: min x(N) s.t. x(S) >= v(S) for all proper S; core
    nonempty iff opt <= v(N)."""
    n, N = game.n, game.N
    A_ub, b_ub = [], []
    for S in range(1, N):
        A_ub.append([-1 if S >> i & 1 else 0 for i in range(n)])
        b_ub.append(-game.v[S])
    c = [1] * n
    opt, x = exact_lp_min(c, A_ub, b_ub)
    if opt is None or opt == 'unbounded':
        return False
    return opt <= game.v[N]

def is_balanced_collection(coalitions, n):
    """Exact: does there exist delta_S > 0 with sum delta_S * 1_S = 1_N?
    LP: max t  s.t. delta_S >= t, sum delta_S 1_S = 1_N, delta >= 0. Balanced iff opt t > 0."""
    m = len(coalitions)
    if m == 0:
        return False
    # vars: delta_1..delta_m, t ; maximize t == minimize -t
    c = [0] * m + [-1]
    A_eq, b_eq = [], []
    for i in range(n):
        A_eq.append([1 if S >> i & 1 else 0 for S in coalitions] + [0])
        b_eq.append(1)
    A_ub, b_ub = [], []
    for j in range(m):
        row = [0] * (m + 1)
        row[j] = -1; row[m] = 1
        A_ub.append(row); b_ub.append(0)      # t - delta_j <= 0
        row2 = [0] * (m + 1); row2[j] = -1
        A_ub.append(row2); b_ub.append(0)     # -delta_j <= 0
    opt, sol = exact_lp_min(c, A_ub, b_ub, A_eq, b_eq)
    if opt is None or opt == 'unbounded':
        return False
    return -opt > 0

def kohlberg_certify_prenucleolus(game, x, weights=None):
    """Exact Kohlberg criterion for the (positively) weighted prenucleolus:
    x is it iff x(N)=v(N) and for every threshold alpha over weighted excesses
    e(S,x)/w_S, D(alpha) = {S proper : e_w(S,x) >= alpha} is balanced.
    (Positive weights only rescale the multipliers, so plain balancedness of the
    level sets remains the right condition; the level SETS themselves change.)
    Returns (True, None) or (False, reason)."""
    n, N = game.n, game.N
    if sum(x) != game.v[N]:
        return False, "not efficient"
    if weights is None:
        exc = {S: game.excess(x, S) for S in range(1, N)}
    else:
        exc = {S: game.excess(x, S) / weights[S] for S in range(1, N)}
    levels = sorted(set(exc.values()), reverse=True)
    D = []
    for alpha in levels:
        D = [S for S in range(1, N) if exc[S] >= alpha]
        if not is_balanced_collection(D, n):
            return False, f"D(alpha={alpha}) of size {len(D)} not balanced"
    return True, None

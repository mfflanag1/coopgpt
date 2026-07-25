"""Leximin-above-floors core selection phi(v).

phi(v) := the core point that lexicographically maximizes the ascending-sorted
vector of (x_i - v({i})) over core(v). Single-valued (leximin over a polytope).
Computed by the Maschler-style iterative LP scheme over PLAYER COORDINATES:
  repeat: maximize the common lower level s of (x_i - m_i) over free players;
          fix (pin) every free player that cannot exceed m_i + s on the level
          optimal face; continue until all players pinned.

Two implementations: float (scipy, screening) and exact (Fraction LP, certifying).
m_i = v({i}); on exact games m_i = min_core x_i.
"""
from fractions import Fraction as F
from scipy.optimize import linprog
from tugame import exact_lp_min

# ---------------- float ----------------
def leximin_core_float(n, v, tol=1e-7):
    N = (1 << n) - 1
    m = [v[1 << i] for i in range(n)]
    fixed = {}                        # player -> value
    # base core constraints (proper S): x(S) >= v(S)
    def solve_level(free):
        # vars: x_0..x_{n-1}, s  ; maximize s
        nv = n + 1; si = n
        A, b = [], []
        for S in range(1, N):
            row = [0.0] * nv
            for i in range(n):
                if S >> i & 1:
                    row[i] = -1.0
            A.append(row); b.append(-float(v[S]))
        for j, val in fixed.items():   # x_j = val
            pass
        Aeq = [[1.0] * n + [0.0]]; beq = [float(v[N])]
        for j, val in fixed.items():
            row = [0.0] * nv; row[j] = 1.0
            Aeq.append(row); beq.append(val)
        for i in free:                 # x_i - s >= m_i
            row = [0.0] * nv; row[i] = -1.0; row[si] = 1.0
            A.append(row); b.append(-m[i])
        c = [0.0] * nv; c[si] = -1.0
        r = linprog(c, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq, bounds=[(None, None)] * nv, method="highs")
        return r
    def max_xi(i, free, s):
        nv = n
        A, b = [], []
        for S in range(1, N):
            row = [0.0] * nv
            for k in range(n):
                if S >> k & 1:
                    row[k] = -1.0
            A.append(row); b.append(-float(v[S]))
        Aeq = [[1.0] * n]; beq = [float(v[N])]
        for j, val in fixed.items():
            row = [0.0] * nv; row[j] = 1.0
            Aeq.append(row); beq.append(val)
        for k in free:
            row = [0.0] * nv; row[k] = -1.0
            A.append(row); b.append(-(m[k] + s))
        c = [0.0] * nv; c[i] = -1.0
        r = linprog(c, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq, bounds=[(None, None)] * nv, method="highs")
        return None if not r.success else -r.fun
    free = list(range(n))
    guard = 0
    while free and guard < n + 2:
        guard += 1
        r = solve_level(free)
        if not r.success:
            return None
        s = -r.fun
        pinned = []
        for i in list(free):
            mx = max_xi(i, free, s)
            if mx is None:
                return None
            if mx <= m[i] + s + tol:
                pinned.append(i)
        if not pinned:                 # numerical stall: pin the argmin
            xs = r.x
            i0 = min(free, key=lambda i: xs[i] - m[i])
            pinned = [i0]
        for i in pinned:
            fixed[i] = m[i] + s
            free.remove(i)
    return [fixed[i] for i in range(n)]

# ---------------- exact ----------------
def leximin_core_exact(g):
    n, N, v = g.n, g.N, g.v
    m = [v[1 << i] for i in range(n)]
    fixed = {}
    def core_rows():
        A, b = [], []
        for S in range(1, N):
            A.append([F(-1) if S >> i & 1 else F(0) for i in range(n)]); b.append(-v[S])
        return A, b
    def solve_level(free):
        nv = n + 1; si = n
        A, b = [], []
        for S in range(1, N):
            row = [F(0)] * nv
            for i in range(n):
                if S >> i & 1:
                    row[i] = F(-1)
            A.append(row); b.append(-v[S])
        Aeq = [[F(1)] * n + [F(0)]]; beq = [v[N]]
        for j, val in fixed.items():
            row = [F(0)] * nv; row[j] = F(1); Aeq.append(row); beq.append(val)
        for i in free:
            row = [F(0)] * nv; row[i] = F(-1); row[si] = F(1); A.append(row); b.append(-m[i])
        c = [F(0)] * nv; c[si] = F(-1)
        opt, x = exact_lp_min(c, A, b, Aeq, beq)
        return opt, x
    def max_xi(i, free, s):
        nv = n
        A, b = [], []
        for S in range(1, N):
            A.append([F(-1) if S >> k & 1 else F(0) for k in range(n)]); b.append(-v[S])
        Aeq = [[F(1)] * n]; beq = [v[N]]
        for j, val in fixed.items():
            row = [F(0)] * nv; row[j] = F(1); Aeq.append(row); beq.append(val)
        for k in free:
            row = [F(0)] * nv; row[k] = F(-1); A.append(row); b.append(-(m[k] + s))
        c = [F(0)] * nv; c[i] = F(-1)
        opt, x = exact_lp_min(c, A, b, Aeq, beq)
        return None if opt is None or opt == 'unbounded' else -opt
    free = list(range(n)); guard = 0
    while free and guard < n + 2:
        guard += 1
        opt, x = solve_level(free)
        if opt is None or opt == 'unbounded':
            return None
        s = -opt
        pinned = []
        for i in list(free):
            mx = max_xi(i, free, s)
            if mx is None:
                return None
            if mx == m[i] + s:
                pinned.append(i)
        if not pinned:
            i0 = min(free, key=lambda i: x[i] - m[i])
            pinned = [i0]
        for i in pinned:
            fixed[i] = m[i] + s
            free.remove(i)
    return [fixed[i] for i in range(n)]

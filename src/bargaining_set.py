"""Exact Davis-Maschler (ADM) bargaining set membership oracle for the grand coalition.

Solution concept: IM_1^(i)(N,v), the individually-rational classical bargaining set.
x in BS iff x is an imputation (efficient + IR) and NO justified objection exists.

Objection of i against j at x: (S,y) with i in S, j not in S, y(S)=v(S), y_i>x_i, y_k>=x_k (k in S).
Counterobjection (T,z): j in T, i not in T, z(T)=v(T), z_k>=y_k (k in S∩T), z_k>=x_k (k in T\S).
A counterobjection via T exists  iff  v(T) >= y(S∩T) + x(T\S).
Objection is justified iff for ALL T (j in T, i not in T): v(T) - y(S∩T) - x(T\S) < 0.

x NOT in BS iff exists (i,j,S) with i in S, j not in S, v(S) > x(S), and a feasible
objection y minimizing max_T [v(T) - y(S∩T) - x(T\S)] achieves a value < 0.
LP per (i,j,S):
    minimize  delta
    s.t.  v(T) - y(S∩T) - x(T\S) <= delta   for all T with j in T, i not in T
          y_k >= x_k  (k in S)
          sum_{k in S} y_k = v(S)
Strictness y_i > x_i needs only v(S) > x(S) (perturbation argument, see wildcard_notes).

All exact (Fraction) via exactlp two-phase simplex.
"""
from fractions import Fraction as F
from tugame import Game, exact_lp_min


def members(S, n):
    return [i for i in range(n) if S >> i & 1]


def justified_objection(game, x, i, j):
    """Return (S, y, delta) for a justified objection of i against j at x, or None.
    A justified objection certifies x is NOT in the bargaining set."""
    n, N, v = game.n, game.N, game.v
    # candidate objecting coalitions S: i in S, j not in S, proper, v(S) > x(S)
    for S in range(1, N + 1):
        if not (S >> i & 1) or (S >> j & 1):
            continue
        if S == N:
            continue
        xS = sum(x[k] for k in range(n) if S >> k & 1)
        if v[S] <= xS:                      # no room for a strict objection via S
            continue
        Smem = members(S, n)
        idx = {k: t for t, k in enumerate(Smem)}   # var index of y_k
        m = len(Smem)
        # counter coalitions T: j in T, i not in T (proper or grand; T=N excluded since i in N)
        A_ub, b_ub = [], []
        for T in range(1, N + 1):
            if not (T >> j & 1) or (T >> i & 1):
                continue
            # v(T) - sum_{k in S∩T} y_k - x(T\S) <= delta
            row = [F(0)] * (m + 1)
            for k in Smem:
                if T >> k & 1:
                    row[idx[k]] = F(-1)
            row[m] = F(-1)                  # -delta
            xTminusS = sum(x[k] for k in range(n) if (T >> k & 1) and not (S >> k & 1))
            A_ub.append(row)
            b_ub.append(x_neg := (xTminusS - v[T]))  # RHS = x(T\S) - v(T)
        # y_k >= x_k  ->  -y_k <= -x_k
        for k in Smem:
            row = [F(0)] * (m + 1)
            row[idx[k]] = F(-1)
            A_ub.append(row)
            b_ub.append(-x[k])
        # equality sum y_k = v(S)
        A_eq = [[F(1)] * m + [F(0)]]
        b_eq = [v[S]]
        c = [F(0)] * m + [F(1)]             # minimize delta
        opt, sol = exact_lp_min(c, A_ub, b_ub, A_eq, b_eq)
        if opt is None or opt == 'unbounded':
            continue
        if opt < 0:
            y = {Smem[t]: sol[t] for t in range(m)}
            return (S, y, opt)
    return None


def in_bargaining_set(game, x):
    """True iff imputation x is in the ADM bargaining set IM_1^(i). Also returns
    a witness justified objection (i,j,S,y,delta) when False."""
    n, N, v = game.n, game.N, game.v
    if sum(x) != v[N]:
        return False, ("not efficient", None)
    for i in range(n):                       # individual rationality
        if x[i] < v[1 << i]:
            return False, ("not IR", i)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            jo = justified_objection(game, x, i, j)
            if jo is not None:
                S, y, delta = jo
                return False, (i, j, S, y, delta)
    return True, None


def is_in_core(game, x):
    return game.in_core(x)


def float_has_justified_objection(game, x, tol=1e-7):
    """Fast scipy screen: True if x has a clear justified objection (=> NOT in BS).
    Conservative: only returns True when a justified objection is found with margin
    below -tol, so it never wrongly rejects a genuine BS point (exact oracle confirms
    survivors). Returns False if x looks possibly-in-BS."""
    import numpy as np
    from scipy.optimize import linprog
    n, N, v = game.n, game.N, [float(t) for t in game.v]
    xf = [float(t) for t in x]
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            for S in range(1, N):
                if not (S >> i & 1) or (S >> j & 1):
                    continue
                xS = sum(xf[k] for k in range(n) if S >> k & 1)
                if v[S] <= xS + tol:
                    continue
                Smem = [k for k in range(n) if S >> k & 1]
                idx = {k: t for t, k in enumerate(Smem)}
                m = len(Smem)
                A_ub, b_ub = [], []
                for T in range(1, N + 1):
                    if not (T >> j & 1) or (T >> i & 1):
                        continue
                    row = [0.0] * (m + 1)
                    for k in Smem:
                        if T >> k & 1:
                            row[idx[k]] = -1.0
                    row[m] = -1.0
                    xTmS = sum(xf[k] for k in range(n) if (T >> k & 1) and not (S >> k & 1))
                    A_ub.append(row); b_ub.append(xTmS - v[T])
                for k in Smem:
                    row = [0.0] * (m + 1); row[idx[k]] = -1.0
                    A_ub.append(row); b_ub.append(-xf[k])
                A_eq = [[1.0] * m + [0.0]]; b_eq = [v[S]]
                c = [0.0] * m + [1.0]
                res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                              A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                              bounds=[(None, None)] * (m + 1), method="highs")
                if res.success and res.fun < -tol:
                    return True
    return False


if __name__ == "__main__":
    # Validation on the 2025 Atay-Nunez-Solymosi minimal many-to-one example.
    firms = {0, 1}; workers = {2, 3, 4}; n = 5
    def worth(S):
        nf = sum(1 for k in firms if S >> k & 1)
        nw = sum(1 for k in workers if S >> k & 1)
        return 0 if nf == 0 or nw == 0 else min(nw, 2 * nf)
    g = Game(n, [F(worth(S)) for S in range(1 << n)])
    core_pt = [F(0), F(0), F(1), F(1), F(1)]
    ker_pt = [F(1), F(1), F(1, 3), F(1, 3), F(1, 3)]
    bad_pt = [F(3), F(0), F(0), F(0), F(0)]
    print("core point (0,0;1,1,1): in_core", g.in_core(core_pt),
          "in_BS", in_bargaining_set(g, core_pt)[0])
    inbs, w = in_bargaining_set(g, ker_pt)
    print("kernel point (1,1;1/3,1/3,1/3): in_core", g.in_core(ker_pt),
          "in_BS", inbs, "(paper: should be True, outside core)")
    inbs2, w2 = in_bargaining_set(g, bad_pt)
    print("bad point (3,0;0,0,0): in_core", g.in_core(bad_pt),
          "in_BS", inbs2, "witness", w2)

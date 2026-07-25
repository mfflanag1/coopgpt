"""Fully exact prenucleolus via successive LPs over Fractions — independent of
the float screening path AND of the Kohlberg certifier. For final witnesses only.

Maschler scheme: repeatedly min t s.t. v(S) - x(S) <= t on unfixed coalitions,
x(N) = v(N), fixed coalitions pinned. A coalition is fixed at level t_k iff its
excess is t_k in every optimal solution (per-coalition exact test LP).
"""
from fractions import Fraction as F
from tugame import exact_lp_min

def exact_prenucleolus(game):
    n, N = game.n, game.N
    proper = list(range(1, N))
    row = {S: [1 if S >> i & 1 else 0 for i in range(n)] for S in proper}
    fixed = {}
    unfixed = set(proper)
    while unfixed:
        A_ub = [[-a for a in row[S]] + [-1] for S in unfixed]
        b_ub = [-game.v[S] for S in unfixed]
        A_eq = [[1] * n + [0]]
        b_eq = [game.v[N]]
        for S, lev in fixed.items():
            A_eq.append([-a for a in row[S]] + [0]); b_eq.append(lev - game.v[S])
        c = [0] * n + [1]
        opt, sol = exact_lp_min(c, A_ub, b_ub, A_eq, b_eq)
        if opt is None or opt == 'unbounded':
            return None
        t_k = opt
        newly = []
        for S in list(unfixed):
            # min excess of S subject to t = t_k: maximize x(S)
            A_eq2 = A_eq + [[0] * n + [1]]
            b_eq2 = b_eq + [t_k]
            c2 = [-a for a in row[S]] + [0]
            opt2, _ = exact_lp_min(c2, A_ub, b_ub, A_eq2, b_eq2)
            if opt2 is None or opt2 == 'unbounded':
                newly.append(S); continue
            ex_min = game.v[S] + opt2          # v(S) - max x(S)
            if ex_min == t_k:
                newly.append(S)
        if not newly:
            return None                        # should not happen
        for S in newly:
            fixed[S] = t_k
            unfixed.discard(S)
    A_eq = [[1] * n + [0]]
    b_eq = [game.v[N]]
    for S, lev in fixed.items():
        A_eq.append([-a for a in row[S]] + [0]); b_eq.append(lev - game.v[S])
    opt, sol = exact_lp_min([0] * (n + 1), None, None, A_eq, b_eq)
    if sol is None:
        return None
    return sol[:n]

if __name__ == "__main__":
    from permutation import permutation_game
    K = [[0, 7, 0, 0], [1, 0, 0, 1], [1, 0, 0, 0], [0, 9, 1, 0]]
    K2 = [r[:] for r in K]; K2[3][2] += 1
    x = exact_prenucleolus(permutation_game(K))
    y = exact_prenucleolus(permutation_game(K2))
    print("independent exact x =", [str(u) for u in x])
    print("independent exact y =", [str(u) for u in y])
    assert x == [F(1, 2), F(33, 4), F(1, 2), F(7, 4)], "MISMATCH before-game"
    assert y == [F(2, 3), F(23, 3), F(1, 3), F(7, 3)], "MISMATCH after-game"
    print("WITNESS CONFIRMED by fully independent exact successive-LP path")

"""SD-prenucleolus (Arin-Katsev), from the verbatim recursion in the 2018
Springer chapter (reconstructed by Max from machine-readable text, repaired
against the chapter's worked example).

Pointwise SD-satisfaction recursion for given efficient x:
  H_0 = empty. Round k: for each unfixed proper S,
    H(S)   = union of fixed T with T subseteq S      (a PLAYER set)
    f(i,S) = min{ F(T) : T fixed, i in T subseteq S }  for i in H(S)
    if H(S) != S  (relevant):   F_H(S) = (x(S)-v(S) - sum_{i in H(S)} f(i,S)) / (|S|-|H(S)|)
    if H(S) == S  (completed):  F_H(S) = x(S)-v(S) - sum_{i in S} f(i,S) + max_{i in S} f(i,S)
  alpha_k = min over unfixed of F_H(S); ALL minimizers get fixed at alpha_k. Repeat.

SD-prenucleolus: the efficient x whose sorted-ascending satisfaction vector is
lexicographically maximal. Computed by a successive-LP scheme (each stage's
candidate formulas are linear in x since fixed values are constants), then
certified by (a) pointwise-recursion consistency and (b) the SD-Kohlberg-style
balancedness of every low-satisfaction level set.
"""
from fractions import Fraction as F
from tugame import Game, popcount, members, is_balanced_collection, exact_lp_min
import numpy as np
from scipy.optimize import linprog as flinprog

# ---------------------------------------------------------------- pointwise
def sd_satisfactions(game, x):
    """Exact SD-satisfaction vector F(S;x) as dict S->Fraction. x: list of Fractions."""
    n, N = game.n, game.N
    proper = list(range(1, N))
    fixed = {}
    xs = {S: game.xS(x, S) for S in proper}
    while len(fixed) < len(proper):
        best, arg = None, []
        for S in proper:
            if S in fixed:
                continue
            fvals = {}
            for T, FT in fixed.items():
                if T & ~S == 0:
                    for i in members(T, n):
                        if i not in fvals or FT < fvals[i]:
                            fvals[i] = FT
            surplus = xs[S] - game.v[S]
            free = popcount(S) - len(fvals)
            if free > 0:
                cand = (surplus - sum(fvals.values())) / free
            else:
                cand = surplus - sum(fvals.values()) + max(fvals.values())
            if best is None or cand < best:
                best, arg = cand, [S]
            elif cand == best:
                arg.append(S)
        for S in arg:
            fixed[S] = best
    return fixed

# ------------------------------------------------- successive-LP computation
def _stage_forms(game, fixed_forms, fixed_vals, unfixed, exact=True):
    """Linear candidate form for each unfixed S given fixed constants:
    returns dict S -> (kind, coeff_scale, const) meaning:
      relevant:  x(S) - k*t >= v(S) + sum_f      (kind='rel', k=free count)
      completed: x(S) -   t >= v(S) + sum_f - max_f  (kind='comp')
    encoded as (k_or_1, rhs_const)."""
    n = game.n
    out = {}
    for S in unfixed:
        fvals = {}
        for T, FT in fixed_vals.items():
            if T & ~S == 0:
                for i in members(T, n):
                    if i not in fvals or FT < fvals[i]:
                        fvals[i] = FT
        free = popcount(S) - len(fvals)
        if free > 0:
            out[S] = (free, game.v[S] + sum(fvals.values()))
        else:
            out[S] = (1, game.v[S] + sum(fvals.values()) - max(fvals.values()))
    return out

def sd_prenucleolus_float(game):
    n, N = game.n, game.N
    proper = list(range(1, N))
    rowS = {S: np.array([1.0 if S >> i & 1 else 0.0 for i in range(n)]) for S in proper}
    fixed_vals = {}                 # S -> float alpha
    pinned = []                     # (S, k, rhs) equality: x(S) - k*alpha = rhs
    unfixed = set(proper)
    for _ in range(2 * len(proper) + 2):
        if not unfixed:
            break
        forms = {S: (k, float(r)) for S, (k, r) in
                 _stage_forms(game, None, fixed_vals, unfixed).items()}
        # LP: max t  s.t. x(S) - k_S t >= rhs_S  (unfixed), pinned equalities, x(N)=v(N)
        A_ub, b_ub = [], []
        for S in unfixed:
            k, rhs = forms[S]
            A_ub.append(np.append(-rowS[S], k)); b_ub.append(-rhs)
        A_eq = [np.append(np.ones(n), 0.0)]; b_eq = [float(game.v[N])]
        for (S, k, rhs, alpha) in pinned:
            A_eq.append(np.append(rowS[S], 0.0)); b_eq.append(rhs + k * alpha)
        c = np.zeros(n + 1); c[n] = -1.0     # maximize t
        res = flinprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                       A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                       bounds=[(None, None)] * (n + 1), method="highs")
        if not res.success:
            return None
        t_k = res.x[n]
        newly = []
        for S in list(unfixed):
            k, rhs = forms[S]
            sat = (rowS[S] @ res.x[:n] - rhs) / k
            if sat < t_k + 1e-7:
                # forced? maximize sat_S with t pinned at t_k
                A_eq2 = A_eq + [np.append(np.zeros(n), 1.0)]; b_eq2 = b_eq + [t_k]
                res2 = flinprog(np.append(-rowS[S] / k, 0.0), A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                                A_eq=np.array(A_eq2), b_eq=np.array(b_eq2),
                                bounds=[(None, None)] * (n + 1), method="highs")
                if res2 is None or not res2.success:
                    newly.append((S, k, rhs)); continue
                if (-res2.fun - rhs / k) < t_k + 1e-7:
                    newly.append((S, k, rhs))
        if not newly:
            newly = [(S, forms[S][0], forms[S][1]) for S in unfixed
                     if (rowS[S] @ res.x[:n] - forms[S][1]) / forms[S][0] < t_k + 1e-7]
        for (S, k, rhs) in newly:
            fixed_vals[S] = t_k
            pinned.append((S, k, rhs, t_k))
            unfixed.discard(S)
    A_eq = [np.append(np.ones(n), 0.0)]; b_eq = [float(game.v[N])]
    for (S, k, rhs, alpha) in pinned:
        A_eq.append(np.append(rowS[S], 0.0)); b_eq.append(rhs + k * alpha)
    res = flinprog(np.zeros(n + 1), A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                   bounds=[(None, None)] * (n + 1), method="highs")
    if not res.success:
        return None
    return res.x[:n]

# ---------------------------------------------------------------- certifier
def sd_kohlberg_certify(game, x):
    """x efficient, Fractions. Certificate:
    for every level alpha of the exact SD-satisfaction vector F(.;x),
    D(alpha) = {S : F(S;x) <= alpha} must be a balanced collection.
    (SD analogue of Kohlberg; level sets from the LOW end since satisfactions
    are maximized.) Returns (True, F) or (False, reason)."""
    if sum(x) != game.v[game.N]:
        return False, "not efficient"
    Fx = sd_satisfactions(game, x)
    levels = sorted(set(Fx.values()))
    for alpha in levels:
        D = [S for S, val in Fx.items() if val <= alpha]
        if not is_balanced_collection(D, game.n):
            return False, f"D(alpha={alpha}) size {len(D)} not balanced"
    return True, Fx

def certified_sd_prenucleolus(game, max_den=10 ** 8):
    from nucleolus import rationalize
    xf = sd_prenucleolus_float(game)
    if xf is None:
        return None
    x = rationalize(xf, game)
    if x is None:
        return None
    ok, info = sd_kohlberg_certify(game, x)
    if ok:
        return x
    return None

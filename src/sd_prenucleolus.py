"""The SD-prenucleolus (Arin & Katsev 2011, "The SD-prenucleolus for TU games",
UPV/EHU Working Paper IL.56/11; publ. MMOR 2014 / IJGT 2016).

Definition reconstructed VERBATIM from the primary source (recovered via the
Internet Archive capture of addi.ehu.es/bitstream/10810/6230/1/IL201156.pdf).

Satisfaction vector F(S,x)  (Sec 3.2, "The Algorithm"):
  Build a collection H of "settled" coalitions, round by round, H_0 = {}.
  For a coalition S let  sigma_H(S) = union of settled T in H with T subset S,
  and  f(i,S) = min { F(U) : U in H, i in U subset S }  for i in sigma_H(S).
    * relevant     (sigma_H(S) != S):
        F(S) = [ x(S) - v(S) - sum_{i in sigma} f(i,S) ] / ( |S| - |sigma| )
    * non-relevant (sigma_H(S) == S):
        F(S) = x(S) - v(S) - sum_{i in S} f(i,S) + max_{i in S} f(i,S)
  Each round settle every unsettled S attaining the minimum current F(S).

SD-prenucleolus: the unique efficient x whose satisfaction vector, sorted in
NON-DECREASING order, lexicographically DOMINATES that of every other efficient
y (Def 4.1).  On monotonic veto games it coincides with the Arin-Feltkamp serial
rule (Sec 6) -- the validation anchor.
"""
from fractions import Fraction as F
from tugame import Game, exact_lp_min

# ---------------------------------------------------------------- satisfaction
def _sigma_and_f(S, H, level, n):
    """sigma_H(S) (bitmask) and f(i,S) for each covered player i."""
    sigma = 0
    for T in H:
        if T & S == T:            # T subset of S
            sigma |= T
    fvals = {}
    for i in range(n):
        if sigma >> i & 1:
            best = None
            for U in H:
                if (U >> i & 1) and (U & S == U) and (best is None or level[U] < best):
                    best = level[U]
            fvals[i] = best
    return sigma, fvals

def sd_satisfaction(game, x):
    """Return dict {S: F(S,x)} over proper nonempty coalitions S (1..N-1)."""
    n, N = game.n, game.N
    x = [F(v) for v in x]
    def xS(S): return sum(x[i] for i in range(n) if S >> i & 1)
    H, level = set(), {}
    unsettled = set(range(1, N))
    while unsettled:
        G = {}
        for S in unsettled:
            sigma, fvals = _sigma_and_f(S, H, level, n)
            popS = bin(S).count("1")
            if sigma == S:                                  # non-relevant
                sumf = sum(fvals.values())
                G[S] = xS(S) - game.v[S] - sumf + max(fvals.values())
            else:                                           # relevant
                sumf = sum(fvals.values())
                G[S] = (xS(S) - game.v[S] - sumf) / (popS - bin(sigma).count("1"))
        m = min(G.values())
        for S in [s for s in unsettled if G[s] == m]:
            level[S] = m
            H.add(S)
            unsettled.discard(S)
    return level

# ------------------------------------------------- affine form of F_H(S)(x)
def _affine(S, H, level, game):
    """Coefficients (a[0..n-1], b) with F_H(S)(x) = a.x + b, given settled H."""
    n = game.n
    sigma, fvals = _sigma_and_f(S, H, level, n)
    popS, popsig = bin(S).count("1"), bin(sigma).count("1")
    if sigma == S:                                          # non-relevant
        sumf = sum(fvals.values())
        a = [F(1) if S >> i & 1 else F(0) for i in range(n)]
        b = -(game.v[S] + sumf - max(fvals.values()))
    else:                                                   # relevant
        d = popS - popsig
        sumf = sum(fvals.values())
        a = [F(1, d) if S >> i & 1 else F(0) for i in range(n)]
        b = -(game.v[S] + sumf) / d
    return a, b

# -------------------------------------------------------- SD-prenucleolus (LP)
def sd_prenucleolus(game):
    """Exact SD-prenucleolus via successive LPs (maximise the minimum
    satisfaction, freeze forced coalitions, repeat). All rational."""
    n, N = game.n, game.N
    proper = list(range(1, N))
    settled = set()                 # coalitions with frozen satisfaction
    s_expr = {}                     # S -> (a,b) affine form used to freeze it
    s_lvl = {}                      # S -> level (Fraction)
    unsettled = set(proper)

    def eq_rows():
        A, b = [[F(1)] * n + [F(0)]], [game.v[N]]     # x(N)=v(N); last col=alpha
        for S in settled:
            a, c = s_expr[S]
            A.append(list(a) + [F(0)]); b.append(s_lvl[S] - c)
        return A, b

    while unsettled:
        expr = {S: _affine(S, settled, s_lvl, game) for S in unsettled}
        # LP1: maximise alpha  s.t.  a_S.x + b_S >= alpha (unsettled), eqs.
        A_eq, b_eq = eq_rows()
        A_ub, b_ub = [], []
        for S in unsettled:
            a, c = expr[S]
            A_ub.append([-ai for ai in a] + [F(1)]); b_ub.append(c)  # -a.x+alpha<=b
        c_obj = [F(0)] * n + [F(-1)]                                 # min -alpha
        opt, sol = exact_lp_min(c_obj, A_ub, b_ub, A_eq, b_eq)
        if opt is None or opt == 'unbounded':
            return None
        alpha = -opt
        xv = sol[:n]
        # forced test: F_S >= alpha on the whole face; S is frozen iff it can
        # NOT exceed alpha, i.e. max_face F_S == alpha (mirror of the nucleolus
        # fixing excess at its minimum on the optimal face). A forced coalition
        # is tight at every optimum, so only test the vertex-tight ones.
        A_ub2, b_ub2 = [], []
        for S in unsettled:
            a, c = expr[S]
            A_ub2.append([-ai for ai in a]); b_ub2.append(c - alpha)  # a.x>=alpha-c
        tight = [S for S in unsettled
                 if sum(expr[S][0][i] * xv[i] for i in range(n)) + expr[S][1] == alpha]
        newly = []
        for S in tight:
            a, c = expr[S]
            o2, _ = exact_lp_min([-ai for ai in a], A_ub2, b_ub2, A_eq, b_eq)
            if o2 is not None and o2 != 'unbounded' and (-o2) + c == alpha:
                newly.append(S)
        if not newly:
            return None                     # degenerate; should not happen
        for S in newly:
            s_expr[S] = expr[S]; s_lvl[S] = alpha
            settled.add(S); unsettled.discard(S)

    A_eq, b_eq = eq_rows()
    _, x = exact_lp_min([F(0)] * n + [F(0)], None, None, A_eq, b_eq)
    return None if x is None else x[:n]

# ----------------------------------------------- independent SD-Kohlberg check
def sd_kohlberg(game, x):
    """Arin-Katsev criterion (proof of core-stability thm, p.20): x is the
    SD-prenucleolus iff for every level alpha the cumulative lower set
    B_alpha = {S proper : F(S,x) <= alpha} is 'balanced', i.e. there is NO
    y != 0 with y(N)=0, y(S)>=0 for all S in B_alpha and y(S)>0 for some such S.
    Returns (True,None) or (False,reason). Independent of the LP search path."""
    n, N = game.n, game.N
    if sum(F(v) for v in x) != game.v[N]:
        return False, "not efficient"
    Fv = sd_satisfaction(game, x)
    for alpha in sorted(set(Fv.values())):
        B = [S for S in range(1, N) if Fv[S] <= alpha]
        # max sum_{S in B}(y(S)) s.t. y(N)=0, 0<=y(S)<=1 for S in B.  >0 => not balanced
        A_ub, b_ub = [], []
        for S in B:
            A_ub.append([-1 if S >> i & 1 else 0 for i in range(n)]); b_ub.append(0)   # y(S)>=0
            A_ub.append([1 if S >> i & 1 else 0 for i in range(n)]);  b_ub.append(1)   # y(S)<=1
        A_eq, b_eq = [[1] * n], [0]
        c = [F(0)] * n
        for S in B:
            for i in range(n):
                if S >> i & 1:
                    c[i] -= 1                     # minimise -sum y(S)
        opt, _ = exact_lp_min(c, A_ub, b_ub, A_eq, b_eq)
        if opt is not None and opt != 'unbounded' and -opt > 0:
            return False, f"B(alpha={alpha}) size {len(B)} not balanced (gap {-opt})"
    return True, None


if __name__ == "__main__":
    # -- Paper Sec 3.2 worked 3-person example: reproduce F(S,x) at x=(5,1,0).
    v = [F(0)] * 8
    v[0b011] = 4     # {1,2}
    v[0b101] = 4     # {1,3}
    v[0b110] = -10   # {2,3}
    v[0b111] = 6
    g = Game(3, v)
    Fv = sd_satisfaction(g, [F(5), F(1), F(0)])
    got = {tuple(i + 1 for i in range(3) if S >> i & 1): Fv[S] for S in Fv}
    print("F at (5,1,0):", {k: str(val) for k, val in sorted(got.items())})
    assert got[(1,)] == 5 and got[(2,)] == 1 and got[(3,)] == 0
    assert got[(1, 2)] == 1 and got[(1, 3)] == 1 and got[(2, 3)] == 11
    print("satisfaction algorithm reproduces paper example EXACTLY")

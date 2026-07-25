"""Procedural egalitarian solution (PES) and egalitarian stability.

Dietzenbacher (GEB 127, 2021) / Dietzenbacher-Borm-Hendrickx (2017). Exact rationals.

Egalitarian procedure. P^0 = empty. At step k, for each nonempty S:
  chi_i^k(S) = gamma_i^{k-1}                                    if i in S ∩ P^{k-1}
             = (v(S) - sum_{j in S∩P^{k-1}} gamma_j^{k-1}) / |S\P^{k-1}|  else.
  A^k = { S : sum_{i in S} chi_i^k(S) = v(S)  AND
              for all i in S, for all T ∋ i: chi_i^k(T) <= chi_i^k(S) }
      = { S : (fully-fixed => sum = v(S)) AND every member attains its
              global max chi over all coalitions containing it }.
  P^k = union of A^k;  gamma_i^k = chi_i^k(S) for i in P^k (= that max).
Iterate until P^k = N.  Claims gamma-hat, admissible collection A-hat = final A^k.

EGALITARIAN STABLE  iff  N in A-hat  iff  (at termination) sum(claims) = v(N).

PES: strong claimants D = players in EVERY inclusion-maximal coalition of A-hat.
Strong get their claim; others get min(claim, lambda), lambda s.t. total = v(N).
"""
from fractions import Fraction as F


def members(S, n):
    return [i for i in range(n) if S >> i & 1]


def egalitarian_procedure(game):
    """Returns (claims: list[Fraction] length n, A_hat: list[int coalition masks],
    is_ES: bool)."""
    n, N, v = game.n, game.N, game.v
    P = 0            # bitmask of fixed players
    gamma = {}       # i -> Fraction for i in P
    A_hat, claims = [], {}
    for _step in range(1, n + 2):
        # chi_i^step(S) for every nonempty S, and the per-player global max.
        chi = {}
        maxchi = {i: None for i in range(n)}
        for S in range(1, N + 1):
            mem = members(S, n)
            fixed = [i for i in mem if P >> i & 1]
            unfixed = [i for i in mem if not (P >> i & 1)]
            sum_fixed = sum((gamma[i] for i in fixed), F(0))
            d = {}
            if unfixed:
                share = (v[S] - sum_fixed) / len(unfixed)
                for i in fixed:
                    d[i] = gamma[i]
                for i in unfixed:
                    d[i] = share
            else:
                for i in fixed:
                    d[i] = gamma[i]
            chi[S] = d
            for i in mem:
                if maxchi[i] is None or d[i] > maxchi[i]:
                    maxchi[i] = d[i]
        # A^step: sum-condition + every member attains its global max.
        A = []
        for S in range(1, N + 1):
            d = chi[S]
            mem = members(S, n)
            if sum((d[i] for i in mem), F(0)) != v[S]:
                continue
            if all(d[i] == maxchi[i] for i in mem):
                A.append(S)
        Pnew = 0
        for S in A:
            Pnew |= S
        # gamma^step: for i in P^step, chi_i in an admissible coalition = maxchi[i].
        # Keep any previously-fixed player defensively (theory: P is nondecreasing).
        newP = Pnew | P
        gnew = {}
        for i in range(n):
            if not (newP >> i & 1):
                continue
            gnew[i] = maxchi[i] if (Pnew >> i & 1) else gamma[i]
        P, gamma = newP, gnew
        A_hat, claims = A, gnew
        if P == N:
            break
    claims_vec = [claims[i] for i in range(n)]
    is_ES = N in A_hat
    return claims_vec, A_hat, is_ES


def _cea_lambda(caps, total):
    """Constrained-equal-awards level: lambda >= 0 with sum(min(c, lambda)) = total,
    for 0 <= total <= sum(caps). Exact."""
    caps = sorted(caps)
    m = len(caps)
    if m == 0:
        return F(0)
    prev = F(0)
    capped = F(0)
    for k in range(m):
        # region lambda in [prev, caps[k]]: players 0..k-1 capped, k..m-1 get lambda.
        rem = total - capped
        lam = rem / (m - k)
        if prev <= lam <= caps[k]:
            return lam
        capped += caps[k]
        prev = caps[k]
    return caps[-1]  # total == sum(caps): everyone at their cap


def pes(game):
    """Procedural egalitarian solution as list[Fraction]."""
    claims, A_hat, _is_ES = egalitarian_procedure(game)
    n, N, v = game.n, game.N, game.v
    maximal = [S for S in A_hat
               if not any(T != S and (S & T) == S for T in A_hat)]
    if maximal:
        D = maximal[0]
        for S in maximal[1:]:
            D &= S
    else:
        D = 0
    strong = [i for i in range(n) if D >> i & 1]
    nonstrong = [i for i in range(n) if not (D >> i & 1)]
    sum_strong = sum((claims[i] for i in strong), F(0))
    lam = _cea_lambda([claims[i] for i in nonstrong], v[N] - sum_strong)
    x = [None] * n
    for i in strong:
        x[i] = claims[i]
    for i in nonstrong:
        x[i] = min(claims[i], lam)
    return x, D

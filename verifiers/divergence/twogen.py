"""Analytic theory of TWO-generator exact games.

Setup.  g,h >= 0 with g(N)=h(N)=T.  Singleton-normalization means min(g_i,h_i)=0
for every i, so the supports A={i:g_i>0}, B={i:h_i>0} are DISJOINT.  Players
outside A u B are null (forced to 0), so assume A u B = N.

v(S) = min(g(S n A), h(S n B)).

CLAIM 1 (dual description of the core).  Writing f(S) := max(g(S n A), h(S n B)),

    Core(v) = { x >= 0 : x(N)=T,  x(S) <= f(S) for all S }

Proof sketch: x(S) >= v(S) for all S is the same family of inequalities as
x(N\\S) <= T - v(S), and T - v(S) = max(T-g(S n A), T-h(S n B))
             = max(g(A \\ S) , h(B \\ S)) = f(N \\ S).

CLAIM 2 (egalitarian levels).  With mu = max_{core} min_i x_i (the leximin floor)
and M = min_{core} max_i x_i (the leximax-min ceiling):

    mu <= min_{S != empty}  f(S)/|S|            [since x(S) <= f(S)]
    M  >= max_{S != N}     (T - f(S))/(n-|S|)   [since x(N\\S) >= T - f(S)]

This module tests whether these two bounds are EQUALITIES for 2-generator games.
"""
import sys, random, itertools
from fractions import Fraction as F
import lib


def fmax(n, g, h):
    """f(S) = max(g(S), h(S)) for all S (g,h have disjoint supports)."""
    full = (1 << n) - 1
    f = [F(0)] * (1 << n)
    for S in range(1, full + 1):
        f[S] = max(sum(g[i] for i in range(n) if S >> i & 1),
                   sum(h[i] for i in range(n) if S >> i & 1))
    return f


def check_claim1(n, g, h):
    """Verify v(S) = T - f(N\\S) for all S, i.e. the dual description."""
    full = (1 << n) - 1
    v = lib.envelope(n, [tuple(g), tuple(h)])
    f = fmax(n, g, h)
    T = F(sum(g))
    for S in range(1, full):
        if v[S] != T - f[full ^ S]:
            return False, S, v[S], T - f[full ^ S]
    return True, None, None, None


def bounds(n, g, h):
    full = (1 << n) - 1
    f = fmax(n, g, h)
    T = F(sum(g))
    mu_ub = min(f[S] / bin(S).count("1") for S in range(1, full + 1))
    M_lb = max((T - f[S]) / (n - bin(S).count("1")) for S in range(0, full))
    return mu_ub, M_lb


def disjoint_pair(n, rng, T):
    """Random singleton-normalized 2-generator data with A u B = N."""
    a = rng.randint(1, n - 1)
    perm = list(range(n)); rng.shuffle(perm)
    A = perm[:a]; B = perm[a:]
    g = [F(0)] * n; h = [F(0)] * n
    for blk, vec in ((A, g), (B, h)):
        rem = T
        for j, i in enumerate(blk):
            if j == len(blk) - 1:
                vec[i] = F(rem)
            else:
                take = rng.randint(1, rem - (len(blk) - 1 - j))
                vec[i] = F(take); rem -= take
    return g, h


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    rng = random.Random(seed)
    bad1 = bad_mu = bad_M = 0
    tight_mu = tight_M = 0
    tested = 0
    worst = []
    for _ in range(trials):
        T = rng.choice([4, 6, 8, 10, 12, 16, 20])
        if T < n:
            continue
        g, h = disjoint_pair(n, rng, T)
        ok, S, x, y = check_claim1(n, g, h)
        if not ok:
            bad1 += 1
            print("CLAIM1 FAIL", g, h, S, x, y)
            continue
        r = lib.gap_ratio(n, [tuple(g), tuple(h)])
        if r is None:
            continue
        w, mn, mx, l1, ratio = r
        tested += 1
        mu, M = min(mn), max(mx)
        mu_ub, M_lb = bounds(n, g, h)
        if mu > mu_ub:
            bad_mu += 1; print("MU BOUND VIOLATED", g, h, mu, mu_ub)
        if M < M_lb:
            bad_M += 1; print("M BOUND VIOLATED", g, h, M, M_lb)
        if mu == mu_ub:
            tight_mu += 1
        else:
            worst.append(("mu", [str(q) for q in g], [str(q) for q in h],
                          str(mu), str(mu_ub), str(ratio)))
        if M == M_lb:
            tight_M += 1
    print(f"n={n} tested={tested}  claim1 failures={bad1}  "
          f"mu-bound violations={bad_mu}  M-bound violations={bad_M}")
    print(f"  mu bound TIGHT in {tight_mu}/{tested} "
          f"({100*tight_mu/max(1,tested):.1f}%)")
    print(f"  M  bound TIGHT in {tight_M}/{tested} "
          f"({100*tight_M/max(1,tested):.1f}%)")
    for wq in worst[:4]:
        print("   mu not tight:", wq)


if __name__ == "__main__":
    main()

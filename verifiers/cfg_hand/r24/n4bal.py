"""IS  mu >= lambda  TRUE FOR ALL BALANCED (not just exact) GAMES AT n <= 4 ?

This is the pivot of the round-24 reduction: the face F_p is the core of a
four-player game w that need NOT be exact, and what is needed of it is exactly
mu_w >= lambda_w with lambda_w built from w's own caps f_w(A) = w(U) - w(U\\A).

Generator for balanced games at n = 3, 4: draw a random nonnegative "core seed"
point set, then draw v(S) uniformly in [chosen lower bound, min over seeds of
x(S)] so that the seeds stay in the core -- this reaches NON-EXACT balanced
games (v(S) strictly below the attained minimum), which the envelope generator
never produces.  REACHABLE SHAPES: singleton-normalized balanced games whose
core contains one of the drawn seeds, with values on a fine rational grid;
in particular every value profile v <= (attained min) is reachable in the
limit of the grid, so non-exactness is reached at every coalition.

Positive control: the same test on EXACT games (envelopes), where mu = lambda
is the known n <= 4 theorem, must show zero violations.
Negative control: the same test at n = 5, where the designed balanced witness
of REPORT_A3 is known to violate mu = lambda, must FIND violations.
"""
import random
import sys
from fractions import Fraction as F

import genn as G

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 7
NTRY = int(sys.argv[2]) if len(sys.argv) > 2 else 300


def envelope(n, gens):
    full = (1 << n) - 1
    total = sum(gens[0])
    v = [F(0)] * (full + 1)
    for S in range(1, full):
        v[S] = min(sum(g[k] for k in G.bits(n, S)) for g in gens)
    v[full] = F(total)
    return v


def rand_seeds(rng, n, total, rows):
    gens = []
    for _ in range(rows):
        cuts = sorted(rng.randrange(total + 1) for _ in range(n - 1))
        gens.append(tuple(F(b - a) for a, b in zip([0] + cuts, cuts + [total])))
    return gens


def rand_balanced(rng, n, den=4):
    """Balanced, singleton-normalized, generally NON-exact."""
    full = (1 << n) - 1
    while True:
        total = rng.randint(3, 10)
        gens = rand_seeds(rng, n, total, rng.randint(1, 4))
        if any(min(g[k] for g in gens) != 0 for k in range(n)):
            continue
        v = [F(0)] * (full + 1)
        v[full] = F(total)
        ok = True
        for S in range(1, full):
            if G.card(S) == 1:
                v[S] = F(0)
                continue
            hi = min(sum(g[k] for k in G.bits(n, S)) for g in gens)
            # draw v(S) in [0, hi] on a 1/den grid
            steps = int(hi * den)
            v[S] = F(rng.randint(0, steps), den) if steps > 0 else F(0)
        if ok:
            return v, gens


def run(n, mode, rng, ntry):
    viol = []
    nonexact = 0
    tested = 0
    for _ in range(ntry):
        if mode == "balanced":
            v, gens = rand_balanced(rng, n)
        else:
            total = rng.randint(3, 12)
            gens = rand_seeds(rng, n, total, rng.randint(2, 4))
            if any(min(g[k] for g in gens) != 0 for k in range(n)):
                continue
            v = envelope(n, gens)
        f, T = G.fvec(n, v)
        if T <= 0:
            continue
        tested += 1
        lam = G.lam_of(n, f)
        # non-exactness?
        ne = False
        for S in range(1, (1 << n) - 1):
            mn, _ = G.core_min(n, f, T, S)
            if mn != v[S]:
                ne = True
                break
        if ne:
            nonexact += 1
        mu = G.mu_of(n, f, T)
        if mu < lam:
            viol.append((mu, lam, T, v[:], ne))
    return tested, nonexact, viol


def main():
    rng = random.Random(SEED)
    for n in (3, 4, 5):
        for mode in ("exact", "balanced"):
            tested, ne, viol = run(n, mode, rng, NTRY if n < 5 else NTRY // 2)
            tag = "EXACT   " if mode == "exact" else "BALANCED"
            print(f"n = {n}  {tag}  games {tested}  (non-exact among them "
                  f"{ne})   mu < lambda violations: {len(viol)}")
            for w in viol[:3]:
                print(f"      mu = {w[0]}  lambda = {w[1]}  T = {w[2]}  "
                      f"non-exact = {w[4]}")
                print(f"      v = {[str(x) for x in w[3]]}")


if __name__ == "__main__":
    main()

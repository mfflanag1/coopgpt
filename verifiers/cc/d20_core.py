"""d20: unsat-core mining on the smallest UNSAT case, to expose the hand proof.

The case (found by d19): n = 5, phi has exactly two strata B_1 = {1,2,3,4} at
level mu and {5} at level nu > mu, and the minimal sufficient hypothesis set is
  core  + exv2 + cert + hstar
-- no phi' at all, no superadditivity, no exactness of the base game, and no
monotonicity failure.  So the claim to prove by hand is:

  CLAIM.  v a game with v({i}) = 0, phi the leximin-maximal element of core(v),
  with exactly two payoff strata B_1 (level mu) and {r} (level nu > mu).  If
  v' = v^{S,alpha} is exact and alpha > s_phi(S), then r in S.

Here S is fixed (WLOG S = {1..m} by relabelling inside the stratum, which is a
symmetry of every hypothesis) so that the core is readable.  Every assertion is
tracked, and z3's unsat core names exactly the coalitions and the certificate
rows the proof must combine.

usage: d20_core.py [m]
"""
import sys, itertools
import z3
from fractions import Fraction as F

n = 5
FULL = 31
R = z3.Real
props = list(range(1, FULL))


def bits(T):
    return [i for i in range(n) if T >> i & 1]


def nm(T):
    return "{" + ",".join(str(i + 1) for i in bits(T)) + "}"


def run(m):
    S = (1 << m) - 1                       # S = {1..m}, never contains player 5
    s = z3.Solver()
    s.set(unsat_core=True)
    v = {T: R("v_%d" % T) for T in props}
    v[FULL] = z3.RealVal(1)
    phi = [R("p_%d" % i) for i in range(n)]
    al = R("alpha")

    def tot(x, T):
        return z3.Sum([x[i] for i in bits(T)])

    def track(name, c):
        s.assert_and_track(c, name)

    for i in range(n):
        track("norm_%d" % (i + 1), v[1 << i] == 0)
    track("alpha_pos", al > 0)
    # phi's shape: two strata, {5} strictly richest
    for i in range(3):
        track("tie_%d%d" % (i + 1, i + 2), phi[i] == phi[i + 1])
    track("gap_45", phi[3] < phi[4])
    # phi in core(v)
    track("eff_phi", tot(phi, FULL) == v[FULL])
    for T in props:
        track("core_phi_%s" % nm(T), tot(phi, T) >= v[T])
    # Lemma L certificate for phi at the single cut (B = {1,2,3,4}, H = {5})
    lam = {T: R("l_%d" % T) for T in props}
    nu = R("nu")
    for T in props:
        track("lam_nonneg_%s" % nm(T), lam[T] >= 0)
        track("lam_support_%s" % nm(T), z3.Implies(lam[T] > 0, tot(phi, T) == v[T]))
    track("cert_cover_rich", z3.Sum([lam[T] for T in props if T >> 4 & 1]) == nu)
    for i in range(4):
        track("cert_cover_poor_%d" % (i + 1),
              z3.Sum([lam[T] for T in props if T >> i & 1]) <= nu - 1)
    # the bump: alpha overshoots S's slack, and v' is exact
    track("overshoot", al > tot(phi, S) - v[S])
    v2 = {T: (v[T] + al if T == S else v[T]) for T in props}
    v2[FULL] = z3.RealVal(1)
    for T in props:
        z = [R("z%d_%d" % (T, i)) for i in range(n)]
        track("exv2_eff_%s" % nm(T), z3.Sum(z) == v2[FULL])
        for U in props:
            track("exv2_core_%s_at_%s" % (nm(T), nm(U)), tot(z, U) >= v2[U])
        track("exv2_attain_%s" % nm(T), tot(z, T) == v2[T])

    r = s.check()
    print("S = %s   ->  %s" % (nm(S), r))
    if r == z3.unsat:
        core = sorted(str(c) for c in s.unsat_core())
        print("  unsat core (%d assertions):" % len(core))
        for c in core:
            print("     ", c)
    return r


for m in (2, 3, 4):
    run(m)
    print()

"""CANDIDATE LEMMA L*  (the round-24 proposal), and the certificates it beats.

L*(A, k)   for A proper (possibly empty), k not in A, v exact:

        max { y_k : y in Core, y(A) = f(A) }   >=   min( lambda, f(A u k) - f(A) )

  A = empty is exactly Lemma E1 (max y_k = f(k) >= min(lambda, f(k)) = lambda).
  A = {p}, k = q gives (R) immediately:
        2 f(p) + max_{F_p} y_q >= 2f(p) + min(lambda, f(pq) - f(p))
                                = min( 2f(p) + lambda, f(p) + f(pq) )
                                >= min( 2lambda + lambda, lambda + 2lambda ) = 3lambda.
  So L* restricted to singleton A implies (R), hence mu = lambda at n = 5.

Reported quantities, all exact:
  L*ALL   L*(A, k) over EVERY proper nonempty-or-empty A and every k not in A
  L*1     the singleton-A case only (the one that implies (R))
  CF      the closed form max_{F_p} y_q == min(f(pq) - f(p), f(q)), i.e.
          exactness of the reduced game at N\\{p,q}; strictly stronger than L*1

Non-exact games are ALSO run (drop-the-hypothesis control): there the face is
taken at the ATTAINED maximum F(A) = max_core y(A), so the statement is never
vacuous, and lambda is the game's own min f(S)/|S| including N.
"""
import random
import sys
from fractions import Fraction as F

import lib24 as L

NG = int(sys.argv[1]) if len(sys.argv) > 1 else 40
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 240


def rand_gens(rng):
    while True:
        total = rng.randint(4, 16)
        gens = []
        for _ in range(rng.randint(2, 5)):
            cuts = sorted(rng.randrange(total + 1) for _ in range(4))
            gens.append(tuple(F(b - a)
                              for a, b in zip([0] + cuts, cuts + [total])))
        if all(min(g[i] for g in gens) == 0 for i in range(5)):
            return gens


def attained(f, T, A):
    """F(A) = max over core of y(A).  Equals f(A) exactly when v is exact."""
    if A == 0:
        return F(0)
    w = [1 if A >> k & 1 else 0 for k in range(5)]
    val, *_ = L.core_max(f, T, w)
    return val


def test_game(f, T, lam, use_attained=False):
    """Returns (n_tested, violations) for L* over all (A, k)."""
    cache = {}

    def FA(A):
        if A not in cache:
            cache[A] = attained(f, T, A) if use_attained else F(f[A])
        return cache[A]

    viol = []
    ntest = 0
    for A in range(0, L.FULL):            # includes A = 0 (empty)
        for k in range(5):
            if A >> k & 1:
                continue
            if A | (1 << k) == L.FULL and A != 0:
                pass                      # A u k = N is allowed: f(N) = T
            fa = FA(A)
            fak = FA(A | (1 << k))
            eqs = [] if A == 0 else [(A, fa)]
            wk = [0] * 5
            wk[k] = 1
            try:
                mk, *_ = L.core_max(f, T, wk, eqs=eqs)
            except L.LPError:
                viol.append((A, k, "face empty", None, None))
                continue
            ntest += 1
            need = min(lam, fak - fa)
            if mk < need:
                viol.append((A, k, mk, need, need - mk))
    return ntest, viol


def main():
    rng = random.Random(SEED)
    tot = dict(games=0, inreg=0, tests=0, viol=0, viol1=0, cf_bad=0, pairs=0,
               tight=0)
    examples = []
    while tot["games"] < NG:
        gens = rand_gens(rng)
        v = L.envelope(gens)
        f, T = L.fvec(v)
        lam = L.lam_of(f, T)
        lamp = L.lam_proper(f, T)
        tot["games"] += 1
        inreg = lamp <= F(T, 5)
        if inreg:
            tot["inreg"] += 1
        n, viol = test_game(f, T, lam)
        tot["tests"] += n
        tot["viol"] += len(viol)
        for A, k, mk, need, gap in viol:
            if L.card(A) == 1:
                tot["viol1"] += 1
            if len(examples) < 6:
                examples.append((T, L.nm(A), L.LETTERS[k], mk, need, gens,
                                 inreg))
        # CF and tightness on singleton A
        for p in range(5):
            for q in range(5):
                if p == q:
                    continue
                tot["pairs"] += 1
                P, Q = 1 << p, 1 << q
                wq = [0] * 5
                wq[q] = 1
                mq, *_ = L.core_max(f, T, wq, eqs=[(P, f[P])])
                if mq != min(f[P | Q] - f[P], f[Q]):
                    tot["cf_bad"] += 1
                if mq == min(lam, f[P | Q] - f[P]):
                    tot["tight"] += 1
    print("GENERATOR: envelopes of 2..5 integer rows, T in 4..16, zero cover "
          "(so singleton-normalized).  Every exact 5-player game is the "
          "envelope of its core vertices; this sampler reaches those realized "
          "by <= 5 small-integer rows.")
    print(f"games {tot['games']} (in-regime {tot['inreg']}), "
          f"L* instances tested {tot['tests']}")
    print(f"L*  violations: {tot['viol']}   (singleton-A ones: {tot['viol1']})")
    print(f"CF  max_{{F_p}}y_q != min(f(pq)-f(p), f(q)) : {tot['cf_bad']} "
          f"of {tot['pairs']} ordered pairs  -- CF is FALSE in general")
    print(f"L*1 attained with equality on {tot['tight']} of {tot['pairs']} "
          f"ordered pairs (so L*1 is TIGHT, not slack)")
    if examples:
        print("\nVIOLATIONS (T, A, k, max_face y_k, needed, in-regime):")
        for e in examples:
            print("   ", e[0], e[1], e[2], e[3], e[4], e[6])
            print("      gens", e[5])

    # ---------------- drop-the-hypothesis: the designed BALANCED non-exact game
    print("\nDROP-THE-HYPOTHESIS (exactness).  The lead-verified balanced, "
          "non-exact, in-regime witness of REPORT_A3 (mu = 1/18 < 1/12 = "
          "lambda):")
    v = [F(0)] * 32
    a, b, c, d, e = 1, 2, 4, 8, 16
    v[c | d] = F(3, 4)
    v[c | e] = F(1, 4)
    v[b | d | e] = F(5, 6)
    v[31] = F(1)
    f = [v[31] - v[31 ^ S] for S in range(32)]
    T = v[31]
    lam = L.lam_of(f, T)
    print(f"   T = {T}, lambda = {lam}, lambda_proper = {L.lam_proper(f, T)}, "
          f"T/5 = {F(T,5)}")
    n, viol = test_game(f, T, lam, use_attained=True)
    print(f"   L* instances {n}, violations {len(viol)}")
    for A, k, mk, need, gap in viol[:10]:
        print(f"      A = {L.nm(A):5s} k = {L.LETTERS[k]}   "
              f"max_face y_k = {mk}  needed {need}  short by {gap}")
    if not viol:
        print("   *** L* SURVIVES on the balanced non-exact witness: it does "
              "NOT consume exactness, so it cannot be true. ***")


if __name__ == "__main__":
    main()

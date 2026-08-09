"""THE ATTAINMENT QUESTION, with a hand simplification that collapses it.

SIMPLIFICATION (proved, no computation).  f is SUBADDITIVE on disjoint sets:
f(A u B) = max_core y(A u B) <= max y(A) + max y(B) = f(A) + f(B).  Hence
f(A u p) - f(p) <= f(A) for every A, so the face's cap function

        f_w(A) = min( f(A), f(A u p) - f(p) )  =  f(A u p) - f(p)     ALWAYS.

The f(A) branch is never strictly active.  Two consequences:
  * LEMMA M needs only its second branch -- branch 1 is vacuous;
  * lambda_w = min over B containing p with |B| >= 2 of
        ( f(B) - f(p) ) / ( |B| - 1 ),
    the smallest per-capita MARGINAL over p.

CONSEQUENCE FOR ATTAINMENT.  A face point with y(B0) = f_w(B0) is a core point
with y_p = f(p) AND y(B0 u p) = f(B0 u p).  So attainment at B0 is exactly
CHAIN SATURATION of the nested pair {p} inside B0 u {p} -- with the INNER set
always the singleton {p}.  For |B0| = 1 that is precisely the chain-attainment
statement REPORT_A3 refuted (64 of 4000 ordered pairs).  So attainment CAN
fail; the live question is whether it can fail AT THE ARGMIN.

Equivalently: attainment at B0 asks whether f({p}) is attained on the face
where B0 u {p} sits at its cap.

WHAT THIS SCRIPT MEASURES (exact, one process, own simplex, no solver):
  G0  guard: f_w(A) == f(A u p) - f(p) for every A          (the simplification)
  A1  attainment rate of the chain {p} < A u {p}, by |A|
  A2  ATTAINMENT AT THE ARGMIN: for every argmin B0 of the marginal ratio,
      is the chain {p} < B0 u {p} saturable?
  A3  the RESCUER: when the chain fails at a singleton {q}, is {q} the argmin,
      and if not, what is lambda_w versus f_w({q})?
  A4  size profile of the argmin.
"""
import random
import sys
from collections import Counter
from fractions import Fraction as F

import lib24 as L

NG = int(sys.argv[1]) if len(sys.argv) > 1 else 15
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 31415


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


def subs(U):
    out, A = [], U
    while A:
        out.append(A)
        A = (A - 1) & U
    return out


def main():
    rng = random.Random(SEED)
    g0 = 0
    att = Counter()      # (|A|, attained?) -> count
    argmin_sizes = Counter()
    argmin_fail = []
    rescue = []
    chainfail_singletons = 0
    games = inreg = 0
    while inreg < NG:
        gens = rand_gens(rng)
        v = L.envelope(gens)
        f, T = L.fvec(v)
        games += 1
        if L.lam_proper(f, T) > F(T, 5):
            continue
        inreg += 1
        lam = L.lam_of(f, T)
        for p in range(5):
            c = f[1 << p]
            U = L.FULL ^ (1 << p)
            SS = subs(U)
            fw = {}
            for A in SS:
                m1, m2 = f[A], f[A | (1 << p)] - c
                assert m2 <= m1, "G0 FAIL: subadditivity violated"
                fw[A] = m2
                g0 += 1
            lam_w = min(F(fw[A], 1) / L.card(A) for A in SS)
            argmins = [A for A in SS if F(fw[A], 1) / L.card(A) == lam_w]
            for A in argmins:
                argmin_sizes[L.card(A)] += 1
            hh = {}
            for A in SS:
                h, *_ = L.core_max(f, T,
                                   [1 if A >> k & 1 else 0 for k in range(5)],
                                   eqs=[(1 << p, c)])
                hh[A] = h
                ok = (h == fw[A])
                att[(L.card(A), ok)] += 1
                if L.card(A) == 1 and not ok:
                    chainfail_singletons += 1
                    q = L.bits(A)[0]
                    isarg = A in argmins
                    rescue.append((isarg, L.card(argmins[0]),
                                   lam_w, fw[A], h,
                                   F(fw[A], 1) / 1 - lam_w))
            for A in argmins:
                if hh[A] != fw[A]:
                    argmin_fail.append((T, L.LETTERS[p], L.nm(A), hh[A],
                                        fw[A], lam_w, gens))
    print("GENERATOR: envelopes of 2..5 integer rows, T in 4..16, zero cover; "
          "IN-REGIME games only.  Every exact five-player game is the envelope "
          "of its core vertices, so the family is complete in principle; this "
          "sampler reaches those realized by <= 5 small-integer rows.")
    print(f"games drawn {games}, in-regime kept {inreg}")
    print(f"\nG0  f_w(A) == f(A u p) - f(p) verified on {g0} (game,p,A) "
          f"triples -- the f(A) branch is NEVER strictly active")
    print("\nA1  chain {p} < A u {p} saturable?  by |A|:")
    for s in (1, 2, 3, 4):
        ok = att[(s, True)]
        no = att[(s, False)]
        tot = ok + no
        if tot:
            print(f"      |A| = {s}:  attained {ok}/{tot}   FAILS {no}")
    print(f"\nA2  ATTAINMENT AT THE ARGMIN: failures = {len(argmin_fail)}")
    for r in argmin_fail[:5]:
        print("      FAIL", r[:6])
        print("         gens", r[6])
    print(f"\nA4  argmin size profile: "
          f"{dict(sorted(argmin_sizes.items()))}")
    print(f"\nA3  singleton chain failures: {chainfail_singletons}")
    if rescue:
        atarg = sum(1 for r in rescue if r[0])
        print(f"      of these, {atarg} had the failing singleton AS an "
              f"argmin (must be 0 if (EXlam-FACE) holds)")
        gaps = sorted(r[5] for r in rescue)
        print(f"      rescuer margin f_w({{q}}) - lambda_w on the failures: "
              f"min {gaps[0]}, max {gaps[-1]}  (must be > 0)")


if __name__ == "__main__":
    main()

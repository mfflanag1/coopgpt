"""GUARDS for every load-bearing claim of round 24.  Exact rationals only.

A  FACE = CORE OF w.   F_p := {y in Core(v) : y_p = f(p)} equals, coordinate-
   wise on U = N\\{p}, the core of the four-player game w with
   w(A) = max(v(A), v(A u p) - f(p)),  w(U) = T - f(p).   Checked by comparing
   max over F_p of y(A) with max over Core(w) of x(A) for every A, on every
   game.  (The identity itself is proved and uses no exactness; this is a
   guard on the algebra.)

B  LEMMA M.   For t >= lambda:  2t + lambda_{w_t} >= 3*lambda, where
   lambda_{w_t} = min over nonempty A subset U of min(f(A), f(A u p) - t)/|A|.
   POSITIVE CONTROL: reported minimum must be 0 (the lemma is tight).
   DROP THE HYPOTHESIS: with t < lambda the same quantity must go NEGATIVE
   somewhere, or the hypothesis t >= lambda is doing no work.

C  (EXlam-FACE), the one open step.
   For every nonempty A subset U:  max{y(A) : y in Core(v), y_p = f(p)}
                                       >= lambda_w |A|.
   Equivalent (by THEOREM(4), whose hypothesis it is) to mu_w = lambda_w for
   the face game w.  Reported with its minimum margin and its tight count.

D  DROP THE HYPOTHESIS (exactness).  Same test on the lead-verified BALANCED
   non-exact in-regime witness of REPORT_A3.  There the face must be taken at
   the ATTAINED maximum of y_p (f(p) is not attained), and (EXlam-FACE) must
   FAIL -- otherwise the reduction does not consume exactness and cannot be
   true.

E  THE CHAIN.  (EXlam-FACE) + LEMMA M => (R).  Checked end to end: the
   certificate 2 f(p) + max_{F_p} y_q is compared with 3*lambda.
"""
import random
import sys
from fractions import Fraction as F

import lib24 as L
import genn as G

NG = int(sys.argv[1]) if len(sys.argv) > 1 else 30
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 777


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


def relabel(A, U):
    """bitmask on N restricted to U -> bitmask on the 4 players of U."""
    order = L.bits(U)
    return sum(1 << i for i, k in enumerate(order) if A >> k & 1)


def main():
    rng = random.Random(SEED)
    stA = 0
    stB = dict(min=None, dropmin=None, dropbad=0)
    stC = dict(min=None, bad=0, tight=0, n=0)
    stE = dict(min=None, bad=0)
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
            fw = {A: min(f[A | (1 << p)] - c, f[A]) for A in SS}
            lam_w = min(F(fw[A], 1) / L.card(A) for A in SS)

            # ---- A: face == core of w
            f4 = [F(0)] * 16
            for A in SS:
                f4[relabel(A, U)] = fw[A]
            f4[15] = T - c
            for A in SS:
                wA = [1 if A >> k & 1 else 0 for k in range(5)]
                h, *_ = L.core_max(f, T, wA, eqs=[(1 << p, c)])
                a4 = relabel(A, U)
                h4, _ = G.core_max(4, f4, T - c,
                                   [1 if a4 >> i & 1 else 0 for i in range(4)])
                assert h <= h4, "A FAIL: face point outside Core(w)"
                stA += 1
                # ---- C: (EXlam-FACE)
                d = h - lam_w * L.card(A)
                stC["n"] += 1
                if stC["min"] is None or d < stC["min"]:
                    stC["min"] = d
                if d < 0:
                    stC["bad"] += 1
                if d == 0:
                    stC["tight"] += 1

            # ---- B: Lemma M at t = f(p) and t = lambda, and the drop
            for t in (c, lam):
                lw = min(F(min(f[A | (1 << p)] - t, f[A]), 1) / L.card(A)
                         for A in SS)
                m = 2 * t + lw - 3 * lam
                if stB["min"] is None or m < stB["min"]:
                    stB["min"] = m
            for t in (F(0), lam / 2):
                if t >= lam:
                    continue
                lw = min(F(min(f[A | (1 << p)] - t, f[A]), 1) / L.card(A)
                         for A in SS)
                m = 2 * t + lw - 3 * lam
                if stB["dropmin"] is None or m < stB["dropmin"]:
                    stB["dropmin"] = m
                if m < 0:
                    stB["dropbad"] += 1

            # ---- E: the chain, per ordered pair
            for q in L.bits(U):
                wq = [0] * 5
                wq[q] = 1
                mq, *_ = L.core_max(f, T, wq, eqs=[(1 << p, c)])
                cert = 2 * c + mq - 3 * lam
                if stE["min"] is None or cert < stE["min"]:
                    stE["min"] = cert
                if cert < 0:
                    stE["bad"] += 1

    print("GENERATOR: envelopes of 2..5 integer rows with common total T in "
          "4..16 and a zero in every coordinate (so singleton-normalized); "
          "only IN-REGIME games kept (lambda_proper <= T/5).  Every exact "
          "five-player game is the envelope of its core vertices, so the "
          "family is complete in principle; this sampler reaches those "
          "realized by at most 5 small-integer rows.  Zero counts below are "
          "statements about that family.")
    print(f"games drawn {games}, in-regime kept {inreg}")
    print(f"\nA  face-vs-Core(w) comparisons: {stA}, all consistent")
    print(f"B  LEMMA M   min (2t + lambda_w - 3lambda) over t in "
          f"{{f(p), lambda}} = {stB['min']}   (must be >= 0; 0 = TIGHT)")
    print(f"   drop t >= lambda: min over t in {{0, lambda/2}} = "
          f"{stB['dropmin']}, negative in {stB['dropbad']} cases "
          f"(the hypothesis is load-bearing)")
    print(f"C  (EXlam-FACE)  min_A (h(A) - lambda_w|A|) = {stC['min']}   "
          f"violations {stC['bad']} of {stC['n']}   equality cases "
          f"{stC['tight']}")
    print(f"E  chain 2f(p) + max_{{F_p}} y_q - 3lambda: min {stE['min']}   "
          f"violations {stE['bad']}")

    # ---- D drop-the-hypothesis on the balanced non-exact witness
    print("\nD  DROP EXACTNESS: the lead-verified balanced non-exact "
          "in-regime witness (mu = 1/18 < 1/12 = lambda)")
    v = [F(0)] * 32
    a, b, cc, d, e = 1, 2, 4, 8, 16
    v[cc | d] = F(3, 4)
    v[cc | e] = F(1, 4)
    v[b | d | e] = F(5, 6)
    v[31] = F(1)
    f = [v[31] - v[31 ^ S] for S in range(32)]
    T = v[31]
    lam = L.lam_of(f, T)
    worst = None
    for p in range(5):
        # f(p) need not be attained here: use the attained maximum
        cmax, _, *_ = L.core_max(f, T, [1 if k == p else 0 for k in range(5)])
        U = L.FULL ^ (1 << p)
        SS = subs(U)
        lam_w = min(F(min(f[A | (1 << p)] - cmax, f[A]), 1) / L.card(A)
                    for A in SS)
        for A in SS:
            h, *_ = L.core_max(f, T,
                               [1 if A >> k & 1 else 0 for k in range(5)],
                               eqs=[(1 << p, cmax)])
            dd = h - lam_w * L.card(A)
            if worst is None or dd < worst[0]:
                worst = (dd, L.LETTERS[p], L.nm(A), h, lam_w, cmax, f[1 << p])
    print(f"   worst (EXlam-FACE) margin = {worst[0]}  at p = {worst[1]}, "
          f"A = {worst[2]}   (h = {worst[3]}, lambda_w = {worst[4]}, "
          f"attained max y_p = {worst[5]} vs f(p) = {worst[6]})")
    if worst[0] < 0:
        print("   (EXlam-FACE) FAILS on the balanced non-exact witness: the "
              "reduction DOES consume exactness.")
    else:
        print("   *** (EXlam-FACE) survives without exactness -- then it "
              "cannot be true, since mu < lambda there. AUDIT REQUIRED. ***")


if __name__ == "__main__":
    main()

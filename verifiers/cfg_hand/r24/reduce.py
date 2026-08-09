"""THE ROUND-24 REDUCTION, and the test of its one remaining hypothesis.

SETUP.  p fixed, c := f({p}), U := N\\{p} (four players).
F_p := {y in Core(v) : y_p = c}.  It is nonempty (exactness at N\\{p}) and it
is the CORE of the four-player Davis-Maschler reduced game

        w(A) = max( v(A), v(A u p) - c )   for A subset of U,   w(U) = T - c,

because y in Core(v) with y_p = c is exactly: y|_U >= v(A) on A subset U and
y_p + y(A) >= v(A u p), i.e. y(A) >= v(A u p) - c.   [no exactness used]

Its cap function is
        f_w(A) := w(U) - w(U\\A) = min( f(A u p) - c , f(A) ),
and lambda_w := min over nonempty A subset U of f_w(A)/|A|.

LEMMA M (proved by hand, verified below).   2c + lambda_w >= 3*lambda.
    For A with |A| = s the two branches give
      f(A)/s      >= lambda           so 2c + f(A)/s     >= 2lambda + lambda;
      (f(Aup)-c)/s: 2c + (f(Aup)-c)/s = c(2 - 1/s) + f(Aup)/s
                                     >= lambda(2 - 1/s) + lambda(s+1)/s = 3lambda,
    using c >= lambda, 2 - 1/s > 0, and f(A u p) >= lambda(s+1).

CONSEQUENCE.  If  max_{F_p} y_q >= lambda_w  then
        max_Core (2 y_p + y_q) >= 2c + lambda_w >= 3 lambda,   i.e. (R).

  max_{F_p} y_q >= lambda_w is LEMMA E1 FOR THE REDUCED GAME w: it holds
  verbatim if w is EXACT at U\\{q}, since then max_{F_p} y_q = f_w({q}) >= lambda_w.

So (R) reduces to a single hypothesis about the face.  This script measures:
  MLEM   lambda_w - (3 lambda - 2c)                >= 0 ?   [Lemma M, control]
  E1w    max_{F_p} y_q - lambda_w                  >= 0 ?   [the hypothesis]
  MUw    exists y in F_p with y_k >= lambda_w for all k in U ? [stronger]
  EXw    is w exact?  (at which A does it fail)
"""
import random
import sys
from fractions import Fraction as F

import lib24 as L

NG = int(sys.argv[1]) if len(sys.argv) > 1 else 30
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 2401


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


def subsets_of(U):
    subs = []
    A = U
    while A:
        subs.append(A)
        A = (A - 1) & U
    return subs


def analyse(f, T, lam, p):
    c = f[1 << p]
    U = L.FULL ^ (1 << p)
    lam_w = None
    arg = None
    for A in subsets_of(U):
        fw = min(f[A | (1 << p)] - c, f[A])
        val = F(fw, 1) / L.card(A)
        if lam_w is None or val < lam_w:
            lam_w, arg = val, A
    return c, U, lam_w, arg


def main():
    rng = random.Random(SEED)
    st = dict(games=0, inreg=0, pairs=0, mlem_min=None, e1w_min=None,
              e1w_bad=0, muw_bad=0, exw_bad=0, exw_tot=0, tightE1=0)
    bad = []
    while st["games"] < NG:
        gens = rand_gens(rng)
        v = L.envelope(gens)
        f, T = L.fvec(v)
        lam = L.lam_of(f, T)
        st["games"] += 1
        if L.lam_proper(f, T) <= F(T, 5):
            st["inreg"] += 1
        for p in range(5):
            c, U, lam_w, arg = analyse(f, T, lam, p)
            # Lemma M control
            m = lam_w - (3 * lam - 2 * c)
            if st["mlem_min"] is None or m < st["mlem_min"]:
                st["mlem_min"] = m
            # exactness of w
            for A in subsets_of(U):
                st["exw_tot"] += 1
                wA = [0] * 5
                for k in L.bits(A):
                    wA[k] = -1
                val, *_ = L.core_max(f, T, wA, eqs=[(1 << p, c)])
                minA = -val
                if minA != max(v[A], v[A | (1 << p)] - c):
                    st["exw_bad"] += 1
            # mu_w : all coordinates of U at least lambda_w on the face
            lows = [F(0)] * 5
            for k in L.bits(U):
                lows[k] = lam_w
            lows[p] = c
            if not L.core_feasible(f, T, lows):
                st["muw_bad"] += 1
            for q in L.bits(U):
                st["pairs"] += 1
                wq = [0] * 5
                wq[q] = 1
                mq, *_ = L.core_max(f, T, wq, eqs=[(1 << p, c)])
                d = mq - lam_w
                if st["e1w_min"] is None or d < st["e1w_min"]:
                    st["e1w_min"] = d
                if d == 0:
                    st["tightE1"] += 1
                if d < 0:
                    st["e1w_bad"] += 1
                    if len(bad) < 8:
                        bad.append((T, p, q, mq, lam_w, lam, c, L.nm(arg),
                                    gens))
    print("GENERATOR: envelopes of 2..5 integer rows, T in 4..16, zero cover.")
    print(f"games {st['games']} (in-regime {st['inreg']}), "
          f"(p,q) instances {st['pairs']}")
    print(f"LEMMA M control  min (lambda_w - (3lam - 2c)) = {st['mlem_min']}  "
          f"(must be >= 0)")
    print(f"E1w  min (max_{{F_p}} y_q - lambda_w) = {st['e1w_min']}   "
          f"violations {st['e1w_bad']}   tight {st['tightE1']}")
    print(f"MUw  faces with no point having all U-coords >= lambda_w: "
          f"{st['muw_bad']} of {st['games'] * 5}")
    print(f"EXw  reduced game w NOT exact at A: {st['exw_bad']} of "
          f"{st['exw_tot']} (A, p) pairs")
    for b in bad:
        print("  E1w FAIL", b[:8])
        print("     gens", b[8])


if __name__ == "__main__":
    main()

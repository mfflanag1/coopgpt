"""THE ONE REMAINING HYPOTHESIS: does the slice satisfy (EXlambda)?

Slice at y_p = t:   P_t = {y in Core(v) : y_p = t},  nonempty for t in [0, f(p)]
(exactness of v at {p} and at N\\{p}).  As a four-player game on U = N\\{p} it is
w_t with caps  f_w(A) = min( f(A), f(A u p) - t ),  lambda_w = min_A f_w(A)/|A|.

  LEMMA M (proved): t >= lambda  =>  2t + lambda_w >= 3*lambda; at t = lambda,
                    lambda_w >= lambda.
  THEOREM(4) (proved by the empty n<=4 cover residue): nonempty core +
                    (EXlam) => mu >= lambda.
  (EXlam) for the slice:  h(A) := max{y(A) : y in P_t} >= lambda_w |A|, all A.

If (EXlam) holds for the slice then mu_w >= lambda_w, so P_t has a point with
every U-coordinate >= lambda_w; at t = lambda that point together with y_p =
lambda gives mu(v) >= lambda outright.

Reported, exactly, for t = f(p) and t = lambda:
   EXLAM   min over A of ( h(A) - lambda_w |A| )      >= 0 ?
   MUW     P_t has a point with all U-coords >= lambda_w ?
   LWL     lambda_w - lambda                          (>= 0 by Lemma M at t=lam)
   EXW     is w_t exact (h(A) == f_w(A) for all A)?
"""
import random
import sys
from fractions import Fraction as F

import lib24 as L

NG = int(sys.argv[1]) if len(sys.argv) > 1 else 25
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 24024
ONLY_INREGIME = True


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
    out, A = [], U
    while A:
        out.append(A)
        A = (A - 1) & U
    return out


def analyse(f, T, lam, p, t):
    U = L.FULL ^ (1 << p)
    subs = subsets_of(U)
    fw = {A: min(f[A | (1 << p)] - t, f[A]) for A in subs}
    lam_w = min(F(fw[A], 1) / L.card(A) for A in subs)
    res = dict(lam_w=lam_w, exlam=None, exw=0, tightA=[])
    for A in subs:
        wA = [1 if A >> k & 1 else 0 for k in range(5)]
        h, *_ = L.core_max(f, T, wA, eqs=[(1 << p, t)])
        d = h - lam_w * L.card(A)
        if res["exlam"] is None or d < res["exlam"]:
            res["exlam"] = d
        if h != fw[A]:
            res["exw"] += 1
    lows = [F(0)] * 5
    lows[p] = t
    for k in L.bits(U):
        lows[k] = lam_w
    res["muw"] = L.core_feasible(f, T, lows)
    return res


def main():
    rng = random.Random(SEED)
    agg = {}
    for tag in ("t=f(p)", "t=lambda"):
        agg[tag] = dict(n=0, exlam_min=None, exlam_bad=0, muw_bad=0,
                        exw_bad=0, lwl_min=None, tight=0)
    games = inreg = 0
    bad = []
    while inreg < NG:
        gens = rand_gens(rng)
        v = L.envelope(gens)
        f, T = L.fvec(v)
        games += 1
        if ONLY_INREGIME and L.lam_proper(f, T) > F(T, 5):
            continue
        inreg += 1
        lam = L.lam_of(f, T)
        for p in range(5):
            for tag, t in (("t=f(p)", f[1 << p]), ("t=lambda", lam)):
                a = agg[tag]
                a["n"] += 1
                r = analyse(f, T, lam, p, t)
                if a["exlam_min"] is None or r["exlam"] < a["exlam_min"]:
                    a["exlam_min"] = r["exlam"]
                if r["exlam"] < 0:
                    a["exlam_bad"] += 1
                    if len(bad) < 6:
                        bad.append((tag, T, p, r["exlam"], r["lam_w"], lam,
                                    gens))
                if r["exlam"] == 0:
                    a["tight"] += 1
                if not r["muw"]:
                    a["muw_bad"] += 1
                if r["exw"]:
                    a["exw_bad"] += 1
                d = r["lam_w"] - lam
                if a["lwl_min"] is None or d < a["lwl_min"]:
                    a["lwl_min"] = d
    print("GENERATOR: envelopes of 2..5 integer rows, T in 4..16, zero cover; "
          "only IN-REGIME games (lambda_proper <= T/5) kept.  Every exact "
          "5-player game is the envelope of its core vertices, so the family "
          "is complete in principle; this sampler reaches those realized by "
          "<= 5 small-integer rows.")
    print(f"games drawn {games}, in-regime kept {inreg}")
    for tag in ("t=f(p)", "t=lambda"):
        a = agg[tag]
        print(f"\n  SLICE {tag}   ({a['n']} slices)")
        print(f"    (EXlam)  min_A (h(A) - lambda_w|A|) = {a['exlam_min']}   "
              f"violations {a['exlam_bad']}   tight slices {a['tight']}")
        print(f"    MUW      slices with no point having all U-coords "
              f">= lambda_w: {a['muw_bad']}")
        print(f"    EXW      slices whose reduced game w_t is NOT exact: "
              f"{a['exw_bad']}")
        print(f"    lambda_w - lambda: min {a['lwl_min']} (Lemma M control, "
              f"must be >= 0 at t = lambda)")
    for b in bad:
        print("  EXLAM FAIL", b[:6])
        print("     gens", b[6])


if __name__ == "__main__":
    main()

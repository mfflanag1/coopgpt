"""d17: end-to-end audit of the SIX-player C-C-left counterexamples.

At n = 6 core-vertex enumeration is out of reach (C(62,5) = 6.4M bases), so the
second, solver-independent leg of the audit is CERTIFICATE CHECKING instead:

  * exactness of v is free -- v is the lower envelope of nonnegative rows with a
    common total, every coordinate vanishing in some row (paper4's envelope
    lemma); the driver re-verifies those two combinatorial facts directly.
  * exactness of v' is certified by PRIMAL WITNESSES: for each proper T a point
    x^T is extracted from z3 and then verified with pure Fraction arithmetic --
    x^T(N) = v'(N), x^T(U) >= v'(U) for all proper U, and x^T(T) = v'(T).  The
    verification never calls a solver, so z3 is used only to propose.
  * leximin-maximality of phi and phi' is certified by DUAL CERTIFICATES:
    Lemma-L multipliers are extracted and the identities are checked with pure
    Fraction arithmetic.  By Lemma L (sufficiency direction, proved in
    PROOF.txt) these certificates PROVE optimality; the two leximin algorithms
    and the z3 no-better UNSAT are then corroboration, not the load-bearing step.

usage: d17_audit6.py
"""
import sys, itertools
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L
import z3

n = 6
FULL = 63
CASES = [
    ("A", [(6, 7, 11, 0, 13, 3), (0, 22, 0, 10, 0, 8), (0, 0, 21, 0, 19, 0)],
     0b111110, F(25, 16)),
    ("B", [(3, 0, 37, 0, 0, 0), (5, 4, 22, 0, 5, 4), (0, 18, 0, 11, 11, 0)],
     0b011110, F(17, 6)),
]


def check_point_in_core(v, x):
    """Pure Fraction verification -- no solver."""
    if L.xsum(x, n, FULL) != v[FULL]:
        return False
    return all(L.xsum(x, n, T) >= v[T] for T in L.masks(n))


def exactness_by_verified_witnesses(v):
    """z3 proposes a witness per coalition; Fractions verify it.  Returns
    (n_verified, n_needed, failures)."""
    x = [z3.Real("w%d" % i) for i in range(n)]
    base = L.core_constraints(n, v, x)
    good, bad = 0, []
    for T in L.masks(n):
        o = z3.Optimize()
        o.add(base)
        h = o.minimize(z3.Sum([x[i] for i in L.members(n, T)]))
        if o.check() != z3.sat:
            bad.append((T, "core empty"))
            continue
        m = o.model()
        pt = [L.rat(m.eval(x[i], model_completion=True)) for i in range(n)]
        if check_point_in_core(v, pt) and L.xsum(pt, n, T) == v[T]:
            good += 1
        else:
            bad.append((L.nm(n, T), [str(q) for q in pt]))
    return good, len(list(L.masks(n))), bad


def lemmaL_certificates_verified(v, x):
    """Extract Lemma-L multipliers from z3 and verify the identities with
    Fractions only.  Returns (n_cuts_certified, n_cuts, details)."""
    B = L.strata(n, x)
    tight = [T for T in L.masks(n) if L.xsum(x, n, T) == v[T]]
    ok = 0
    det = []
    for j in range(len(B)):
        H = sum(1 << i for b in B[j + 1:] for i in b)
        Bj = sum(1 << i for i in B[j])
        lam = {T: z3.Real("l%d" % T) for T in tight}
        nu = z3.Real("nu")
        s = z3.Solver()
        for T in tight:
            s.add(lam[T] >= 0)
        for i in range(n):
            cov = z3.Sum([lam[T] for T in tight if T >> i & 1]) if tight \
                else z3.RealVal(0)
            if H >> i & 1:
                s.add(cov == nu)
            elif Bj >> i & 1:
                s.add(cov <= nu - 1)
        if s.check() != z3.sat:
            det.append((j, "NO CERTIFICATE"))
            continue
        m = s.model()
        lv = {T: L.rat(m.eval(lam[T], model_completion=True)) for T in tight}
        nv = L.rat(m.eval(nu, model_completion=True))
        # ---- pure Fraction verification of the extracted certificate
        good = all(q >= 0 for q in lv.values())
        for T, q in lv.items():
            if q > 0 and L.xsum(x, n, T) != v[T]:
                good = False                      # support outside the tight family
        for i in range(n):
            cov = sum(lv[T] for T in tight if T >> i & 1)
            if H >> i & 1 and cov != nv:
                good = False
            if Bj >> i & 1 and cov > nv - 1:
                good = False
        ok += good
        sup = {L.nm(n, T): str(q) for T, q in lv.items() if q > 0}
        det.append((j, "verified" if good else "EXTRACTION FAILED",
                    "nu=%s" % nv, sup))
    return ok, len(B), det


for name, rows, S, ALPHA in CASES:
    print("=" * 78)
    print("CASE %s   rows (common total %d): %s" % (name, sum(rows[0]), rows))
    gens = [tuple(F(q) for q in r) for r in rows]
    print("  common total shared by all rows:",
          len({sum(r) for r in gens}) == 1,
          "   every coordinate vanishes in some row:",
          all(any(r[i] == 0 for r in gens) for i in range(n)))
    print("  => v is exact and singleton-normalized by paper4's envelope lemma,")
    print("     with no computation at all.")
    v = L.envelope(n, gens)
    okv, badv = L.exactness_report(n, v)
    print("  (cross-check) v exact by z3 on all 62 proper coalitions:", okv, badv[:2])
    assert okv
    phi = L.lmin(n, v, both=True)
    print("  phi  =", [str(q) for q in phi], "(staged + ladder agree, unique)")
    w = L.bumped(v, S, ALPHA)
    print("  S =", L.nm(n, S), "  alpha =", ALPHA, "  s_phi(S) =",
          str(L.slack(n, v, phi, S)), "  alpha_ex =",
          str(L.alpha_exact_max(n, v, S)), "  g(S) =", str(L.g_of(n, v, S)))
    print("  v' differs from v at exactly one coalition:",
          [T for T in range(1, FULL + 1) if w[T] != v[T]] == [S])
    g, tot, bad = exactness_by_verified_witnesses(w)
    print("  v' exact -- %d/%d primal witnesses VERIFIED IN PURE RATIONAL"
          " ARITHMETIC:" % (g, tot), not bad, bad[:2])
    assert g == tot and not bad
    phi2 = L.lmin(n, w, both=True)
    print("  phi' =", [str(q) for q in phi2], "(staged + ladder agree, unique)")
    for tag, gm, al in (("phi ", v, phi), ("phi'", w, phi2)):
        c, k, det = lemmaL_certificates_verified(gm, al)
        print("  Lemma-L dual certificates for %s: %d/%d cuts verified in pure"
              " rational arithmetic" % (tag, c, k))
        for d in det:
            print("      cut %d: %s  %s" % (d[0], d[1], d[2] if len(d) > 2 else ""))
            if len(d) > 3:
                print("             support:", d[3])
        assert c == k
    D = [phi2[i] - phi[i] for i in range(n)]
    suf = L.suffixes(n, v, phi)
    H, js = L.hstar(n, v, phi)
    Hhat = [Hj for _, Hj, s in suf if s > 0][0]
    Wl = [i for i in L.members(n, S) if phi2[i] < phi[i]]
    Wm = sum(1 << i for i in Wl)
    print("  strata poor->rich:", [[i + 1 for i in b] for b in L.strata(n, phi)])
    print("  richer suffixes / slacks:",
          [(L.nm(n, Hj), str(s)) for _, Hj, s in suf])
    print("  H* =", L.nm(n, H), "  Hhat =", L.nm(n, Hhat), "  W =", L.nm(n, Wm),
          "  all losers =", L.nm(n, sum(1 << i for i in range(n) if D[i] < 0)),
          "  gainers =", L.nm(n, sum(1 << i for i in range(n) if D[i] > 0)))
    print("  Delta =", [str(q) for q in D])
    print("  C-C  LEFT  W subset H*  :", (Wm & ~H) == 0,
          "   <-- REFUTED at n=6" if (Wm & ~H) else "")
    print("  C-C  RIGHT H* subset S  :", (H & ~S) == 0)
    print("  C-C^ LEFT  W subset Hhat:", (Wm & ~Hhat) == 0)
    print("  C-C^ RIGHT Hhat subset S:", (Hhat & ~S) == 0)
    print("  Theorem A: loss =", str(sum(phi[i] - phi2[i] for i in Wl)),
          " s_phi(W) =", str(L.slack(n, v, phi, Wm)),
          " ok:", sum(phi[i] - phi2[i] for i in Wl) <= L.slack(n, v, phi, Wm))
    print("  Prop D+:", all(L.xsum(D, n, T) >= 0 for T in L.masks(n)
                            if L.xsum(phi, n, T) == v[T]),
          "  Lemma C+:", all(L.xsum(D, n, T) <= 0 for T in L.masks(n)
                             if T != S and L.xsum(phi2, n, T) == w[T]))
    assert Wl and (Wm & ~H) != 0 and (Wm & ~Hhat) == 0 and (Hhat & ~S) == 0
print("=" * 78)
print("Both six-player cases audited: C-C left FAILS at n = 6 on two distinct")
print("base games, and C-C^ holds on both.")

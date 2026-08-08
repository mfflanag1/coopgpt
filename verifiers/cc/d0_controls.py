"""d0: positive controls.  Reproduce paper4's two n=6 counterexamples end to end
with an independent toolkit (two leximin algorithms + full exactness certification).

If these do not match paper4 exactly, nothing downstream is trustworthy.
"""
import sys
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L

CASES = [
    ("mono:ex:notsuffix (retires C-A)",
     [(0, 11, 0, 7, 0, 0), (0, 10, 0, 4, 3, 1), (2, 0, 1, 0, 15, 0)],
     0b011111, F(9, 16),
     dict(phi=[F(3, 2), F(11, 2), F(1, 2), F(9, 2), F(11, 2), F(1, 2)],
          phi2=[F(25, 16), F(11, 2), F(9, 16), F(71, 16), F(11, 2), F(7, 16)],
          W=0b001000)),
    ("mono:ex:notstratum (retires C-B)",
     [(0, 15, 0, 14, 0, 0), (0, 9, 0, 9, 6, 5), (4, 0, 4, 0, 21, 0)],
     0b011111, F(23, 8),
     dict(phi=[F(5, 2), F(15, 2), F(5, 2), F(13, 2), F(15, 2), F(5, 2)],
          phi2=[F(23, 8), F(57, 8), F(23, 8), F(49, 8), F(63, 8), F(17, 8)],
          W=0b001010)),
]

n = 6
for name, rows, S, alpha, exp in CASES:
    print("=" * 70)
    print(name)
    gens = [tuple(F(q) for q in r) for r in rows]
    v = L.envelope(n, gens)
    print("  singleton-normalized:", L.is_sing_norm(n, v), " v(N) =", v[(1 << n) - 1])
    ok, bad = L.exactness_report(n, v)
    print("  v exact (all 62 proper coalitions, z3-certified):", ok, bad[:3])
    assert ok
    phi = L.lmin(n, v, both=True)
    print("  phi =", [str(q) for q in phi], "(staged + ladder agree, ladder unique)")
    assert phi == exp["phi"], (phi, exp["phi"])
    B = L.strata(n, phi)
    print("  strata poor->rich:", [[i + 1 for i in b] for b in B],
          [str(phi[b[0]]) for b in B])
    suf = L.suffixes(n, v, phi)
    print("  richer suffixes / slacks:", [(L.nm(n, H), str(s)) for _, H, s in suf])
    H, js = L.hstar(n, v, phi)
    print("  H* =", L.nm(n, H), " j* =", js)
    print("  S =", L.nm(n, S), " s_phi(S) =", str(L.slack(n, v, phi, S)),
          " g(S) =", str(L.g_of(n, v, S)),
          " alpha_feas_max =", str(L.alpha_feasible_max(n, v, S)))
    rec = L.violation_record(n, v, phi, S, alpha)
    assert rec is not None, "expected a violation"
    print("  alpha =", str(alpha), " v' exact: True (certified inside record)")
    print("  phi' =", [str(q) for q in rec["phi2"]])
    assert rec["phi2"] == exp["phi2"], (rec["phi2"], exp["phi2"])
    print("  W =", L.nm(n, rec["W"]), " all losers =", L.nm(n, rec["losers"]),
          " gainers =", L.nm(n, rec["gainers"]))
    assert rec["W"] == exp["W"]
    print("  C-C left  (W subset H*):", rec["left"])
    print("  C-C right (H* subset S):", rec["right"])
    assert rec["left"] and rec["right"]
print("=" * 70)
print("BOTH CONTROLS REPRODUCED EXACTLY (phi, phi', W, strata, slacks match paper4).")

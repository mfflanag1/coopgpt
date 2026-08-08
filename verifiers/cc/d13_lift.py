"""d13: does the C-C-left failure survive at larger n?

Adding a NULL player p (v(T u p) = v(T), v({p}) = 0) to an exact singleton-
normalized game keeps it exact and singleton-normalized: for T not containing p
the old core witness extended by 0 works, and for T containing p one has
v(T) = v(T\\p), attained by the same point.  In the core x_p = 0 is forced
(x(N) = v(N) = v(N\\p) <= x(N\\p)), so Lmin just gains a new poorest stratum
{p} at level 0 and is otherwise unchanged; bumping a coalition that omits p is
still an exact bump with the same phi'.

The new player must be put INSIDE the bumped coalition.  If p stayed outside,
exactness of v' would fail at S u {p}: v'(S u p) = v(S) while every core(v')
point has x(S u p) = x(S) >= v(S) + alpha.  (This is exactly Theorem B's
exactness pushback, v(T) >= v(S) + alpha + v(T\S) for T strictly containing S,
with T = S u {p}; a null outsider makes it fail.)  With p inside S the pushback
inequalities for the enlarged game reduce to those of the old one.

If that is right the five-player counterexample lifts to every n >= 5.  This
driver checks it from scratch at n = 6 and n = 7 -- exactness of both games on
all proper coalitions, both leximin allocations by two algorithms, the strata,
every suffix slack, H*, and the verdict.
"""
import sys
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L

BASE = [F(q) for q in
        [0, 0, 0, 106, 0, 136, 0, 136, 0, 161, 0, 161, 176, 297, 176, 297,
         0, 242, 0, 242, 242, 393, 242, 484, 176, 418, 176, 418, 418, 534, 418, 660]]
S5 = 0b11101
ALPHA = F(20)


def add_null(n, v):
    """One null player appended as index n."""
    old = (1 << n) - 1
    w = [F(0)] * (1 << (n + 1))
    for T in range(1, (1 << (n + 1))):
        w[T] = v[T & old] if (T & old) else F(0)
    return w


v, n, S = BASE, 5, S5
for step in range(3):
    print("=" * 72)
    print("n = %d   v(N) = %s   S = %s   alpha = %s" % (n, v[(1 << n) - 1],
                                                        L.nm(n, S), ALPHA))
    ok, bad = L.exactness_report(n, v)
    print("  v exact on all %d proper coalitions:" % ((1 << n) - 2), ok, bad[:2])
    assert ok
    phi = L.lmin(n, v, both=True)
    print("  phi  =", [str(q) for q in phi], "(two algorithms agree, unique)")
    w2 = L.bumped(v, S, ALPHA)
    ok2, bad2 = L.exactness_report(n, w2)
    print("  v' exact:", ok2, bad2[:2])
    if not ok2:
        print("  --> the lift FAILS: v' is inexact at %s (core min %s, v' = %s)"
              % (L.nm(n, bad2[0][0]), bad2[0][1], bad2[0][2]))
        print()
        print("LEMMA (no exact bump survives a null player).  Let p be a null")
        print("player of v (v(T u p) = v(T), v({p}) = 0) and let v' = v^{S,alpha}")
        print("with alpha > 0.  Then v' is NOT exact.  Indeed every core point has")
        print("x_p = 0, so x(S u p) = x(S) = x(S \\ p).  If p is not in S then")
        print("v'(S u p) = v(S u p) = v(S) while core(v') forces x(S u p) >=")
        print("v(S)+alpha; if p is in S then v'(S \\ p) = v(S \\ p) = v(S) while")
        print("core(v') forces x(S \\ p) = x(S) >= v(S)+alpha; and if S = N \\ p")
        print("the core of v' is empty.  In every case exactness fails.")
        print()
        print("So the five-player counterexample does NOT lift by a null player,")
        print("in either placement, and n >= 6 stays OPEN for the left inclusion.")
        break
    phi2 = L.lmin(n, w2, both=True)
    print("  phi' =", [str(q) for q in phi2], "(two algorithms agree, unique)")
    print("  strata poor->rich:", [[i + 1 for i in b] for b in L.strata(n, phi)])
    suf = L.suffixes(n, v, phi)
    print("  richer suffixes / slacks:",
          [(L.nm(n, Hj), str(s)) for _, Hj, s in suf])
    H, js = L.hstar(n, v, phi)
    Hhat = [Hj for _, Hj, s in suf if s > 0][0]
    Wl = [i for i in L.members(n, S) if phi2[i] < phi[i]]
    Wm = sum(1 << i for i in Wl)
    print("  H* =", L.nm(n, H), "  Hhat =", L.nm(n, Hhat), "  W =", L.nm(n, Wm))
    print("  s_phi(S) =", str(L.slack(n, v, phi, S)),
          "  alpha_ex =", str(L.alpha_exact_max(n, v, S)))
    print("  C-C RIGHT  H* subset S :", (H & ~S) == 0)
    print("  C-C LEFT   W subset H* :", (Wm & ~H) == 0,
          "   <-- REFUTED" if (Wm & ~H) else "")
    print("  repaired   W subset Hhat:", (Wm & ~Hhat) == 0,
          "   Hhat subset S:", (Hhat & ~S) == 0)
    assert Wl and (Wm & ~H) != 0, "the lift lost the failure"
    v = add_null(n, v)
    S = S | (1 << n)          # the new null player joins the bumped coalition
    n += 1
print("=" * 72)
print("Conclusion: the counterexample is genuinely five-player; the cheap lift")
print("is blocked by the lemma above.  n >= 6 requires a fresh search.")

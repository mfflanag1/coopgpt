"""d12: is the C-C-left counterexample a knife edge?

Sweeps the whole admissible exact window (s_phi(S), alpha_ex(S)] of the
Theorem-1 game and reports W at each bump, and also sweeps the OTHER bumped
coalitions of the same base game.  Every bump listed is certified exact.
"""
import sys
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L

n = 5
FULL = 31
V = [F(q) for q in
     [0, 0, 0, 106, 0, 136, 0, 136, 0, 161, 0, 161, 176, 297, 176, 297,
      0, 242, 0, 242, 242, 393, 242, 484, 176, 418, 176, 418, 418, 534, 418, 660]]
phi = L.lmin_staged(n, V)
H, js = L.hstar(n, V, phi)
suf = L.suffixes(n, V, phi)
Hhat = [Hj for _, Hj, s in suf if s > 0][0]
print("phi =", [str(q) for q in phi])
print("suffix slacks:", [(L.nm(n, Hj), str(s)) for _, Hj, s in suf])
print("H* (innermost slack) =", L.nm(n, H), "   Hhat (outermost slack) =",
      L.nm(n, Hhat))

print("\n--- S = {1,3,4,5}: the whole admissible window ---")
S = 0b11101
sS = L.slack(n, V, phi, S)
amax = L.alpha_exact_max(n, V, S)
print("window = (%s, %s]" % (sS, amax))
bad = tot = 0
for k in range(1, 25):
    al = sS + (amax - sS) * F(k, 24)
    w = L.bumped(V, S, al)
    ok, _ = L.exactness_report(n, w)
    if not ok:
        print("  alpha=%-8s v' NOT exact (should not happen inside the window)" % al)
        continue
    p2 = L.lmin_staged(n, w)
    Wl = [i for i in L.members(n, S) if p2[i] < phi[i]]
    if not Wl:
        print("  alpha=%-8s no violation" % al)
        continue
    Wm = sum(1 << i for i in Wl)
    tot += 1
    lf = (Wm & ~H) == 0
    bad += (not lf)
    print("  alpha=%-8s phi'=%-34s W=%-8s  W in H*: %-5s  W in Hhat: %s"
          % (al, str([str(q) for q in p2]), L.nm(n, Wm), lf, (Wm & ~Hhat) == 0))
print("violations in the window: %d, of which C-C-left FAILS at %d" % (tot, bad))

print("\n--- every other bumped coalition of the same base game ---")
for S2 in range(1, FULL):
    if bin(S2).count("1") < 2 or S2 == S:
        continue
    s2 = L.slack(n, V, phi, S2)
    g = L.g_of(n, V, S2)
    if g is None or g <= s2:
        continue
    am = L.alpha_exact_max(n, V, S2)
    if am is None or am <= s2:
        continue
    for k in (4, 2, 1):
        al = s2 + (am - s2) * F(1, k)
        w = L.bumped(V, S2, al)
        ok, _ = L.exactness_report(n, w)
        if not ok:
            continue
        p2 = L.lmin_staged(n, w)
        Wl = [i for i in L.members(n, S2) if p2[i] < phi[i]]
        if not Wl:
            continue
        Wm = sum(1 << i for i in Wl)
        print("  S=%-11s alpha=%-7s W=%-8s  right(H* in S): %-5s  left(W in H*): %-5s"
              "  W in Hhat: %s"
              % (L.nm(n, S2), al, L.nm(n, Wm), (H & ~S2) == 0, (Wm & ~H) == 0,
                 (Wm & ~Hhat) == 0))

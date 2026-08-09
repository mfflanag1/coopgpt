"""n=7 CFG-family instance, built by DESIGN-BACKWARDS (pins first, rows second).

TARGET (T = 32 so all integral; mu = 1/16 -> 2, rho = 11/32 -> 11):
    Lmin x = (2,2,2,2,2,11,11)   strata (5,2)
    Lmax z = (0,0,0,8,8,8,8)     M = T/4 = 8, three zeros
    predicted ratio |x-z|_1 / T = 24/32 = 3/4 = (n-4)/(n-3)

WHY r22's two-generator attempt failed: the envelope of {x,z} zeroes only the
Lmax zero-set {1,2,3}, so v({i}) > 0 for i = 4..7 and the game is not
singleton-normalized.  The fix is to choose the PINS first, then find a ZERO
COVER that respects them.

x - z = (2,2,2,-6,-6,3,3), so a coalition can be tight for BOTH selections only
where x(S) >= z(S).  Two families do all the work:
  PAIR CAPS  v(N\{i,j}) = 28 for {i,j} in {1,2,3}: gives y_i + y_j <= 4, which
      caps the stage-1 level at 2 and pins players 1,2,3.
  QUAD CAPS  v({5,6,7}) = v({4,6,7}) = 24 = 8*3: gives y({1,2,3,4}) <= 8 and
      y({1,2,3,5}) <= 8, pinning players 4 and 5 once 1,2,3 sit at 2.  The SAME
      two coalitions are the nu-anchors forcing max_i y_i >= 8, so one pair of
      values does both jobs -- floor pinning and ceiling level.
Ceiling uniqueness: if max_i y_i <= 8 then v({5,6,7}) = 24 forces y_5=y_6=y_7=8
and v({4,6,7}) = 24 forces y_4 = 8; the total leaves y_1=y_2=y_3=0.  So z is
the ONLY core point with max <= 8, hence Lmax.

Every row below satisfies g_i+g_j <= 4 on {1,2,3}, g_1+g_2+g_3+g_4 <= 8 and
g_1+g_2+g_3+g_5 <= 8 (so the caps are not disturbed), totals 32, and the six
rows together zero all seven coordinates.
"""
import sys
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/wt/coopgames/verifiers/lib")
import lib23 as L
import lmax as LM

n, FULL, T = 7, 127, 32
ROWS = [
    (2, 2, 2, 2, 2, 11, 11),   # = x, the target Lmin
    (0, 0, 0, 8, 8,  8,  8),   # = z, the target Lmax; zeroes 1,2,3
    (0, 0, 0, 0, 8, 12, 12),   # zeroes 4
    (0, 0, 0, 8, 0, 12, 12),   # zeroes 5
    (2, 2, 2, 1, 1,  0, 24),   # zeroes 6
    (2, 2, 2, 1, 1, 24,  0),   # zeroes 7
]
print("generator rows (common total 32):")
for r in ROWS:
    print("   ", r, " sum", sum(r))
assert len({sum(r) for r in ROWS}) == 1
print("zero cover:", all(min(r[i] for r in ROWS) == 0 for i in range(n)))

gens = [tuple(F(q) for q in r) for r in ROWS]
w, shift = L.normalize(n, L.envelope(n, gens))
assert all(s == 0 for s in shift), shift
print(f"v(N) = {w[FULL]}")

print()
print("designed pin values, as realized:")
def m(*ix):
    return sum(1 << (i - 1) for i in ix)
for lab, S, want in [("v({3,4,5,6,7})", m(3,4,5,6,7), 28),
                     ("v({2,4,5,6,7})", m(2,4,5,6,7), 28),
                     ("v({1,4,5,6,7})", m(1,4,5,6,7), 28),
                     ("v({5,6,7})",     m(5,6,7),     24),
                     ("v({4,6,7})",     m(4,6,7),     24)]:
    print(f"   {lab:16s} = {w[S]}   (designed {want})  "
          f"{'OK' if w[S] == want else 'MISMATCH'}")

print()
ex, bad = L.is_exact_lp(n, w)
print(f"EXACT at definition level (LP over the core, no vertex enumeration): {ex}"
      + ("" if ex else f"   fails at {L.nm(n, bad)}"))
x = L.lmin(n, w)
z = LM.lmax(n, w)
print(f"Lmin = {[str(q) for q in x]}   strata {[len(b) for b in L.strata(x)]}")
print(f"Lmax = {[str(q) for q in z]}   strata {[len(b) for b in L.strata(z)]}")
gap = sum(abs(x[i] - z[i]) for i in range(n))
print(f"||Lmin - Lmax||_1 = {gap},  ratio = {F(gap, T)}   (predicted 3/4)")
tx = [F(q) for q in (2,2,2,2,2,11,11)]
tz = [F(q) for q in (0,0,0,8,8,8,8)]
print()
print("VERDICT:")
print(f"  Lmin matches target : {x == tx}")
print(f"  Lmax matches target : {z == tz}")
print(f"  ratio = 3/4         : {F(gap, T) == F(3,4)}")
print(f"  exact + normalized  : {ex and all(w[1 << i] == 0 for i in range(n))}")
print("  => n=7 CFG-FAMILY INSTANCE REALIZED"
      if (x == tx and z == tz and F(gap, T) == F(3,4) and ex)
      else "  => NOT realized as designed")

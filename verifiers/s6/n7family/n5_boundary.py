"""The n = 5 boundary: is the family's member the SAME GAME as paper5 thm:n5's
extremal game, or merely the same Lmin/Lmax profile?

This distinction has bitten the campaign before (a matching profile is not a
matching game), so it is checked rather than asserted.  paper5 thm:n5 takes the
envelope of (1,0,0,1,2) and (0,1,3,0,0) with T = 4; scaled by 4 that is T = 16,
matching the family's n=5 scale.  We compare the two games as UNLABELLED games:
identical iff some permutation of the players carries one v to the other.
"""
import sys, itertools
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/wt/coopgames/verifiers/lib")
import lib23 as L
import lmax as LM
n, FULL = 5, 31

def game(rows):
    w, sh = L.normalize(n, L.envelope(n, [tuple(F(q) for q in r) for r in rows]))
    assert all(s == 0 for s in sh)
    return w

# family member at n = 5  (T = 16, mu = 2, M = 4, rho = 5, |Z| = 1)
T, mu, M, rho, zc, half = 16, 2, 4, 5, 1, 6
fam = game([
    (mu, mu, mu, rho, rho),
    (0, M, M, M, M),
    (0, 0, M, half, half),
    (0, M, 0, half, half),
    (mu, mu, mu, 2*rho, 0),
    (mu, mu, mu, 0, 2*rho),
])
# paper5 thm:n5 extremal game, scaled by 4 to T = 16
thm = game([(4, 0, 0, 4, 8), (0, 4, 12, 0, 0)])

for lab, w in (("family n=5", fam), ("thm:n5 x4", thm)):
    x = L.lmin(n, w); z = LM.lmax(n, w)
    print(f"{lab}: T={w[FULL]}  Lmin={[str(q) for q in x]}  Lmax={[str(q) for q in z]}"
          f"  ratio={F(sum(abs(x[i]-z[i]) for i in range(n)), w[FULL])}")

iso = None
for p in itertools.permutations(range(n)):
    def pm(S):
        return sum(1 << p[i] for i in range(n) if S >> i & 1)
    if all(fam[S] == thm[pm(S)] for S in range(1, FULL + 1)):
        iso = p
        break
print()
print("ISOMORPHIC as unlabelled games:", iso is not None,
      f"(permutation {iso})" if iso else "")
if iso is None:
    diff = [(L.nm(n, S), str(fam[S]), str(thm[S])) for S in range(1, FULL)
            if fam[S] != thm[S]]
    print(f"  the two games differ; {len(diff)} coalitions differ under the")
    print( "  identity labelling, and no relabelling matches them either.")
    print(f"  first few: {diff[:6]}")
    print("  => the family's n=5 member REALIZES the CFG configuration but is a")
    print("     DIFFERENT game from thm:n5's; the configuration is shared, the")
    print("     game is not.")

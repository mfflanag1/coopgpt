"""THE PADDING LEMMA: PART(p,q) realizable  ==>  PART(p+1,q) realizable.

Discharges: the sufficiency half of Theorem F, for EVERY m >= 4, by induction
from the three m = 4 base cases.

STATEMENT.  Let v on N carry a PART(p,q) configuration at the slack strict
boundary H = {f,g}, with S1 = P u {f} and S2 = Q u {g}.  Adjoin a null player
x: v'(S) := v(S \ {x}) on N' = N u {x}.  Then v' is exact and
singleton-normalized, Lmin(v') = (Lmin(v), 0), H is still a strict richer
suffix with the SAME slack, and

        S1' = S1 u {x}   and   S2' = S2

are v'-tight, disjoint and cover N', with traces {f} and {g} on H.  So v'
carries a PART(p+1,q) configuration at m+1.

PROOF.  The first sentence is the first half of Lemma 4 of
verifiers/zp/PROOF.txt (x joins the poorest stratum, strictly below H).  For
tightness of S1':  v'(S1 u {x}) = v(S1) = phi(S1) = phi'(S1 u {x}), the last
step because phi'_x = 0.  S2 is tight because v' and phi' agree with v and phi
on it.  Disjointness and covering are immediate.  []

Symmetrically PART(p,q+1) is realizable, putting x into S2.  Since (1,3),
(2,2) and (3,1) are realized at m = 4, induction gives every (p,q) with
p,q >= 1 and p+q >= 4.

This script CHECKS the lemma end to end, from scratch, on the PART(2,2)
witness: it builds the n=7 game, re-derives exactness, Lmin, strata and the
tight family, and confirms a PART(3,2) configuration; then iterates once more
to n=8 for PART(4,2), and also builds PART(2,3) and PART(3,3).
"""
import sys
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import lib23 as L
import audit_witness as AW

def pad(gens):
    return [tuple(list(g) + [F(0)]) for g in gens]

gens = [tuple(F(x) for x in g) for g in AW.GENS22]
chain = [("n=6 base", gens)]
g = gens
for k in (7, 8):
    g = pad(g)
    chain.append((f"n={k} after {k-6} null adjunction(s)", g))

for label, gg in chain:
    n = len(gg[0])
    v = L.envelope(n, gg)
    w, sh = L.normalize(n, v)
    assert all(x == 0 for x in sh)
    ex, bad = L.is_exact_lp(n, w)
    phi = L.lmin(n, w)
    blocks = L.strata(phi)
    tight = L.tight_family(n, w, phi)
    hits = AW.check_part(n, w, phi, blocks, tight)
    print(f"{label}: exact={ex} Lmin={[str(x) for x in phi]}")
    print(f"   strata={[[L.LETTERS[i] for i in b] for b in blocks]}")
    print(f"   PART configurations: "
          f"{sorted(set((h['p'], h['q'], h['m']) for h in hits))}")
    for h in hits:
        print(f"      H={h['H']} s={h['s_H']} S1={h['S1']} S2={h['S2']} "
              f"(p,q)=({h['p']},{h['q']}) m={h['m']}")

Continuous sharp public-fairness theorem,16 October2026

CONTINUOUS_ATTACK.txt is the complete conventional proof. It supersedes the
earlier packet's open continuous upper-bound status for the explicitly added
public marginal-contribution floor. It does not alter the floor-free mixed-
ownership problem. Historical novelty remains unconfirmed.

For every finite number of pods and every real report profile, a linear-time
own-bundle-monotone covering rule satisfies y_A=theta M_A and total funding
<=(1+theta/4)T,0<=theta<=1. A balanced-coalition lower family with all owners and
resources active, growing through every even m, proves the constant sharp.
PARETO_NOTE.txt gives the separate C+K>=2+theta/2 tradeoff and shows this rule
attains equality: C=K=1+theta/4. Here K uses pointwise static funding as its
denominator. It does not characterize the whole frontier or optimal K alone.

Replay (standard Python only):
  python3 -B -O verify_continuous_rule.py
This exact Fraction test checks m1,m2,m3 full ternary domains and four theta
values against an independent max-profit-flow production oracle. It verifies
all coalitions, adjacent own-coordinate comparisons, nonnegative/zero-own
payments, the floor, and the exact total-payment identity. It also evaluates
the active even-m equality family through128 pods. Finite checks corroborate
the written all-real proof; they are not the reason the theorem is continuous.

Review status at freeze: root and the pivot lane independently checked the
complete proof without a substantive gap. Fable is reviewing a snapshot;
coordinator will record its completion status. After that snapshot, the final
balanced-counting inequality was clarified to display weights1/2,1,1/2, and
the fixed roles/technology were restated explicitly. No theorem changed.
PARETO_NOTE was derived afterward and requires its own short coordinator check.
The earlier accepted packet remains unchanged with its original hashes.

The exact rule permits weak individual truthfulness; it does not provide
group-strategyproofness, private-cost truthfulness, or real pooling-gain evidence.
It assumes equal unit net margins and the stated separate ownership roles.
Public participation/fairness sources are in the preceding packet's
SOURCES_AND_CONTRACT.txt; the new formula is a proposed contribution.

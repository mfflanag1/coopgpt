**Provisional verdict: no substantive findings in reviewed scope.** The finite-n chain (translation reduction → symmetrization → null bound → q-potential → approximate Banzhaf induction → five-owner witness) checks out step by step; the only defect found is a mis-stated justification in the zero-sum merge case that does not affect the bound.

## Findings

**1. Low — PAIRWISE_GAIN_LINEAR_OWNER_LOWER.txt lines 119–121 (zero-sum merge case).**
Text says: if a merge removes two active coordinates, "use the smaller previous error, which is at most E_(r−1)". But when z_i+z_j=0, the merged coordinate becomes *null*, so h_merged is a null payment in [0,ε] while B_merged=0; its error is ≤ε, not ≤E_(r−2) (E_2=0 at r=4). The pair-sum error is then ≤2ε, which still satisfies the recursion: 2ε ≤ E_(r−1)+ε holds for r≥4 (E_3=1.5ε), and at r=3 the merged profile is (2,0,…) with G=0 so all payments are exactly 0. Bound (8) survives; the sentence should be corrected. Verification: recheck the three cases r=3,4,5 with z_i+z_j=0.

**2. Informational — hypothesis not load-bearing.** The "zero withdrawals by a member" convention is used only to derive cross-coordinate 1-Lipschitz (reduction §5), and the 2-Lipschitz remark on q (line 78) is never used. The lower proof needs only: singleton monotonicity, pair neutrality with both members' restoration bundles nonzero, coverage, budget, anonymity, resource symmetry. The theorem therefore holds under the weaker pair contract too; worth stating.

**3. Informational — symmetrization proof is sketch-level.** Lines 170–179 of the reduction assert that permutation/resource averaging preserves feasibility and translation equivariance. I verified: constraints are linear in y per profile, F=min is symmetric, translation commutes with both operations. Anonymity is genuinely needed (equal null payments; h_2=q(2−x) at (x,2−x); y_1=y_2=1/2 at (1,−1)), so this paragraph is load-bearing and should be promoted from "optional" to a stated lemma.

## Steps verified
- Translation operator maps X→X (G invariant, every coalition value shifts by t(Q)); L^m averaging error ≤KG/L; cluster point fixed; FIP for all t≥0.
- Pair condition (5) ⇔ original outside-production contract (both directions, non-canonical high profiles read via h).
- (3): S=0 at pure profiles, nonneg payments, equal nulls by anonymity.
- (4): G=0 at (2,0,…) forces all h=0; pair neutrality transports.
- q(3)≥1/2 and q(4)≥1 from (1,−1),(2,−2) symmetry + own monotonicity, both at total 2.
- Banzhaf merger identity recomputed by hand (conditioning on j∈R); r=1,2 exact; merged profiles stay in the class (total 2, neg mass non-increasing, ≤5 actives, null ε applies since n−r′≥n−5).
- (9) recomputed by hand: L(t)=[−q(t+2)+2q(t+1)−2q(t−1)+q(t−2)]/4; L(0)=L(2)=(2r₁−r₂)/4, L(1)=−r₁/2, E L=−r₂/8.
- E_5=57ε/8, 3E_5=171ε/8, ε=2K/(n−5) ⇒ K≥(n−5)/342.
- Upper: y_i=f_i+G/2 covers all Q (|Q|G/2≥G≥F(b(Q))−Σ_Q f_i by superadditivity), singleton/pair protection, budget S+nG/2.
- No owner splitting, homogeneity, or null-zero assumption used in the finite proof.

## Scope limitations
- Only the three notes and script in the packet reviewed; prior results (n=3 value 5/4, n=4 lower 9/7, ZERO_COOPERATION…) not checked.
- Script tests exact identities and the upper rule on random rational samples; it is not evidence for the all-mechanism lower bound. Not run.
- "Root verified" statements treated as non-evidence.

**Verdict: findings (one low-severity justification error, no effect on the stated bound; theorem (1) and upper n/2 hold as written).**

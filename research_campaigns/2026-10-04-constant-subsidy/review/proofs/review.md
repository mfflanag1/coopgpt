**Provisional verdict: no findings in reviewed scope.** I found no explicit error or counterexample in either draft. Every coefficient and inequality I could recompute by hand checks out; what remains are scope caveats and imported, unverified ingredients. Nothing was executed.

## Findings

**1. LOWER_BOUND_DRAFT lines 27–66 — verified, no defect.**
- **Coalition values:** C1–C4 have values 1, 2, t−1, t (L and H both give 1+2q = t−1 in C3). D1, D2, D4 have values 1, 2, t.
- **Profile X combination:** C1 + q·C2 + (t−1)·C3 + C4 has coefficients a: 2t, b: tq, u: t(k−1), v: tq(k−1), w: (k−1). The right side is 1 + 2q + (t−1)² + t = t². So (X) holds.
- **Profile Y combination:** A has coefficient 4q+6 = 4 + 2(t−1); the right side is 2t−1. So (Y) holds.
- **Deviation:** raising one unit owner in an L pool from 1 to t gives (t,1,2,…,2), a permutation of H, with T = t unchanged. Under the invariant rule that owner is paid A before and w after, so w ≥ A.
- **Final algebra:** the stated bound follows; the m=3 formula, the limit 3/4 and the k>17 threshold are correct.
- **Symmetrization:** valid because all pools have exactly m owners, so the wreath-product group acts on the fixed partition; averaging preserves coverage, budget and own-report monotonicity.
- **Limits:** the iterated and diagonal limits are correct. Each instance gives a bound strictly below 1; only the supremum is 1, so "≥1" applies solely to a constant uniform in both k and m.

**2. Low — LOWER_BOUND_DRAFT lines 12–16: theorem statement omits hypotheses.**
The bound is proved only for k ≥ 3 pools of equal size m, which appear in MODEL but not in THEOREM. For fixed m the bound is capped at 1 − 1/(2m−2). Suggested check: restate with explicit quantifiers and certify the two dual combinations in exact rationals for m = 2, 3, 4.

**3. THRESHOLD_DRAFT lines 16–28, 31–48 and 53 — verified, no defect.**
- **Coverage:** holds since v(S) ≤ T.
- **Monotonicity:** d_i = min(x,B); other own-pool caps equal min(c_l,B), constant in x. The win set is an intersection of down-sets (strict or weak per rival by priority), and expands as rivals' statistics rise. Conditional b_i is the Lebesgue length of E_x ∩ [0,d_i].
- **Medians, atoms, ties:** Φ_j ≤ a_j ≤ a_s ≤ Φ_s, with s lowest-priority among maximal medians, forces W ≠ s even on ties.
- **Probability:** p = r^(−r)/2 is right, and (1−p)^n ≤ 1/(1+np) is valid.
- **Total:** 1 + (r−1)·P(W≠s) is correct.
- **Asymptotics:** r^r ≤ k^(1−ε) holds for large k.

**4. Low — THRESHOLD_DRAFT lines 36–38: sampling law is implicit.**
"Distribution of Φ_j on the small box" must mean Z uniform on [0,1/r]^r, and the medians must be fixed before s is chosen. The text should say so.

**5. Medium (evidence gap) — THRESHOLD_DRAFT lines 21–22, 28, 55–57.**
The order-optimality claim imports three things not in the packet:
- that the M/k top-up is monotone and costs at most T;
- that the earlier sum-statistic rule belongs to this class;
- that its O(log k/log log k) bound is uniform in owner counts.

The lower bound itself is unaffected, since the top-up only raises payments. Suggested check: review SCALING_THEOREM.txt and the earlier upper-bound proof against this class definition.

## Scope limitations
- This was a hand check of the two drafts only; no exact LP or dual certification was supplied, and the prior-campaign files were not reviewed.
- The lower bound's 100% figure is for the unrestricted rule class and proves neither divergence nor existence of a constant.
- The (r−1)/4 divergence is restricted to the independent-threshold class and requires at least r owners in every pool; at that witness the marginal vector costs only T, as the draft says.
- Novelty was not assessed.

## Verdict
No findings in reviewed scope for the lower bound and the class lower bound; insufficient evidence for the order-optimality claim until the imported upper-bound ingredients are reviewed.

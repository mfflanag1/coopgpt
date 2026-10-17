**Provisional verdict: no substantive errors found in reviewed scope.** Every slope, the funding constant, inequality (3)/(4), and the 9/16 vs 11/24 counterexample recompute correctly by hand. Most important note: the checker hard-codes the two star-boundary payments (1/3, 1/8) rather than deriving them from formula (1), so it does not independently confirm the counterexample's boundary half.

## Findings

**F1 (Low, checker lines 64–65).** `boundary_one=Q(1,3)` and `boundary_half=Q(1,8)` are literals. Hand check: (2,1/2,−1): B=1, r=(1,1/2), R=3/2, p=1/3, u₁=1/3 ✓; (2,1/2,−1/2): B=1/2, r=(1,1), R=2, p=1/4, u₁=1/8 ✓. Values are right, but the script should compute them via the star formula to count as verification. Suggested fix: factor the star rule into a function and call it.

**F2 (Low, txt lines 50–56 and 66–68; checker 45–49).** "Every required pair slope" and the checker only cover pairs that *contain the varied owner*. Pairs excluding the varied owner have negative slope (−pa(r_k+r_l)) when x_i rises. This is consistent with the pair-Lipschitz form actually used in §4 (pair (i,j) with j varied), but the definition is not in the packet; if the standard requires all pairs, §3 would not hold. Verification: confirm the definition in the main paper.

**F3 (Low, txt lines 89–94).** Inequality (4) silently needs three things: anonymity ⇒ equal null payments (deterministic rule, or in expectation), coverage of the active grand coalition ⇒ active payments ≥ F, and gain budget in the form Y ≤ (1+K)F. All are reasonable but only "nonnegativity and the gain budget" are cited. Arithmetic is right: Σ_J K(B−b_j)/(n−k+1) = K(m−1)B/(n−k+1), giving KB/(n−k+1) after dividing by m−1.

**F4 (Info, checker lines 17–21, 28–32).** Every mask adds `pb`, so only coalitions containing the negative owner are checked (others have worth 0, trivially covered). The `coalition_checks` count and the "all coalitions" comment overstate coverage slightly.

**F5 (Info, checker line 34).** The exponential branch is never exercised numerically; the bound p ≤ 1/(2R) for R ≥ 2 is asserted analytically. I verified it: g(R)=R·e^{−(R−2)/2} has g(2)=2 and g′ ≤ 0 for R ≥ 2. The funding maximum at R=3 giving 1/(2√e) ≈ 0.30327 also checks.

## Verified by hand (no issues)
- C¹ match at R=2 (p=1/4, p′=−1/8 both sides); agreement at A=B (R=1, p=1/2).
- a=−p′/p=1/min(R,2); slopes D u_i=p(1−ar_i), D u_k=−par_k, D u_B=pa; B-variation Dp=paU/B and all three singleton slopes; pair sums 1 and 1−p[1+aU(1−r_i)].
- p(1+aU) ≤ 1 on both branches (≤1/R for R≤2; ≤1/2 for R≥2).
- (3): m pair bounds summed minus coverage of {i}∪J (worth B since x_i≥B).
- Counterexample: B=3/2, R=4/3, p=3/8, 9/16 − 11/24 = 5/48; local pair slope 1+(1−s_j)paU.

## Scope limitations
Definitions of pair-Lipschitz, gain-K budget, "protected pair," and "null-zero rule" are not in the packet; checker not executed by me; no files outside the two supplied.

## Verdict
No findings of correctness significance; minor verification gaps (F1–F3) worth closing. The document's own scope disclaimer (star chart only, not a global mechanism) is accurate.

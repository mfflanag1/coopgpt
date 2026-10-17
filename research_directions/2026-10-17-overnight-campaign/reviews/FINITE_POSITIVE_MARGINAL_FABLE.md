**Provisional verdict: no substantive findings in reviewed scope** (one documentation/code mismatch). The dual logic is sound and the two coordinates I could recompute by hand (v_1 and v_15, v_14) match the stated vector exactly. I could not execute the checker; all statements below are from reading.

## Findings

**1. Medium — transition description contradicts the actual transition (THEOREM.txt L38, CHECK.py L22–23).**
Text says focal owner 0 reports (0,0,t/k) "then restores (0,0,1/k)". For t≥1 that would be a *decrease*, and the only t=0 row would be a no-op. The code actually computes `high = min(center, leaf + (S&1))` with `leaf` already containing `t*(S&1)`, i.e. the focal moves t/k → (t+1)/k. Formula (3) and the prose at L43–45 ("at least t+1 centers present") are consistent with t/k → (t+1)/k, not with 1/k. Since t<k, (t+1)/k ≤ 1, so the profile stays in [0,1]^3 and the inequality direction (coalition payment must not decrease under the coalition's report increase ⇒ D·W ≥ 0) is correct. Fix the wording in both files; no change to the mathematics.
*Verification:* confirm by inspection that `direct_transition` with t=0 gives D_{4,11,0;1}=11/15 (which it must, since v_1 = (162/125)(11/15) = 594/625 matches the JSON).

**2. Low — checker independence is partial but adequate.**
`direct_transition` genuinely reconstructs each row from raw 2^16 scaled min3 coalition values, and `direct_coverage` reconstructs c_l from a raw pure-three game; neither reuses formula (3). The remaining proof steps (symmetrization, balanced-profile budget ΣW≤κ, inequality directions, "v≤1 ⇒ ΣW ≥ v·W ≥ 5") are analytic only. L66's `min(l+1,…)-min(l,…)==1` is a vacuous stand-in for the balanced-profile step; the `verification_coefficients` comparison at L64 is a consistency check against the author's own JSON, not an independent derivation. Acceptable, but the file should not describe itself as checking "all 16 dual inequalities" beyond v_l ≤ 1.

**3. Hand-verified identities (no finding).**
- Balanced profile: every marginal is 1, total 16·ΣW ≤ κ·16 ⇒ (1). ✓
- Coverage: P(both other pure owners in uniform l-subset of 15) = l(l−1)/(15·14); three owners ⇒ (2). ✓
- Row (3): δ(S)=[0∈S][no keeper][c≥t+1]; focal gain counts Σ_j C(k,j)C(z,l−j); each keeper loses when 0∈R and no other keeper ⇒ −(q−1)Σ_j C(k,j)C(z,l−1−j). ✓ Scaling by k cancels.
- v_15: only the q=2 row contributes (−1 each); 15 − 281/20 = 19/20. ✓
- v_14: 13 − (45187/500)(2/15) = 3563/3750; q=2 and q=4 rows contribute 0 at l=14. ✓
- v_1 = 594/625 is the maximum; slack 31/625 matches CHECKS.json. ✓
- Symmetrization preserves nonnegativity, funding, all-coalition coverage and size-≤4 TCWM as a convex average on the same 16-owner domain. ✓

## Scope limitations
- No code execution; the 12 interior coordinates of v and all 14 rows are only verified by the author's script, which I read but did not run.
- Did not audit SEMIVALUE_MIXTURE_* or GENERAL_FACE_AVERAGE beyond confirming the cited factor-2 reference and the TCWM direction convention.
- Novelty, sharpness at 5, and any unrestricted-mechanism lower are explicitly out of scope and not confirmed.

## Verdict
**Findings** — one documentation mismatch (Finding 1) that should be corrected; the certificate's mathematics and checker design are otherwise consistent within the reviewed scope. The theorem as a finite architecture lower (κ ≥ 5 for fixed nonnegative whole-owner marginal weights, N=16, s=4) is supported by the supplied evidence, contingent on the script passing as reported.

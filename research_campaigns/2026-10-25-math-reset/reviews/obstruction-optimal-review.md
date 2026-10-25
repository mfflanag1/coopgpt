**Provisional verdict: no findings in reviewed scope (one low-severity documentation inconsistency).** The most important check — that the three added coverage families zero every slack while leaving the marked a_g rows and nu_z untouched — recomputes correctly, and the quantifier limitation (chosen optimal dual, not all optimal duals) is stated correctly and is substantiated by a valid counter-example.

## Findings

**1. Low — Verification record does not match the packet's exact-check file.**
`OPTIMAL_COVERAGE_OBSTRUCTION_ADDENDUM.txt:98` claims Fraction checks at m=1,2,3,7,20,64; `EXACT_CHECK.json` contains m=1,2,4,8,16,64. The JSON also records only `optimal_variant_L`, `L_over_D`, `all_slacks_zero`; it has no field for the all-singleton z-row variant, coverage incidence one per owner, or the slack-free resource identity, all of which line 98–101 says were checked. Suggested verification: regenerate the JSON from the actual check script, or amend lines 98–101 to match. This does not affect the symbolic argument, which I recomputed independently below.

## Recomputation (all consistent with the text)

- **Base g-array** (lines 120–124 of base): a_g all 0; b_g: v_g = −1/2; c_g: w_g = −1; z: (1/2,1/2,1). Confirmed from the four comparison rows.
- **Augmentation:** +1/2 on v_g at b_g, +1 on w_g at c_g, +1/2 on u_g,v_g at z → g = 0 at a_g,b_g,c_g and (1,1,1) at z = nu_z. sigma ≡ 0. Correct.
- **Objective:** F(b_{v_g}(b_g)) = 1, F(b_{w_g}(c_g)) = 1, F(b_{U∪V}(z)) = 4m. Added (1/2)m + m + 2m = 7m/2; total L = 6m = D. L_cov = 4m, L_cmp = 2m. Correct.
- **Capacity-weighted residual (line 62–63):** u_g: ½·1 + ½·2 = 3/2; v_g: ½·1 + ½·2 = 3/2; w_g: 1·1 = 1 — matches the base residual (3/2,3/2,1) with no slack. Correct.
- **All-singleton variant:** each lambda_(z,{i}) = 1/2 with F = 2 gives 1 per owner, 2m total; incidence unchanged. Correct.
- **Normalized D=1:** dividing by 6m scales eta_g to 1/(12m); the lemma gives D' ≥ (6m−3)/12 = m/2 − 1/4 with D'=1, same ratio. Scale-invariant; correct.
- **Lower bound survives augmentation:** the lemma (base §1) uses only the marked rows and A_2(a_g) disjointness (base §4), both independent of the added coverage; "other coverage" is explicitly tolerated (base line 56). nu_z=1 is still the only budget so D=6m. Correct.
- **Quantifier (lines 85–91):** grand-coalition coverage at z with coefficient 1, nu_z=1, no comparisons: g(z,i)=1=nu, objective F(B_z)=6m=D — a valid optimal, trivially one-layer certificate whose coverage is retained at cost 6m. So the addendum correctly asserts existence of a bad optimal dual and correctly disclaims a bound over all optimal duals or any failure of K=1.
- **Upper witness:** none claimed for the augmented array (lines 93–95), and line 177's two-sided estimate is correctly restricted to the base array. No gap.

## Scope limitations

- The weak-duality step (lines 52–55) relies on the LP framing and the K=1 payment rule of base §2, which were reviewed previously and are taken as given here.
- I did not re-audit base §1/§4 (disjoint-neighborhood lemma) beyond confirming the augmentation introduces nothing it depends on.
- Cannot confirm the Fraction checks were run; only the JSON contents are evidence.

## Verdict

**No invalidating findings in reviewed scope.** The augmentation yields a feasible, zero-slack, optimal (L=D=6m, or L=D=1 normalized) certificate; the all-singleton variant is equivalent; the m/2 − 1/4 repair lower bound carries over unchanged; and the "chosen optimal dual vs. any optimal dual" distinction is stated accurately. Only the verification-log/JSON mismatch should be corrected.

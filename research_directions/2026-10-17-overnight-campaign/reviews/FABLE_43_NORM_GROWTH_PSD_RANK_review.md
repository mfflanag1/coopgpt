**Provisional verdict: no substantive findings in reviewed scope** (both proofs check out analytically; scripts read, not run). Most important note: the ℓ_p lower bound's step (9) depends on the TCWM contract applying to a coalition that includes an *unchanged* member (the original group-(m−1) owner); the contract definition is not in the packet.

## Findings

**1. [Low / dependency] P_NORM…LOWER.txt lines 113–116 — TCWM scope for mixed coalitions.**
The derivation "new group paid at least b" needs: if only the m−1 zero owners restore, the total of {old group-(m−1) owner} ∪ {zero owners} is nondecreasing. If TCWM covered only the set of changers, one would get only ≥ (m−1)w and (9)–(10) collapse. The text explicitly asserts the inclusive form, and the PSD file's second counterexample (unchanged owners 2,3 in the coalition) uses the same convention, so this is consistent program-wide — but verify against SHARP_TCWM_MULTIGLOVE_THEOREM.txt's definition.

**2. [Info] P_NORM_GROWTH_CHECK.py lines 28–33 — gate differs from the text.**
The script uses m = isqrt(p // ceil(log₂p)) rather than the text's m = ⌊√(p/log₂p)⌋, and does not test m ≥ √(p/log₂p)/2. Both facts are elementary (⌊x⌋ ≥ x/2 for x ≥ 2; x ≥ 2.53 at p = 32), so no gap, but the checker does not cover §4 as written. Lines 19 and 25 are tautological identity checks.

**3. [Info] PSD_GAIN_ORIGINAL_RANK_THEOREM.txt line 45 — Scope 1 relies on an external file.**
PSD_RANK_FUNDING_BASELINE.txt is not in the packet. I verified the claim directly: with f_i ≡ 0, y_i = rank(X_i)T/m, and a coalition restoring D_i: if F(ΣD) > 0 then Σ_Q rank(X_i+D_i) ≥ Σ_Q rank(D_i) ≥ m, so Σ_Q Δy ≥ T′ − (Σ_Q r_i/m)T ≥ T′ − T ≥ F(ΣD) when Σ_Q r_i ≤ m, and ≥ (Σ_Q r_i/m)(T′−T) ≥ T′−T otherwise; if F(ΣD)=0 monotonicity of r and T suffices. Holds.

**4. [Info] Line 48 — "improves the standard rank-m grand-marginal gain factor" is a comparative claim whose comparator is undefined in the packet.** No worst-case claim is made, so nothing to falsify; note R/m can equal n.

## Verified steps (independently rederived)
- Embedding: L linear; ‖x‖_p ≤ S; L(e_j) on boundary; V(diag)=2 exactly (incl. m=2); max|S−2a_j| = S−2 under min a_j = 1; (6) via dropping all but the max term.
- (7): (1+1/m²)^{m²} ≥ 2 ⇒ 1−m^{−1/p} ≤ 1/(m²+1); S₀=(m−2)m+2, S₁=(m−1)m+1 < m² ⇒ V < 3.
- Symmetrization preserves budget/coverage/TCWM/nonnegativity; group payments a,b,w justified by coordinate+owner permutations.
- (8): budget minus diagonal coverage, w ≥ 0; m=2 case valid (vacuous if κV₀<2).
- (10): (m−1)[1−(κV₀−2)/(2(m−1))] = m−κV₀/2 ⇒ κ ≥ 2m/9; (3) parameter conversion correct.
- PSD: G = λ_min(ΣU_i) ≥ 0; rank(U_i) ≤ rank(X_i) (f_i>0 forces full rank); PD residual ⇒ Σ_Q a_i ≥ 1; Loewner monotonicity ⇒ residual ≤ G; coverage holds.
- OUT: PSD rank monotone (ker(X+D) ⊆ ker X); (a′−a)G′ ≥ 0; (1−a)Δf + aΔT ≥ F(D) by Weyl, valid even when ΔG < 0.
- Both counterexamples recomputed exactly (2/3→13/30, loss 7/30; (½,½,½)→(1,0,0), F(D)=0). Script arithmetic matches.

## Scope limitations
Scripts not executed; diagonal-only tests acknowledged in text. Contract definitions (TCWM, full-OUT, κ_opt) and the two referenced files not supplied. Historical priority not assessed.

## Verdict
No findings of error in reviewed scope. Routine rank lemma correctly scoped (no worst-case improvement claimed); the ℓ_p growth result is valid conditional on the inclusive TCWM coalition convention (Finding 1).

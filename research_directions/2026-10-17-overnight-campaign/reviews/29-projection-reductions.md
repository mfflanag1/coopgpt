**Provisional verdict: no substantive findings in reviewed scope.** Both KKT constructions and the Gram maximum principle check out algebraically; the only gaps are minor hygiene/scoping items, none of which undermine the stated results.

## Findings

**1. (Low) Implicit `b^i ≥ 0` — UNIFORM_VETO_AMPLIFICATION_REDUCTION.txt, lines 7, 42, 93.**
"Downward relaxation `b^i ≤ 1`" never states a lower bound, yet "These demands lie in [0,1]" (line 42) and "These are at most 1" (line 93) require `b^i ≥ 0` for the composite to remain in the nonnegative-demand class. Verification: add `0 ≤ b^i ≤ 1` to the base definition. (The dual-mass lemma itself survives either way, since `||q||² = λᵀb` and the pair (λ, μ) is feasible for the full dual regardless of μ.)

**2. (Low) Cross-file dependencies not in packet — lines 61–70 (veto file); line 80 (column file).**
The "fixed-owner production transfer" relies on BALANCED_CLOSURE_AND_ROW_RELAXATION.txt and BOOLEAN_PROFILE_REALIZATION_LEMMA.txt; the "truthful on every local monotone report array" and "incentives are immediate" claims (column file, lines 66, 74) depend on a mechanism model not supplied. These cannot be audited here. The projection results themselves do not depend on them.

**3. (Informational) Attainment remark is unnecessary — veto file, lines 56–59.**
For each `i`, `q^i_i` is continuous in `b^i` over the compact box, so the base supremum is attained; the approximation step is harmless but not needed.

## Verified steps (independently recomputed)

- **Dual-mass lemma (1):** `||q^i||² = λᵀb ≤ L_i`; dual feasibility gives `2L_i − ||q^i||² ≤ ρ`; hence `L_i ≤ ρ`. ✓
- **Veto full projection:** minimizing `c² + K(1−c)²ρ` gives `u = Kρ/(1+Kρ)`. ✓
- **Veto witness KKT:** veto stationarity `α_i((K−1)ρ + L_i) = 1 − α_i` holds by definition of `α_i`; complementary slackness inherits from base. Lower bound (4) algebra: `(K²ρ² + KE) − (1+Kρ)² = K(E−2ρ) − 1`. ✓
- **Union product:** full multipliers `∏λ_{S_k}/(Kρ^{K−1})` sum to `z_j/K` per coordinate; witness multipliers give `α_i q^i` in block `k` and `α_i L_i z/ρ = β_i z` elsewhere; off-focal tuple demand `α_i + (K−1)β_i = 1`. ✓
- **Finite threshold:** `K/(ρ+(K−1)L_i)` has derivative sign `ρ − L_i ≥ 0`, so `E_K/ρ_K` is nondecreasing with limit `ρ Σ(p_i/L_i)²`; strict limit `> 2` forces some finite `K`. Also `(5)` implies `(3)` via `p_i/L_i ≥ p_i/ρ`. ✓
- **Column-two:** `x = Aᵀλ ≥ 0` automatically, so the sign constraint is inactive. On an open piece a tight row with fixed other RHS must be independent and have positive multiplier; `q = Bᵀ(BBᵀ)⁻¹b_B` is valid for any independent spanning subset of tight rows. Weak diagonal dominance of `G` follows from column incidence ≤ 2. Maximum-principle propagation: equality forces neighbors to attain the max with alternating sign; a source-free equality component yields a nonzero kernel vector, contradicting PD. Own derivative `w_r` or `w_r + w_s ≥ 0`. ✓ Checked on path examples (e.g., `G = tridiag(1,2,1)`, `w = (3,−2,1)/4`).
- **Funding 2T bound and sharpness example** `2(k+1)/(k+2)` with `a = 2c = 2/(k+2)`. ✓

## Scope limitations

No files executed or inspected beyond the two supplied. The target conjecture (2) and the notion of "own-row envelope" are taken as defined internally. Production/incentive transfer claims are unverified (Finding 2).

## Verdict

**No findings** of correctness, regression, or research-validity significance in the reviewed scope. The two architecture results are sound as stated; recommended edits are limited to making `b^i ≥ 0` explicit.

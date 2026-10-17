**Provisional verdict: no findings in reviewed scope.** The KKT identity (1)–(2), the firm-nonexpansive bound (3), the scalar corollary (4), and the growing veto/group obstruction all check out algebraically; the production realization and own-report envelope at the all-ones profile are correctly derived. The note correctly refrains from claiming the diagonal inequality Σ E_i² ≤ T².

## Findings

**No correctness findings.** Verified by hand:

- **Total incident multiplier = d** (line 14): q_i = Σ_S λ_S A_{S,i} = Σ_{S∋i} λ_S since A is 0/1. ✓
- **(1)** (lines 20–23): u − dp = A_offᵀλ_off with λ_off ≥ 0, off rows tight when λ_off > 0 at unchanged b_S, and u ∈ K_{−i} because off rows omit i. These are exactly the KKT conditions of proj_{K_{−i}}(dp); omitting x ≥ 0 is harmless since A_offᵀλ_off ≥ 0 and the KKT point is unique. ✓
- **(2)**: Σ_S α_S(d + 1_{S∖i}·u) = Σ α_S b'_S ≤ B uses b' ≤ b on incident rows only. ✓
- **Firm nonexpansivity sign** (line 28): ⟨Pu−Pv, x−y⟩ ≥ ‖Pu−Pv‖² with x = dp, y = 0 gives d p·(u−r) ≥ ‖u−r‖². ✓ Then d² + ‖u−r‖² ≤ d(d + p·u) − d p·r ≤ d Σ α_S[b_S − r(S∖i)]. ✓
- **(4)**: dropping ‖u−r‖² ≥ 0 and dividing by d > 0; r depends only on unchanged off rows, so the bound is uniform over relaxations. ✓
- **Example (5)**: symmetric KKT x = Σ λ_g 1_{row g} gives u = mℓ, u + kℓ = 1 ⇒ ℓ = 1/(m+k), u = m/(m+k); ‖x‖² = m/(m+k). ✓ General b_g: λ_g = (b_g−u)₊/k, u = (1/k)Σ(b_g−u)₊ has a unique solution (LHS increasing, RHS nonincreasing); dλ_g/db_g = (1 − 1/(k+a))/k ≥ 0 on active regions, so own payments are monotone and E_i equals the full-profile value. ✓
- **σ values**: group owner i: off system is the (m−1)-group system, r_0 = (m−1)/(m+k−1), r = 0 on g∖i (unconstrained) ⇒ σ_i = k/(m+k−1); veto: K_{−0} unconstrained, r = 0, σ_0 = 1. For m = k = t: Σσ = 1 + t³/(2t−1), Σσ² = 1 + t⁴/(2t−1)², both Θ(n) vs. true 1/2. ✓
- **Production realization** (lines 75–93): F is concave, homogeneous, nondecreasing; v(S) = 1 iff S ⊇ {0} ∪ (whole group); multi-group rows redundant. Under group-owner report h at others = 1, multi-group rows have demand min{1, h+1} = 1, implied by another full-group row; under veto report h all productive rows have demand h, implied by single-group rows. So the cover polyhedra equal the sparse system with b_g = h, and (5) with monotonicity gives the actual M_i^F at the all-ones profile. ✓
- **Checker witnesses**: both hand-verified (representation q = Aᵀλ, tightness of positive-multiplier rows, incident sum = d; witness 2 is genuinely nonmonotone: coord 1 rises from 1 to 13/12).

**Clarification (not an error), line 92:** "true all-profile own-report envelope" means sup over owner i's own reports with all others fixed at 1. At general heterogeneous base profiles multi-group rows are not implied by single-group rows (e.g. c_0 ≥ m_g + m_{g′}), so the sparse reduction is specific to the all-ones base. The note only needs and only uses that case.

**Checker limitation:** the growing-example checks are closed-form arithmetic, not independent KKT recomputation via `projection`; adequate given the symmetric derivation, but not an independent test.

## Scope limitations
Snapshot only; no execution. Checker's `projection` returns the first feasible active set with nonnegative Gram-solution multipliers; it skips singular Gram systems, which could miss degenerate instances (not an issue for the two witnesses).

## Verdict
**No findings in reviewed scope.** The exact identities and the Θ(n) obstruction to curvature-free scalar slacks follow. The diagonal conjecture Σ E_i² ≤ T² remains unproved, as the note states.

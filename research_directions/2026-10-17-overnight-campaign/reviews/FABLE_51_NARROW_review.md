**Provisional verdict: no findings in reviewed scope.** Both four-owner obstructions check out algebraically and logically under the stated architecture and the campaign's weak-underreport pair-TCWM definition. Most important observation: the arguments' validity hinges on (a) the standalone-plus-residual form `y_i = f_i + u_i(z)` being assumed, and (b) pair-TCWM protecting a pair when only one member restores — both are flagged in the notes, not hidden.

## Findings

**1. Adaptive semivalue barrier — polynomials verified (no defect).**
- `z_L=(2,1,-1,0)`: owner 0 marginal is 1 iff S∋2, S∌1 → `p(1-p)` (null owner 3 contributes factor 1); owner 1 same by symmetry; owner 2 marginal 1 iff S∩{0,1}≠∅ → `2p-p²`. Identity (1): `3a+∫p² = ∫(3p-3p²+p²) = ∫(3p-2p²) = a+b` ✓.
- `z_H=(2,1,-1,-1)`: owner 0: `2p(1-p)² + 2p²(1-p) + p³ = 2p-2p²+p³` ✓; owner 2: cases P∈{1,2,3} give `p(1-p)² + p(1-p) + p² = 2p-2p²+p³` ✓; owner 3 symmetric.
- `u≡0` at `(2,1,0,0)` since v≡0 ✓; `∫p² dμ_L>0` else a=b=0 contradicts a+b=1 ✓; `3t≥2` from `v({0,2,3})=2` ✓; `2t−a > 4/3−1/3 = 1` strict ✓. Padding to n>4 leaves polynomials unchanged (null-owner membership sums to 1) ✓.

**2. Common-degree barrier — arithmetic verified (no defect).**
`d_L=(1,1/4,5/4,0)`, `d_H=(5/4,1/2,5/4,1/2)` ✓; γ_L=4/9, γ_H≥2/5, 7/10−25/36 = 1/180 ✓. Symbolic range: `(1+3t)(2+t) > 2(1+t)³ ⇔ t(1−3t−2t²)>0 ⇔ t<(√17−3)/4≈0.281` ✓; t=1/4 inside. The `p→0` limit `B_i^p/p → Σ_j v({i,j}) = d_i` ✓, so the CONSEQUENCE claim is consistent.

**3. Lipschitz necessity (reduction §3) — correct under form (P).** Restoring `x'−x` of the opposite resource to a pure owner raises `f_j` by `x'−x` and shrinks `|z_j|` to `x`; pair-TCWM yields the upper inequality. Both notes' "original-report deviation" sections instantiate this correctly (payments `1+a` vs `2t`; `25/36` vs `≥7/10`).

**4. Minor (low) — wording/scope, adaptive note line 6–7.** "The law can depend on every report" overstates: `μ_z` is indexed by the residual profile only; dependence on raw `(a,b)` is only WLOG via the translation reduction, which does require gain funding. The theorem text does say gain funding is used only for the reduction, so this is consistent but could mislead a reader of line 6 alone.

**5. Minor (low) — script coverage.** `check_adaptive_and_degree.py` verifies polynomial identities and the 1/180 gap, but does not assert the adaptive contradiction `2t−a>1` nor the symbolic range bound. Suggested verification: add `assert 2*Q(2,3) - Q(1,3) > 1` and a check of `2t²+3t−1<0` at `t=1/4`.

## Scope limitations
- Cannot execute the script; `Fraction(0)**0 == 1` behavior assumed.
- Did not verify `PAIRWISE_GAIN_TRANSLATION_REDUCTION.txt` (not in packet), on which the "architecture WLOG" rests.
- The weak-underreport pair-TCWM definition (unchanged protected member allowed) is taken from the reduction note as given; if the campaign definition required both members to change, the pair deviations here reduce to singleton-plus-bystander and the contradictions would need rechecking.
- Novelty/priority not assessed.

## Verdict
**No findings in reviewed scope.** Both architecture obstructions are correct as stated; items 4–5 are presentational.

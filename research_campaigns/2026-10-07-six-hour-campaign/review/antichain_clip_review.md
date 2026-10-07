**Provisional verdict: no findings (no invalid step located) in reviewed scope, subject to the dependency caveats below.** Most important observation: both notes check out line by line; the only unverifiable steps are those that rest on CONTRACT.txt definitions not in the packet.

## Findings

**ANTICHAIN_CASES.txt — §1 (1), lines 19–30.** Verified: the R₋ₑ flow avoids e, so every containing cut C satisfies D(cᵗ)(C∖{e}) ≥ R₋ₑ; if d > T−R₋ₑ every containing cut exceeds T ≥ T(cᵗ), so a minimum cut C₀ excludes e; then (Bₜ−Aₜ)₊ ≤ Bₜ ≤ Σ_{C₀} D_h U_h gives z ≤ T(cᵗ)/2 ≤ T/2. Case d ≤ T−R₋ₑ is trivial. Zero cases (T=0, D_e=0, R₋ₑ=0) collapse correctly. *Low (dependency):* steps "flow feasible under c ⇒ feasible under D(c)", "min structural cut under D equals T(cᵗ)", and "D_e(cᵗ) ≤ D_e(c)" all rely on the CONTRACT definition D_h = min(c_h, maxflow through h); consistent with BASE_FLOW_DOMINATION line 26 but not checkable here.

**§2 (2), lines 36–41.** Valid: paths through f avoid e, so R₋ₑ ≥ D_f; the three-case split (D_f ≤ T/2, D_e ≤ T/2, both > T/2) covers everything, including equality.

**§3 (3), lines 44–79.** Verified: prefix/suffix path regions are edge-disjoint in a DAG, so D_i = min(c_i,B); external caps are constant for aggregate ≥ B because bundle flow is ≤ B regardless of bundle capacity; minimal cuts δ⁺(S) contain all or none of the bundle; z_i = D_i·p follows from E min(D_i,(B−A)₊) = D_i·Pr(D_iU_i < B−A); Wp ≤ B uses the supplied domination lemma. Monotonicity for t ≥ δ_i holds since only D_i = min(t,B) moves. Algebra δ_i W ≤ B D_i reduces to s_i(B−D_i−s_i) ≤ 0, true since D_i ≥ B−s_i. B=∞/B=0 edge cases handled. No gap found.

**§4 scope statement** is accurate (not an overclaim): a bundle plus one extra owner is explicitly excluded.

**COMMON_CLIP_OBSTRUCTION.txt.** Cuts: δ⁺{s}=2, δ⁺{s,B}=1+h, δ⁺{s,A,B}=3+h, δ⁺{s,A}=4.1 ⇒ T=min(2,1+h); clipped caps correct. Identity line 25 checked in all three regimes. Survival (1−r/δ)(1−r)²/(2T) recomputed (needs T≥1, satisfied). E W = (δ/4−δ²/6+δ³/24)/T = 187/(8000T) ✓. Formula (3) derived via E[min(h,Y+W)−min(h,Y)] = ∫₀^δ Pr(W>r)F_N(h−r)dr ✓. Large-N bound: Chebyshev 1/(120000·0.0225)=1/2700, 187/112000−1/2700 = 3929/3024000 ✓. §5 effective-cap claim (D_z=D_x=1, D_g=0.1, D_Yi=1/6, D_h=h) ✓.

**common_clip.py.** `coeff` and `density` lists match the survival polynomial and its negative derivative; atom mass 1−1/(2T) correct; `monomial_integral` correctly expands (a±r)^p r^k; density representation uses E min(h,Y+w) = ½+w−L_N(1−h+w) correctly. Rough numeric sanity check (w(3/4)≈0.5123, w(1)≈0.5117) is consistent with the certified gap ≈6.4×10⁻⁴.

*Informational:* the asserted N=5 gap < 0 shows the certificate depends on concentration; the note's "sufficiently concentrated Y" wording is appropriate.

## Scope limitations
- CONTRACT.txt (definitions of D, structural cuts, z, y) not supplied; dependency steps above accepted as stated.
- I did not execute the script; I rely on the stated successful run.
- COMMON_CLIP lines 6–8 (budget property of the candidate rule) are outside the audited claim and unverified.
- BASE_FLOW_DOMINATION treated as reviewed, not re-audited.

## Verdict
**No findings in reviewed scope.** Both proofs and the exact-integration code are internally consistent; stated scope limitations are not overclaimed.

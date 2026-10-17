**Provisional verdict: no findings in reviewed scope (all displayed arithmetic independently re-derived and confirmed; scope labels correct).** Most important point: the 2×2 Huber counterexample is exact — I reproduce y′₁−y₁ = −187/672800 by hand — and the caps/lifts genuinely leave it unchanged.

## Findings

**No correctness findings.** Verification details by file:

**PSD_SPECTRAL_HUBER_OBSTRUCTION.txt**
- Minimizer (lines 13–19): h is C¹ and convex; restricted to anti-aligned frames the objective is convex in p₂, stationary at p₂=a/(2b)<1/2, p₁=1−a/(2b)>1/2. Anti-alignment is strictly optimal since h(p₁)>1/4>h(p₂); uniqueness holds. Both forms of (1) check.
- det X = det Y = 0; C = diag(1/4,1); P = diag(7/8,1/8); y₁ = 23/160 ✓.
- X′, C′ entries ✓. tr C′ = 873/580 = 37/145+5/4; det C′ = 26825/84100 = (37/145)(5/4) ✓, so eigenvalues are exact.
- P(C′) = [[26/29,−24/725],[−24/725,3/29]], trace 1 ✓. y′₁ = 12066/84100 = 6033/42050 ✓; difference −187/672800 ✓ (LCD 2⁵·5²·29²).
- Differential K (lines 54–58): recomputed dP₁₁, dP₂₂, dP₁₂ at diagonal C; K entries, det K = −3/3200, (1,6)K(1,6)ᵀ = −1/40 all ✓.
- Caps: 23/160<1/4 and 6033/42050≈0.1435<37/145≈0.255; F(Y)=0 so V₁=T. Inactive ✓.
- 3D lift: with third eigenvalue c, p_b=a/(2b), p_c=a/(2c), p_a=1−a/(2b)−a/(2c)>1/2 at both profiles, so block price = P₂ₓ₂ − (a/(2c))Π_a ✓. Using Π_{a′}=(24,−1)(24,−1)ᵀ/577, I get decrease −21818/1941028000 = −10909/970514000 ✓. For m≥3 with Σ1/c_k=1/10: −561313/3882056000 ✓. Zero eigenvalues persist for both owners; f_i=0 so reserve/netting variants are vacuous ✓.

**PSD_SHIFTED_HARMONIC_STOPPING.txt**
- Total = m/D+θT ✓; D≥1/(cT) ✓; limit profile ✓.
- Example: C′−θI = diag(c+ε,c,…,c), P′₁₁ = c/[mc+(m−1)ε], payment c(1+ε)/[mc+(m−1)ε]; change = ε(1−mθ)/[m(mc+(m−1)ε)] ✓. T′=1 needs m≥2 ✓. Bound m−(m−1)θ ≥ m−1+1/m ✓.

**PSD_CONTINUOUS_GAIN_WEIGHTS_OBSTRUCTION.txt**
- Pair profile: both singular, f=0, sum=εI, G=ε, F(U_i+U_j)=G ⇒ a_i+a_j≥1; continuity and pair-summing give Σa_i(0)≥n/2 ✓ (needs n≥2, m≥2, both assumed).
- "Stronger condition implies (1)": uses F(Σ_Q U)≤G (PSD monotonicity, U_i⪰0) and nonnegativity of a_i when the ratio is 0 ✓.
- Neighborhood sup claim follows from one pair sequence ✓. Reserve-profile variant ✓.

**Scope labelling.** All three documents correctly distinguish architecture obstructions from unrestricted lower bounds (file 1 lines 86–95; file 2 line 2; file 3 lines 2, 47). No quantifier overreach detected: file 1 claims only for this aggregate-price rule with two owners; file 2 only for the θ-family; file 3 only under continuity of normalized weights.

## Scope limitations
- External claims not verifiable here: scalar funding factor (m+1)/2 (file 1 line 8 — consistent with Tr(PC)=a+(m−1)a/2−a²Σ1/(2c_k), but the "scalar branch" assumption is unstated there); "scalar TCWM lower's leading coefficient 1/2" (file 2); APPROXIMATE_CORE_MAJORANT_BELOW_TWO.txt and the min-k embedding (file 3).
- Anti-alignment optimality (file 1 line 15) is asserted, not proved; it is standard (rearrangement over frames) and I accept it.
- The referenced verify_*.py scripts were not supplied; nothing was executed.

## Verdict
**No findings in reviewed scope.** All arithmetic, eigenvalue identities, price formulas, cap inactivity, singular-owner lifts, and the three algebraic lemmas check by hand; hypotheses (m≥2, n≥2, θ∈[0,1), distinct eigenvalues, continuity at zero) are stated where used.

**Provisional verdict: no invalidating findings in reviewed scope.** Both claims recompute correctly; the only items are dependency-status and presentation notes.

## Findings

**1. (Low) TWO_CAPPED lower construction: implicit smallness condition for the deviation formula.** Lines 75–77 use "changed core coefficient is e q" and Δ=ε[Kρ−(2e−1)]. This requires the post-deletion long ratio ρ−1 to stay ≥1 (hardware still short), i.e. L/2−log2 ≥ 1, ε ≲ 0.034, and ρ > (2e−1)/K ≈ 2.58 for Δ>0. Both hold for "small ε" but are not stated. Recomputed: Z=T+ε(ρ−1), Z'=T+eε(ρ−2), Δ=Z'−Z=ε[Kρ−(2e−1)] ✓; owner1 gain q0[(1−T)(1−e^{−Δ})−ε] with q0=c·e^{−Z} ✓; Δ²,TΔ=o(ε) ✓. Hardware owners' loss Kε equals the sharp outgoing bound exactly—consistent, not a violation. Verification: state the ε threshold explicitly.

**2. (Low) TWO_CAPPED upper: constants recomputed and correct.** (2): S≥2+Z−2ε, Z≥M≥X; X≥4ε ⇒ y≥X/2 ✓. (3): d/dy[1−(1+y)e^{−y}]=ye^{−y}, so ∫≥y²/(2e) on y≤1 ✓. (4) maximizer X²=4eKε, value (cK/2)εL+(cK/2)[log(4eK)−1]ε ✓. r≥2 region: 1+e^{−2}≈1.135<C≈1.184 ✓. All O(ε) terms are explicit scalars (3c(A−1), 2c(A−1), (1+K)cε), so uniformity holds. Leading coefficient cK/2 matches lower.

**3. (Dependency note) SUBSET (SD3) relies on MARGINAL_FLOOR_STABILITY (4), whose own header reads "review pending", while SD calls it "accepted".** Per task it is a supplied dependency; flag the status mismatch only. Logically (4) is proved for 0≤u≤1 but q≥c forces u≤1, and (q−c)_+=0 otherwise, so SD3 is fully covered.

**4. SUBSET algebra recomputed, all correct.**
- Power-short: d_J≥a_J−(h−T) via Σclip=h−ρT≤h−T ✓; chain to T[2−q−(1+c)h/T] ✓ (uses 1−c−q>0, a_J≤h, h/T≥ρ).
- B(1)=1/2−c=Kc ✓; B'=q−1−c≤−1/2−c≤−2Kc ⟺ c≥1/6 ⟺ e≤3 ✓; (SD5) ✓.
- δ_j/(cT)=1−(1−u)e^u; identity 1−(1−u)e^u−(2u−1)²=(1−u)(4u−e^u) ✓ (since 1−(2u−1)²=4u(1−u)); e^u/u decreasing on [1/2,1], 2√e≈3.30<4 ✓.
- Zero-output: (1−c)a_J−2h≤0 ✓; Cauchy–Schwarz with Σ(h_j−T_j)=H−M, Σδ_j=CM−Z ✓.
- (SD2): d_i<a_i≤1 ⇒ d_i=p_i+z_i ✓; c/(1−c)=1/(2e−1)≈0.225<1, genuinely stronger at M=1,δ=0 ✓.
- Rational directions: LHS coefficient −c(v+Zminus) with v,Zminus≥0 needs chi for outer relaxation; RHS upper K, upper c ✓.
- (SD6): from JOINT_ROLE (1),(2) with B=1,q=t, plus v≤1−Z+L (= global (13) chain) ✓; t=0 by continuity, B≥q>0 satisfied for t∈(0,1).

**5. (Scope) SUBSET §6: "pi bounded by 11/8" is undefined in this file; subset_role_probe.json not in packet.** Correctly labelled as diagnostic, not evidence.

## Scope limitations
No code executed; certificate scripts (certify_marginal_stability.py, verify_joint_role_scalar.py, probe JSON) not supplied. GLOBAL_DIFFUSE_SECOND_ORDER (14), SHARP_INCOMING/OUTGOING, and MARGINAL_FLOOR (4) treated as accepted dependencies, not re-proved. Audit covers only the two stated claims.

## Verdict
**No findings in reviewed scope** beyond minor presentation (item 1) and dependency-status labelling (item 3). The cK/2 coefficient and (SD1)/(SD2)/(SD6) are correctly derived from the supplied dependencies.

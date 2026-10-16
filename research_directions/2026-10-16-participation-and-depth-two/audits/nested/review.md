**Provisional verdict: no substantive defects found in reviewed scope.** All claimed derivations, production values, cap/uncap conditions, and numerical constants reproduce by hand; the script encloses the correct reduced formulas with correct interval orientation. Most important observation: the file's own scope statements are accurate — the three counterexamples defeat *proof routes* (coarse budget, joint charge) and the unmodified rule N, and nothing in the file promotes the failed inequalities into a bound on the actual envelope E.

## Findings

**1. Cross-influence lemma (lines 8–12) — verified, no defect.**
Case B≥A: y_i=a_i+q(d_i−a_i), ∂/∂b_k=−q(d_i−a_i)/A for uncapped k; since a_i≤A, sign(d_i−a_i)=sign(b_i−a_i) in both the capped (d_i=A≥a_i) and uncapped (d_i=b_i) subcases, and |d_i−a_i|≤A gives magnitude ≤q≤1/2. Case B<A: dq/dB=qt/B is correct (ρ=k+U/B). For a_i>B, b_i≤B forces k≥1, so q(1+t)≤qρ≤1/2 holds. Tie A=B: all holdings ≤T, ρ=1, payment (a_i+b_i)/2 on both sides, so continuity and the a_i=b_i invariance claim hold. Telescoping over coordinates is valid because each coordinate direction is monotone and 1/2-Lipschitz.

**2. Envelope reduction (lines 14–20) — verified.** Raising own (H_i,B_i) to full values is legitimate since z_i is own-nondecreasing; the remaining difference is only in others' B_k, so monotonicity+Lipschitz gives E_i≤N_i+I_i/2 with direction fixed at the full profile. C²+C/2≈1.99368 checks (C²≈1.40171). Minor: this constant is not certified by the script, but it is only a hypothetical premise that the file then refutes.

**3. Four-owner influence obstruction (lines 22–24) — verified exactly.** Tie local rule gives z_i=1/2; one withdrawal yields ρ=2, q=1/(2e), opposite-pool payments 1/(2e) each; drop 1−1/e per owner; directions all −1/2<0. 2(1−1/e)≈1.26424>C and >2(2−C²)≈1.19657.

**4. Four-owner counterexample to N (lines 28–35) — verified.** F=min(7+x,4)=4; q=½e^{−1−x}; T′=4+(1+x)q<5≤5+x (cap) and >1 (A,B uncapped); N_I=3+xq+r(1+q) with T′−3−xq=1+q; derivative algebra correct; r≥½e^{−1/2}>1/4≥1−x uses e<4. Hand values N_I(7/8)≈3.3993<N_I(3/4)≈3.4009. Script `nested` uses correct monotone orientation for r.

**5. Six-owner joint charge (lines 37–42) — verified.** F=1, Z=C, T′=C, hardware uncapped (1/2<C), ΣN=C+½e^{1−2/C}(2−C)≈1.388746; influence 3e^{−1/2}−e^{−1}−2e^{−3}≈1.352138; sum ≈2.06482>2. Positive/negative direction assignments and omitted terms (counter-direction changes) are correct.

**6. Script cosmetics (verify_residual.py).** Line 64 comment "not uncapped" tests T>2 where T>1 suffices (harmless, stronger). Line 75 `additional_exact_checks:7` is hardcoded, not counted. Neither affects correctness.

## Scope limitations
- Cannot execute `verify_residual.py`; interval logic checked by reading only.
- Own-monotonicity of z_i and the outer primitive is taken from MIXED_PRIMITIVE.txt's lemma (consistent with its stated proof) and not re-derived here.
- No assessment of whether E actually stays below 2F; file correctly labels this OPEN.

## Verdict
**No findings** of mathematical error in reviewed scope; two minor script-labeling nits.

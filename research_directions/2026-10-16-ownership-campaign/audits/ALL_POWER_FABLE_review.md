**Provisional verdict: no mathematical failure found in reviewed scope; evidence contingent on the (unsupplied) exact-check output.** Most important point: Cases II and III rest on margins of ~1.4e-5 and ~8e-7 (my hand values: S(1/2,23/50) ≈ −3.14e-4 vs bound −3e-4; S(51/100,1/2) ≈ −2.08e-5 vs bound −2e-5). These are only certified by `verify_power_bottleneck_scalar.py`, whose `.json` output is not in the packet.

## Findings

**1. (Low — evidence gap) Scalar endpoints are razor-thin and rely solely on an unexecuted script.**
`ALL_POWER_BOTTLENECK_C_SQUARED.txt:221-223, 234-238`; `verify_power_bottleneck_scalar.py:97,103`. I re-derived the formulas in the script (`scalar`, `scalar_u`, `beta_derivative_upper`, `grid_u`, `U`, `Uprime`) against (8),(12),(13),(9),U and they match; `eminus` uses a correct Lagrange-remainder sandwich (S₄₀ ≥ e^{−x} ≥ S₄₁ for x ≥ 0); 26 checks listed = 26 claimed. But I cannot confirm they pass. Verification: run `python3 -I -O verify_power_bottleneck_scalar.py` and attach the JSON; add the two tight margins (`S(.5,.46)`, `S(.51,.5)`) to the manuscript so reviewers see how small they are.

**2. (Exposition only) Case III evaluates S outside the model domain.**
`:228-230`. Reducing beta to 51/100 with u ∈ [2/5,1] fixed can give u > beta; S is then used algebraically. This is legitimate (the (13) bound and (12) concavity are algebraic in u ∈ (0,1]), but the text should state the extension explicitly.

**3. (Exposition only) Implicit step in (2), middle cell.**
`:81-82`. The bound W_t ≥ −q(r−h) uses b−a_i ≤ b ≤ t and r ≥ h (capped accounts contribute t each). Both hold but neither is stated.

## Verified steps (brief)
- Normalization, β ≤ C, no-cap assertion: z_j^i ≤ M^i (per-recipient Φ_i ≤ T), so b_j^i ≤ P+M ≤ 1 ✓; W formulas agree at t=1 ✓.
- Derivative bounds: uncapped W_t = q(r−h)(a_i−b)/t ≤ qr ≤ 1/2 (r ≥ h); capped ≤ q(1+r−h) ≤ qr; W_t ≤ W_b on both pools ✓; total-UP gain ≤ (G−D)_+/2 and G−D identity ✓; invocation of 2Δ₊ lemma (low-ratio branches contribute ≤0 by total/own nonincrease) ✓.
- b_*(t) monotonicity: lower cell ≥0, upper cell ≥1−qr ≥1/2, middle ≥[1−q(3r−2)]/3 with max (3/2)e^{−2/3}<1 ✓; b ≤ b_*+ε_i and ε_i identity ✓; (3) algebra ✓.
- k, Lipschitz 4c at t=1/2 ✓; retention-path gain, lower-cell ≤0, g_β convex/increasing/superadditive ✓; raw(β)=1+k(β)(β−1) ✓; OD invocation for β ≤ 1/2 (ratio 1/β ≥ 2) ✓.
- (6): J(2)=J′(2)=0, J″=−q[1+a(ρ−3)]<0; hardware-short max 1/2−c−a<0, c+a=(1−c)²/C ✓.
- (7),(8),(9),(10)→(11): all algebra checked, including 1−a=4c/C and p-coefficient −Cc+2A/7<0 ✓. JOINT_ROLE (2) invoked with B=A+d ≥ q=d>0 ✓.
- (12),(13) and their monotonicity claims; Case IV: 1−k(7/10)≈0.326<C²/4≈0.350, k(3/5)−k(6/5)≈0.334<0.350, U concave, U(3/4)≈−0.0104, U′(3/4)≈0.019 ✓; four cases exhaust [1/2,C]×[0,β] ✓.

## Scope limitations
- Cannot execute the script; JSON absent. Prior lemmas (retention, total-increase, OD, joint-role) accepted as previously reviewed; only their hypotheses were checked.
- No independent search for a positive-grid extremizer; no check of P+M>H.

## Verdict
No findings of mathematical failure in reviewed scope; two exposition nits; correctness of Cases II/III is contingent on the exact certificate passing, which the packet does not evidence.

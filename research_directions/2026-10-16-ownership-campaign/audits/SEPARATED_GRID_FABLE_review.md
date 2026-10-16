**Provisional verdict: no findings of substantive error in reviewed scope** (conditional on the stated dependencies). The most delicate point is the u≥1 branch of the scalar estimate, which is correct but has essentially zero algebraic slack beyond the strict inequality √e < 27/16.

## Findings

**1. (Low / note) SEPARATED_GRID_ALL_PROFILES.txt L84–88.** The bound (1/2)[√e/3 − 1/2] < 1/32 follows from √e < 27/16 with *equality* at that rational: (27/16)/3 − 1/2 = 1/16, halved = 1/32. The inequality is strict only because √e ≈ 1.6487 < 1.6875; the real margin (≈0.0064) is not reflected in the checker, which has no √e check. Not an error; suggest adding an exact certificate (e.g. e < 729/256 via the same Taylor bound) for completeness.

**2. (Low / verified) Re-use of the power-theorem scalar reduction under (SG), L40–49.** I checked that ALL_POWER §1–2 formulas (W_i(t,b), W_t ≤ 1/2, cap-cell monotonicity (2), k(t) for t ≥ hmax) only require: (a) every opposing account ≤ H with grid caps constant, and (b) own account ≤ 1 along the path. Under (SG), local accounts are each ≤ M^i ≤ M ≤ H (individual payments ≤ branch output), grid accounts are min(p_k,1) and fixed, and b_*(t) ≤ b0 ≤ 1. The "capped total = pi + Z^i exactly" claim holds in both P ≥ 1 (hardware-short always) and P < 1 (pi = P; for t < 1 the opposing side is short and uncapped). Total-UP comparisons stay at t ≥ β ≥ 1, so the pool switch arises only in DOWN comparisons, where (2) is invoked. Consistent.

**3. (Verified) Scalar estimate §2.** Recomputed: chord constants A = B + 1/2, B = 1−2c; vertex u* = 1/4 + 1/(4B) + w/2; T = A + B/2 = 2−3c; V(w) = (T−Bw)²/(12B) − e^{−w}/4; V'' = B/6 − e^{−w}/4 < 7/66 − 15/128 ≈ −0.0111; tangent bound 27/1000 + 50·(9/1000)² = 621/20000 < 1/32. Cases u ≤ 1/2 (k'' ≤ 0 for u ≤ 1/2, h'(1/2) = 2−10c > 0, f ≤ 1/12 − c/3 < 1/44) and u ≥ 1 check. Checker interval directions (V0_upper uses Tu, Bl; Vp bounds use Tu/Tl) are conservative; alternating Taylor bracketing is valid for x ≤ 1 and, for x = 2, after j > 2. c² > 1/32 ⇔ e² < 8: true.

**4. (Verified) Role bound L65–70.** (z_i − a_i)_+ ≤ Σ_j v_ij; Σ v ≤ H_j/2 per branch via ρe^{1−ρ} ≤ 1 and 1−q(ρ) ≤ ρ/2. Convex superadditivity of g_β (max of affine maps, g(0)=0) justifies concentration.

**5. (Verified) SEPARATED_GRID_FUNDING.txt (P ≥ H).** Gain formula q0[(e^u−1)g − e^u D], f_g maximum e^{3g−1}/3 − g ≤ K, at most one owner with g > 1/3, interpolation derivative ≤ q0(1−D/u), Γ = C + c + K/2 = 3/4 + 1/e + √e/6, and C²−Γ > 0 via √e < 5/3, 1/(4e²) > 1/36 (exact zero at the rationals, strict in reality). Correct.

**6. (Verified) GRID_CAP_RANGE_BOUND.txt.** Decomposition 1 + (Q−q_−)R + q_−(S−1), R ≤ pi + L, S ≤ pi + Z, and JOINT_ROLE_TRADEOFF (1) with (B,q) = (Q,q_−) give (1). Monotonicity in m and pi, 27/16 at pi = 1, and the pi = 15/7 margin (≈2.3e−4, exact in JSON) check. Note the margin is thin; the claim depends on the certificate, not on slack.

**7. (Verified) OVERFLOW_DECREASE obstruction.** z_A = 1−q, overflow q, deletion gives coefficient eq and account 1−(e−2)q < 1; multi-branch decrease (e−1)q with m ≥ 2 > e−1. Ratio n(e−1)/2 diverges. Sound as a non-existence statement for a linear-in-P charge.

## Scope limitations
Did not execute scripts; did not audit the cited universal retention/increase lemmas, primitive monotonicity, or ALL_POWER §3–5 beyond what this note invokes (§1–2 reductions). No git diff available.

## Verdict
No findings in reviewed scope; two low-severity robustness notes (items 1, 6).

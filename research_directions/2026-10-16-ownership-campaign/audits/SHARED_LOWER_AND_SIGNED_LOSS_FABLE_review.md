**Provisional verdict: no findings in reviewed scope (both claims check arithmetically and logically); several load-bearing dependencies are not in the packet.** Most important observation: the shared-branch construction's report (iii) produces a *capped* other-loss of J·ε ≈ 1.504ε, which exceeds 3/2 — this is not a contradiction, because the signed local loss there is only (1−γ)J·ε ≈ 1.128ε and the 3/2 theorem explicitly excludes cap hiding. The two notes are mutually consistent on exactly this point.

## Findings

**1. Low — SHARED_RESPONSE §1–§4, arithmetic replayed by hand (no execution).**
Shared branch: cap sum (1+γ)t_s ⇒ q_s = e^{−γ}/2; z_A = ε, z_G = γε; after A's deletion each hardware fragment t_s/4 equals the new short total ⇒ ratio 4 ⇒ q_s′ = e^{−3}/2. Hardware loss (1−q_s−q_s′)t_s = Jε with J = 2e^{1/4}−e^{−11/4}−1 ≈ 1.504 ✓. G's raw outer account 1+ε+γJε stays capped ✓. S′ = 2−(1+J)ε, gain (8) ✓. Residual branch reproduces B ≈ 1.136 from TWO_RESPONSE (4) ✓. G's budget γε+(3/4)ε = ε ✓. Core Δ = ε[Kρ−(2e−1)] and g₁ expansion reproduce −c[2e+K log 2] ✓ (K+1−2e = −e). F−2B identity (10) and the elementary bounds (e^{11/4}>10, e^{1/4}−e^{1/5}>1/20) ✓; numerically F−2B ≈ 0.084. No error found.

**2. Low — check_shared_response_lower.py.**
Branch indexing (core 0..k−1, shared k, residual k+1, extra k+2), multiplicity handling, cap-count check, and `expected`/`targetS` match the text. It is a 5-point finite corroboration, correctly labelled as such; it does not establish the o(ε) terms.

**3. Low — SIGNED_OTHER_LOCAL_LOSS §2–§6.**
§2: (2) correct; d+v−1 ≤ dv ⇐ (1−d)(1−v) ≥ 0; bound K v(1−v) ≤ K/4 ✓. §3: (3) correct in both cases; the step "t ≤ W" when A>t holds because W ≥ min(A,t) (true but only asserted). Ratio-reduction to s=0 valid since numerator decreasing, denominator increasing, qd>0 ✓. §4: f′ numerator A_v e^d(d−1)+(1−v) is increasing ⇒ endpoint maximum ✓; (6),(7) ✓. §5: Padé inequality and 2/(v+1) ≤ 3/2 ✓ (x=2 at v=1/3 exactly, boundary fine). §6: small-v bound equals 3/2 only through strict e^{1/4}<9/7 (margin ≈0.003) — thin but exact and certified.

**4. Low — certify_signed_other_three_halves.py.**
U₁₂ geometric tail valid for x≤1 (hi≤1 ✓); L₁₇ odd-degree lower bound valid for x = (1−lo)/lo ≤ 3 ✓; the monotonicity direction assignment (exp(v),+v ← hi; −v, exp(1−1/v) ← lo) is correct; nonneg-bracket guard handles the sign of the product. Hand estimate of (7) peaks ≈1.47 near v≈0.34, consistent with reported 1.4798 interval max.

## Scope limitations (missing dependencies)
- "Accepted core" (Z_core, ρ≥3, Δ, all-core-accounts<1) and the outer-stage rule definition are not in the packet; semantics inferred only from `primitive()` in the script.
- SHORT_STAGE_NONLINEAR_THREE_HALVES.txt (H₊² ≤ (9/4)UD) underpins §1 of the 3/2 theorem, including the mixed-owner claim; unverifiable here.
- The "accepted (e−1)z_i" bound is cited but not supplied.
- Tie orientation at t=1 / equal totals relies on the primitive's `sa<=sb` convention; proof text treats it by continuity only.

## Verdict
No findings in reviewed scope. Both theorems are internally consistent, correctly scoped to the original mechanism, and the exact certificates are sound as written; validity of the asymptotic lower and of §1 of the structural theorem rests on the four unsupplied dependencies above.

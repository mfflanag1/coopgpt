**Provisional verdict: no mathematical findings in reviewed scope; evidence gap on the executed certificate.** Most important concrete point: the packet contains the script but not `asymmetric_scalar_certificate.json` or any run output, so the (A_W) step — the only regime whose margin is thin (worst upper ≈1.7089 vs 1.71, ≈0.001) — is verified here only by independent derivation of the script's logic, not by its execution.

## Findings

**1. (Medium – evidence gap) Certificate output absent.** `ASYMMETRIC_RANGE_171_100_THEOREM.txt:138–144` cites 3072 passed intervals; `verify_asymmetric_scalar.py` writes a JSON that is not in the snapshot. I checked the script's soundness: `exp_lower` (odd degree 19) and `exp_upper` (even degree 10) are correct one-sided Taylor bounds for exp(−x), x≥0 (Lagrange remainder sign); `floor_grid` rounds q1 and q0 down, giving B ≥ Q(p) and q0_lower ≤ q0(p); the objective 1+Q[p+½exp(−q0/Q)] is increasing in Q and p and decreasing in q0 (∂/∂Q = p+½e^{−q0/Q}(1+q0/Q) > 0), so using Q(lo), p=hi, q0(hi) is a valid enclosure. Spot evaluation at p≈0.65 gives ≈1.7087, consistent with the displayed worst 1.708935 and an interval overestimate of ≈4×10⁻⁴. Verification: supply the JSON / stdout, or rerun with `python -I`.

**2. (Low) One (A_W) step not covered by the script.** Line 137 claims q0>27/100 on p∈[0,¼]; the script only checks 5/4+50/127<171/100. The claim is elementary (exp(−0.434)≥1−0.434=0.566>27/49≈0.551) but should be added to the rational certificate for completeness.

**3. (Informational) Monotonicity bound is tight, not slack.** Line 35–41: for the opposing-short orientation v(1+α)=51/100·100/51=1 exactly, so the own-short derivative lower bound 1−q(1+βρ) equals 0 at ρ=1 (tie, own long account zero). Weak monotonicity still holds; any future increase of v or α breaks it. The decreasing claim for exp(β(1−ρ))(1+βρ) is correct (derivative −β²ρ·exp(·)≤0).

## Verified steps (no issues found)
- Primitive: coverage, tie continuity (both formulas → v a_i+w b_i since caps are inactive at a tie), own-long derivative q[1−β(d_i−s_i)/T]≥q(1−β), own-short derivative 1−q+qe_i+βq(ρ−m)(d_i−s_i)/T with ρ≥m and |d_i−s_i|≤T.
- Range mechanism: D_i depends only on p, B_i, K; shift map b→b+ηe_i for p_i increases; one-owner case = F.
- Low K: q(T) nondecreasing in T (ρ nonincreasing), optimum at ρ=Zh/K+1/α, ∂/∂Z>0 since Z≥M, ratio (1+t)[1+(v/α)e^{α/(1+t)−1}] increasing in t; using C=148/125 is conservative. Value ≈1.7045.
- High P: coefficient-w transfer of the coupling argument; 1+w·57/40=1.69825.
- Intermediate: q≥q1 via ρ≤1/T≤1/p; q≥q0 via ρ≤k; 1−q≥w; (A_role) algebra; support-function hypotheses Q≥w≥q0>0 satisfied; (A_power) uses w·2≤1 for g nonincreasing; 2−w+c≈1.694.
- Old evaluator: short-pool argument needs only q(T) nondecreasing and 1−q>0; long-pool needs only a positive constant coefficient; complexity unchanged.
- Regimes K≤H, P≥H, P<H<K (F=H / F<H) are exhaustive.

## Scope limitations
Did not re-prove the local primitive properties (Z≤CM, role decomposition, support functions) or the frozen high-P coupling; only checked their invocation hypotheses. Did not execute any code; no JSON output reviewed.

## Verdict
Findings: one evidence gap (certificate output missing), one minor uncertified prose step; no invalid inequality or counterexample located in the reviewed claim.

**Provisional verdict: no invalidating findings in reviewed scope.** The Hessian (5), the slope bound (7)–(9), the curvature bound (10), and the exactness argument (3) all recompute correctly. The most important residual point is not a mathematical error but an unverifiable dependency: formula (2) presupposes that the parent's outer-payment formula (8) applies verbatim when x_*(q) < a_i, and that (ER) holds for negative-gap owners — neither primitive is in the packet.

## Findings

**1. (Info) Hessian (5) recomputed — correct.**
Evidence: NEGATIVE_GAP…, lines 54–64. With L = w·exp(−S/H), grad L = e^{−S/H}[X − (w/H)A], and Hess S = Hess β_i = −W (C_A affine), one gets e^{−S/H}[(1+w/H)W − (XAᵀ+AXᵀ)/H + (w/H²)AAᵀ]. X_j = −ψ_j′ = h_ij+T_j−u_j and W = diag(T_j/q_j) match JOINT_RESPONSE lines 70–72, 85.

**2. (Info) Slope bound (7)–(8) — correct but loose.**
V_j sums c_kj − h_kj over a subset of opponents; Σc_kj ≤ R_jT_j, Σh_kj ≤ T_j, so V_j ∈ [−T_j, R_jT_j] and |V_j| ≤ R_jT_j as R_j ≥ 1. Then Σ q_jV_j²/T_j ≤ Σ T_j R_j² e^{1−R_j}/2 ≤ (2/e)Σ_variable T_j ≤ (2/e)H; R²e^{1−R}/2 is maximised at R=2 with value 2/e. The weighted Cauchy–Schwarz (9) with weights T_j/q_j is valid. Note the bound uses q_j ≤ q0_j, i.e. full-box Q, which is fine since regions ⊂ Q.

**3. (Info) Curvature (10) — correct.** 2xy ≤ (x+y)²/2 = (Vᵀv)²/2 holds for all signs of xy; (2/H)xy ≤ D_v/e; dropping (w/H²)y² ≥ 0 gives ≥ (1−1/e+w/H)D_v > 0 for nonempty J. Strict convexity on each convex region follows.

**4. (Info) Exact recovery and no relaxation gap — correct.** On a closed cap region A, min(β_k,H) equals H for k∈A and β_k for k∉A, so C_A = C exactly there; the closed regions cover Q; every q ∈ Q is a legal report via t_j = u_j ∈ [0, u_max,j]. Because no auxiliary x variable is used, the parent's monotonicity argument (lines 134–141) is not needed. Compactness gives attainment; strict convexity gives uniqueness of q (not of the physical report above caps — correctly stated).

**5. (Low — unverifiable from packet) Outer formula for negative gap.**
Lines 29–43 rely on parent (8) with x_*−a_i < 0 and on total capped opposing ≥ H. Parent (8) is stated before any sign assumption, so the use is internally consistent, but the underlying "hardware-short primitive" is not in the snapshot. Verification: confirm from the primitive's definition that payment = a_i + (x−a_i)e^{1−total/H}/2 is the full-domain formula, not a positive-gap branch.

**6. (Low — assumption, explicitly kept) (ER) for negative-gap owners.** The parent cites a restoration threshold S ≥ 3/2 + e·z_i; whether that theorem covers d_i < a_i is not shown here. The addendum correctly keeps (ER) as a hypothesis (line 8, 120–121).

**7. (Low) Four-program count.** The crossing bound in CONVEX_LOCAL_FOUR_PROGRAM_BOUND lines 51–61 uses only opponents' affine accounts, p_k<H, M≤H — independent of i's gap sign, so c_i ≤ 2 transfers. The fixed-branch constant C = 1+1/(2e) (line 43) is asserted without proof in the packet.

## Scope limitations
No code executed; outer/local primitive definitions and the restoration theorem are not in the snapshot; the strict inequality count c_i < 111/40 assumes those bounds.

## Verdict
No findings invalidating the claim. Remaining explicit assumptions: (A), (ER), (LB), the outer formula's validity for x_*<a_i, and the fixed-branch constant C.

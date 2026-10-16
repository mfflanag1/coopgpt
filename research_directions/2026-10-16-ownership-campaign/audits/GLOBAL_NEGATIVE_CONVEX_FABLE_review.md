**Provisional verdict: no findings in reviewed scope.** The most important check — that the regional strict-convexity bound (3) and the derivative-jump sign (4) combine into global strict convexity across cap boundaries — holds as written; I re-derived each step below and found no error.

## Findings

No correctness findings. Verification record (so the verdict is auditable):

**Hessian identity, NEGATIVE_GAP_CONVEX_LOCAL_EXTENSION.txt:62–64.** With E=exp(−S/H), Hess S = −W (C_A affine, Hess β_i = −W from ψ_j''=−T/q_j, JOINT:72), one gets Hess L_A = E[(1+w/H)W − (XAᵀ+AXᵀ)/H + (w/H²)AAᵀ]. Matches (5). Quadratic-form bound: 2xy ≤ (x+y)²/2 follows from (x−y)²≥0; x+y = Vᵀv since A=V−X; slope bound −T_j ≤ V_j ≤ R_jT_j follows from Σ_{k≠i}h_kj ≤ T_j and Σc_kj = R_jT_j; max of R²e^{1−R}/2 is 2/e at R=2; weighted Cauchy–Schwarz gives (Vᵀv)² ≤ (2H/e)D_v. Final bound (1−1/e+w/H)D_v > 0 is correct for nonzero v because W is positive definite (T_j>0, q_j>0).

**Line-restriction argument, GLOBAL…:33–59.** Each β_k(q(t)) is affine in t, so finitely many breakpoints; on open intervals L(q(t)) coincides with some L_A(q(t)) (identically-tied opponents contribute the constant H under either assignment), so (3) is the regional bound applied pointwise — it does not require region membership, only q∈Q. At breakpoints L' = E[w' − (w/H)S'] with w, w', S, E continuous and S'₊−S'₋ = C'₊−C'₋ ≤ 0 by concavity of the piecewise-affine C; multiplying by −w E/H = −L/H < 0 gives a nonnegative jump. A function with one-sided derivatives strictly increasing on pieces and nondecreasing across finitely many breakpoints is strictly convex; Q convex ⇒ global strict convexity. Correct.

**Negative-gap premise, NEGATIVE_GAP…:30–34.** d_i < a_i ≤ H forces b_i = d_i, and β_i(q) ≤ b_i by ψ_j' ≤ 0 (JOINT:85), so w>0 uniformly and min(β_i,H)=β_i; the parent payment formula (8) then reduces to a_i − (e/2)L. Consistent.

**Subgradient direction, GLOBAL…:67–80.** Superdifferential of C at q is exactly the set of V in (5) (finite-sum rule for everywhere-finite concave functions; each min(β_k,H) has θ_k∈[0,1] at a tie). Directional derivative of concave C is min over supergradients; substituting, L'(q;v) = max_g gᵀv with g from (5). Since L is convex on Q and difference quotients dominate directional derivatives, each such g is a subgradient on Q, including box-boundary points (where the full subdifferential may additionally contain normal-cone terms; the note claims only "a subgradient", which is accurate).

**Attainment/uniqueness/recovery.** Q compact, L continuous ⇒ attained; strict convexity ⇒ unique q*; t_j = −T_j log(q_j/q0_j) ∈ [0,u_max,j] by construction (JOINT:57–61). Non-uniqueness of reports above T_j is correctly flagged.

**ER/LB preservation.** The note adds no new hypothesis and explicitly retains ER, LB, and the physical-bottleneck condition; the S ≥ H requirement is inherited from JOINT §1 (unchanged M under LB).

## Scope limitations

- The local primitive formulas ψ_j (JOINT:65), z_kj (JOINT:67), and payment identity (8) (JOINT:91–92) are taken as given; their derivation from the exponential primitive is not in the packet.
- Justification of (ER) (owner-specific restoration theorem) and the fixed-lattice construction are outside the packet.
- No numerical checks were performed, per instructions.

## Verdict

**No findings in reviewed scope.** The global strict-convexity claim, the sign of the cap-boundary derivative jump, the handling of simultaneous and persistent ties, the subgradient direction, attainment, unique price recovery, and preservation of ER/LB all check out against the supplied regional proof and parent coordinates.

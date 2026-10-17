**Provisional verdict: no mathematical defects found in the reviewed scope; several steps rest on named dependencies that cannot be verified here.** Most important concrete point: the Θ-claim in COMMON_CAP_PARTICIPATION_FLOOR_FRONTIER line 14–16 is a worst-case statement over models with M-dependent power-owner count, not a per-model statement; as written it could be read as the latter.

## Findings

**1. (Low, clarity/correctness of statement) COMMON_CAP_PARTICIPATION_FLOOR_FRONTIER.txt:14–16, 75–79.** "Optimal funding order over all finite actual-owner models is Θ_k(M^{α/2}+θM^α)" is a sup over models: the M^{α/2} term needs R≈√Q~M^{α/2} pure power owners (line 78), while AI_OWNERSHIP_BOUNDARY §2 shows a single power owner gives optimum 1 at θ=0. Suggest: "worst case over finite actual-owner models". Verification: none needed beyond rewording.

**2. (Low, hypothesis gap) AI_OWNERSHIP_BOUNDARY.txt:43–45, 50–51.** Coverage and OUT proofs apply the hypothesis "every admissible coalition disjoint from H has zero production" to *derived* coalitions (S minus null members; the support of d). This needs admissibility closed under taking subsets, which is not stated. Harmless in the common-power model where all coalitions are admissible, but the "General lemma" should state it.

**3. (Low, unverified dependency) AI_OWNERSHIP_BOUNDARY.txt:85–96, 121, 132–139.** The transfer lemma is correct as stated (I checked (1) via superadditivity of min, exact coalition-value agreement, and Δ_i ≥ T_i(d_i) ⇒ βG(ΣΔ_i) ≥ βG(ΣT_i(d_i))). However h_i = Σ_j min(a_j,b_j) can exceed any unit cap; the quoted two-pool constants (3/2, 1+c, 1+max(c,θ), 1+μ(β)) must hold without a per-owner cap (homogeneous rules). Verification: confirm the two-pool theorems are scale-free, or add the cap-free hypothesis.

**4. (Low, cross-file scope) AI_OWNERSHIP_BOUNDARY.txt:175–178** states divergence "requires BOTH" unbounded power owners and split branches; CONCENTRATED_POWER_HARDWARE_FLOOR_LOWER shows one power owner suffices once floors are added. "In this family" should explicitly read "floor-free".

**Verified (no defect):**
- Residual-flow deletion loss (FRONTIER 41–49): z_j^i=z_j[1−max_v s_iv] is feasible at C−b_i since row-v use ≤ (1−s_iv)C_v; chain (4) is exact; u_P=h, u_jl=λg_j/x_jl ≤ fg_j/x_jl because r^{1/k} ≥ r for r≤1.
- Funding (3): P≤G gives hP+fkG = F[1+k(G/P)^α] with G/P≤M because g_j≤P; P>G gives (1+k)F.
- Floor seed/recurrence (FRONTIER 60–66; FLOOR_LOWER 50–64): q_m ≥ k_m/(k_m+1)·q_{m−1} with coalition size k_m+1; both files agree (k=2: Q_{M,2}=A_M=4^M/(2C(2M,M)), A_4=64/35, 131/35 example correct). Q_{M,k}=M!Γ(1+1/k)/Γ(M+1/k)~Γ(1+1/k)M^α confirmed; Stirling constants √π, √(π/2), √(2π/e) and the D_{M,s} maximizer at M=s,s+1 confirmed.
- Convex mixture (8): OUT, coverage, nonnegativity are linear inequalities with identical right sides; floors follow from y^0≥0.
- Owner-cover activation cases (BOUNDARY 47–54) and fractional version are complete; "active at low ⇒ active at high" closes the case split.

## Scope limitations
Cannot verify: the full-OUT proof for the C=1 rule ("applies verbatim", FRONTIER 28), K0 = k+max{1,√k M^{α/2}}, the no-floor lower (7), two-pool constants c and μ(β), universal dimension bounds (d+1)/2 and 1+c(d−1), the layer-identity corollary (FRONTIER 101–103), and check_ai_ownership_boundary.py. No files outside the packet inspected; no code run.

## Verdict
No findings of mathematical error in reviewed scope; items 1–4 are statement/scope gaps; insufficient evidence on dependency constants.

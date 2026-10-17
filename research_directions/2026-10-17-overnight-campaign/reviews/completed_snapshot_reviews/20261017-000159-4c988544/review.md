**Provisional verdict: no findings in reviewed scope.** The exact decomposition (1) checks out algebraically for every coalition profile, and the componentwise transfer of coverage, monotonicity, floor, and budget from the two supplied baseline theorems is valid as written. The most important thing I verified is that (1) is a pure capacity identity (public sets J_t, K_t do not depend on reports), so it holds at every coalition S, at N\{A}, and at N\{A_a}, which is what the coverage and telescoping steps actually need.

## Findings

**F1 (Info) — Decomposition (1), lines 38–64.** Verified: with q_i = min(L_i, h_i − g_i), marginal grid value is b_i on [0, r_i] and b_i − a_i on the next ell_i units (both cases h_i ≥ L_i and h_i < L_i). Since b_i ≥ u_i, greedy with first-segment-first tie order respects the per-pod prefix, so the fractional knapsack is exact and its value is ∫₀^∞ min(P, R_t) dt with R_t = Σ_{J_t\K_t} r_i + Σ_{K_t} h_i (uses K_t ⊆ J_t). The unit component T_t has ell'_i = ell_i on J_t\K_t, r'_i = h_i on K_t, so T_t = Σ_{J_t\K_t} ell_i + min(P, R_t). The set {t : i ∈ J_t\K_t} = (u_i, b_i] has length min(a_i, b_i), giving Σ a_i ell_i = Σ (a_i − b_i)_+ ell_i + Σ min(a_i,b_i) ell_i. (1) follows. Edge cases a_i = 0, b_i = 0, all-zero: consistent.

**F2 (Info) — Hypothesis match with inputs.** UNIT_FLOOR_THEOREM and PURE_ROLE_BUNDLES_v2 accept arbitrary nonnegative reports with fixed identities; component profiles (h'_i = h_i·1[J_t], L'_i = L_i·1[J_t\K_t], P' = P) are coordinatewise images of the actual reports, so every allowed underreport maps to an allowed underreport per component, and zero rows are within hypotheses. The unit rule's M equals T_t(N) − T_t(N\{A}) because T_t(N\{A}) = min(P, Σ_{J_t} h_i) = G. Floor telescopes: A gets θΣf_i + θ∫M^t = θM_A exactly (single-A), and ≥ θM_a per owner in the PURE_ROLE version (that theorem only guarantees "≥"; the route file states this correctly). Budget line 84 is correct.

**F3 (Low) — Dependency status, not a defect of this file.** Both inputs are self-labelled "candidate proof, awaiting independent audit." Per the task I treated them as fixed; this reduction inherits any defect in them, in particular the Lipschitz/denominator arguments of UNIT_FLOOR and the Q<P<H case of PURE_ROLE.

**F4 (Low) — Section 2 floor-free corollary.** Append argument verified (local-only ell_j at j ∉ I uses disjoint hardware and pod-indexed L_j; feasible at the full profile). C's monotonicity relies only on F nondecreasing in P and B independent of P. Note this corollary coincides with the θ = 0 case of Section 4, so there is no inconsistency between the two.

**F5 (Low) — Sharpness wording, lines 14–16, 96–98.** The lower family (a=b=1) proves the universal constant cannot be lowered over the whole domain; it does not and need not claim sharpness for each fixed public (a,b) profile. The file's wording is consistent with this; flagging to prevent over-reading.

## Scope limitations
- Did not re-audit the two baseline theorems; treated as inputs.
- Section 6 normalization checked only for strictly positive coefficients (as stated); I confirmed route-dependent hardware coefficients also normalize via q' = γ^l q, g' = γ^g g followed by per-pod rescaling, but the file does not claim this and it was not required.
- No numerical experiments run; no test of the O(m²) arithmetic claim beyond counting ≤ 2m breakpoints × linear unit rule.
- No private-cost truthfulness, pooling, or novelty assessed.

## Verdict
No findings in reviewed scope. The route-value extension is a correct reduction conditional on the supplied unit-value and pure-role-bundle theorems; hypotheses match.

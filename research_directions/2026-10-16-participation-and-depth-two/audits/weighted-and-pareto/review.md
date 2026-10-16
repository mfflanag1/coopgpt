**Provisional verdict: no substantive errors found in reviewed scope.** Both corollaries check out arithmetically and logically against the base packet. Most important finding: PARETO_NOTE_v2 line 5 states the hypothesis as "any SINGLE all-profile mechanism satisfying the public marginal floor," but the proof uses three further properties (coverage, nonnegativity, own-grid monotonicity) that are not named in the statement.

## Findings

**1. Low — PARETO_NOTE_v2.txt lines 5–11 vs. 17–21: hypotheses used but not stated.**
Line 18 uses coalition coverage ({C,H1},{C,H2}); line 18 "total_O ≥ a+c+x+y" uses nonnegativity of any extra payments; line 20 "c_V ≥ c_O" uses own-grid monotonicity. The theorem statement names only the floor. The m=1 paragraph (line 39) lists the intended ambient properties, so this is an omission of wording rather than a logical gap, but the statement should say "nonnegative, coalition-covering, own-monotone mechanism." Verification: compare line 5 with line 39.

**2. Verified (no finding) — PARETO inequality and attainment.**
At O: ell=(1,1), r=(0,0), G=1, T=2, M=1, so a ≥ θ; 2c+x+y ≥ 2 ⇒ c_O ≥ 2+θ−2C. At V: P=2, G=2, M=0, {A,H1,H2} worth 2 ⇒ total_V ≥ 4+θ−2C. B_θ(V)=2: lower bound T=2; upper bound by (A,C,H1,H2)=(0,0,1,1), which covers every coalition ({C,H_i}: 1 ≥ 1; {A,C,H_i}: 1 ≥ 1; {C,H1,H2}: 2 ≥ 2). Hence C+K ≥ 2+θ/2. Base rule at O: x_i=1/2, X=1, y_C=1/2, total 2(1+θ/4). At V: x_i=1, X=2, y_C=1/2, θ-mixture (0,θ/2,1,1), total 2(1+θ/4) over B_θ=2. Line 27 figures match. 13/10 and 81/68 arithmetic correct.

**3. Verified (no finding) — m=1 counterrule.**
T=min(h, L+P) and G=min(P,h) nondecreasing in h, so (1−θ)T+θG is own-hardware monotone; T−θM = G+(1−θ)M ≥ G covers {C,H}; T ≥ ell covers {A,H}; total T so B_θ=T, C=K=1.

**4. Verified (no finding) — WEIGHTED_VALUES decomposition.**
Replacement step: if g_i ≤ h_i−ell_i new service = ell_i+g_i ≥ q_i+g_i; else = h_i ≥ q_i+g_i; grid use weakly falls, hardware ≤ h_i. Greedy residual satisfies all prefix sums simultaneously; any feasible g has prefix sum ≤ min(P, Σ_{i≤k} r_i); telescoping with d_k ≥ 0 gives both bound and attainment. Equal local/grid value (line 7) is genuinely used in the replacement step.

**5. Verified (no finding) — payments.**
Component k equals the base rule on the profile with h_i=0 for i>k; base line 30 ("zero when all her own resources are zero") makes outside-prefix owners null with zero payment. T_k(N\{A}) = min(P, Σ_{i≤k} h_i) = G_k, so M_k = T_k(N)−T_k(N\{A}) and y_A = θ[F_v(N)−F_v(N\{A})] exactly. Each owner's coordinate enters each component identically, so fixed nonnegative weighted sums preserve coordinatewise own-monotonicity, nonnegativity, coverage, and the (1+θ/4) bound. O(m²) after O(m log m) sort is correct for m prefix evaluations.

## Scope limitations
- Base rule (CONTINUOUS_ATTACK) taken as audited; only its zero-report behaviour (line 30), coordinatewise A-monotonicity (line 36), and budget identity (line 100) were used.
- Frozen static theorem B_θ/T ≤ 1+θ/4 not re-derived.
- No tool execution; numerical checks done by hand.
- Historical novelty not assessed.

## Verdict
**No findings of error in reviewed scope**; one low-severity wording omission (Finding 1).

**Provisional verdict: no invalid steps found in reviewed scope.** Most important observation: both primary proofs check out step-by-step; the only non-trivial dependence not provable from the packet is the branch-aggregation step's implicit assumption that branches are *parallel, independent* primitives (the file itself defers nested/outer effects).

## Findings

**Primary (SHORT_STAGE, SHARP) — verified, no defects**

- SHORT §(1): d/dT[qρT] = q[ρ²−m(ρ−1)] recomputed; each long-role derivative (capped: q(1+ρ−m), uncapped: q(ρ−m)l_k/T) is individually ≥0 and others' short-role payments rise as T falls, so H ≤ ur−vtR is valid without a positive-part gap.
- SHORT (4): substitution v=u e^{−δ} reproduces z²A²(r+δ)/(δ−zA) exactly; monotonicity numerator δ[1+2zδ−z²A] confirmed.
- SHORT (6): exp(2δ)F = (5δ−13)e^{2δ}+(17+8δ)e^δ−4(1+δ) confirmed; Taylor coefficient 2^{n−1}(5n−26)+8n+17 gives 0,0,1/2,−1/2,1/24,41/120, positive for n≥6. Bracket 60−60δ+5δ²+41δ³ >0 confirmed.
- SHARP §1: D_l formula (1), concavity in d, and derivative sign 2+u−(2−u)e^u with g′=ψ≥0 confirmed.
- SHARP §2: recipient comparison (1−q₀−q_b)(s_k−l_k)≤0 correct; q_bD_Q ≥ q_min A via D_all ≤ D_Q+1−A and x e^{−x/t} decreasing for x≥t is correct in both branches.
- SHARP §3: u,ε,w bookkeeping consistent (v=1+u−d stays in [0,t] exactly on d∈[ε,1]); C_t≤e via φ(t)=t−1/t−2log t with φ′=(1−1/t)²; G′ sign −R(R−1)J(w), J′=Rw−1≤0, J(t)≥0 via (x+2)e^{−x}≥2−x all recomputed.
- Sharpness: payments (1−c,c,c), loss 1/2−c=(e−1)c, equality holds.

**Low — SHARP §4 lines 151–156 (scope).** Branch Cauchy–Schwarz treats each branch as an independent primitive with disjoint own coordinates. Nested branches (a primitive's output feeding another) are not covered; the file says so at 171–174, but the headline "unbounded branches" should be read as *parallel* branches only.

**Secondary (OPTIMAL_CONCENTRATION_PRICE) — lower/class claims verified**

- §2 cancellation: λ=1/2, P=1/(4uv), y_u=H(t)/(4v), y_v=H(t)/(4u) confirmed; t∈(1/2,2/3) since u<2v. Realization condition t/[2(1−t)]<u<1 ⇔ v>1/2 confirmed. Endpoint comparisons (d,d)→(u,d) and (L,R)→(L,L) give c=1/2; (L,1/2) and (1,R) give H(2/3)=1/2. Note only H(2/3)≤1/2 is actually needed for §3, and it follows directly from the (1,R), R:1/2→1 comparison; local constancy is redundant but correct.
- §3: λ=1−R, P=1−R, Y(R)=H(1/(1+R))R(1−R); t-substitution yields CP_ceiling exactly.
- §4: P=(1+s)³/(27s), 8(1−s)(2s−1)−s² = −17s²+24s−8 confirmed; J(2/3)=4/243 and J(1)=−2 recomputed; log-derivative sign checks at s=0.67 (+) and 0.70 (−) agree with J; G(2/3)=125/972; G(ρ)≈0.12875.

**Low — §6 lines 137–142 (missing stated hypothesis).** Deriving CP_balance from the continuity class uses P→1 as D→A from both orientations. This holds for the water product (companion line 60) but is not stated here; the implication is specific to this fixed P, not to arbitrary continuous rules.

## Scope limitations
Cannot execute; the h′/monotonicity claims of the upper construction (companion §§3–7) are not re-derived here. Exactness of ρ's isolation (J′<0 on [2/3,1]) spot-checked only at x=1/3.

## Verdict
No findings invalidating (SN), (SNL), CP_ceiling, or CP_optimum lower bound within the reviewed scope; two low-severity scope/hypothesis notes above. Exact-optimum claim remains conditional on the separately reviewed upper construction.

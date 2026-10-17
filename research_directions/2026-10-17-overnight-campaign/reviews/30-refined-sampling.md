**Provisional verdict: no findings in reviewed scope.** Every load-bearing step I was asked to check (own-bit conditioning, scalar cap inequality, rank/trace bound, dependence on w(B), integration by parts, endpoints, exact normalization, asymptotic domination) reproduces correctly. The most important point to record is that the refinement is a pure analysis change: mask rules and the surrogate are untouched, and the new weight ω_D depends only on the public integer D.

## Findings

**No correctness findings.** Verification notes, step by step:

- **Conditioning (root 19).** Σ_i q·E_{B_{-i}} min{a_i(B_{-i}),G} equals both sides of the swap since P(i∈B)=p independently of B_{-i}. Correct.
- **Inequality (2) (root 21–24).** Case x≤G: ⇔ x+h ≤ G+h. Case x≥G: ⇔ Gh ≤ hx. Both hold for h≥0; zero-denominator case gives 0. Tight, correct.
- **Dependence on w(B) (root 20, 29).** Requires h_i = Σ_{j∈B\i} a_j(B\i) = w(B\i) ≤ w(B). The *exact* training-sum identity is supplied by CONE §6 line 137 (ψ vanishes on W, ℓ touches C_B) and PSD §2 (v_B^T U_B v_B = λ_min). Monotonicity of w is superadditivity. Note the older LOW_RANK lemma only hypothesises ≤G; the refined lemma correctly states the stronger hypothesis at root line 12. Factoring (G+w(B)) out of the sum before applying the trace bound is valid because tr(V_B)≤D holds for every B.
- **Rank/trace (root 25–29).** Column-substochastic ⇒ ‖V‖₁≤1 ⇒ |λ|≤1; nullity ≥ |B|−D ⇒ ≤D nonzero eigenvalues; trace ≤ Σ|λ| ≤ D. Columns are restrictions of L to B, rank ≤ D. Correct; diagonalizability not needed.
- **PSD route (root 33–37).** x_i+h_i = tr(P_{B\i}U_B); 0≤U_i≤U_B gives range inclusion, U_i ≤ α_iU_B, hence ratio ≤ α_i ≤ tr(U_B^{†/2}U_iU_B^{†/2}); summing gives rank(U_B)≤m. Zero-denominator case forces x_i=0. Correct.
- **Density identities (root 51–52).** h'/h = (D+1)/p − D/p² = (p−Dq)/p² = 1/p − Dq/p²; (ph)' = h(−1+1−Dq/p) = −(Dq/p)h. Correct.
- **Integration by parts (root 53–60).** −∫phg' = −[phg]₀¹ − ∫(Dq/p)hg; the +D∫(q/p)hg from (1) cancels exactly. Endpoints: p·h = p^{−D}e^{−Dq/p}→0 at q=1; at q=0, h=1, g(0)=w(N)=G. Yields G[1+D∫(q/p)h]. Correct.
- **Normalization (root 62–71).** Under t=q/p, h dq = (1+t)^{D−1}e^{−Dt}dt; d/dt[(1+t)^De^{−Dt}] = −Dt(1+t)^{D−1}e^{−Dt}, endpoints 1 and 0 ⇒ the D∫ term = 1. K_D = 2/Z_D; rational formula via binomial expansion checks (Z₁=1, Z₂=3/4, Z₃=17/27, Z₄=142/256 ⇒ K₂≈2.67, K₃≈3.18, K₄≈3.61, all below 1+2√D).
- **Asymptotics (root 76–86).** φ(t)=t−t²/4−log(1+t) has φ'=t(1−t)/(2(1+t))≥0 on [0,1], so the t≤1 bound holds; (D−1)/(4D)≥1/8 for D≥2. For t≥1, log(1+t)≤t·log2 and D−(D−1)log2 ≥ D(1−log2). Pointwise limit exp(−s²/2) ⇒ √D·Z_D → √(π/2), K_D ~ √(8D/π). Convergence is from below (e^{−t} factor), so K_D > √(8D/π) for finite D; the file correctly refrains from an O(1) claim.

**Minor (presentation only), root 82–84:** the t≥1 tail is phrased as a vanishing tail estimate rather than a D-independent dominating function on s≥√D; the bound exp[−s√D(1−log2)] ≤ exp[−s(1−log2)] closes this trivially. Not a gap.

**Incentive survival (root 45–49).** ω_D is a positive integrable function of the public D; mask weights ∫ω p^{|B|}q^{n−|B|}dq are report-independent constants, and coverage/OUT are linear inequalities preserved under nonnegative averaging. Confirmed.

## Scope limitations
- Upstream results (cone fixed-mask coverage/OUT, §6 surrogate existence, PSD selector argument) were checked only insofar as the refined lemma depends on them; I did not re-derive the facial-geometry claims.
- CONE_CHECKS.json and CONE_APPLICATIONS_AND_LIMITS.txt are referenced but not in the packet; no numerical cross-check was possible or performed.
- No claim about K_{d+1} ≤ 1+2√(d+1) for all d is asserted in the file; I verified it only for D≤4 and asymptotically.

## Verdict
**No findings in reviewed scope.** The refined inequality (1), the density identity (3), the exact bound (4)–(5), and the asymptotic √(8/π) coefficient are all validated; the mechanism itself is unchanged, so individual OUT and coalition coverage carry over.

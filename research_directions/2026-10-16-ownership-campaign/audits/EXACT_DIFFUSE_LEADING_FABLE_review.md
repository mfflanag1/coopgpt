**Provisional verdict: no substantive findings in reviewed scope.** The fixed-owner construction, deviation accounting, and two-sided asymptotic (B) recompute correctly; only low-severity hypothesis-statement gaps found.

## Findings

**1. (Low) Section 5 real-ρ variant omits the hypothesis ρ ≥ 3.** `DIFFUSE_PREMIUM_EXACT_LEADING_v2.txt:146-150` chooses ρ = 1+log(T/(2ε)) for "any fixed T" and asserts Δ = ε[Kρ−(2e−1)] and the cap check. The post-deviation coefficient equals e·q only if the new ratio ρ−1 ≥ 1 (hardware still short), and the changed-cap check eε ≤ T/(2e) < 1 requires q ≤ e⁻²/2, i.e. ρ ≥ 3 ⇔ ε ≤ T/(2e²). This is automatic as ε→0 but should be stated. Verification: add the explicit condition; the integer construction already has n ≥ 3.

**2. (Low) Passage from pointwise bound to W(ε) ≤ D(ε) uses monotonicity of D not proved in the dependency.** `SHARP_INCOMING_ENTROPY_v2.txt:129` parenthetically asserts D is increasing on [0,1]. This is true (A = exp(Kε) increasing; B decreasing because ε(1+log(1/ε)) has derivative log(1/ε) ≥ 0; D increasing in A, decreasing in B per lines 97-98), but the one-line justification should be recorded since (B)'s upper side depends on it.

## Verified recomputations (by hand, from packet)

- Branch j: short T/k, capped long nT/k, ρ=n, q=e^{1−n}/2; z_{B_i}=k·q·T/k=ε; z_{A_jh}=(1−q)T/(km) ≤ ε/k iff m ≥ (1−q)/q. Z = (1−q)T + nε = T+ε(n−1). ✓
- Bottleneck: (n−1)e^{2−n} ≤ 1 for n≥3 gives ε(n−1) ≤ cT, so P+M = 2−ε(n−1) > 1. ✓ Outer: all accounts <1, S=2, q₀=c, ΣN_i=(1−c)+2c=C. ✓
- Deviation: ratio n−1 ≥ 2, coefficient eq; Z' = (1−eq)T + eε(n−1) = T+eε(n−2); Δ = ε[(e−1)n−(2e−1)] > 0 (n=3 gives ε(e−2)). ✓ eε ≤ T/(2e)<1 for n≥3 ✓. gain = (1−c e^{−Δ})(1−T) − [(1−c)(1−T)+cε] = c[(1−T)(1−e^{−Δ})−ε]. ✓ Only one ε subtracted. ✓
- Parameterization: n = L−logL−θ ⇒ T = 2εe^{n−1} = 2e^{−1−θ}/L ✓; L≥8 ⇒ n≥5, T<1 ✓.
- Lower remainder: (1−T)(1−e^{−Δ}) = Δ − TΔ − O(Δ²); TΔ = O(ε), Δ² = O(ε²L²) = o(ε), all θ-uniform ⇒ cKε(L−logL)+O(ε). ✓
- Upper expansion: B/A = 1 − KεL − 2Kε + O(ε²L²) ⇒ (A/2)e^{−B/A} = c + cKεL + O(ε). ✓ Gap ⇒ O(ε log L). ✓
- Interface: (I-sharp) → (6) with M ≤ H=1 and monotonicity of v[1+log(1/v)]; outgoing K z_i → A; (5),(7),(8),(9),(10) and maximization at r=B/A reproduce D. The sharp long-stage ratio bound [e^u−v]/d ≤ (e^u−1)/u ≤ K uses d ≥ u = d+v−1 ✓; the α-minimum K−1−(K/2)e^{−1/K} ≈ 0.24 > 0 ✓.
- Finite check n=k=8, T=1/8, m=3000: m ≥ (1−q)/q ≈ 2192 ✓; 24,010 owners ✓; 927265/131072 arithmetic ✓.

## Scope limitations

- Could not run any checker; the 100-digit replays are taken as corroboration only, as the file itself states.
- Outer own-monotonicity, coalition coverage, and the sharp outgoing bound O_i ≤ Kz_i are imported as previously audited; not re-derived here.
- Did not re-audit the frozen v1 short-stage estimate (incoming ≤ s_i/2) beyond checking that its use in the switching case of v2 §1 is consistent.
- No assessment of all-mechanism optimality, which the note correctly disclaims.

## Verdict

No findings beyond two low-severity statement gaps (ρ ≥ 3 in §5; explicit monotonicity of D). The exact leading asymptotic W(ε) = C + c(e−1)ε log(1/ε) + O(ε loglog(1/ε)) is supported by the packet.

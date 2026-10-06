**Provisional verdict: no findings in reviewed scope.** I re-derived every load-bearing step of POISSON_CANDIDATE.txt independently and could not refute any of them. The most important check: the gain over Lemma 4.1 comes entirely from charging each export class h only to the slice r·n_r·z_r (r=h+1) of the destination budget rather than to the whole budget; since Σ_r r n_r z_r ≤ y(N) pointwise (x_r ≥ 0), all d slices together cost at most α·E[y(N)], which is exactly what line 45 uses. That step is sound.

## Verification of load-bearing steps

1. **Coalition inequality (1), all histograms (lines 23–29).** Coalition 1 (one low per pool; m−h ≥ m−d ≥ 1 lows exist) has worth 1. Coalition 2 has worth m−d+1 when some type<d pool exists, m when n_d=k; using m−d+1 in both cases is valid. Weights (m−d), d give constant (m−d)+d(m−d+1) = (d+1)m−d² = A and low coefficient (m−d)+d(m−d+1) = A for h<d. Correct, including n_0=0 and n_d=k. Absent types contribute n_h=0, so undefined x_h/z_h never appear with nonzero coefficient.

2. **Monotonicity edge (line 36).** Raising one low in a type-h pool gives histogram n−e_h+e_{h+1}; after pool/within-pool symmetrization the changed owner is a high owner of a type-(h+1) pool, paid z_{h+1}(n'). Only the changing owner's own payment is compared — no unchanged-owner transport. Symmetrization preserves own-monotonicity because ȳ_i(c)=|G|⁻¹Σ_g y_{g(i)}(g·c) and each summand is nondecreasing in c_i. No randomization of the mechanism: every inequality is a valid linear inequality for the deterministic symmetrized rule; μ(n) are nonnegative weights.

3. **Identity (2).** μ(n)n_h/[μ(n')n'_{h+1}] = p_h/p_{h+1} by direct factorial cancellation. Sources {n_h>0} ↔ destinations {n'_{h+1}>0} bijectively; (3) follows. With p_h ∝ λ^h/h!, A·p_h/p_{h+1} = A(h+1)/λ = α(h+1). Correct.

4. **Budget accounting (4).** α Σ_r r E[n_r z_r] ≤ α E[y(N)] and E[n_d((m−d)x_d+dz_d)] ≤ E[y(N)] use disjoint parts of each destination's budget; summing gives (1+α)E[y(N)] ≤ (1+α)B·E[T] since y(N)(n) ≤ B·T(n) for every n with T(n) ≥ m > 0. I also checked the dual certificate (lines 73–79): residual coefficients are −(1+α)μn_h(m−h) for lows h<d, −αμn_d(m−d) for x_d, −r μ n_r for z_r (r<d), and exactly 0 for z_d; constants sum to A+d(d−1)p_d^k. Matches.

5. **E T.** Pool total m+(m−1)h, T=m+(m−1)min_j H_j; tail-sum formula and E T ≤ m[1+d(1−p_0)^k] ≤ m[1+d e^{−kp_0}] are correct.

6. **Asymptotics.** q=⌈log(d+1)⌉≥2 gives m>d. k≥k_d ⇒ kp_0≥2q ⇒ d e^{−2q} ≤ d/(d+1)² → 0; A/m = d+1−d/q = (1−o(1))d. λ ≈ d²q² > d, so terms increase to h=d and λ^d/d! ≤ Z ≤ (d+1)λ^d/d!, giving log k_d = d log d + 2d log log d + O(d) = (1+o(1))d log d. With d = ⌊(1−ε)log k/log log k⌋, log k_d ≤ (1−ε+o(1))log k < log k eventually; the finite bound applies at that exact k with no monotonicity of B_k. liminf ≥ 1−ε, then ε↓0. Combined with Theorem 3.1, B_k ~ log k/log log k.

## Minor remarks (not defects)
- Line 13's first inequality silently uses m−1 ≤ m; harmless.
- The candidate relies on the manuscript's symmetrization lemma; that lemma's proof (lines 315–320) is terse but correct as argued above.

## Scope limitations
- I did not execute the exact row verifier; my dual-coefficient check is by hand only.
- Only POISSON_CANDIDATE.txt and manuscript.tex were reviewed; the symmetrization lemma and Theorem 3.1 (upper bound) were taken from the manuscript as stated, not re-audited.
- No priority or novelty assessment.

**Verdict: no findings in reviewed scope.** The candidate proof of liminf B_k·log log k/log k ≥ 1 survives this audit.

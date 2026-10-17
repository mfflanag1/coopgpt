**Provisional verdict: no findings (no concrete mathematical defect) in the reviewed scope.** The most consequential checked item is the own-report derivative inequality (4) in PSD_FIXED_SPECTRAL_SHAPE_STOPPING.txt: it is correctly derived and correctly integrated without any sign assumption on f'.

## Findings

No defects of severity ≥ minor. Verified steps and residual observations:

**Fixed spectral shape (lines 24–56)**
- Payment (3): at C = diag(1,s,…,x,…,s), T=1, P_jj = f(x)/(1+(m−2)f(s)+f(x)); Tr(PX)=x·f(x)/D(x). Correct.
- Derivative necessity: g(x)=x f(x)/D(x) is nondecreasing by own-report monotonicity (xE_jj increases in PSD order; T stays 1 for x near s>1). g is differentiable at s exactly where f is, so g'(s)≥0 a.e. Numerator expands to f(1+kf)+s f'(1+(k−1)f) — matches (4).
- Integration: (log I)' = 1/s + f'(1+(k−1)f)/[f(1+kf)] equals (4) divided by s f(1+kf)>0; log I is locally AC because f is continuous, positive, locally AC on [1,R]. I(1)=(1+k)^{−1/k}=m^{−1/(m−1)}. q(s)=sf(s) ≥ c_m(1+kf)^{1/k} ≥ c_m. Correct.
- A(s) increasing in q: ∂/∂q numerator = k(1−1/s)>0. Limit gives B_m; exp(−u)≥1−u gives m−log m. Correct.
- Observation (not a defect): "worst factor at least B_m" is a supremum over s→∞; no finite profile attains ≥B_m. Consistent with the note's wording.
- Observation: "continuous at 1" is redundant if local AC is on [1,∞); harmless.

**Positive resolvent (lines 20–31)**
- Pairwise identity: Σ_{i,j} f_j(λ_j−λ_i)/λ_i pairs to (λ_j−λ_i)(λ_jf_j−λ_if_i)/(λ_iλ_j). Correct; nonnegative under nondecreasing h. Equality for f=1/λ confirmed. C_L arithmetic m/(1+(m−1)/L)→m correct. Resolvent integrand λ/(λ+s) nondecreasing, finite for λ>0. Convex-mixture argument via linearity valid.

**Compression note §7 (lines 146–176)**
- X_i=I−e_ie_iᵀ: standalones 0, C=(m−1)I, G=m−1. QX_iQᵀ=I_r−u_iu_iᵀ, f_i^Q=1−‖u_i‖², Σ‖Qe_i‖²=Tr(QQᵀ)=r, compressed grand = m−1, so G_Q=r−1 for every Q. Correct and orientation-independent as claimed.
- (6): total ≤ Wκ(r−1); grand coverage requires total ≥ T = G = m−1 (standalones vanish). Algebraic substitution e_i=z_i−κf_i gives Σe_i ≤ κ(m−1)−κ(m−r)=κ(r−1). Correct.
- Scope is correctly stated: "(6) is a scaling requirement, not a mechanism lower bound"; the counter-example diag(1,0,0), diag(0,1,0) (global gain 0, compressed gain 1) checks out.
- Observation: (6) implicitly assumes the composition total is exactly the ν-integral of local components with no additional global term. The text's framing ("from these components alone") makes this explicit enough.

**Architecture vs. mechanism scope**: all three notes explicitly disclaim unrestricted lower bounds (lines 68–83, 15–18, 171–186). No overreach observed.

## Scope limitations
- Sections 1–6 of the compression note, the shifted-harmonic and Huber claims, and the cited T·C⁻¹ result were not audited.
- Checker scripts were not in the packet; I did not run anything.
- I did not assess whether B_m is attainable or whether (4) suffices for global incentives (the note does not claim either).

## Suggested verification
- Symbolically expand d/dx[x f(x)/D(x)] at x=s and compare with (4); numerically test (log I)' identity for a non-monotone f (e.g., f=1/λ+0.1 sin λ scaled).
- Random orthonormal Q (various r) on X_i=I−e_ie_iᵀ: confirm Σλ_min(QX_iQᵀ)=m−r exactly.

**Verdict: no findings in reviewed scope.**

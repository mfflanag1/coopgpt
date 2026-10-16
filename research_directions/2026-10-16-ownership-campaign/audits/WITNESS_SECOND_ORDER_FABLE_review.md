**Provisional verdict: no findings in reviewed scope (minor presentational gaps only).** I recomputed every displayed formula and inequality in the note and found them correct; the chain Section 2 → 3 → 4 → 5 does optimize the actual envelope over the full whole-owner report boxes of every owner type in the stated class.

## Findings

**1. Low — Section 4 line 145–147: order of logic.** "Maximizing (10) over the full T interval gives the ACTUAL class optimum" needs the maximizer T_* to lie inside the region {T≤1/2, ρ≥6} where g_1(1−T)=F_ε(T) was established. This is only justified afterwards by (12) (T_*~1/L ⇒ ρ(T_*)≈L−logL≥6). Not an error, but the dependency should be stated explicitly.

**2. Low — Result paragraph line 10 vs Section 2.** "Arbitrary productive-hardware fragmentation" is load-bearing only together with the cap h₀≤T_j/2 (used at lines 70, 81: δ≤T/2 for the grid-cap check and h/s≤1/2 in the 1/8 term). The class definition states it, but the Result wording should repeat the restriction to avoid an overreach reading.

**3. Informational — line 173–174.** The o(ε) remainder is actually O(ε·logL/L) from (12) (log x = logL + log(x/L)); the note could state this.

## Checks performed (all passed)

- Setup: q=e^{1−ρ}/2=ε/T, local payments εd_i, Z=T+ε(ρ−1), S=2, outer coefficient c, ΣN_i=1+c.
- Section 2: R≥ρ via min(d_iT_j,s)/s ≥ d_i; derivative (6) rederived from Z_j=(1−q)s+qD with D′=m, q′=q(R−m)/s; bounds 1≤Z_j′≤1+5/(2e²) (sign R(3−R) at m=0; m=R gives 1+q(R−1)); R_o≥2; Q′≥0 since Z_j′<2≤R_o; QR_o≤1/e<1/2; q_jR≤3e^{−2}/2<1/2; payment h(1−Qq_j) with derivative ≥3/8. Pure-grid E=N via long-side primitive monotonicity with stable outer orientation.
- Section 3: V,U,Δ,z′ rederived; Δ≥0 and z′≤εd from monotonicity of e^u(ρ−1−u), e^u(d−u) on [0,1], ρ≥3; (7) exact; g_d convex, g_d(0)=0 (second bracket ≤0); gain difference cε(1−d)[e^{−Δ}V−1] correct, and Δ≤ε(ρ−1)(V−1)≤(V−1)/e≤logV under (8); superadditivity (9) and equality instance valid. Hardware restoration is covered by the audited short-coordinate own monotonicity including cap switches of grid accounts when H′ falls (no orientation flip since opposing ≥2H′).
- Section 4: ∂/∂u_j of (7) rederived exactly; braces ≥3(1/2−ε)−1>0; corner maximum; (10) with Δ(T)=ε[K log(T/2ε)−e]; exclusion bounds (cK/2)ε(L+1−log2) and 6cKε vs F_ε(1/L)~cKεL.
- Section 5: F′, F″<0, endpoint signs (left limit K/(2e²)), (11), x=O(L), expansion (12), and the stationarity identity e^{−Δ}=1/(1+Kε(x−1)) giving Kε(x−2+1/x)−ε → (SO) with constant −[2e+Klog2] (verified: K−Klog2−e−2K−1 = −(2e+Klog2)).

## Scope limitations

- Relied on the primitive own-monotonicity statements in root/campaign_review_context.txt as previously audited; did not re-prove them.
- No numerical replay was run; all verification is by hand algebra on the snapshot.
- Did not assess the general theorem DIFFUSE_PREMIUM_EXACT_LEADING_v2.txt (stated as already reviewed) or any claim outside the defined parallel-branch class.
- Did not evaluate whether the class definition itself (common cap proportions, branch0-only hardware for local owners, no local owner on productive hardware) is the intended witness architecture; the note correctly flags these as real restrictions.

## Verdict

**No findings in reviewed scope.** The class-specific second-order optimum (SO), uniqueness of T_*, and the O(ε) coefficient are supported by the supplied proof for arbitrary cap vectors, branch weights/counts, and fixed owner identities, modulo the two low-severity presentational items above.

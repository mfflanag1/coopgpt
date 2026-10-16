**Provisional verdict: no findings in reviewed scope.** I re-derived every step of Theorem A (half-gap, constant 1/2) and the algebra of Theorems B–C and could not falsify any of them. Most important observation: the strongest-looking step, the convex-concentration reduction in §3c (lines 105–122), checks out, including the sign of (6) and the r-monotonicity certificate.

## Findings

**No correctness findings.** Verification details (so the "no findings" is auditable):

- **Cross-monotonicity (lines 14–29).** With a ≤ b fixed, a-short payment a+q[min(b,T)−a] is nondecreasing in opponents' a-reports (T, min(b,T), q all nondecreasing since ρ is nonincreasing in T) and nonincreasing in b-reports (ρ↑, q↓). b-short payment b−q(b−a) has the same signs. Formulas agree at the tie (ρ=1, q=1/2, both give (a+b)/2), so monotonicity is global. Restoration/deletion is therefore sound for arbitrary mixed deviations of a single actual owner.
- **(1)**: dρ/dT = −(r−m)/T gives q′(T)=q(r−m)/T; qr = ½·r e^{1−r} ≤ ½. Correct.
- **§2**: long case |∂/∂h_i| = q[min(b,T)−a]/T ≤ q ≤ ½; short case (b−a)q′ ≤ (b−a)/(2T) ≤ ½ since T ≥ b. Gain ≤ h_i/2, sum ≤ (H−b)/2 ≤ (H−z_k)/2. Correct.
- **§3a**: needed q(1+2(e−1)r) ≤ 1. Max of (1+2A₀r)e^{−r} is 2A₀e^{−1+1/(2A₀)}, increasing in A₀, < 4e^{−3/4} < 2 via e^{3/4} > 65/32. Correct (numerically ≈1.69).
- **§3b**: gain ≤ u(B−b)/(2b) ≤ (1−b)/2 ≤ (1−z_k)/2 using u ≤ b, z_k ≤ b. Correct.
- **§3c**: replacement by caps preserves full and all single-deletion payments (checked three sub-cases; D>1 always since B>1). (3),(4) exact/valid; g continuous at r (q e^r=½), convex (slopes ½ → 1/(2b)). Sufficiency of (5): (1−z_k)/(2u) ≥ (1/b−q)/2 ⟺ u ≤ b. r≥1: (1+r−b)e^{−r} decreasing, Q(b)=(1−2c)b²−(2−3c)b+1 with Q′ ≤ −c, Q(1)=c>0. r≤b: single coordinate 1+r−b>r gives 1/(2b)−q ≤ 1/(2b)−q/2. r≥b: bracket (6) has derivative 1/b−(3/2)e^{−r} ≥ 1/r−(3/2)e^{−r} > 0 (r e^{−r} ≤ 1/e < 2/3), value ½e^{−b}>0 at r=b. All correct.
- **§4**: positive-part subadditivity over branches; diagonal zero by own monotonicity. Correct.
- **Theorem B**: Σ_i(v_i−c)_+ ≤ (Σv_i−c)_+ holds for c≥0; the two ranges combine exactly to min{U_k/2,(p_k−U_k/2)_+}; ≤ p_k/2 and ≤ min(p_k,U_k)=p_k−w_k verified.
- **Theorem C**: decomposition at lines 170–172 is exact; L_i ≤ min(w_i,z_i) holds; (UR_multi) is invoked at its stated hypotheses (full-profile Δ₋, whole-owner underreports; ρ=2 boundary has δ=0 so "<2" vs "≤2" is immaterial).

## Scope limitations

- **Cap threshold modelling (Theorems B/C).** S^i uses the *full* hardware total H as cap for every deviated profile. In the actual outer primitive the cap is min(H_restored, B^i); if a deviation drives B^i below H (outer pool switch) or the deviator cuts its own outer hardware, min(b_k,H) is not the true capped account. The document implicitly assumes outer hardware restored (as in the universal file's Theorem 2) but does not say so. This is a stated scope gap ("outer response step remains"), not an error, but Theorem C should not be cited as a statement about actual outer payments.
- Grid restoration is taken as a definition; the WLOG argument (grid cut reduces (S−S^i)/3−(d_i−d_i^i) by ≥ 2η_i/3) is not written, though it is easy.
- I did not re-audit the universal retention proof or the primitive's own-monotonicity; both are assumed as stated.
- No numerical falsification was run; spot checks were done by hand only.

**Verdict: no findings in reviewed scope.**

**Provisional verdict: no material findings in reviewed scope.** The threshold-star identity, the two measure-limit steps, the symmetrization/hypergeometric-coupling passage, and the moment comparison all check out by independent rederivation. Most important observation: the proofs are correct; the only soft spots are presentational quantifier phrasing, not logical gaps.

## Findings

**1. (Info) Threshold identity (1)/(B) rederived — correct, including endpoints.**
Gate §1 lines 52–65. With centers totalling ≤1 and nonfocal leaves at 1, focal gains ε exactly on {no other leaf sampled} ∩ {≥t+1 centers}: ε(1−p)^(s−1)T. Unchanged leaf j: F(R∪j)=C both times; F(R) rises by ε only when focal ∈ R, other s−2 leaves absent, ≥t+1 centers: −εp(1−p)^(s−2)T. Sum factors to ε(1−p)^(s−2)(1−sp)T. At p=1, s>2 both sides are 0; s=2 gives −ε, consistent with the pair test. Checker `direct_marginals` encodes this exactly; the 230 count matches the loop structure (10 (k,t) pairs × 5+6+6+6 p-values). Not run.

**2. (Info) Measure limits — correct.**
§2: (1−2p)p^k → −1·1_{1}, DCT with bound 1, so μ({1})=0. §3: existence of a non-atom a∈(1/s,1) with μ((a,1))>0 follows from continuity from below plus countability of atoms; T_{k,⌊ka⌋}→1_{(a,1]} off {a}; h_s<0 strictly on (1/s,1); μ({1})=μ({a})=0 handles both boundary points. Sound.

**3. (Info) Extension coupling and weak limit — correct.**
Permutation averaging preserves coverage/TCWM/funding because each is a linear inequality invariant under relabeling on the fully eligible symmetric domain; averaged weights depend only on |R| (verified via (π·y)_i(b)=y_{π(i)}(b_π)). Restricted indicators of a uniform k-subset equal q without-replacement draws from a fixed k-marked label set, so TV ≤ q(q−1)/(2(n−1)) uniformly in k; |E₁f−E₂f| ≤ F(b_N)·TV for f∈[0,F(b_N)]. Mass bound Σ_kW_{n,k}≤κ_n from the balanced profile; weak limit mass equals lim mass ≤ L. Pure-owner moment (k)_{r−1}/(n−1)_{r−1} → p^{r−1} within the same δ. Conclusion L ≥ s^{r−1}/r follows. Check-script case counts (3883, 2920) match their loop ranges.

**4. (Low, exposition) Quantifier phrasing in Gate Theorem (A), line 17–18.**
"Satisfies TCWM on every finite owner population" should be read as "simultaneously for all populations with the same μ"; the text later says this (lines 32–33, 78–80) but the theorem statement itself could be sharpened.

**5. (Low, exposition) Gap between lower s^{r−1}/r and upper r·s^{r−1} is factor r².**
Both notes state the constant is not investigated. The upper's factor r comes from the loose grand-marginal inequality (5); on min_r the balanced profile only shows s^{r−1}. Nothing wrong, but the "Θ_r" claim should not be read as constant-sharp.

**6. (Low) Comparative claims not in packet.**
Statements that an unrestricted min_r mechanism achieves (r+1)/2, full-OUT 1+c(r−1), and the Ω(s^{1/4}) general lower (Gate line 30, Extension lines 30–32, Final Gate lines 35–37) cite results outside the supplied files; cannot be verified here. They do not affect the architecture lower itself.

## Scope limitations
- Did not execute any script; JSON outputs taken as asserted, only cross-checked against loop counts.
- Did not audit energy note §2 inequalities (5)/(6) or its "accepted" status beyond consistency of (8) with Gate (1).
- Historical novelty not assessed.

## Verdict
**No findings in reviewed scope** (material). The fixed-positive-mixture support theorem and the liminf ≥ s^{r−1}/r architecture lower are correctly proved as stated, with scope (report-independent nonnegative whole-owner weights, min_r, limit support only) accurately delimited.

**Provisional verdict: no findings in reviewed scope (source inspection only; dependencies outside the packet unverified).** Most important observation: the certified margin is razor-thin (worst accepted bound 1.3999823 vs 7/5, gap ≈1.8e-5), so the theorem's validity rests entirely on every relaxation direction being correct; I checked each and found none reversed.

## Findings

**1. (Info) Scalar reduction (7) — verified step by step, no gap found.**
- Positive recipient: restored account d−D ≤ 1 (uses (ii) and D ≥ 0). Hardware-short payment a+q(g−D) with q=½exp(1−total) is exact; hardware-long case: a < d−D ≤ T so both own coordinates uncapped, coefficient 1−q ≤ k(T) since ρ_h ≤ 1/T. Total lower bound S−D−O requires d_i ≤ 1 for all others (condition (ii)) — correctly used.
- κ: min{K√(zD), w−z} ≤ crossing value; I verified κ is increasing in D ((K²D+2w)² ≥ K²(K²D²+4Dw)) and in K, w, so evaluating at (dh, w_hi, K=7/4) is an upper bound.
- Negative recipients: S' ≤ P+Z' ≤ P+CM = S+(C−1)M ≤ S+c uses S=P+Z (no clipping, needs (ii)), Z ≥ M, M ≤ H. Regime-switch bound (a_i+d_i)/2 ≤ a_i−q_*(a_i−d_i) since q_* ≤ ½. Σ_{i≠r}(a_i−d_i)=1+g−S ✓.

**2. (Info) HARDWARE_DIRECTED_OUTGOING (1),(2) — checked.** (1): V_ij+ΣU_kj ≤ H_j holds in both pools. (2) first stage: positive derivative sum ≤ qρ(ρ−m)+qm ≤ qρ² because ρ ≥ m ≥ 1 whenever m ≥ 1; max ½e^{1−ρ}ρ² = 2/e at ρ=2. Hardware-long: ≤ q ≤ ½. U_{−i} drift ≤ qρ ≤ ½ per unit withheld. Second stage relies on the cross-sign property (RECIPIENT_RESPONSE_HALF_v2, not supplied); the "payment ≥ l_k" and V_k ≤ l_k claims check directly from both pool formulas.

**3. (Info) certify_one_positive.py — exact by inspection.** Decisions are Fraction comparisons; `float` appears only in output/error strings; `raise`, not `assert`, guards unresolved boxes (so `-O` is irrelevant). Box tightening (gl ≥ dl, gl ≥ sl−1, dh ≤ gh, sh ≤ 1+gh) discards only infeasible points. Taylor directions (deg-13 lower, deg-12 upper for e^{−y}, y ≥ 0) are correct by Lagrange remainder; `sqrt_hi` rounds up exactly; constant checks (e bounds 1957/720, 11743/4320; K ≤ 7/4, η ≤ 5/4, c ≤ 23/125, 7/5 < C²) are correct. Monotonicity x ↦ x·k(max{x,T}): derivative 1−½e^{1−1/x}(1+1/x) ≥ 0 via (r+2)e^{−r} ≤ 2 ✓; needed x ≤ 1 holds since x = gh−dl ≤ 1. Hand evaluation of the reported worst box reproduces ≈1.4000, consistent with the JSON.

**4. (Low) Model assumption not restated.** The envelope is bounded only over *underreports* (coordinatewise decreases). If the model's E_i admits any overreport (grid or hardware), nothing here covers it. Suggest stating this explicitly in §1.

## Scope limitations
- I did not run the script; counts (1627/814, discarded 0 — internally consistent with 813 bisections) and `worst_upper` are self-reported.
- Not supplied: RECIPIENT_RESPONSE_HALF_v2 (cross-sign property), SHORT_STAGE_NONLINEAR_THREE_HALVES, the outer primitive's definition and own-coordinate monotonicity, and the primitive properties M ≤ Z ≤ CM, z_i ≤ M (the latter two I sanity-checked from the formula: Z_j = T(1+q(ρ−1)) ∈ [T, CT]).
- SN theorem accepted as audited per task scope.

## Verdict
No findings in reviewed scope. The 7/5 bound follows from (7), and (7)'s certificate is exact and correctly oriented; residual risk lies in the unsupplied dependencies and the unverified execution.

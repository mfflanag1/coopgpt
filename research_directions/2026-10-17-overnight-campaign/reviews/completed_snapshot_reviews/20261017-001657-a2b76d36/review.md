**Provisional verdict: no substantive findings in reviewed scope.** Every displayed derivative, tie, floor case, integral identity, and both lower-bound constructions check out by hand. Only minor notational/presentational issues below.

## Findings

**1. (Low) `energy/SHARP_SOURCE_PRICE_FLOORS.txt` line 50 — notation mismatch.** "Each energy owner gets e_j=m_j" uses m_j, which line 45 defines as (H−E+e_j)_+. In the E≤H regime that quantity is ≥ e_j, not equal. The claim is correct only for the general marginal T−min(H,E−e_j) (line 57), which does equal e_j when E≤H. Suggest writing "e_j = M_j" or defining m_j once as T−min(H,E−e_j). No effect on the proof.

**2. (Low) §7 growing family (lines 121–132).** For every finite k, ε the bound (4+(k−2)ε)/(3+(2k−3)ε) is strictly below 4/3; exact sharpness rests entirely on the two-energy-owner instance (lines 112–118). The text says "tends 4/3", which is accurate, but §1's "uniformly over both owner counts" should be read as: the class infimum is 4/3, not that each count attains it. Already caveated at line 25–26.

**3. (Informational) `root/COALITION_FIVE_FOURTHS_CANDIDATE.txt`.** Baseline b0 gives owner 3 zero capacity in both resources. The argument is valid, but if the intended class forbids zero reports, the instance should be perturbed (e.g., owner 3 reports (η,0)/(0,η) at b0); the inequalities then degrade only by O(η). Also, the hypothesis "all coalition coverage" is used only for 2-member coalitions and "factor κ" only at F(N)=1, so the stated hypotheses are sufficient and not over-used.

## Independent verification summary

- **Rule seams:** at E=H both regimes give ρ=1, energy e_j, hardware h_i/3; q_E continuous at ρ=2 (1/3). ✔
- **Coverage (§3):** E≤H: worth ≤ e(S). H≤E: h(S) ≥ min and Σ_S min(e_j,H) ≥ min(e(S),H) ≥ min(e(S),h(S)); q_E∈(0,2/3]. ✔
- **Long-side (§4):** derivative q + (d/T)q' ≥ q+q'; q_H+q_H'=0; linear branch 2/3−ρ/3 ≥0 on [1,2]; exp branch 0. m_j=(H−E_others)_+ is constant in e_j. ✔
- **Short hardware (§4):** dρ/dH=−U/H², U/T≤ρ; bound 1−q+ρq' = 0 on linear branch; on exp branch 1−(1+ρ)e^{2−ρ}/3, zero at ρ=2, derivative −ρe^{2−ρ}/3 ≤0. ✔
- **Funding (§5–6):** ρe^{1−ρ}≤1; (1−ρ/3)(ρ−1) has derivative (4−2ρ)/3 ≥0 on [1,2]; exp branch derivative e^{2−ρ}(2−ρ)/3 ≤0. Unique-large case: total = max{1+qt, 1+(1−t)(1−q)} with 1−q=(1+t)/3. Small case: (4) recomputed; k=1 excess (1−δ²)/3; k≥2 excess ≤ (1+δ)/3−(k−1)δ ≤ (1−2δ)/3. All e_j≥... δ≥1 and two-large cases give zero marginals. ✔
- **§7 two-owner:** x≥2−κ, x'≤2κ−2, monotonicity ⇒ κ≥4/3. Growing family: H_low≤E iff ε≤1; E<H_high; algebra of (2+E)/(H_low+E) correct. ✔
- **§8 (5):** objective depends only on row/column sums, so sorted allocation is optimal for each served quantity; Fubini on the indicator c(x)≤t≤v(x) gives min(E_t,H_t). Floor identity follows by applying (5) to N and N∖{j}. ✔
- **5/4 file:** coalition values at bA/bB correct; p1,p3 ≤ κ−1 at bA, p2,p3 ≤ κ−1 at bB; monotone-total hypothesis correctly instantiated (owner 3's own coordinate, other reports fixed); 1 ≤ x1+x2+2x3 ≤ 4(κ−1). ✔

## Scope limitations

- §9's mixed bound depends on an "accepted floor-free primitive" with factor 1+1/(2e), and the 5/4 file's upper 3/2 depends on a "Huber graph rule"; neither is in the packet, so those statements are unverified.
- Historical novelty/priority not assessed per task.
- No code run; no files outside the two supplied were inspected.

## Verdict

**No findings** (no mathematical errors) in the reviewed scope. The 4/3 upper bound, all-profile own-monotonicity, the integral decomposition, and both lower bounds are verified; items 1–3 are presentational only.

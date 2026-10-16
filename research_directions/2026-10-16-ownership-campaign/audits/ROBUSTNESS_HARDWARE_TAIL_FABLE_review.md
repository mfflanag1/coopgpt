**Provisional verdict: no findings of error in the reviewed scope; two low-severity gaps (one unstated step, one unverified inherited constant).** Most important: the weighted theorem's negative-savings factor "exceeds 4/5" (WEIGHTED…FUNDING.txt:65) is asserted, not derived, and holds only by a narrow margin that depends on an unstated bound `z_i g_i ≤ 1/4`.

## Findings

**1. Low — WEIGHTED_PRODUCTION_ROBUSTNESS_FUNDING.txt:61–65, (R5).** The audited negative-gap theorem gives factor `L(K²z_i g_i)` with `L(1)=2/e≈0.736<4/5`, so "uniform savings factor exceeds 4/5" is false without a bound on `K²z_i g_i`. It does hold here: for a negative gap `d_i=p_i+z_i≤a_i≤1` so `z_i+g_i≤1`, `z_i g_i≤1/4`, `K²/4≈0.738`, and `L(0.738)≈0.812>0.8` (L is decreasing). Margin ≈0.012; the step should be written out. Verification: add `L((e-1)^2/4) > 4/5` to the Fraction checker.

**2. Low — WEIGHTED…:68–72, (R6).** `sum V_i^power ≤ min(m,1/2)` is stated without proof. I verified it: local-short branch gives `(1-q)L_j ≤ H_j/2` via `exp(1-s) ≥ 2-s`; local-long branch gives `qD ≤ T_j/2` via `ρe^{1-ρ} ≤ 1`. Both also `≤ min(H_j,L_j)`. Recommend recording this derivation since (R6) is the only place hardware mass enters.

**3. Info — algebra checked and consistent.**
- (R3): `d_i ≥ u_i`, `L_i ≥ m-η`, `S ≤ π+Z` all hold; RHS is never negative under the hypotheses (`S-ε-η ≥ 1-c-1/4 > 0`), so the negative-case remark at :55 is moot.
- (R7)→(R8): `r*=1-(1-θ)w`, value `c·exp[η+b-θ(b-ε)]`; monotone in ε and η as claimed. (R9) derivatives, `-3/25` bound, (R10) Taylor lower bound (correct sign for alternating series), and `c e^{3/4}=e^{-1/4}/2<2/5` all verified. Numerically the bound is ≈1.383.
- Weighted floor validity (GRID_WEIGHTED…:12–20): inequality (1) needs only `0≤z'_k≤U_k`; layer-cake plus coalition coverage of `N\{i}` needs no marginal property of `U_k`. The "no marginal assumption" claim is correct as written.
- Addendum: `F''≤0`, `F'(1/8)>17/24`, `V=(7/8)[A-b(1/8)]`, `r*=1-V/A`, monotone substitution (`A e^{-k/A}` increasing in A), and `7081/5081 = 1+(5/8)·3200/5081` all reproduce. Margins: `exp(-217/320)>1/2` holds by only ≈0.015.

**4. Info — script coverage.** `verify_weighted_robustness_constants.py` does not check `exp(-1/4)<4/5` or `exp(1/4)>5/4` (used at :91, :101), nor Finding 1. The addendum's "accompanying Fraction script" is not in the packet.

## Scope limitations
Not in packet, hence unverified: half-gap lemma giving ceiling `(1+z_k)/2`; FIXED_OPPONENT_COALITION_FLOOR restoration and the all-orientation majorant `k(t)≤e^{1-t}/2` (I spot-checked the long-grid orientation only: `1-e^{1-1/t}/2 ≤ e^{1-t}/2`, equality to second order at t=1); individual bounds (P)/(N) and (I-sharp) from v1; the grid-tail `π≥15/7 ⇒ C²` result (Section 5). No tests executed.

## Verdict
**No findings in reviewed scope** that invalidate either claim (η≤1/4 ⇒ <7/5; ε≤1/8 ⇒ 7081/5081), conditional on the listed inherited dependencies. Two low-severity unstated steps (Findings 1–2) should be made explicit; Finding 1 is tight enough that it must be in the certified checker.

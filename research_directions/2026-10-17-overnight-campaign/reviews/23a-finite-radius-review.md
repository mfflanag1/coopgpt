**Provisional verdict: no substantive mathematical defects found in reviewed scope.** Both derivations check algebraically; the only unverifiable items are the exact rational certificates and definitions imported from files outside the packet. Most important observation: the ladder recurrence (5) depends on TCWM being defined for coalitions containing *unchanged* members — this is standard but must match the project's definition.

## Findings

**1. (Info) Ladder recurrence and constants verified** — `FINITE_ARITY_THREE_LADDER_CERTIFICATE.txt` L53–75, 79–84, 99–118.
- Coalition {a_m} ∪ (k_m old actives) has size k_m+1 ≤ min(s, 2m−1); 2m−2 old actives exist, so k_m ≤ 2m−2 is the correct cardinality cap. (5) follows since w ≥ 0.
- Symmetry at C_m: active-branch permutations and a_j↔b_j swaps fix C_m (a_j=b_j=1), so common q_m is justified. Inactive branches (0,1) are not fixed by swaps, but no claim is made about them.
- Final elimination: κ ≥ 1 + D(1/R − κ/R²) ⇔ κ ≥ (R²+DR)/(R²+D). Correct.
- Unrestricted identity: (M−1)∏(2m−2)/(2m−1) = (1−1/M)·∏2m/(2m−1) since the ratio of products telescopes to 1/M; checked at M=2,3 (both give 2/3, 16/15). A_M = 4^M/(2·C(2M,M)) correct.
- Ratio (101): saturated factor [M/(M−1)]·[(s−1)/s] > 1 ⇔ s > M; saturation occurs at M ≈ (s−1)/2 < s, so maximum at M=s, s+1. Correct.
- D_(s,s) formula (110) and asymptotic √(π/(2e))·√s correct; R-optimizer R=1+√(1+D) with value R/2 verified by differentiation; constant (1/2)(π/(2e))^{1/4} ≈ 0.436 and π^{1/4}/2^{7/4} both reproduce.
- Numerics by asymptotic estimate: D_(84,167) ≈ 8.039, D_(83,165) ≈ 7.989; D_(113,113) ≈ 8.009, D_(112,112) ≈ 7.973. Consistent with "first M/s with D>8" and with κ > 2.0031 / 2.0007. **Verification:** root should recompute the exact fraction in (8) with Fraction arithmetic (checker not in packet).

**2. (Low — definitional dependency) TCWM with unchanged members** — L57–62. The incentive coalition contains k_m owners whose reports do not change. If the project's TCWM is stated only for coalitions all of whose members strictly raise reports, (5) fails. Under the usual "weakly increase" definition it is valid. **Verification:** confirm definition in BOUNDED_COLLUSION_GROWTH.txt; also confirm K_3(s), K_3^OUT(s) are sup-over-models quantities so that one family gives a lower bound.

**3. (Info) Radius-r rule verified** — `SHARP_GENERAL_STAR_STOPPING_THEOREM.txt` L83–128.
- Budget: p0·T + (r−p0+1)·R_p ≤ (r+1)T. Coverage: S∩P≠∅ via T_p; S ⊆ L meeting J_P via R_p ≥ v_p(S); S ⊆ L∖J_P via c_P(S) ≥ v_b(S) ≥ v_p(S) (downward). Padding gives R_p ≥ t, so c_i ≤ t ≤ R_p.
- Label changes under own increase: i∉P stays out (others fixed) → P and (J_P,c_P) fixed; i∈P stays in (increase cannot restore ≤ hub); i entering P: old payment ≤ R_old ≤ T_old ≤ T_new. Exhaustive. Decreases are the reverse comparisons of the same pairs.
- Minor gap: |L| ≥ s needed for s-subsets; holds since r ≤ n. Edge case |L|=s (J=L, t=0) is covered implicitly.

**4. (Info) Checker `verify_arbitrary_hub_radius.py`** faithfully implements the rule: core via minimizing form (line 23–24) is a valid efficient core for min-linear F; only comparable in-domain pairs are tested (line 48). Domains are small (n ≤ 5, r ≤ 2).

## Scope limitations
- `check_finite_arity_three_ladder.py`, `BOUNDED_COLLUSION_GROWTH.txt`, and the TCWM / outside-production definitions are not in the packet.
- Exact rational values (8) and the "first M/s with D>8" claims checked only to ~3 decimal asymptotics.
- (SL) lower family and historical-novelty claims not audited.

## Verdict
No findings of substantive mathematical defect in reviewed scope; one definitional dependency (Finding 2) and exact numerics require root's independent execution.

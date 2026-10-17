**Provisional verdict: no substantive findings in reviewed scope** (four claims rederived by hand; two low-severity notes). Most important concrete item: Claim 3's KKT remark that nonnegativity multipliers vanish "at a zero coordinate [by] stationarity plus A,λ≥0" does not follow as written (stationarity there gives ν_i = Σ_{S∋i}λ_S ≥ 0, not ν_i = 0); the conclusion is nonetheless true because the projection onto {Ax≥b} alone is A^Tλ ≥ 0 and hence already feasible for x≥0.

## Findings

**F1 (Low) — unrestricted/RANK_TWO_PROJECTION_MONOTONICITY.txt:57–58.** Justification for ν=0 at zero coordinates is incomplete as stated (see above). Verification: replace with "min-norm point of {Ax≥b} is A^Tλ≥0 since A≥0, so it equals q." Static bound rT and the star example (q_center=m/(m+1)) check out.

**F2 (Low) — energy/RATIONAL_NINETY_PERCENT_OUTSIDE_RULE.txt:17–21, 55–56.** Claim 1's coalition/incentive conclusions are entirely routed through the common-scalar transfer lemma in SHARP_PARTIAL_OUTSIDE_FRONTIER.txt §3, which is itself "deep audit pending." I rederived that lemma's steps (derivative decomposition α_jB_j+(1−α_j)A_j; hinge values H(1)=s, H(t)/t=min(t,s)/t, E[(1−U)h]=(s/t)R(s); both hinge cases reduce to (4) at s or t; empty corner via (3); |J|≥2 via 2μ≥β) and found no gap, but the discrete law's use of it should be recorded as conditional on that audit.

## Verified (hand computation)

- **Claim 1:** Σu_l = 1/8 + 14 − (49/72)·9 = 8 exactly. Tail design 1−u_{3+k}=v r^k makes successive post-jump g-values exactly equal (difference v r^k(−1/18+8/144)=0), so β16=(1+u_16)/2 = 1 − 49·8¹²/(2(9¹⁴−8¹⁴)) = 16795118763825/18478745943857 ✓. (A) at i=1,2,16 holds with equality; i=3 needs u_3≥5/32, and u_3=1−v≈0.15747 ✓. Equivalence (A)⇔coverage via E(t−U)_+ = max_i[(i/16)t−S_i] and completing the square ✓. Funding (k+1)/2 by Jensen ✓. LP paragraph: bounds u_1≥1/(2N), u_N≤1−1/(2N) derived correctly; polytope bounded so a rational vertex exists ✓.
- **Claim 2:** Reduced-profile core uniqueness (K={H_i,L_i}∪{H_s} has worth 2; two worth-1 coalitions force H_i,L_i≥1), own-monotone lift, all-low coalition worth 1 ⇒ total ≥ k+1 at worth 3 ✓. Min-norm core (2/k,1/k) is in the core (average ≥ min) ✓.
- **Claim 3:** Component classification (tree / tree+anchor / odd unicyclic) by rank count ✓; derivatives b/(a+b), 0 or 1, 1/2 on odd cycle (checked on triangle and general odd cycle) ✓; dependent-active-row exclusion on open intervals ✓.
- **Claim 4:** Payments (1,x,2−x), lower plans (1,1,1) and (1,0,2) forcing x=1 and x=0 ✓; Shapley (1/3,1/3,1/3)→(1/2,0,1/2) ✓; mean-plan reduction and scaling invariance ✓.

## Scope limitations

- Checkers (verify_efficient_core_envelope_obstruction.py, verify_optimal_utilization_all.py, the 32-inequality fraction checker) were not supplied or executed; I verified only representative inequalities by hand.
- PROJECTION_ENDPOINT_OBSTRUCTION.txt (rank-3 boundary), COALITION_PRICE_REDUCTION_CANDIDATE.txt, SHARP_MULTIPOOL_OUTSIDE_CANDIDATE.txt, and the ABV16 manuscript are outside the packet; the "rank-three boundary," lower-bound reductions, and prior-art statements are unverified.
- Sharpness of (d+1)/2 (needed for "EXACT sharp") is assumed from elsewhere.

## Verdict

No findings of substantive error in reviewed scope; F1 is a proof-wording defect with a valid repair, F2 is a dependency note.

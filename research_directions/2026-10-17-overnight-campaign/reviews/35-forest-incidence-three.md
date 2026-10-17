**Provisional verdict: no substantive errors found in either claim within the reviewed scope.** The most important observation is that both proofs are complete on their stated hypotheses; the only gaps are (a) the forest file leans on an uncited standard parametric-QP fact for finite piecewise affinity, and (b) the 12/11 document proves only the lower bound, so "exact" is not justified by the text alone (though it is in fact tight on this star — see below).

## Findings

**1. (Low) Finite-piecewise-affine step is asserted, not proved** — `INCIDENCE_FOREST_EFFICIENT_SELECTOR.txt:49–53`. The argument needs: along a one-parameter RHS change the projection is piecewise affine with finitely many pieces, and the active set is constant on each open piece. This is a standard fact for strictly convex parametric QP with RHS perturbation, and the incidence-two file (lines 37–44) gives a slightly fuller sketch. Not an error; verification: cite or reproduce the finite-face argument once.

**2. (Low) Tightness of 12/11 is not shown** — `EFFICIENT_CORE_SELECTOR_INCIDENCE_TWO.txt:136–147`, `verify_incidence_three_subsidy_boundary.py:17` (label `minimum_necessary_funding_factor`). The text proves κ ≥ 12/11 only. I checked by hand that it is attained on this star: y(high) = (12/11)·**1**; at low_i take y_i = 12/11, y_{i+2} = y_{i+3} = 3/2, y_{i+1} = y_{i+4} = 9/22 (sum 54/11, S_i and S_{i+3} tight, S_{i−1} = 3/2, S_{i+1} = S_{i+2} = 75/22 ≥ 3, own-monotone). If "exact" is to be claimed, this construction should be stated.

**3. (Informational) Embedding into a production model relies on external lemmas** — line 155–156 cites "balanced closure/Boolean realization lemmas" not in the packet. Cannot verify.

## Checks performed (all passed by inspection)

- **Lemma, branch decomposition:** removing row r from a tree places each owner of r in distinct components (else a cycle through r); non-r components are homogeneous ⇒ zero in the min-norm solution; branch variables are disjoint ⇒ objective separates; image of H_i under the root map is {0} or ℝ; homogeneity gives cost α_i t² (α_i ≥ 1); reduced problem min Σα_i t_i² s.t. Σt_i = 1 yields t_i > 0 on free branches, 0 on pinned. At least one free branch follows from feasibility. Conclusion d_i ≥ 0 for i ∈ r holds with no genericity.
- **Active-face sensitivity:** x* − c lies in the span of active normals (including weakly active ones), so x* = proj onto the active affine set; derivative in b_r is B^T(BB^T)^{-1}e_r for r in an independent basis on J. **Dependent row:** if a_r|_J = Σλ_s a_s|_J then b_r = Σλ_s b_s is fixed, so r cannot remain active while b_r varies on an open interval; if a_r|_J = 0 then no positive owner lies in r. Correct. Deleting rows/columns preserves the forest.
- **ε-limit:** f_ε(x_ε) ≤ f_ε(e) with Σx_ε ≥ T gives ‖x_ε‖ ≤ ‖e‖ and Σx_ε ≤ T + (ε/2)‖e‖² → T; limit points are efficient with norm ≤ ‖e‖, hence equal e. Pointwise inequalities pass to the limit. Correct.
- **12/11 profiles:** T(high) = 5 and T(low_i) = 9/2 via the uniform dual 1/3; the stated low cover satisfies all five rows (S_{i−1} = 3/2, others = 3); S_i ∩ S_{i+3} = {i}, S_i ∪ S_{i+3} = all; row (i−1) contains i so the IC link is own-incident; 5κ ≥ 5(6 − 9κ/2) ⇒ κ ≥ 12/11. κ = 1 argument: strictly positive optimal dual forces all rows tight; cyclic-triple matrix invertible (x_r = x_{r+3}, gcd(3,5) = 1). Correct.

## Scope limitations

No files executed; test scripts read only. External references (ABV2016, RANK_TWO/COLUMN_TWO files, closure lemmas) not in packet. No novelty assessment.

## Verdict

**No findings of error in reviewed scope.** Two minor documentation gaps (Findings 1–2); no missing hypotheses identified.

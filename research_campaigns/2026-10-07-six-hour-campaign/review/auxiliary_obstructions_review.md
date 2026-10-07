**Provisional verdict: no invalidating findings in reviewed scope.** Most important observation: the uniform-mixture Θ(K) lower bound is linear in the *cut count* K only because the instance has n = K·B^(K−1) owners (K = Θ(log n)); it therefore does not exclude an O(log n)-in-owners budget. This is consistent with the stated scope (line 93) but should be flagged wherever the result is cited against an "O(log K)" conjecture.

## Findings

**1. UNIFORM_MIXTURE_OBSTRUCTION.txt — argument verified; scope caveat (Low).**
- Permutation identity (L15–21): conditioning on U_e=t gives others present i.i.d. with prob t and e absent; with q=1−t this is exactly Pr(e∈W | B_e=0). Correct.
- Lower bound (L39–49): at τ_i > max_{j<i} τ_j, pools 1..i−1 have positive score, pool i has score 0, and pool i precedes all later zero-score pools in priority, so it is selected regardless of tie rule. Pr(τ_i<τ_j)=m_i/(m_i+m_j)=1/(1+B^{i−j}) ≤ B^{−(i−j)}; union bound gives K − K/(B−1). Correct.
- Upper bound (L55–66): selected cut's partial score ≤ score of a true min D-cut ≤ T; last charge ≤ D_e ≤ T; earlier charges are disjoint increments inside that score. 2T per cut. Correct.
- Hand-checked (2,1): six permutations give charges 2,3,2,2,3,2 → 7/3 (matches L76). Hand-checked m=1,R=2 → 3/2 (matches L89). Formula at m=2,R=1 → 7/3, consistent with (2,1).
- Caveat: n is exponential in K; the Θ(K) statement is only in cut count.

**2. RARE_TAIL_OBSTRUCTION.txt — verified, no finding.**
- D equals reports at the lowered profile since every edge capacity ≤ 3/4 < 7/8 = T′. Focal score ≤ 1/8+3ε/4 ≤ 7/32 < 1/4 ≤ every competitor's score (each has an owner with X=1, D ≥ 1/4). Event probability q(1−q)(1−q²)^{K−1} is correct by independence. (1−1/K)^{K−1} = (1+1/(K−1))^{−(K−1)} ≥ e^{−1} > 1/4, and 1−q ≥ 1/2 for K ≥ 4. Bound √K/64 follows. Variance formula checks.
- Note (scope, already stated L2–3, L33–35): this obstructs the monotone *envelope*, not z itself, and only this family.

**3. PATH_STAR_STOPPING.txt — verified, no finding.**
- (A), core domination, and the 3T shortcut-flow argument are correct.
- (B): sum of m path constraints with disjointness outside e gives mδ ≤ (m−1)p_e + BT_e. (C): for e∉C, Σ_k c(P_k∩C) ≤ T; f_e>0 forces m>B and T_e<T/B hence M_e>(1−1/B)T; max of (u−β)/u² is 1/(4β) at u=2β. Threshold 4(B−1)³ ≥ LB and B=2+√L/2 (LHS−RHS = 4+6√L+L > 0) check.
- Section 3: T_e(t)=min(T,b_e+t) is correct since C avoids e. Maximum of x(1−Bx)/(1−x) on (0,1/B): stationary point Bx²−2Bx+1=0 → x=1−√(1−1/B), value B(1−√(1−1/B))² = (√B−√(B−1))² ≤ 1/(4(B−1)). Budget of mixture T−α(T−T_e) ≤ BT_e iff α ≥ (T−BT_e)/(T−T_e), guaranteed by definition of h_e. Focal payment min(h_e,t)→h_e is nondecreasing since h_e ≤ T−b_e. Only focal-coordinate comparisons exist in X(c). Correct.

**4. verification/uniform_mixture.py — logic consistent with text.** `subset_budget` aggregates all non-arrived owners of the selected pool with weight 1/(n·C(n−1,k)), the correct probability of a given predecessor set; `min` with index key implements first-index tie priority; `record_lower` is the correct inclusion–exclusion. I did not execute it.

## Scope limitations
No tools; could not execute the verifier or check files outside the packet. Did not search for alternative polynomial-size instances or for other noise families. Results are method/domain obstructions as stated, not mechanism lower bounds.

## Verdict
**No findings in reviewed scope** beyond the exponential-owner-count caveat for the Θ(K) claim.

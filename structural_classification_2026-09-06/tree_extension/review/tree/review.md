# Review: ALL_TREES.md (all-tree leximin protection, c(G)=1/k)

I re-derived every step of the argument by hand against the exact representation in TREE_CORE_AND_PATH.md. I found no correctness defect. Details of what was checked, plus minor notes, follow.

## Findings

### F1 (Info / no defect) — Exact representation is correctly reused, root-agnostic
ALL_TREES.md:15–25 roots at the target sector r, whereas TREE_CORE_AND_PATH.md:3 roots at vertex 0. This is fine: the diagonalization/relabeling is done once for the whole tree (independent of root), and the necessity/sufficiency proof (TREE_CORE_AND_PATH.md:22–30) never uses which vertex is the root. I re-verified sufficiency: grouping the reconstruction formula by edge a→b gives `sum_v p_v(i_v) = sum_{a→b}[U_b(i_b) − U_b(i_a) + d_ab(i_a)] ≥ sum A_ab(i_a,i_b)`, and label-wise sums telescope to s(j). So z built from any feasible Z with p≥0 is a genuine full-core point. No hidden partial-core substitution.

### F2 (Info / no defect) — Clipping lemma inequalities verified
- Structural constraints (line 22) are per-layer difference constraints; min-closure and uniform per-layer translation (line 11) are correct, so Z is structurally feasible.
- Nonroot, x-branch: `z_v(j) = U_v^x − ΣZ_b + Σd ≥ U_v^x − ΣU_b^x + Σd = x_v(j)` since Z_b ≤ U_b^x always (independent of which branch attains the min at b). Ties handled.
- Nonroot, y-branch: `z_v(j) ≥ y_v(j) + (s_v − Σ_b s_b)β = y_v(j)+β`. Correct with s_v = 1+Σs_b.
- Root: `z_r(j) ≥ x_r(j)` and `z_r(j) ≥ y_r(j) − (k−1)β` using Σ_b s_b = k−1. Correct.
- Nonnegativity of z follows from x,y ≥ 0 and β ≥ 0; efficiency from telescoping. So z ∈ full core.

Note: the bound `min(x, y+β) ≥ min(x, β)` silently uses y ≥ 0, i.e., y must be a core point (stated at line 52). Harmless but worth making explicit in the lemma statement.

### F3 (Info / no defect) — Threshold and contradiction are exact
With H > kα, choosing α<β<H/k gives `z_r(j) ≥ H − (k−1)β > H/k > β > α`. The condition is tight: a β>α with H−(k−1)β>α exists iff H>kα, so the argument cannot be pushed past 1/k, consistent with sharpness.

Sorted-leximin contradiction (line 62): I checked the case split. Let μ ≤ α be the smallest old value at which some coordinate strictly increases (the target qualifies at α). Entries with old value <μ are unchanged (they are ≤α, weakly increase, and by minimality don't strictly increase); entries at μ weakly increase with at least one strict; entries in (μ,α] stay ≥ old > μ; entries >α stay >α ≥ μ (nonroot via `min(x,y+β)>α`, root via `z≥x`). Hence the sorted prefix below μ is identical and the multiplicity of μ strictly drops with nothing falling to μ or below — strict lexicographic improvement. Covers α=0.

### F4 (Info) — Hand-checked example consistent with the theorem and with tightness beyond m=1
K_{1,3}, m=2, A_{c,leaf}(1,1)=1 on each edge, all other entries 0. Then T=3, all label‑2 payoffs are 0, and with a=p_c(1), b_i=p_leaf_i(1): core is a+Σb_i=3, a+b_i≥1, a+b_i+b_j≥2, all ≥0. Leximin is a=b_i=3/4; H_c=3 (a=3,b=0 is feasible); so x_c/H_c = 1/4 exactly. Leaf ideals are 1, ratios 3/4. So the 1/k bound is attained on a branching star at m=2 as well, and the proof's contradiction correctly does not fire (H = kα exactly, empty β interval). Supports, does not prove.

### F5 (Low) — Sharpness example admissibility
Line 64's m=1 market with a single unit edge is degenerate (zero matrices on other edges). It satisfies the stated admissibility (nonnegative, connected tree, T=1>0) and gives ratio exactly 1/k. If "admissible" were later tightened to require every edge matrix positive, use all edges equal to 1/(k−1) instead — the core is still the simplex and the conclusion is unchanged. No defect under the stated model.

### F6 (Low) — Scope statement accurate
Line 68 correctly limits the result to trees; nothing in the argument (min-closure of per-layer difference constraints, subtree shift bookkeeping) survives a cycle, since the exact cut representation itself requires acyclicity for consistent diagonalization and single crossing edges. The C4 status is unaffected.

## Scope limitations
- No tools; I could not run numeric core/leximin solvers. Verification is by hand algebra and one small hand-computed example (F4).
- I did not re-audit compactness/existence/uniqueness of full leximin (TREE_CORE_AND_PATH.md:46); the argument here only needs existence of some leximin-optimal x, which is standard on a compact set.
- Novelty not assessed, per instructions.

## Verdict
**No findings in reviewed scope.** The closure fact, cut-layer clipping with subtree shifts s_vβ, nonnegative reconstruction bounds, root comparison `H − (k−1)β`, full-core preservation, and the all-stage sorted-leximin contradiction all check out. The argument establishes x_i ≥ H_i/k for every player on every fixed tree, and the m=1 example shows equality, giving c(G)=1/k for trees (including K_{1,3}). Cyclic graphs remain open, as the file states.

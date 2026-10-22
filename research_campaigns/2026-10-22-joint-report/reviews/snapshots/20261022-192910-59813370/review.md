**Provisional verdict: no invalidating findings in reviewed scope.** Both theorems check line by line (coalition worths, core descriptions, averaging, envelope transfers). The most important observation is a scope-wording issue in Theorem 2, not an error.

## Findings

**F1 (Low, scope wording) — `theory/selection_seed_barrier_below_two.txt` lines 66–68.**
"It is not a lower bound for arbitrary eligible mechanisms" is understated. Any eligible mechanism x is own-monotone, so its own-report envelope is itself (sup_{a_i≤b_i} x_i(a_i,b_-i)=x_i(b)), and x restricted to the F_j, L_ij profiles is a covering seed with total ≤ βT. Applying the proof's inequalities directly: β ≥ γ_β·[1+(k−1)/(2m)] with γ_β=1−(β−1)m/(m−1), i.e. β ≥ c(2m−1)/(m−1+cm), c=1+(k−1)/(2m). As k→∞ this gives β ≥ 2−1/m−o(1): a *constant* arbitrary-mechanism bound approaching 2 on this d=k family. This is dominated by the recorded log/loglog rate and is consistent with the min{d,…} upper bound (d=k grows), so it passes the continuation gate as nothing new — but the scope paragraph should say "constant, not growing" rather than "not a lower bound." Verification: substitute x for q and E in lines 25–52.

**F2 (Info) — `theory/selection_efficient_core_envelope_barrier.txt` lines 4–11.**
Existence of an all-profile efficient-core selector on this domain is not shown; core nonemptiness holds for min-of-pool-sums (balanced), and the lower bound would be vacuous rather than false otherwise. No action needed.

**F3 (Info) — randomization, both files.**
Covered correctly by linearity: expected allocations stay in the (convex) core / remain covering with total ≤BT, and E[sup] ≥ sup E, so both "envelope the expectation" and "expectation of per-realization envelopes" satisfy the bound. The budget hypothesis must hold in expectation at all k+C(k,2) displayed profiles including L_ij (the pair charge needs L≤εm there); line 9 says so.

## Verified steps (no issues)
- Thm 1 core at L_ij: four worth-1 coalitions + efficiency force pair sums =1, yielding (λ,λ,1−λ,1−λ); singleton at F_j. a_ij+a_ji=1; Σ_jΣ_{i≠j}a_ij = k(k−1)/2; factor (2+(k−1)/2)/2=(n+6)/8. k=2 sanity: max_j ≥2.5 ⇒ 1.25.
- Thm 2: γ>0 ⟺ m>1/(2−B) ✓; L≤(B−1)m from worth-m coalition ✓; uniform averaging gives q_a+L/(m−1)≥1 ✓; pair charge ≥γ (k=2 degenerate case handled) ✓; sum/(km)=γ[1+(k−1)/(2m)] ✓; threshold B=2−1/m ✓; sharpness assignment at L_ij covers all coalitions (worth ≤ pool-ℓ contribution ≤ payments) with cost 2m−1 ✓, explicitly not a mechanism. m=2,B=1 reproduces Thm 1.
- Fixed owners, fixed technology, genuine single-owner underreports, bad index may depend on q — all as stated.
- Architecture vs arbitrary-mechanism distinction correctly drawn in Thm 1 (domination clause); Thm 1's (n+6)/8 exceeding 1+2√d for large n is consistent only because it is architecture-specific.

## Scope limitations
Snapshot only; `selection_contextual_failures.txt` §2 not supplied (I re-derived the core descriptions independently). No computations run. I did not assess novelty or the 90-minute gate beyond F1's implication.

## Verdict
No counterexample or invalid step found. One scope-wording correction (F1) recommended.

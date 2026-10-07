**Provisional verdict: no findings in reviewed scope.** I traced every step of sections 1–6 against the manuscript's Lemma `weighted-hierarchy` / Theorem `order` and found no invalid step or missing hypothesis. The most delicate step—the disjoint Y/Q budget split in (7)—is correct: (1+α)E Y + (m/R)E Q ≤ max(1+α, m/R)·E[Y+Q] uses only Y,Q ≥ 0 and Y+Q ≤ B·T pointwise.

## Verified steps (evidence in SIMPLE_DAG_SHARP_LOWER.txt)

- **Module/flow identities (ll. 57–78).** Edge count 2Rm+2R+m and vertex count check. Full module flow m+(m−1)h: middle cut bounds it; routing all variable capacity through one left/right fan works because m+(m−1)h ≤ m²−m+1 ≤ H. Series composition gives (3).
- **Coalition support (ll. 70–76, 105–117).** For fixed J, one fan pair with capacity H ≥ Σc_j realizes Σc_j. Second family: type h<d has m−h ≥ q0 low owners; worth is q0 or m ≥ q0, so (5) is valid in both cases. (m−d)·(4)+d·(5): constants give (d+1)m−d²=A; h<d coefficient (m−d)+d(m−d+1)=A; aux coefficient mQ/R. (6) checks.
- **Inclusion probabilities (ll. 80–84).** Per-module uniform independent fan choice gives each auxiliary edge probability exactly 1/R or 0; linearity of expectation gives aux payment ≤ Q/R with no fan-symmetrization needed. Worth is constant across fan choices, so averaging coverage inequalities is legitimate.
- **Symmetrization (ll. 86–102).** Branch permutations are graph automorphisms; module permutations are not graph automorphisms but are game automorphisms (preserve min over module flows for all c, S), which is all the averaging argument needs (same logic as manuscript ll. 318–322). T is preserved.
- **Transport (ll. 134–145).** One variable report 1→m changes exactly one module type; x_h(n) ≤ z_{h+1}(n') is a single-owner monotonicity comparison; multinomial identity and A·p_h/p_{h+1}=α(h+1) match manuscript (455–463).
- **Tail (ll. 151–153, 169–177).** (1−p_0)^k ≤ e^{−k/Z}, T ≤ m(1+d); k_d/Z ≥ 2ℓ gives d·e^{−2ℓ} ≤ d/(d+1)² → 0, so g=√(log d) growth is harmless.
- **Cut count (ll. 159–167).** Minimal a–b cuts are δ⁺(S) for the post-removal reachable set, so C ≤ 2^{#internal}; minimality forces a cut into a single module, giving K=kC exactly.
- **Asymptotics (ll. 179–192).** λ>d ensures monotone Poisson terms; log Z=(1+o(1))d log d; m=d⌈√log(d+1)⌉=o(d log d) absorbs 4m log 2; inversion d=⌊(1−ε)log K/log log K⌋ gives log K_d ≤ (1−ε/2)log K eventually. The at-most-K definition makes monotonicity in K trivial.
- **Section 1 (ll. 29–48).** Pay-the-higher-report rule: below mate payment 0, at equality Q_e/2 ≥ 0, above mate d is constant so Q_e constant → own-monotone. Q_e=0 at d_e=0 for any core allocation (N∖{e} constraint). v(S)=v_d(S*) and p(S) ≥ ΣQ_e(d) ≥ v_d(S*); total = T. Correct.

## Low-severity observations (not errors)

- "Structural cut" is used before being defined as minimal a–b edge cut (l. 159); and the file never states that the manuscript's layered graph has exactly k minimal cuts, which is what makes K the natural generalization of k for the comparison in ll. 17–18.
- Q(n) depends on fan indices (no fan symmetrization); this is harmless since only the total Q is used, but worth stating.

## Scope limitations

- The 1,586 flow checks and C_{2,2}=39, C_{3,3}=689 (ll. 196–202) are agent-reported; no checker output is in the packet. These are supplementary and the proof does not depend on them.
- The upper bound on simple DAGs (l. 19) is not reviewed; the "sharp constant" remark remains conditional.

## Verdict

No findings in reviewed scope. The derivation is a faithful transplant of the manuscript's weighted-hierarchy argument with correctly accounted auxiliary owners.

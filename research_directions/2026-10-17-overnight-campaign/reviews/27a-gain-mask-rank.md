**Provisional verdict: no findings in reviewed scope for Theorems A/B and the §6 identity; insufficient evidence for Theorem C's quoted estimate (4).** Most important point: the 1+2√r coefficient in (5) rests entirely on the unsupplied manuscript bound D_r(a), which neither the proof text nor the checker verifies.

## Findings

**1. Theorem C / (4)–(5): quoted estimate unverified (Medium, scope).** `GAIN_ONLY_…txt:36–43, 180–182`. The document only proves the rule *identity* (residual mask + f_i = (6)); the bound D_r(a) is imported. The checker's min-r block (`check_gain_only_mask.py:122–134`) tests only `original==wrapped`, never `sum(y)<=s+D_r(a)*g`. I did confirm the algebra: with −a−log(1−a) ≤ a²/(2(1−a)) and a=1/(1+√r), D_r(a) ≤ 1/a + ra/(1−a) = 1+2√r. Also note the identity is established for the fixed-priority *global-row* support (§2 line 57), while the default convention (lines 50–56) is face-restricted with +∞. If the manuscript's D_r(a) derivation depended on a specific selection, the transfer must use that one. Verification: add a D_r(a) assertion to the min-r loop; cite the manuscript lemma and its support convention.

**2. Checker never exercises the discontinuous/+∞-price branches (Low).** `check_gain_only_mask.py:35–49`: F is continuous min-linear and `p=min(forms,…)` is always finite (e.g. C_B=0 picks `forms[0]`), so the proof cases "outside-face closed member hits its finite cap" (line 81) and "only the high report is outside" (lines 93–94) are proof-only. I read them independently and find them sound: for i∉B the support face is fixed; b_i−d outside the face ⇒ b_i outside; min of two quantities each rising by ≥F(d) rises by ≥F(d). Mixture tests use a∈{1/2,2/3,1}, not sqrt(2/(n+1)); the step (1)⇒(2) is pure algebra and checks (both terms equal n/√(2(n+1))).

**3. Independent verification of the core steps (Info, no error).**
- Russo–Margulis: −g′(q)=Σ_i E[w(B∪i)−w(B\i)], so −(1−q)g′(q)=E Σ_{i∈B}[w(B)−w(B\i)] (line 112) is correct; integration by parts and g(q)≥(1−q)^nG give exactly (1). The bound is attained for b_1=e_1, b_2=e_2, F=min under the +∞ convention (total = S+B_2(a)G), so Theorem A is tight there, not loose.
- Rank lemma: boundedness of P needs b_i≠0 (hence the null-discard), extreme-point supports are linearly independent ⇒ ≤ rank, Φ convex/Ψ linear, (m−1) count correct; rank-1 forces H≡0 on span(C). The checker's `rank` handles zero rows (rank 0 ⇒ both sides 0).
- H(x)=p·x−F(x): ΣH(b_i)=G and m_i−f_i=H(b_i)+H(C−b_i) verified; grand-marginal coverage via p·b(Q)≥F(b(Q)) and OUT via F(C)−F(C−d)≥F(d) correct.
- Cap coverage (lines 71–83): T−Σ_{h∉Q}f_h ≥ F(b(Q)) by superadditivity; open members' marginals dominate ell_{C_B}(b_h) since C_B−b_h lies in the face. Correct.

## Scope limitations
- The manuscript mask theorem (D_r(a), "three-pool failure") was not in my packet; I cannot audit (4) beyond the algebraic reduction above.
- I did not run the checker; its arithmetic is exact `Fraction`, weights verified nonnegative/summing to 1 (lines 64–68), but coverage is n≤5, d≤4, 12 trials.
- No assessment of novelty, coalition incentives, or efficiency computation (none claimed).

## Verdict
Findings: Theorems A and B and the §6 identity check out on independent reading; Theorem C's numerical estimate (4) is unverified in this snapshot (insufficient evidence), and the checker does not cover it or the discontinuous-F branches.

**Provisional verdict: no findings in reviewed scope.** I re-derived every normalization, cut count, marginal, limit, and both integral formulas; all check out. The most important point to flag is a dependency, not an error: the "overpays its envelope by a linear factor" comparison (lines 55–57) relies on y=z for TTSP graphs via a co-cut theorem not in the packet.

## Findings

**F1 (Low, dependency) — POTENTIAL_OBSTRUCTION.txt:55–57.** "The original envelope on this TTSP graph equals z" and "its total is at most 3/2" presuppose y=z, which THEOREM.txt:160 attributes to an "earlier co-cut theorem" outside the packet. The core no-go (Σp ≳ K/12·T vs. target C·U(K)·T) does not need this; only the "overpay the envelope" phrasing does. Verification: check that t·Pr(a_j∈W) is nondecreasing in t on this graph (with D_{a_i}=t for all serial edges, D_b=½, D_r=1).

**F2 (Informational) — line 27.** "Small numerical samples did not show an aggregate violation." From the exact formulas, the attempted inequality Σ[Ψ(c)−Ψ(c⁰)] ≤ Σz already fails at k=5 (≈1.19 vs ≈1.17) and clearly at k=10 (≈1.48 vs ≈1.21). Not an error in the obstruction, but the remark suggests earlier sampling used k≤4 or was noise-limited; worth a one-line correction.

## Verified steps (no issues)

- **Domination (lines 14–22).** F(D₋ₑU₋ₑ, uDₑ)=min(A+uDₑ,B) with A,B as in THEOREM (4); non-minimal cuts cannot undercut this. g concave, g(0)=0 ⇒ E g(Uₑ)≥g(1)/2; g(1)=min(Dₑ,(B−A)₊) so E g(1)=zₑ exactly (ties measure-zero when Dₑ>0). Ψ(c⁰)≤E F(D₋ₑ(c)U₋ₑ,0) by coordinatewise monotonicity of D. p own-report monotone ⇒ p≥y by THEOREM:174–177.
- **Structure (lines 31–37).** Vertices k+2, owners k+2, structural cuts {r},{a_j,b} ⇒ K=k+1, H=k+1, L=k+1, T=1. D_a=1, D_b=β, D_r=1.
- **Deletion normalizations.** Delete a_j: T=½, D_A=0, D_b=D_r=½ ⇒ Ψ(c⁰)=β·E min(U,U')=β/3. Delete b: k+1 serial unit edges ⇒ 1/(k+2). Delete r: 0.
- **Lower bound.** E min(βU_b,U_r)=β/2−β²/6 ⇒ marginal ≥β(1−β)/6=1/24, pₑ≥1/12, Σp≥k/12.
- **Exact total (line 54)** and limit Ψ→5/24 (bounded convergence, A_k→0 a.s.); Ψ_k−5/24≤1/(k+1) so Σp=k/12+O(1).
- **Integrals (lines 62–72).** Conditional expectations ½−x³/(6β) (x≤β) and ½−x²/2+βx/2−β²/6 (x≥β) re-derived; integration against kx^{k−1} reproduces φ_k term-by-term. Sanity: k=1,β=1 gives 11/24 (direct check ✓); k→∞ gives β/2−β²/6 ✓. q_k re-derived; k→∞ limit ¾ ✓. Base total 1+βq_k ✓.
- Logical scope (lines 48–49, 58–59) correctly limited: Σz≤3/2 here, so neither envelope conjecture is touched.

## Scope limitations

No tools run; no numerics executed beyond hand arithmetic. Co-cut/TTSP monotonicity theorem and the D-normalization properties (THEOREM §2–3) taken as given from the packet. Did not search for alternative potentials.

## Verdict

No findings in reviewed scope. The potential is truthful, coverage-preserving, and dominates z/y as claimed; the k-serial-plus-bypass family is an exact, correctly normalized linear obstruction to O(U(K))T budgets for this specific repair. Only the "overpays y" comparison depends on an external y=z result (F1).

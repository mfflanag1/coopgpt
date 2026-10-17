**Provisional verdict: no substantive findings in reviewed scope.** The lemma's four audited steps check out; the most important observation is that the argument is tight up to the factor 2 (balanced min‑r unit‑bundle example below), so no slack is being hidden.

## Findings

**1. Own‑bit conditioning identity (2) — verified.** (LOW_RANK…, lines 12–14.) For fixed i, independence of bit i from B∩([n]\{i}) gives E[1{i∉B} h_i(B)] = q·E_{B''}h_i(B'') and E[1{i∈B} h_i(B\{i})] = p·E_{B''}h_i(B''), B'' uniform‑product on [n]\{i}. Summing over i yields (2). No regularity of a(·) is needed; a(B) may depend on B arbitrarily. Verification: a 2‑owner exact enumeration suffices.

**2. Scalar inequality (line 17) — verified for all v_i ≥ 0, G > 0.** Case v ≤ G: 2v/(G+v) ≥ v/G ⇔ v ≤ G. Case v ≥ G: 2v/(G+v) ≥ 1 ⇔ v ≥ G. Second step uses Σ_B v^i = v_i + Σ_{j∈B\{i}} a_j(B\{i}) ≤ v_i + G (constraint applied to the set B\{i}, which is where it is genuinely required) and nonnegativity of off‑diagonal entries. Zero column ⇒ v_i = 0 ⇒ both sides 0. G = 0 is correctly excluded.

**3. Trace ≤ rank with zeros and complex eigenvalues — verified.** V is nonneg with column sums ∈ {0,1}, so ‖V‖₁ ≤ 1 ⇒ ρ(V) ≤ 1. trace V = Σ_k λ_k (algebraic multiplicity, over ℂ) is real, equals Σ Re λ_k ≤ Σ_{λ_k≠0} |λ_k| ≤ #{nonzero λ_k}. alg.mult(0) ≥ geom.mult(0) = |B| − rank V, so #{nonzero} ≤ rank V. Rank over ℂ equals rank over ℝ. Columns lie in π_B(L), dim ≤ D. Line 26's remark is correct; diagonalizability indeed unnecessary.

**4. Ordinary vs nonnegative rank.** Only ordinary linear rank is used (column space ⊆ π_B(L)); nonnegative rank never enters. In the production application, a(B) = bᵀw(B) − f ∈ span{rows of b, f}, so D ≤ d+1 (or, as an analysis bound, rank[bᵀ f] ≤ min(n, d+1)). Correct.

**5. Finite‑M surrogate — verified, with one point worth stating explicitly.** For i ∈ B, supp(b_i) ⊆ supp(C_B), so i's own entry uses only on‑face coefficients and ell_{C_B}(C_B) = F(C_B) gives Σ_{i∈B} a_i(B) = w_game(B) ≤ G (monotonicity of w via superadditivity). Off‑face owners get a_i ≥ G for M large (finitely many (B,i) pairs at a fixed profile; off‑face coordinate sum strictly positive), so min{a_i,G} = G matches the +∞ rule exactly. ell^M is a genuine linear functional on ℝ^d (ell linear on the face, line 65–66 of the context), so a(B) stays in the same (d+1)‑span. B = ∅ (ell_0) is covered: nonzero b_i ⇒ a_i ≥ G, zero b_i ⇒ a_i = 0 = f_i. Suggested statement tweak: say explicitly that M must exceed max over (B,i) of (G + f_i − ell(on‑face part))/‖off‑face part‖₁.

**6. Constants (lines 33–37) — verified.** (1/a)∫₀^a q/(1−q)dq = (−a − log(1−a))/a; −a − log(1−a) ≤ a²/(2(1−a)); with a = 1/(1+√r), r = d+1, coefficient ≤ 1/a + r·a/(1−a) = 1 + 2√r. Open part ≤ G/a from the context's integration by parts. Consistent with Theorem D's 1+2√r (min‑r now gets the slightly weaker √(r+1) from the general route; §7 still gives √r).

**Tightness check (not a defect):** F = min_r, n = rk unit bundles balanced across coordinates, B balanced: a_i(B\{i}) = 1, w(B\{i}) = k−1, trace V = r. So the rank bound cannot be improved below ~D−1 here.

## Scope limitations
No code run; the open‑excess integral and Theorems A–D are taken as supplied context, not re‑derived beyond the constants above. Novelty not assessed.

## Verdict
**No findings** of error in the reviewed claim; only a minor explicitness suggestion on the choice of M.

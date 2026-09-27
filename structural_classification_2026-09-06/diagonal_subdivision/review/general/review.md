# Review: DIAGONAL_SUBDIVISION_NO_GO.md

## Findings

### Verification of the core argument (no defects found)

**Full-team cover, c=d and c≠d (lines 24–30).** For team (a,b,c,d):
p_a+p_b+p_c+p_d = z_a+z_b+z_c + M ≥ A(a,b)+C(b,c)+B(a,c) + M by the source core inequality for source triple (a,b,c). The c-index of the C4 market is identified with the source c-index, so B(a,c) is the correct source entry.
- c=d: B(a,c)=B(a,d) and 1_{c=d}=1, so the second line is equality. ✔
- c≠d: need B(a,c)+M ≥ B(a,d)+0, exactly the hypothesis B(a,d)−B(a,c) ≤ M. ✔
Nonnegativity: z ≥ 0 (singletons worth 0 in a strict market) so all p ≥ M/4 > 0. ✔

**Total and optimum (line 30).** Total = T + 3m(M/4) + m(M/4) = T+mM. Diagonal teams (j,j,j,j) have worth A(j,j)+C(j,j)+B(j,j)+M, summing to T+mM. Cover total = integral matching worth ⇒ LP optimum = integral optimum = T+mM and p is a core point. ✔

**Leximin floor (line 32).** p is a core point with min coordinate ≥ M/4, so the first-stage max-min over the core is ≥ M/4; every coordinate of the leximin vector is ≥ its own minimum = first-stage value. No identification of p with leximin needed. ✔

**Ideal bound (lines 34–36).** Any core point has total T+mM = Σ diagonal team worths and covers each diagonal team, hence each is tight; nonnegativity of teammates gives x_i ≤ team worth ≤ D+M. Ratio ≥ (M/4)/(D+M). ✔ Since all ideals are ≥ M/4 > 0, the "positive ideal" qualifier is vacuous (harmless).

**1/12 specialization (lines 40–44), cross-checked against `source_family.py`.**
- Pair entries: verifier enforces integer 0≤v≤2 (line 35). B entries are only {0,2} (`B[o][o]=B[o][ell]='2'`, line 24–25), row range exactly 2, so M=2 is the minimal admissible bonus. ✔
- Diagonal team values: ℓ: C=1 → 1; o: A=2,B=2,C=0 → 4; r: C=1 → 1. D=4, T=(q+1)+4q+q=6q+1 matches `T=6*q+1`. ✔
- Bound: 2/(4·6) = 1/12, independent of q. Source ratio τ=1/(3q+3)→0. ✔
- Monotonicity in M and scale invariance: M/(4(D+M)) is increasing in M; core/leximin/ideals scale uniformly. ✔
- 5/44 ≈ 0.1136 > 1/12 ≈ 0.0833; consistency remark correct. ✔

**Scope framing.** Line 3, line 46, and line 50 correctly restrict the result to this construction (diagonal bonus M ≥ row-range of B, splitting via this gadget) and explicitly disclaim a universal C4 bound. Not over-promoted.

### Minor / presentational (Low severity)

1. **Line 7 – "strict" should be defined explicitly.** The cover argument only checks full four-teams. If the C4 market allowed edge pairs (e.g., (a,b) earning A(a,b)) to have worth, p need not cover them (source core gives no pair inequalities). The proof is valid only if "strict" means all non-full coalitions have worth 0 (value = max matching by full teams). Suggested verification: add one sentence stating this.

2. **Line 7 – unused hypothesis.** "positive integral grand worth T" plays no role in the argument; either drop it or note it is inherited from the family. Also, the relabeling step tacitly uses that an optimal *integral perfect* matching of worth T exists; this follows from nonnegative worths plus core nonemptiness (LP = IP), and could be stated in one clause.

3. **Uniformity condition worth making explicit.** The bound M/(4(D+M)) is uniform across a family only if D and M are bounded independently of the depth parameter. For this family D=4, M=2 are constants, so the conclusion holds; a general reader applying the lemma to another family needs this caveat.

4. **Line 36 – "every player with positive ideal"** is redundant since H'_i ≥ x'_i ≥ M/4 > 0 for all i; stating this strengthens the claim to "every player" unconditionally (as line 42 already does).

## Scope limitations
- Reviewed only the two supplied files; no tools run. Did not independently verify the source family's core nonemptiness beyond reading the verifier's logic (it checks all m³ triples for both witnesses and the matching efficiency, which suffices).
- Did not check the external claim of a C4 example at 5/44.
- Definitions of "entire core", "ideal", and "leximin" are assumed to be the standard ones (core of the full coalitional game; ideal = max of coordinate over the core; leximin = lexicographic max of sorted vector over the core).

## Verdict
**No findings in reviewed scope** beyond low-severity clarity items. Every cover case, the total/optimum equality, the leximin floor implication, the diagonal-tightness ideal bound, and the 1/12 specialization check out against the frozen family; the document does not overreach to all C4 markets.

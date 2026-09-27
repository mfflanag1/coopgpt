**Provisional verdict: no invalidating findings in reviewed scope (Sections 2, 3, 5); one genuine missing case (I = ∅) and several unstated hypotheses.** I re-derived every inequality in these sections independently; the counting, the coarea argument, the cloning identity, and the rational combination all check out exactly.

## Findings

**F1 (Low–Medium, gap not error). CORE_COMPATIBILITY_UPPER.md:39, 52–57, 84, 187–213 — the case I = ∅ is never covered, yet (5.6) is asserted unconditionally ("MASTER INEQUALITY, valid for any three original core points").**
Evidence: b(t) = "minimum d_j among its internal players" is undefined when a team has no internal player; τ = min_{j∈I} d_j/T and (3.1) likewise require I ≠ ∅. Section 1 only rules out all-leaf teams *"whenever I is nonempty"* (line 37–38), so the configuration "one P-team, three distinct leaf labels" (connected, h = m−|P| = 2, hence not elementary) escapes Sections 2–5 entirely. It is harmless: (4.1) with d_0 = min label worth ≤ T/3 gives R ≤ 1/18 + 17/54 = 20/54 < 2/5. Verification: add an explicit "I = ∅ ⇒ single three-leaf component" clause before (5.2), or state (5.6) with hypothesis I ≠ ∅ (Section 6 separately claims (6.2) forces I ≠ ∅, so the contradiction argument is unaffected).

**F2 (Low, unstated hypotheses).** Lines 60–70, 176–186, 204–206 silently use (i) nonnegativity of original/local core payoffs (needed for y^s_{r,j} ≤ d_j, H_i ≤ d_label, and for discarding retained terms), and (ii) k_j ≥ 1 for every label of a connected component, which makes D_L exactly the leaf-label mass in (2.1) and gives the unmatched counts 2/1/0 in (5.5). Both hold in the frozen class but should be recorded.

**F3 (Low, dependency, not audited here).** Line 183–184 applies (4.1) with the min-worth internal copy designated label 0; this needs the sector permutation implicit in line 140 ("Sector and label permutations permit any one label to be designated 0") and requires the local team to use three *distinct* labels — which is exactly what relocation to distinct copies achieves (line 168–171). Section 4's certificate itself is out of scope.

**Verified as correct (not findings).** (2.1) grouping by sector s is legitimate: P player-disjointness makes retained internal payoffs distinct (r,j) pairs with r ≠ s, and diagonal tightness gives Σ_{r≠s} y^s_{r,j} = d_j − y^s_{s,j}. (2.2) both parts. (3.1): the edge/vertex count K = Σ_{j∈S}(k_j−1)+κ−β−bnd is correct; bnd ≥ κ holds because a boundary-free induced component would be a union of components of a connected graph while missing I∖S; the coarea integral gives Σ(k_j−1)d_j = 2D−D_2 plus min_{j∈I}d_j. Section 5: T′ = T+2D−D_2, C′, and the clone-swap tightness argument are correct; the unmatched-ideal bookkeeping is exact ((k_j−1)Σ_s H_{s,j}, since the k_j used players lie in distinct sectors), so (5.1) holds. I re-derived (5.2)–(5.5) and confirmed the weights 442/333/24 over 799 sum to 1 and cancel q and v exactly, yielding 37/94 − (37/141)p + (61/47)z + (37/94)τ.

## Scope limitations
Sections 1, 4, 6, 7, donor constants, novelty, and all scripts/JSON certificates were not examined; no tools were run. (5.6)'s usefulness depends on Section 6's bounds on z and τ, unverified here.

## Verdict
Findings: one missing case (F1) and two hypothesis-hygiene items (F2, F3); no counterexample and no invalid step found in Sections 2, 3, 5.

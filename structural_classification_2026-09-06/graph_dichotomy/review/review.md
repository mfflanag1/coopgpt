# Review: GRAPH_DICHOTOMY.md and supporting proofs

## Findings

### F1 (Low, documentation consistency) — Stale "open" statements contradict the dichotomy claim
- **ALL_TREES.md:68**: "C4 still has only a finite upper bound (now 5/44 …), so the four-sector milestone and general classification remain incomplete."
- **TREE_CORE_AND_PATH.md:60**: "The four-star and four-cycle remain open in this campaign."
- **GRAPH_DICHOTOMY.md:3, 66**: milestone "completed", classification "proved".

These are load-bearing companion documents cited by GRAPH_DICHOTOMY.md:14; a reader of the packet gets contradictory status statements. Not a mathematical defect, but the scope sections should be updated (or dated) so the record is internally consistent.

*Verification*: text edit only.

### F2 (Low, presentation) — Transfer lemma implicitly assumes the target lies in an old sector
- **GRAPH_DICHOTOMY.md:34**: "The unshifted old ideal witness lifts with target H." This only makes sense when the target is not in the inserted sector d and when j0 is the v-label of the target's diagonal team. Both hold in every application (target c_{L0}, D_{L0}=0, and at later steps the d_s-label of the diagonal L0 team is L0), so nothing breaks, but the lemma as stated should carry the hypothesis explicitly since it is presented as a general k-sector lemma.

*Verification*: add "target belongs to an old sector" to the hypothesis list at line 34.

### Checked and found correct (no finding)

I attempted to break the cyclic half at each of the requested points; none failed.

1. **Cover transfer for arbitrary k (§1, lines 18–23).** With w1 = w0 − B(i,j) + B(i,h) + D_h·1(h=j): case h=j uses z(t) ≥ w0(t); case h≠j uses B(i,j) ≥ 0 and D_h ≥ B(i,h). Lift total T+ΣD equals the extended diagonal matching, so the new integral worth is T+ΣD and the lift is in the entire core. Correct for any k.

2. **Shifted floor lift (lines 25–28).** t = kτ/(k+1): every full team has k old coordinates (−t/k each) and one new (+t), net 0; total −km·t/k + mt = 0; old ≥ τ − τ/(k+1) = t. Correct, uses equal sizes exactly where stated.

3. **Matching shortfall and pinning (lines 30–32).** Extending each P-team by its own v-label gives value w0(t)+D_j; the "every positive D_j occurs as a v-label" hypothesis makes the added bonus exactly ΣD, so shortfall stays δ. |U| = (k+1)(m−r), and Σ_U p ≤ δ = |U|·t on any core point, so on the first optimal face all of U equals t. Correct.

4. **Hypothesis propagation under iteration (line 46).** After each step the a-neighbor's labels in the extended P are still exactly Hset = {O_s, L_s}, D=2 on Hset dominates B's column maxima (B_{O_s,O_s}=B_{O_s,L_s}=2, all other columns zero), and D_{L0}=0 with the target diagonal team all-L0. The induction hypotheses (diagonal-optimal matching, floor δ/[k(m−r)], shortfall δ, target unmatched, ideal witness lifted) are re-established at each step. Correct.

5. **Direct floor formula vs. induction (line 55).** Inductive shifts subtract t_{k+1}/k from every existing coordinate at step k→k+1, where t_k = 1/[k(q+1)]. Identity t_k − t_{k+1}/k = t_{k+1} shows each inserted sector remains at D + t_current; Σ_{k=3}^{ℓ−1} t_{k+1}/k = (1/(q+1))(1/3 − 1/ℓ) = (ℓ−3)t_ℓ/3 matches the stated original-coordinate shift. Old minimum τ_3 − (ℓ−3)t_ℓ/3 = t_ℓ exactly. Correct.

6. **Direct ℓ-cycle team check (my own, not in the packet).** For a team (i at a; h_{ℓ−3},…,h_1 on inserted sectors; j at c; u at b), value − lift cover ≤ B(i,h_{ℓ−3}) − B(i,j) + Σ_s D_{h_s}[1(h_s=h_{s−1}) − 1]. If all h_s = j this is 0; otherwise let s* be the first index (from a's side) where h_{s*}≠h_{s*−1}; then D_{h_{s*}} = D_{h_{ℓ−3}} ≥ B(i,h_{ℓ−3}) and the bound is ≤ −B(i,j) ≤ 0. So the iterated lift is a valid cover for every longer-cycle team. I found **no failing longer-cycle team**.

7. **Source family covers (SOURCE_FAMILY_PROOF.md).** Re-verified all diagonal sums (L,R: 1; O: 4), all C-pair sums for u and y, the four double-entry O cases (u: 4, 4+3τ, 5−3τ, 5; y: 4,4,5,5), disjointness of N_s/E_s, |U| = 3q+3, and H_{c_{L0}} = 1. Correct.

8. **Zero-sector embedding (§3).** Full-team values unchanged; (z,0) covers; P extends by any r distinct labels with unchanged shortfall; pinning and ideal-1 arguments go through verbatim. Zero chords and zero edges to added sectors change nothing since only full teams are productive; the theorem explicitly quantifies over the allowed graph with zero matrices permitted (line 12). Quantifiers on lines 63–66 (∀c>0 ∃q with ratio 1/[K(q+1)] < c, positive T, strictly positive core point, nonnegativity gives c(G) ≥ 0) are correct.

9. **Tree cut representation (TREE_CORE_AND_PATH.md:13–30).** Necessity (label i on S_b, j on complement, subtract tight diagonal j) yields exactly U_b(i)−U_b(j) ≥ A_ab(j,i) − d_ab(j); reconstruction formula and telescoping efficiency verified; sufficiency regroups team sums per edge and uses the constraint with (i,j)=(i_b,i_a). Correct.

10. **Clipping lemma and protection (ALL_TREES.md).** Min-closure and uniform per-layer shifts preserve difference constraints; z_v ≥ min(x_v, y_v+β), z_r ≥ max(x_r, y_r−(k−1)β); with α<β<H/k the target exceeds H/k > β > α, entries ≤ α weakly rise, entries > α stay > α; the two-case lexicographic improvement argument is valid without needing leximin uniqueness. Sharpness with m=1 gives the unit simplex. c(tree) = 1/k correct, including α=0.

## Scope limitations
- No code or numerical checks were run; all verifications are hand calculations on the packet text.
- The path-theorem slack argument (TREE_CORE_AND_PATH.md:34–56) was only skimmed; it is superseded by ALL_TREES.md and is not load-bearing for the dichotomy.
- ../selective_c4/MILESTONE.md and the referenced companion certificate are not in the packet; I did not rely on them.
- No novelty assessment was requested or made.

Suggested independent verification: LP-compute the full leximin and target ideal for the ℓ=5, q=1 market (5 sectors × 4 players, 4^5 teams) and confirm x_target = 1/10, H_target = 1; enumerate all teams against the direct floor formula's cover.

## Verdict
**No load-bearing findings in reviewed scope.** The selective-subdivision lemma generalizes to arbitrary k, iterates with all stated invariants preserved, the direct floor formula agrees with the induction, the zero-sector embedding and quantifiers are sound, and the tree proof/cut representation check out. Only stale scope statements in the companion files (F1) and an implicit hypothesis in the transfer lemma's ideal step (F2) need tidying.

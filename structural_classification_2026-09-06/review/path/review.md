# Review: TREE_CORE_AND_PATH.md

## Findings

**F1 (Low) — Core characterization silently relies on k ≥ 2 and on v(team)=worth (lines 9, 3).**
The claim "core = {p ≥ 0, Σp = T, all full-team covers}" is correct for both integral and fractional coalition values: every v(S) is a (integral or fractional) matching of full teams, so team covers plus p ≥ 0 dominate it; conversely singletons give p ≥ 0 and a full team as a coalition has exactly one feasible matching (itself). The argument does not need the "completion of partial matchings" remark. It does need k ≥ 2 (for k = 1 singletons are productive). Suggested fix: state k ≥ 2 explicitly and note that the integral/fractional distinction is immaterial for the core (T coincides because the projected-edge bound holds for fractional partitions too, by integrality of the bipartite perfect-matching polytope).

**F2 (Low) — T = sum of edge optima: verified; hypothesis "equal sizes" is essential.**
Any partition into m full teams projects to perfect matchings on every edge, and the relabeled diagonal partition attains the sum of edge optima; the tree property guarantees consistent propagation. Correct. Without equal sector sizes the diagonal completion fails; this should be listed as a standing hypothesis rather than an aside.

**F3 (No defect) — Cut representation, index signs, invertibility.**
Checked line 19 against the mixed team (i on S_b, j on complement) minus tight diagonal j: the surviving crossing term is A_ab(parent=j, child=i) − d_ab(j) and internal terms cancel exactly, giving U_b(i) − U_b(j) ≥ A_ab(j,i) − d_ab(j). Line 20 follows from subtracting child subtree sums. Sufficiency regrouping by edges (lines 26–28) is exact using U_0 = 0; the i = j case is 0 ≥ 0. The map U ↦ p is linear with inverse "descendant sum minus internal diagonals", so it is a bijection between the core and the U-polytope, and coordinate maxima H_e are preserved. No error found.

**F4 (No defect) — Network encoding of the path (lines 36–44).**
Slack of anchor→(1,j) is d_01(j) − U_1(j) = p_0(j); of (r,j)→(r+1,j) is d + U_r(j) − U_{r+1}(j) = p_r(j); of (k−1,j)→anchor is U_{k−1}(j) = p_{k−1}(j). Structural arc (r,i)→(r,j) with constant d_{r−1,r}(j) − A_{r−1,r}(j,i) has slack ≥ 0 iff the line-19 inequality with parent r−1 label j, child r label i. Signs are consistent. Note the i = j structural arcs are zero-constant self-loops; harmless for reachability, but simple-cycle extraction must discard them (worth a sentence).

**F5 (Low) — Selected-payoff-slack lemma is cited from an external manuscript; the in-file justification (line 46) suffices but omits two steps.**
I verified the sketch: with R = backward closure of tail(e) under eligible arcs (tight structural arcs, payoff arcs with x_f ≤ x_e), any arc entering R from outside is ineligible, so a shift +ε on R (globally renormalized if the anchor is in R) strictly raises x_e, weakly raises all entries ≤ x_e, decreases only entries > x_e by ≤ ε, and preserves feasibility for small ε; the sorted vector is then strictly lex-larger, contradicting leximin. The two omitted points: (a) if head(e) ∈ R, the eligible path head(e)→tail(e) can be taken simple and cannot use e, so a simple cycle through e exists; (b) leximin existence on the compact core polytope. Both are routine. No dependence on the external manuscript is actually needed.

**F6 (No defect) — Exactly k payoff arcs and the bound (lines 48–52).**
Structural arcs are intra-layer; payoff arcs advance anchor→1→…→k−1→anchor. A simple cycle containing a payoff arc must return to its tail, hence pass the anchor, hence traverse all k transitions exactly once: k payoff arcs. Potentials telescope (anchor potential 0 included), so Σ slacks = Σ constants; at x structural slacks vanish, giving Σ constants = Σ_{payoff f} x_f ≤ k·x_e; for any core y, y_e ≤ Σ slacks(y) = Σ constants. Hence H_e ≤ k·x_e, including x_e = 0 ⇒ H_e = 0. The argument genuinely uses all leximin stages (eligibility threshold x_e varies with e). The m = 1 simplex example gives the matching upper bound. Conclusion c(path_k) = 1/k is sound, provided c is defined as inf over instances of min_e x_e/H_e (with H_e = 0 coordinates excluded or treated as ratio 1) — this definition is not stated in the file.

**F7 (Assessment, no severity) — Branching star obstacle.**
Real for this method: rooting a star at the center gives U_b = p_b for leaves and p_0(j) = Σ_b d_0b(j) − Σ_b U_b(j), a constraint over k−1 potentials, not an arc slack, so the cycle-telescoping step has no analogue. The general perturbation lemma (F5) still applies to any polytope in U-space, but without a cycle there is no k-factor comparison. Nothing in the file implies the bound fails for stars; the k=3, m=1 case is again the simplex (ratio 1/3). Suggested verification: exact-arithmetic LP leximin on random k=3, m=2 and k=4, m=2 stars and cycles, comparing min_e x_e/H_e against 1/k.

## Scope limitations
- Cannot verify the "chain-cycle manuscript" lemma statement; only the in-file sketch was checked.
- No numerical instances were run; F7 verification is a recommendation.
- Novelty not assessed.

## Verdict
**No correctness findings in reviewed scope.** The path theorem c(path_k) = 1/k is valid as argued. Missing explicit hypotheses: k ≥ 2, equal sector sizes as a standing assumption, T > 0, the precise definition of c (handling of H_e = 0), and the two routine steps in the lemma (simple-cycle extraction, leximin existence). The star/cycle cases remain genuinely open; the obstacle is methodological, not evidence of failure.

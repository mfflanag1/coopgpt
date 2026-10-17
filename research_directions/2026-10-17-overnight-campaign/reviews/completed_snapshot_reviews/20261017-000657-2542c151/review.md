**Provisional verdict: no findings of error in reviewed scope.** Every step I could check independently (KKT signs, flow/cover certificate, uniqueness, component formulas, derivative signs, seam-switching, zero-capacity limit) is correct as written. Most important remark: the proof relies on two steps that are true but only implicit, and should be made explicit before promotion (below).

## Findings

**F1 (Low, HUBER_PRICE_THREE_HALVES_CANDIDATE.txt:61–66, 68–72) — implicit lemma: every nonisolated positive-capacity vertex has a tight edge.**
The classification (a)/(b)/(c) and formula (3) presuppose this. It follows from KKT: a nonisolated v with no tight edge has Σλ=0, so c_v h'(p_v)=0 ⇒ p_v=0, contradicting Lemma 1. Not stated. Verification: add one sentence.

**F2 (Low, lines 105–113) — finite-interval argument stated loosely but valid.**
The step "finitely many intersections ⇒ finitely many intervals" needs: each pattern set S_k={s: p(s)=f_k(s)} is closed (continuity), and any boundary point of S_k lies in some S_k∩S_j with f_j≢f_k, which is finite. Hence each S_k is a finite union of intervals/points. I checked this reasoning holds; the text skips it. Also note formulas that coincide identically along the segment must be identified as one formula (derivatives then agree since they derive from the same payment function), which the text does.

**F3 (Info, lines 7–9, 142–145) — scope of "funding".**
Bound (2) is relative to the fractional matching LP. On non-bipartite graphs integral production may be strictly smaller (e.g. triangle (1,1,1): F=3/2, integral=1), so payments may exceed 3/2 of realizable integral output. This is disclosed in LIMITS; not an error, but the claim "extends the depth-two forest result" should be read as: on forests fractional=integral, so the 3/2 strictly supersedes 1.615 there.

**Independently checked steps (exact):**
- h is convex C¹ (h'(½⁻)=h'(½⁺)=1, h(½)=¼ both sides); linear constraints ⇒ KKT necessary and sufficient; multiplier sign c_v h'(p_v)=Σ_{e∋v}λ_e correct.
- Lemma 1 perturbation: raising all zero-price vertices by ε and lowering all price-1 vertices by ε is feasible for small ε (zero/one edges stay tight, one/one and one/interior fine, no zero/zero edges exist); cost change −(Σ_{price-1}c_u)ε + O(ε²) <0. Correct.
- Uniqueness: midpoint-equality in Jensen forces h affine on [p_v,q_v], so disagreement ⇒ both ≥½; the tight-low-neighbor contradiction is correct.
- (3): tight edges from a low vertex stay inside its component ⇒ 2tA=B, t<½ ⇔ B<A.
- (4): λ primal-feasible (h'≤1); r dual-feasible; CS on positive-λ edges and r>0 vertices ⇒ F=Σλ=Σc_v r_v. Component payment (3/2−t)B <(3/2)B; type (b) ratio 1.
- (5): t−(a−b)t/A = t(1−a/A+b/A) ≥0. (6): 1−t+(a−b)/(2A) ≥ 1−t−B/(2A)=1−2t>0. Both hold with regularized A'≥a, B'≥b.
- Zero capacities: a full-graph minimizer of J_c restricted to positive vertices is feasible for the induced problem with equal value, hence equals its unique minimizer; so p(c+ε) converges on positive vertices and payments converge; pointwise limits of monotone functions are monotone. No ghost owner is introduced in the rule.
- Spot checks: path (10,1,0.1) ratio 1.45; triangle (2,1,1) seam at b=1 continuous and monotone on both sides.

## Scope limitations
Snapshot only; no code run; no comparison to the prior 1.615 proof or to original sources; no assessment of novelty or of optimality over all eligible mechanisms (none claimed). Bit-complexity of exact evaluation not reviewed.

## Verdict
No findings of mathematical error in reviewed scope; two low-severity presentational gaps (F1, F2) to close before promotion.

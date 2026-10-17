**Provisional verdict: no findings in reviewed scope.** Both core arguments check out by independent recomputation; the most notable item is a scope gap, not an error: Document 1's pointwise obstruction (line 58–64) relies on an undefined object M_i ("projection envelope"), so only the inequality φ_0 < 1/4 = x_0² is auditable here.

## Findings

**Document 1 (sqrt Shapley obstruction) — verified, no defects found.**
- Coalition values (line 17–19): with unit reports, L_{m−ℓ+1}(c_B) = max(0, j−ℓ+1) for j outside owners present, so v(S)=1 iff veto ∈ S and (A ⊆ S or j ≥ ℓ). Correct. F is a min of concave, homogeneous, monotone terms. Core argument holds (monotonicity of v).
- Shapley (lines 29, 32): ∫₀¹ uᵏ P(Q>u)du = E[Q^{k+1}]/(k+1) by Fubini; Beta(ℓ, m−ℓ+1) moment product matches D. φ_0 = 1 − EQ + D/(k+1) is correct. Recomputed k=2, m=40, ℓ=5: D=5/1763, φ_0=4649/5289, φ_i=5/5289; certificate d²−16ab = 4160/9324507 > 0 is the exact squaring of √a+2√b<1. Correct.
- Asymptotics (lines 43–51): factors increase in j, so the j=k bound is valid; rk²+rk+k+1−3r>0 gives the e^{−3r} step; (4rk+1)k ≤ (4r+1)(k²+1) holds; ℓ>0 needs 2^r>4r, true for r≥5. R ≤ √((4r+1)/k+k⁻⁴)+1/k → 0. Correct; the conclusion "no constant rescaling repairs coverage" follows.
- Pointwise family: symmetric strictly convex minimization gives x_0 = s = 1/2 (with s = t·y); checker's alternating-sum integral for ∫[1−(1−uᵗ)ᵗ] is correct.

**Document 2 (binary-minimum classification) — verified, no defects found.**
- Sufficiency (line 29): upper bounds C/2 and C−C_j valid (each edge has ≥1 endpoint outside any part); antipodal-circle construction has zero same-part overlap exactly when C_j ≤ C/2; identity (2) checks in both cases; weights 1/2, indicator vectors nonnegative.
- Hinge lemma (lines 62–69): all kink hyperplanes pass through the origin, so H_l ≠ H gives codim-2 intersections; the midpoint gap of a binary min across its own kink is strictly positive (α(x)+β(y) < 2α(p)). Sound.
- P4 formula: bipartite ⇒ min-capacity vertex cover; minimal covers {0,2},{1,3},{1,2}. Correct. Paw formula (3): half-integral fractional vertex cover vertices; dominated candidates (A+(B+C)/2, B+(A+C+D)/2) are ≥ listed terms. Correct; witnesses (2,2,1,1), (1,1,3,3) both on H with the stated activity patterns.
- Heredity and forbidden-subgraph argument (lines 104–119): restriction preserves (1); non-transitivity of nonadjacency yields edge uv plus z nonadjacent to both; case analysis on a shortest path to {u,v} is complete. Checker's degree-sequence tests uniquely identify P4 ([1,1,2,2]) and paw ([1,2,2,3]) among 4-vertex graphs.

## Scope limitations
- "Individually own-report monotone" for y_i (Doc 1, line 5) is motivational and unproved in the packet.
- M_i, the "two-input logarithmic full-OUT mechanism", the factor 1+c, and the interval [1.5430633898…,2] are external references; their correctness is not assessed. Document 2's theorem does not depend on them.
- Checker outputs were not executed by me; rational values were recomputed by hand only for the k=2 certificate and the t=16 integral structure.
- Neither document claims unrestricted mechanism impossibility, and none should be inferred.

## Verdict
No findings in reviewed scope for both negative results, with the limitations above.

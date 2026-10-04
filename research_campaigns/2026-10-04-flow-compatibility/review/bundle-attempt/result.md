**Verdict: UNKNOWN for the long side of the bundle class; the short side is proved.** I found neither a proof nor a counterexample for simultaneous maxima on the long side. Below are the proved statements, the exact normal form, and the precise point where the proof stops. Everything is hand-derived; no solver, sampling, new census or web search was used. I read CONTRACT.txt, the obstruction file and the first 200 lines of DISCOVERY.json (case G01 only); INSTANCES.json was not opened.

## Scope
Two-hop bundle only: source arcs a_i ≥ 0 (sum A), sink arcs b_j ≥ 0 (sum B), one player per arc, v(Q,R) = min(a(Q), b(R)), T = min(A,B) > 0. C is the entire original core and H_e = max_C x_e. The arguments use real capacities, so rationals are covered. Nothing here bears on general DAGs of path length ≤ 3 or on C2.

Notation: call the side with the smaller total "short" (set P, capacities p, p(P) = T) and the other "long" (set L, capacities l, l(L) = T + d, d ≥ 0). Core points are written (x on P, y on L). By source/sink symmetry every statement applies with sources short or sinks short.

## Theorem A (short side, proved in full)
If A ≤ B, then H_i = a_i for every source arc, and all are attained at the single core point (x, y) = (a, 0). The dual statement holds for sinks if B ≤ A; if A = B both sides have ideal points.

Proof. The point (a, 0) is in C because a(Q) ≥ min(a(Q), b(R)) and the total is A = T. For the upper bound, x_i ≤ T − v(N∖i) = A − min(A − a_i, B) = a_i. ∎

So the frozen question, within this subclass, reduces entirely to the long side when d > 0.

## Theorem B (exact normal form of the original core)
Put z = p − x on P, ω = (l on L, −p on P) so that ω(N) = d, and v = (y, −z). Then

C ≅ { v ∈ ℝ^N : v(N) = 0, min(ω(A), 0) ≤ v(A) ≤ (ω(A) − d)^+ for all A ⊆ N }.

Proof. For A = R ∪ Q, the constraint x(Q) + y(R) ≥ min(p(Q), l(R)) is p(Q) − z(Q) + y(R) ≥ min(p(Q), l(R)), i.e. v(A) ≥ min(ω(A), 0). Efficiency is v(N) = 0. Singletons give x, y ≥ 0. The upper family is the lower family applied to N∖A. ∎

Consequences, each an exact inequality:
- **(B1) Marginal bound.** y_j ≤ (l_j − d)^+. Subsets of L alone never obstruct: Σ_{j∈S}(l_j − d)^+ ≤ (l(S) − d)^+.
- **(B2) Window equalities (the new mechanism).** If l(S) − d ≤ p(W) ≤ l(S), then y(S) = z(W) at every core point. This is what pushes long maxima strictly below the marginal bound.
- **(B3) Sandwich.** If p(W) ≥ l(S) then 0 ≤ z(W) − y(S) ≤ p(W) − l(S). If p(W) ≤ l(S) − d then 0 ≤ y(S) − z(W) ≤ l(S) − d − p(W).
- **(B4) One-dimensional envelope.** With c = l − y: (x, c) is core iff c(R) ≤ x(Q) + (l(R) − p(Q))^+ for all Q, R and c(L) = x(P) + d. The first family alone implies c(L) ≤ x(P) + d, so C is the face of that cone-like polyhedron where c(L) − x(P) is maximal.

Check against G01 (sources (3,3) long, sinks (2,2,1) short, d = 1): B2 forces y_1 = y_2 = z_1 = z_2 and z_3 = 0, and A = {both 2-capacity sinks, one source} gives z_1 ≤ 1. Hence H = (1,1) for the sources against a marginal bound of 2, matching the stored certificate.

## Theorem C (long side, proved subcases)
- **C1. One short arc.** The long projection is {y ≥ 0 : y(S) ≤ (l(S) − d)^+}, with top y*_j = (l_j − d)^+ by B1.
- **C2. Two long arcs of equal capacity, any short side.** For |L| = 2 the core is: 0 ≤ z ≤ p, y_1 + y_2 = z(P), y_j ≤ β_j(z) := min_W [z(W) + (l_j − d − p(W))^+], with β_j monotone in z. If l_1 = l_2 then β_1 = β_2 = β and H_1 = H_2 = H. Take a core point with y_1 = H; then β(z) ≥ H and z(P) ≤ 2H. Move z linearly towards p: β stays ≥ H and z(P) rises continuously to T ≥ 2H. Stop where z(P) = 2H and set y = (H, H). ∎
- **C3. Two long arcs, all short arcs of equal capacity π.** Averaging over permutations of the short arcs keeps y and makes z = ζ·1. Then y_j ≤ b_j(ζ) with b_j concave and nondecreasing, and y_1 + y_2 = nζ. The function g = b_1 + b_2 − nζ is concave with g(0) = 0 and g(π) ≤ 0, so the feasible ζ form an interval [0, ζ*] with g(ζ*) = 0. The point y = (b_1(ζ*), b_2(ζ*)) is core and dominates every other. ∎
- **C4. Equal short capacity π, every l_j an integer multiple of π with l_j ≤ T, d > 0.** B2 gives y_j = (l_j/π)ζ, and summing gives ζ(n + d/π) = nζ, so ζ = 0. The core is the single point (p, 0).

Checked by hand but not written out as proofs, so treat as unverified:
- |L| = 2 with |P| = 2 and arbitrary capacities: a case analysis gave a top in every case.
- |L| = 3 with equal short capacities: the one counterexample mechanism I tried cannot bind before the singleton bounds do.

## Why the obvious lattice proof fails inside the bundle class
Take p = (5,5), l = (4,4,3), so T = 10 and d = 1. Exact core points:
- x = (2,2), y = (3,2,1), and its mirror y = (2,3,1).
- The join y = (3,3,1) is not in the projection: the coalitions {a,3} and {b,3} force x_a, x_b ≥ 2, so x(P) ≥ 4 > 3.
- Yet a top exists: x = (1,1), y = (3,3,2), which equals the marginal bounds. I checked all 21 coalition inequalities by hand.

So the long projection is not join-closed. Dominating two core points can require raising a third long arc and lowering the short side at the same time.

## Precise obstruction (where the proof stops)
1. Any valid inequality Σ α_j y_j ≤ κ with two or more positive α_j comes from a family {A} with Σ μ_A 1_A = τ·1_N + α and κ = Σ μ_A (ω(A) − d)^+. If every ω(A) ≥ d, then κ = α·l − d(Σμ − τ), which undercuts the marginal sum exactly when Σμ − τ > Σα. Such families exist. For |L| = 2, a 4-partition of P with p(W_1), p(W_2) ≤ l_1 − d and p(W_3), p(W_4) ≤ l_2 − d gives y_1 + y_2 ≤ l_1 + l_2 − 3d.
2. In every instance I worked, the individual maxima dropped by exactly the matching amount. Example: p = (1,1,3,3), l = (3,6), d = 1 has that bound equal to 6 and top (2,4), tight. I have no general proof that the individual maxima always drop to match.
3. For |L| = 2 the missing step is exactly this. Given tight points z¹ (attaining H_1 with y_2 = y_2¹) and z² (attaining H_2 with y_1 = y_1²), find z with β_1(z) ≥ H_1, β_2(z) ≥ H_2 and z(P) ≤ H_1 + H_2. It would suffice that (z¹ ∧ z²)(P) ≥ y_2¹ + y_1². This is unproved, and I am not counting it as progress since it is equivalent to the reduced-game restatement.

A counterexample, if one exists, needs d > 0 and at least two long arcs with l_j > d. By C1–C3 it cannot have |P| = 1, nor |L| = 2 with equal long capacities or with equal short capacities.

## Limitations
- The long-side question (sources if A > B, sinks if B > A) is unresolved for arbitrary capacities.
- Theorem B is an exact reformulation; its content is B2 and B3, not a solution.
- Novelty and priority of A–C against the literature are unchecked.
